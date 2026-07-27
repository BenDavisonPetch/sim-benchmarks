#!/usr/bin/env python3
"""verify_refs.py — reference verification gate (SPEC §5.2A, §8.4).

The authoritative trust boundary for citations. A `verified` ref must have a resolvable
identifier (DOI / arXiv / URL); a `verified` ref with no resolvable identifier is a
contradiction and HARD-FAILS the build (SPEC §5.2A, §11.5). References are never
fabricated — this script is the internet-capable check, not a model judgement.

    python3 scripts/verify_refs.py [--offline] [--meta] [--lookup <doi|arxiv:id|url>]

  --offline : skip the live network resolution (warns, leaves statuses untouched); the
              static "verified ⇒ identifier present" gate still runs (SPEC §5.2A).
  --meta    : additionally print a paste-ready `meta:` block per resolved ref, at spec
              indentation, for hand-insertion under `verification:` (SPEC §5.1).
  --lookup  : ad-hoc resolve of one identifier + metadata dump; no specs are read.

Resolution never contacts a publisher landing page. DOIs go to metadata APIs
(Crossref -> DataCite -> the DOI Handle API), which are not bot-blocked and are not
captcha'd; the old `doi.org/<doi>` HEAD followed a redirect to the publisher, where
Wiley/AGU/Science answer 403 to any non-browser request, so valid DOIs could never be
verified. That rung is gone: a DOI that 404s on all three metadata rungs does not exist.

`resolve` (and the back-compat `resolve_identifier` shim) is imported by validate.py for
its check 10 and by cite_chain.py for its Crossref access.

Refs live as structured frontmatter entries per SPEC §5.1 (key + verification{status,
identifier, source, checked, meta}); a ref may also carry a raw `bibtex` string, which is
parsed with bibtexparser when present (SPEC §8.5).

A `--write` / `--write-meta` in-place upgrade is deliberately NOT implemented: PyYAML
cannot round-trip the authored inline comments in a spec's frontmatter (D-012), and
reindex.py's single-scalar-line edit does not generalize to a nested multi-line ref entry.
Promotion and meta insertion are hand-edits driven by this script's report.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import NamedTuple

import yaml

import speclib as S

try:
    import bibtexparser  # noqa: F401  (SPEC §8.5 mandated dep; used for `bibtex` fields)
    _HAVE_BIBTEX = True
except Exception:  # pragma: no cover
    _HAVE_BIBTEX = False

_TIMEOUT = 15
_MAILTO = os.environ.get("CROSSREF_MAILTO") or os.environ.get("SIM_BENCHMARKS_MAILTO")
_UA = "sim-benchmarks-verify-refs/2.0"
if _MAILTO:  # Crossref polite pool
    _UA += f" (mailto:{_MAILTO})"

_ARXIV_NS = "{http://www.w3.org/2005/Atom}"


class RefMeta(NamedTuple):
    """Resolver-derived bibliographic metadata. Never hand-typed (SPEC §5.1)."""

    title: str | None = None
    year: int | None = None
    first_author: str | None = None
    container: str | None = None
    doi: str | None = None
    arxiv: str | None = None

    def as_dict(self) -> dict:
        return {k: v for k, v in self._asdict().items() if v is not None}


class Resolution(NamedTuple):
    state: str            # "found" | "notfound" | "unreachable"
    detail: str           # paste-ready provenance string for `verification.source`
    resolver: str         # crossref|datacite|doi-handle|arxiv-api|arxiv-abs|url-head|none
    meta: RefMeta = RefMeta()

    @property
    def ok(self) -> bool:
        return self.state == "found"


# ---------------------------------------------------------------------------
# HTTP plumbing
# ---------------------------------------------------------------------------


class _Unreachable(Exception):
    """Transport/5xx failure — the resolver could not decide existence."""


def _get(url: str, accept: str = "application/json") -> tuple[int, bytes]:
    """GET a metadata API. Returns (code, body). 404 is a *decision*, not an error."""
    req = urllib.request.Request(url, headers={"User-Agent": _UA, "Accept": accept})
    try:
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
            code = getattr(resp, "status", None) or resp.getcode()
            return code, resp.read()
    except urllib.error.HTTPError as e:
        if e.code in (404, 410):
            return e.code, b""
        raise _Unreachable(f"HTTP {e.code}") from e
    except Exception as e:  # timeout, DNS, TLS, reset
        raise _Unreachable(str(e)) from e


def crossref_work(doi: str) -> dict | None:
    """Crossref metadata for a DOI, or None if Crossref does not have it.

    Raises _Unreachable on transport failure. Shared with cite_chain.py.
    """
    url = f"https://api.crossref.org/works/{urllib.parse.quote(doi, safe='/')}"
    code, body = _get(url)
    if code == 200:
        try:
            return json.loads(body).get("message") or None
        except Exception as e:
            raise _Unreachable(f"crossref: unparseable JSON ({e})") from e
    return None


# ---------------------------------------------------------------------------
# Per-scheme resolvers
# ---------------------------------------------------------------------------


def _crossref_meta(msg: dict) -> RefMeta:
    year = None
    for field in ("issued", "published-online", "published-print", "created"):
        parts = ((msg.get(field) or {}).get("date-parts") or [[]])[0]
        if parts and isinstance(parts[0], int):
            year = parts[0]
            break
    title = (msg.get("title") or [None])[0]
    container = (msg.get("container-title") or msg.get("publisher-name") or [None])
    container = container[0] if isinstance(container, list) else container
    first_author = None
    for a in msg.get("author") or []:
        first_author = a.get("family") or a.get("name")
        if first_author:
            break
    return RefMeta(title=title, year=year, first_author=first_author,
                   container=container or msg.get("publisher"), doi=msg.get("DOI"))


def _datacite_meta(attrs: dict) -> RefMeta:
    title = None
    for t in attrs.get("titles") or []:
        title = t.get("title")
        if title:
            break
    first_author = None
    for c in attrs.get("creators") or []:
        first_author = c.get("familyName") or c.get("name")
        if first_author:
            break
    year = attrs.get("publicationYear")
    return RefMeta(title=title, year=int(year) if isinstance(year, (int, str)) and str(year).isdigit() else None,
                   first_author=first_author, container=attrs.get("publisher"),
                   doi=attrs.get("doi"))


def _resolve_doi(doi: str) -> Resolution:
    """Crossref -> DataCite -> DOI Handle API. No publisher contact anywhere."""
    unreachable: list[str] = []

    try:
        msg = crossref_work(doi)
        if msg:
            return Resolution("found", f"crossref: {doi} -> 200", "crossref", _crossref_meta(msg))
    except _Unreachable as e:
        unreachable.append(f"crossref: {e}")

    try:
        code, body = _get(f"https://api.datacite.org/dois/{urllib.parse.quote(doi, safe='/')}")
        if code == 200:
            attrs = (json.loads(body).get("data") or {}).get("attributes") or {}
            return Resolution("found", f"datacite: {doi} -> 200", "datacite", _datacite_meta(attrs))
    except _Unreachable as e:
        unreachable.append(f"datacite: {e}")
    except Exception as e:
        unreachable.append(f"datacite: {e}")

    # Existence-only rung: the global Handle registry. Carries no bibliographic metadata.
    try:
        code, body = _get(f"https://doi.org/api/handles/{urllib.parse.quote(doi, safe='/')}")
        if code == 200:
            return Resolution("found", f"doi handle api: {doi} -> 200 (existence only, no metadata)",
                              "doi-handle", RefMeta(doi=doi))
    except _Unreachable as e:
        unreachable.append(f"doi-handle: {e}")

    if unreachable:
        return Resolution("unreachable", f"{doi} -> undecided ({'; '.join(unreachable)})", "none")
    return Resolution("notfound", f"{doi} -> 404 on crossref + datacite + handle api (DOI does not exist)",
                      "none")


def _resolve_arxiv(arxiv_id: str) -> Resolution:
    """arXiv API (https — http 301s and drops the query). Bogus ids give an EMPTY feed at 200."""
    bare = arxiv_id.split("arxiv:")[-1].strip()
    url = f"https://export.arxiv.org/api/query?id_list={urllib.parse.quote(bare)}"
    try:
        code, body = _get(url, accept="application/atom+xml")
        if code == 200:
            try:
                feed = ET.fromstring(body)
            except ET.ParseError as e:
                raise _Unreachable(f"arxiv api: unparseable feed ({e})")
            for entry in feed.findall(f"{_ARXIV_NS}entry"):
                eid = (entry.findtext(f"{_ARXIV_NS}id") or "")
                if bare.split("v")[0] not in eid:
                    continue          # 200 + non-matching/placeholder entry is not a hit
                title = " ".join((entry.findtext(f"{_ARXIV_NS}title") or "").split()) or None
                published = entry.findtext(f"{_ARXIV_NS}published") or ""
                year = int(published[:4]) if published[:4].isdigit() else None
                author = entry.find(f"{_ARXIV_NS}author")
                first = None
                if author is not None:
                    name = (author.findtext(f"{_ARXIV_NS}name") or "").strip()
                    first = name.split()[-1] if name else None
                doi = entry.findtext("{http://arxiv.org/schemas/atom}doi")
                journal = entry.findtext("{http://arxiv.org/schemas/atom}journal_ref")
                return Resolution("found", f"arxiv api: {bare} -> 1 entry", "arxiv-api",
                                  RefMeta(title=title, year=year, first_author=first,
                                          container=journal, doi=doi, arxiv=bare))
            return Resolution("notfound", f"arxiv api: {bare} -> 0 entries (id does not exist)", "none")
    except _Unreachable as e:
        # Fallback rung: the abs page (static HTML, not bot-blocked in practice).
        try:
            code2, _ = _get(f"https://arxiv.org/abs/{urllib.parse.quote(bare)}", accept="text/html")
            if code2 == 200:
                return Resolution("found", f"arxiv abs: {bare} -> HTTP 200 (no metadata)",
                                  "arxiv-abs", RefMeta(arxiv=bare))
            return Resolution("notfound", f"arxiv abs: {bare} -> HTTP {code2}", "none")
        except _Unreachable as e2:
            return Resolution("unreachable", f"{bare} -> undecided (arxiv api: {e}; abs: {e2})", "none")
    return Resolution("unreachable", f"{bare} -> undecided (arxiv api: HTTP {code})", "none")


def _resolve_url(url: str) -> Resolution:
    """HEAD, then GET for hosts that reject HEAD. A URL carries no bibliographic metadata."""
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": _UA})
    try:
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
            code = getattr(resp, "status", None) or resp.getcode()
            state = "found" if 200 <= code < 400 else "notfound"
            return Resolution(state, f"{url} -> HTTP {code}", "url-head")
    except urllib.error.HTTPError as e:
        if e.code in (403, 405):
            try:
                req2 = urllib.request.Request(url, headers={"User-Agent": _UA})
                with urllib.request.urlopen(req2, timeout=_TIMEOUT) as resp:
                    code = getattr(resp, "status", None) or resp.getcode()
                    state = "found" if 200 <= code < 400 else "notfound"
                    return Resolution(state, f"{url} -> HTTP {code} (GET)", "url-head")
            except urllib.error.HTTPError as e2:
                return Resolution("notfound" if e2.code in (404, 410) else "unreachable",
                                  f"{url} -> HTTP {e2.code} (GET)", "url-head")
            except Exception as e2:
                return Resolution("unreachable", f"{url} -> {e2}", "url-head")
        if e.code in (404, 410):
            return Resolution("notfound", f"{url} -> HTTP {e.code}", "url-head")
        return Resolution("unreachable", f"{url} -> HTTP {e.code}", "url-head")
    except Exception as e:
        return Resolution("unreachable", f"{url} -> {e}", "url-head")


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

_MEMO: dict[tuple, Resolution] = {}


def resolve(identifier: dict) -> Resolution:
    """Resolve a DOI / arXiv id / URL against metadata APIs only.

    `state` is tri-valued on purpose: `notfound` means the identifier does not exist
    (an ERROR for a `verified` ref), `unreachable` means the network could not decide
    (a WARN — a socket timeout must never red the build).

    A ref carrying BOTH a doi and an arxiv id resolves both and reports the *priority
    date* (`meta.year = min(years)`), since the preprint predates the journal issue.
    """
    identifier = identifier or {}
    key = tuple(sorted((k, str(v)) for k, v in identifier.items() if v))
    if key in _MEMO:
        return _MEMO[key]

    doi, arxiv, url = identifier.get("doi"), identifier.get("arxiv"), identifier.get("url")
    if doi and arxiv:
        rd, ra = _resolve_doi(doi), _resolve_arxiv(arxiv)
        resolver = rd.resolver if rd.ok else ra.resolver
        detail = f"{rd.detail}; {ra.detail}"
        if rd.ok or ra.ok:
            years = [r.meta.year for r in (rd, ra) if r.meta.year]
            merged = (rd.meta if rd.ok else ra.meta)._replace(
                year=min(years) if years else None,
                title=rd.meta.title or ra.meta.title,
                first_author=rd.meta.first_author or ra.meta.first_author,
                container=rd.meta.container or ra.meta.container,
                doi=doi, arxiv=arxiv,
            )
            res = Resolution("found", detail, resolver, merged)
        elif "unreachable" in (rd.state, ra.state):
            res = Resolution("unreachable", detail, "none")
        else:
            res = Resolution("notfound", detail, "none")
    elif doi:
        res = _resolve_doi(doi)
    elif arxiv:
        res = _resolve_arxiv(arxiv)
    elif url:
        res = _resolve_url(url)
    else:
        res = Resolution("notfound", "no doi/arxiv/url identifier", "none")

    _MEMO[key] = res
    return res


def resolve_identifier(identifier: dict) -> tuple[bool, str]:
    """Back-compat shim (see module docstring): (ok, detail)."""
    r = resolve(identifier)
    return r.ok, r.detail


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def _static_gate(fm: dict, where: str, errors: list[str]) -> None:
    """SPEC §5.2A static gate: every verified ref must carry an identifier."""
    for ref in fm.get("references") or []:
        if not isinstance(ref, dict):
            continue
        ver = ref.get("verification") or {}
        ident = ver.get("identifier") or {}
        if ver.get("status") == "verified" and not (
            ident.get("doi") or ident.get("arxiv") or ident.get("url")
        ):
            errors.append(f"{where}: references[{ref.get('key')}] is 'verified' but has no "
                          f"resolvable identifier (contradiction, SPEC §5.2A/§11.5)")


def _meta_block(meta: RefMeta, indent: str = " " * 6) -> str:
    """Paste-ready block YAML for `verification.meta` (titles contain ':', so safe_dump).

    `doi`/`arxiv` are dropped: they already live in `verification.identifier`, and the
    resolver's echoed copy is case-normalized, which would read as a mismatch.
    """
    fields = {k: v for k, v in meta.as_dict().items() if k not in ("doi", "arxiv")}
    body = yaml.safe_dump({"meta": fields}, default_flow_style=False,
                          allow_unicode=True, sort_keys=True, width=100)
    return "\n".join(indent + line for line in body.rstrip("\n").splitlines())


def _print_lookup(ident: dict) -> int:
    r = resolve(ident)
    print(f"state    : {r.state}")
    print(f"resolver : {r.resolver}")
    print(f"detail   : {r.detail}")
    if r.meta.as_dict():
        print("meta     :")
        print(_meta_block(r.meta, indent="  "))
    return 0 if r.ok else 1


def _parse_lookup(raw: str) -> dict:
    raw = raw.strip()
    if raw.startswith("arxiv:"):
        return {"arxiv": raw[len("arxiv:"):]}
    if raw.startswith("http://") or raw.startswith("https://"):
        return {"url": raw}
    if raw.startswith("10."):
        return {"doi": raw}
    return {"arxiv": raw}          # bare arXiv-style id


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Verify references (SPEC §5.2A).")
    ap.add_argument("--offline", action="store_true",
                    help="skip live resolution; static gate still runs")
    ap.add_argument("--meta", action="store_true",
                    help="print a paste-ready verification.meta block per resolved ref")
    ap.add_argument("--lookup", metavar="ID",
                    help="resolve a single doi / arxiv:<id> / url and dump its metadata")
    args = ap.parse_args(argv)

    if args.lookup:
        if args.offline:
            print("ERROR --lookup needs the network (incompatible with --offline)")
            return 1
        return _print_lookup(_parse_lookup(args.lookup))

    errors: list[str] = []
    warnings: list[str] = []
    n_refs = 0

    for path in S.find_specs():
        where = str(path.relative_to(S.REPO_ROOT))
        try:
            doc = S.load_spec(path)
        except Exception as e:
            errors.append(f"{where}: failed to parse: {e}")
            continue
        fm = doc.frontmatter
        _static_gate(fm, where, errors)

        # Report on unverified candidates + attempt resolution online.
        for listname in ("references", "references_unverified"):
            for ref in fm.get(listname) or []:
                if not isinstance(ref, dict):
                    continue
                n_refs += 1
                key = ref.get("key")
                ident = (ref.get("verification") or {}).get("identifier") or {}
                if args.offline:
                    continue          # one summary line at the end, not one per ref
                if not ident:
                    warnings.append(f"{where}: {listname}[{key}] has no identifier to resolve")
                    continue
                r = resolve(ident)
                status = {"found": "RESOLVED", "notfound": "UNRESOLVED",
                          "unreachable": "UNDECIDED"}[r.state]
                print(f"{status} {where}: {listname}[{key}] {r.detail}")
                if args.meta and r.meta.as_dict():
                    print(_meta_block(r.meta))
                if listname == "references":
                    if r.state == "notfound":
                        errors.append(f"{where}: verified references[{key}] does not exist: {r.detail}")
                    elif r.state == "unreachable":
                        warnings.append(f"{where}: verified references[{key}] not decided "
                                        f"(network): {r.detail}")

    if args.offline:
        warnings.append("live resolution skipped (--offline); the static verified⇒identifier gate ran")

    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")

    if errors:
        print(f"\nFAIL: {len(errors)} error(s), {len(warnings)} warning(s), {n_refs} ref(s).")
        return 1
    print(f"\nOK: {n_refs} ref(s) checked, {len(warnings)} warning(s).")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    sys.exit(main())
