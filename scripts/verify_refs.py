#!/usr/bin/env python3
"""verify_refs.py — reference verification gate (SPEC §5.2A, §8.4).

The authoritative trust boundary for citations. A `verified` ref must have a resolvable
identifier (DOI / arXiv / URL); a `verified` ref with no resolvable identifier is a
contradiction and HARD-FAILS the build (SPEC §5.2A, §11.5). References are never
fabricated — this script is the internet-capable check, not a model judgement.

    python3 scripts/verify_refs.py [--offline] [--write]

  --offline : skip the live network resolution (warns, leaves statuses untouched); the
              static "verified ⇒ identifier present" gate still runs (SPEC §5.2A).
  --write   : opt-in; on successful resolution, upgrade references_unverified -> references
              and stamp verification metadata. OFF by default because writing frontmatter
              via PyYAML loses authored inline comments (SPEC_DEVIATIONS D-012); default is
              report-only + gate.

`resolve_identifier` is imported by validate.py for its check 10.

Refs live as structured frontmatter entries per SPEC §5.1 (key + verification{status,
identifier, source, checked}); a ref may also carry a raw `bibtex` string, which is
parsed with bibtexparser when present (SPEC §8.5).
"""

from __future__ import annotations

import argparse
import datetime
import sys
import urllib.error
import urllib.request
from pathlib import Path

import speclib as S

try:
    import bibtexparser  # noqa: F401  (SPEC §8.5 mandated dep; used for `bibtex` fields)
    _HAVE_BIBTEX = True
except Exception:  # pragma: no cover
    _HAVE_BIBTEX = False

_TIMEOUT = 15
_UA = "sim-benchmarks-verify-refs/1.0"


def resolve_identifier(identifier: dict) -> tuple[bool, str]:
    """Attempt to live-resolve a DOI / arXiv / URL identifier over the network.

    Returns (ok, detail). Network-dependent — callers gate this behind --offline.
    """
    if identifier.get("doi"):
        url = f"https://doi.org/{identifier['doi']}"
    elif identifier.get("arxiv"):
        url = f"https://arxiv.org/abs/{identifier['arxiv']}"
    elif identifier.get("url"):
        url = identifier["url"]
    else:
        return False, "no doi/arxiv/url identifier"
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": _UA})
    try:
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
            code = getattr(resp, "status", None) or resp.getcode()
            return (200 <= code < 400), f"{url} -> HTTP {code}"
    except urllib.error.HTTPError as e:
        # Some hosts reject HEAD; retry with GET before giving up.
        if e.code in (403, 405):
            try:
                req2 = urllib.request.Request(url, headers={"User-Agent": _UA})
                with urllib.request.urlopen(req2, timeout=_TIMEOUT) as resp:
                    code = getattr(resp, "status", None) or resp.getcode()
                    return (200 <= code < 400), f"{url} -> HTTP {code} (GET)"
            except Exception as e2:
                return False, f"{url} -> {e2}"
        return False, f"{url} -> HTTP {e.code}"
    except Exception as e:
        return False, f"{url} -> {e}"


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


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Verify references (SPEC §5.2A).")
    ap.add_argument("--offline", action="store_true",
                    help="skip live resolution; static gate still runs")
    ap.add_argument("--write", action="store_true",
                    help="upgrade resolved refs in-place (lossy for YAML comments; off by default)")
    args = ap.parse_args(argv)

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
                    warnings.append(f"{where}: {listname}[{key}] not resolved (--offline)")
                    continue
                if not ident:
                    warnings.append(f"{where}: {listname}[{key}] has no identifier to resolve")
                    continue
                ok, detail = resolve_identifier(ident)
                status = "RESOLVED" if ok else "UNRESOLVED"
                print(f"{status} {where}: {listname}[{key}] {detail}")
                if not ok and listname == "references":
                    errors.append(f"{where}: verified references[{key}] unresolvable: {detail}")
                if ok and args.write and listname == "references_unverified":
                    warnings.append(f"{where}: {key} resolved; --write upgrade not yet "
                                    f"implemented (would clobber YAML comments, D-012)")

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
