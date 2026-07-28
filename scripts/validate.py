#!/usr/bin/env python3
"""validate.py — single source of truth for "not a mess" (SPEC §8.3).

Runs the twelve SPEC §8.3 checks across every tests/*/spec.md and the generated
INDEX.tsv. Exits non-zero on any error; warnings never fail the build.

    python3 scripts/validate.py [--offline]

`--offline` downgrades the network-dependent verified-ref resolution (check 10) to a
warning (SPEC §8.3 check 10); every other check still runs.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import speclib as S
from speclib import check_expr

try:
    import verify_refs
except Exception:  # pragma: no cover - verify_refs imports cleanly, but stay defensive
    verify_refs = None


# ---------------------------------------------------------------------------
# Result plumbing
# ---------------------------------------------------------------------------


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def err(self, where: str, check: int, msg: str) -> None:
        self.errors.append(f"[check {check}] {where}: {msg}")

    def warn(self, where: str, check: int, msg: str) -> None:
        self.warnings.append(f"[check {check}] {where}: {msg}")


# ---------------------------------------------------------------------------
# Check 1 — parse + required fields
# ---------------------------------------------------------------------------

# Required frontmatter, per docs/spec-schema.md §1.
# List fields that must be PRESENT (empty list allowed): references, references_unverified,
# reference_results, related_to. `eos` is conditional (check 8).
_REQUIRED_PATHS = [
    "slug", "name", "provenance", "one_liner",
    "physics", "physics.materials", "physics.coupling",
    "dimension", "dimension.intrinsic", "dimension.runnable_in",
    "analysis_treatments",
    "capability_flags", "capability_flags.time_dependent_bc",
    "capability_flags.has_internal_boundaries",
    "geometry_stress",
    "geometry", "geometry.coord_system", "geometry.domain", "geometry.regions",
    "units", "units.system",
    "initial_conditions", "initial_conditions.equilibrium", "initial_conditions.perturbation",
    "parameters",
    "domain_bc",
    "time", "time.t_final",
    "validation_modes",
    "references", "references_unverified", "reference_results", "related_to",
    "headline_score",
]


def _get_path(fm: dict, dotted: str):
    cur = fm
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None, False
        cur = cur[part]
    return cur, True


def check_required(fm: dict, rep: Report, where: str) -> None:
    for path in _REQUIRED_PATHS:
        val, present = _get_path(fm, path)
        if not present:
            rep.err(where, 1, f"missing required field '{path}'")
        elif val is None and path not in ("units.b_field_convention",):
            rep.err(where, 1, f"required field '{path}' is null")
    # units.b_field_convention: key must be present (value may be null, conventions §2)
    units = fm.get("units")
    if isinstance(units, dict) and "b_field_convention" not in units:
        rep.err(where, 1, "missing required field 'units.b_field_convention'")
    # provenance enum
    if fm.get("provenance") not in (None, "literature", "synthesized"):
        rep.err(where, 1, f"provenance '{fm.get('provenance')}' not in [literature, synthesized]")
    # slug must equal the directory name (spec-schema §1.1)
    # (checked by caller which knows the path)
    # perturbation shape
    pert = (fm.get("initial_conditions") or {}).get("perturbation")
    if isinstance(pert, dict):
        if pert.get("combine_rule") not in ("additive", "replace"):
            rep.err(where, 1, "initial_conditions.perturbation.combine_rule must be additive|replace")
        if "fields" not in pert:
            rep.err(where, 1, "initial_conditions.perturbation.fields missing (use [] if none)")
    # >=1 validation mode (SPEC §11.6)
    modes = fm.get("validation_modes")
    if not isinstance(modes, list) or len(modes) < 1:
        rep.err(where, 1, "at least one validation_mode is required (SPEC §11.6)")
        return
    for i, m in enumerate(modes):
        if not isinstance(m, dict):
            rep.err(where, 1, f"validation_modes[{i}] is not a mapping")
            continue
        for fld in ("id", "purpose", "procedure", "inputs",
                    "has_exact_solution", "score", "score_justification"):
            if fld not in m:
                rep.err(where, 1, f"validation_modes[{i}] missing '{fld}'")
        if str(m.get("purpose", "")).strip().lower() in ("compare with literature",
                                                          "compare to literature"):
            rep.err(where, 1, f"validation_modes[{i}].purpose must be specific, never "
                              f"'compare with literature' (SPEC §11.6)")


# ---------------------------------------------------------------------------
# Check 2 — registry id existence (SPEC §11.2)
# ---------------------------------------------------------------------------


def check_registry_ids(fm: dict, reg: S.Registry, rep: Report, where: str) -> None:
    def need(kind: str, id_, ctx: str, allow_none: bool = False):
        if id_ is None:
            return
        if allow_none and id_ == "none":
            return
        if not reg.has(kind, id_):
            rep.err(where, 2, f"{ctx}: '{id_}' is not a registry/{kind} id")

    for m in S._materials(fm):
        need("equations", m.get("base"), "materials[].base")
        for t in m.get("terms") or []:
            need("terms", t, "materials[].terms")
        eos = m.get("eos")
        if isinstance(eos, dict) and eos.get("type"):
            need("eos", eos["type"], "materials[].eos.type")
    need("internal-boundary-kinds", (fm.get("physics") or {}).get("coupling"),
         "physics.coupling", allow_none=True)
    for a in fm.get("analysis_treatments") or []:
        need("analysis-treatments", a, "analysis_treatments")
    need("geometry-stress", fm.get("geometry_stress"), "geometry_stress", allow_none=True)
    need("coord-systems", (fm.get("geometry") or {}).get("coord_system"), "geometry.coord_system")
    for face, spec in (fm.get("domain_bc") or {}).items():
        if isinstance(spec, dict):
            need("bc-types", spec.get("type"), f"domain_bc.{face}.type")
            # A bc-type that declares state_keys (a composite condition, e.g.
            # perfect-conductor) accepts only those keys — a stray key is a silently
            # ignored physical statement otherwise.
            allowed = reg.bc_state_keys.get(spec.get("type"))
            if allowed is not None:
                for k in (spec.get("state") or {}):
                    if k not in allowed:
                        rep.err(where, 2, f"domain_bc.{face}.state.{k}: bc-type "
                                          f"'{spec['type']}' accepts only "
                                          f"{sorted(allowed)}")
    for rr in fm.get("reference_results") or []:
        if isinstance(rr, dict):
            need("wall-pressure-treatments", rr.get("wall_pressure_bc"),
                 f"reference_results[{rr.get('key')}].wall_pressure_bc")
    for ib in fm.get("internal_boundaries") or []:
        kind = ib.get("kind") if isinstance(ib, dict) else ib
        need("internal-boundary-kinds", kind, "internal_boundaries[].kind")
    for m in fm.get("validation_modes") or []:
        if isinstance(m, dict):
            need("procedures", m.get("procedure"), "validation_modes[].procedure")


# ---------------------------------------------------------------------------
# Check 3 — score bounds + headline consistency (SPEC §11.8)
# ---------------------------------------------------------------------------


def check_scores(fm: dict, rep: Report, where: str) -> None:
    modes = fm.get("validation_modes") or []
    for i, m in enumerate(modes):
        if not isinstance(m, dict):
            continue
        s = m.get("score")
        if not (isinstance(s, int) and 1 <= s <= 5):
            rep.err(where, 3, f"validation_modes[{i}].score={s!r} must be an int in 1..5")
    computed = S.headline_score(fm)
    declared = fm.get("headline_score")
    if declared != computed:
        rep.err(where, 3, f"headline_score={declared!r} but max(modes)={computed} (SPEC §11.8)")


# ---------------------------------------------------------------------------
# Check 5 + 7 — reference rules (SPEC §5, §11.5)
# ---------------------------------------------------------------------------


def _identifier_present(ref: dict) -> bool:
    ver = ref.get("verification") or {}
    ident = ver.get("identifier") or {}
    return bool(ident.get("doi") or ident.get("arxiv") or ident.get("url"))


def _using_ref_keys(fm: dict) -> set[str]:
    """SPEC §5.4 rule 1: a using-ref RAN this test — it has a `reference_results[]` row.

    Plus `test_origin.authored_from` (the entry was written from it). A ref cited only as a
    `parameters[].source_ref`, or only as a mode `inputs.reference` of `kind: reference`
    (an empirical model / data source), did NOT run the test and is not a using-ref.
    """
    keys = {rr.get("key") for rr in fm.get("reference_results") or [] if isinstance(rr, dict)}
    authored_from = (fm.get("test_origin") or {}).get("authored_from")
    if authored_from:
        keys.add(authored_from)
    return {k for k in keys if k}


def _meta_year(ref: dict):
    year = ((ref.get("verification") or {}).get("meta") or {}).get("year")
    return year if isinstance(year, int) else None


def check_refs(fm: dict, rep: Report, where: str, offline: bool = False) -> None:
    verified_keys: set[str] = set()
    unverified_keys: set[str] = set()
    for ref in fm.get("references") or []:
        if not isinstance(ref, dict):
            rep.err(where, 5, "references[] entry is not a mapping")
            continue
        key = ref.get("key")
        verified_keys.add(key)
        ver = ref.get("verification") or {}
        if ver.get("status") != "verified":
            rep.err(where, 5, f"references[{key}] must have verification.status: verified "
                              f"(got {ver.get('status')!r}); unverified refs go in references_unverified")
        if not _identifier_present(ref):
            rep.err(where, 5, f"references[{key}] is verified but has no resolvable identifier "
                              f"(doi/arxiv/url) — SPEC §11.5")
        # A using-ref carries the date §5.4 orders attribution by, and a doi/arxiv always has a
        # metadata record to take it from. Not required for url-only or non-using refs, nor when
        # only the Handle API resolved the DOI (existence without metadata — recorded in `source`).
        ident = ver.get("identifier") or {}
        handle_only = "handle api" in str(ver.get("source") or "").lower()
        if key in _using_ref_keys(fm) and (ident.get("doi") or ident.get("arxiv")) \
                and _meta_year(ref) is None and not handle_only:
            rep.err(where, 5, f"references[{key}] is a using-ref with a doi/arxiv but no "
                              f"verification.meta.year — paste it from "
                              f"`verify_refs.py --meta` (SPEC §5.1, §5.4 rule 1)")
    for ref in fm.get("references_unverified") or []:
        if not isinstance(ref, dict):
            continue
        unverified_keys.add(ref.get("key"))
        ver = ref.get("verification") or {}
        if ver.get("status") not in ("unverified", "user-supplied"):
            rep.err(where, 5, f"references_unverified[{ref.get('key')}] status must be "
                              f"unverified|user-supplied (got {ver.get('status')!r})")

    # Check 7 membership target (SPEC §5.3 / §8.3 check 7): reference_result & mode
    # `reference` keys must resolve to the VERIFIED references[] list. `--offline`
    # downgrades this to accept references_unverified[] too, because offline authoring
    # (§5.2B) cannot produce a `verified` ref — the verified-only requirement is enforced
    # online. Mirrors check 10's offline downgrade. (SPEC §8.3 check 7 offline clause.)
    resolvable_keys = verified_keys | unverified_keys if offline else verified_keys
    scope_word = "references[]/references_unverified[]" if offline else "verified references[]"

    # Check 7: reference_results[].key must resolve (SPEC §5.3)
    for rr in fm.get("reference_results") or []:
        if isinstance(rr, dict) and rr.get("key") not in resolvable_keys:
            rep.err(where, 7, f"reference_results[{rr.get('key')}].key not in {scope_word} "
                              f"(SPEC §5.3)")
    # Check 7: provenance-only keys must not leak into the problem block
    for banned in ("method", "resolution", "amr"):
        if banned in fm:
            rep.err(where, 7, f"provenance field '{banned}' present at top level — belongs only in "
                              f"reference_results (SPEC §11.1)")
    # validation_mode.inputs.reference.key resolution
    for m in fm.get("validation_modes") or []:
        if not isinstance(m, dict):
            continue
        ref = (m.get("inputs") or {}).get("reference")
        if isinstance(ref, dict):
            kind, key = ref.get("kind"), ref.get("key")
            if kind == "reference-result":
                if key not in {rr.get("key") for rr in fm.get("reference_results") or []
                               if isinstance(rr, dict)}:
                    rep.err(where, 7, f"mode '{m.get('id')}' inputs.reference (reference-result) "
                                      f"key '{key}' has no matching reference_result")
            elif kind == "reference":
                if key not in resolvable_keys:
                    rep.err(where, 7, f"mode '{m.get('id')}' inputs.reference key '{key}' "
                                      f"not in {scope_word}")


# ---------------------------------------------------------------------------
# Check 6 — expressions parse + aux resolve + units + t/time_dependent_bc
# ---------------------------------------------------------------------------


def check_expressions(fm: dict, rep: Report, where: str) -> None:
    params = S._param_names(fm)
    ic = fm.get("initial_conditions") or {}

    # units tags present (SPEC §8.3 check 6)
    units = fm.get("units") or {}
    if not units.get("system"):
        rep.err(where, 6, "units.system must be present and non-empty")

    # aux: ordered, top-down; no forward references (doc §3)
    available = set(params)
    for a in ic.get("aux") or []:
        if not isinstance(a, dict):
            rep.err(where, 6, "aux entry is not a mapping")
            continue
        r = check_expr(a.get("expr"), available, allow_t=False)
        for e in r.errors:
            rep.err(where, 6, f"aux '{a.get('name')}': {e}")
        if a.get("name"):
            available.add(a["name"])

    all_names = S._all_ic_names(fm)

    def check_field_map(fields: dict, ctx: str, allow_t: bool):
        if not isinstance(fields, dict):
            return
        for var, expr in fields.items():
            r = check_expr(expr, all_names, allow_t=allow_t)
            for e in r.errors:
                rep.err(where, 6, f"{ctx}.{var}: {e}")

    for eq in ic.get("equilibrium") or []:
        if isinstance(eq, dict):
            check_field_map(eq.get("fields") or {}, f"equilibrium[{eq.get('region')}]", allow_t=False)
    pert = ic.get("perturbation") or {}
    for f in pert.get("fields") or []:
        if isinstance(f, dict):
            check_field_map(f.get("fields") or {}, "perturbation", allow_t=False)
    for pot in ic.get("potentials") or []:
        if isinstance(pot, dict):
            r = check_expr(pot.get("expr"), all_names, allow_t=False)
            for e in r.errors:
                rep.err(where, 6, f"potential '{pot.get('name')}': {e}")
    # material_fields expressions
    for m in S._materials(fm):
        for mf in m.get("material_fields") or []:
            if isinstance(mf, dict):
                r = check_expr(mf.get("expr"), all_names, allow_t=False)
                for e in r.errors:
                    rep.err(where, 6, f"material_fields '{mf.get('name')}': {e}")

    # domain_bc state: t allowed; track whether any face uses t
    any_t = False
    for face, spec in (fm.get("domain_bc") or {}).items():
        if not isinstance(spec, dict):
            continue
        for var, expr in (spec.get("state") or {}).items():
            r = check_expr(expr, all_names, allow_t=True)
            for e in r.errors:
                rep.err(where, 6, f"domain_bc.{face}.{var}: {e}")
            if r.uses_t:
                any_t = True

    # t <-> time_dependent_bc biconditional (SPEC §2.3, §8.3 check 6)
    declared = bool((fm.get("capability_flags") or {}).get("time_dependent_bc"))
    if any_t != declared:
        rep.err(where, 6, f"capability_flags.time_dependent_bc={declared} but domain_bc state "
                          f"{'references' if any_t else 'does not reference'} t (SPEC §2.3)")

    # has_internal_boundaries consistency (structural derivation, D-008)
    hib_declared = bool((fm.get("capability_flags") or {}).get("has_internal_boundaries"))
    hib_computed = S.compute_has_internal_boundaries(fm)
    if hib_declared != hib_computed:
        rep.err(where, 6, f"capability_flags.has_internal_boundaries={hib_declared} but structure "
                          f"implies {hib_computed} (coupling/materials/internal_boundaries)")


# ---------------------------------------------------------------------------
# Check 8 — eos iff requires_eos (SPEC §11.11)
# ---------------------------------------------------------------------------


def check_eos(fm: dict, reg: S.Registry, rep: Report, where: str) -> None:
    for m in S._materials(fm):
        base = m.get("base")
        has_eos = isinstance(m.get("eos"), dict)
        req = reg.requires_eos.get(base)
        if req is None:
            continue  # unknown base already flagged by check 2
        if req and not has_eos:
            rep.err(where, 8, f"material '{m.get('name')}' base '{base}' requires_eos but no eos given")
        if not req and has_eos:
            rep.err(where, 8, f"material '{m.get('name')}' base '{base}' has requires_eos=false "
                              f"but declares an eos")


# ---------------------------------------------------------------------------
# Check 9 — baseline.config_delta capability invariance (SPEC §6.3A, §11.13)
# ---------------------------------------------------------------------------


def _apply_delta(fm: dict, delta: dict, rep: Report, where: str) -> dict:
    import copy
    out = copy.deepcopy(fm)
    for path, value in (delta or {}).items():
        cur = out
        parts = str(path).split(".")
        ok = True
        for part in parts[:-1]:
            key = int(part) if part.isdigit() else part
            try:
                cur = cur[key]
            except (KeyError, IndexError, TypeError):
                ok = False
                break
        if ok:
            last = parts[-1]
            try:
                cur[int(last) if last.isdigit() else last] = value
            except (KeyError, IndexError, TypeError):
                pass
    return out


def check_baseline(fm: dict, rep: Report, where: str) -> None:
    canonical = S.compute_capability_set(fm)
    for m in fm.get("validation_modes") or []:
        if not isinstance(m, dict):
            continue
        baseline = m.get("baseline")
        if not isinstance(baseline, dict):
            continue
        if "measured" not in m:
            rep.err(where, 9, f"mode '{m.get('id')}' has baseline but no 'measured' quantity (SPEC §6.3A)")
        delta = baseline.get("config_delta") or {}
        altered = _apply_delta(fm, delta, rep, where)
        if S.compute_capability_set(altered) != canonical:
            rep.err(where, 9, f"mode '{m.get('id')}' baseline.config_delta changes the entry's INDEX "
                              f"capability set — forbidden (SPEC §11.13); flags come from the "
                              f"canonical set only")


# ---------------------------------------------------------------------------
# Check 4 — INDEX.tsv in sync (SPEC §11.4)
# ---------------------------------------------------------------------------


def check_index(specs: list[S.SpecDoc], rep: Report) -> None:
    index_path = S.REPO_ROOT / "INDEX.tsv"
    expected = S.render_index(specs)
    if not index_path.exists():
        rep.err("INDEX.tsv", 4, "does not exist — run scripts/reindex.py")
        return
    actual = index_path.read_text(encoding="utf-8")
    if actual != expected:
        rep.err("INDEX.tsv", 4, "out of sync with specs — run scripts/reindex.py (SPEC §11.4)")


# ---------------------------------------------------------------------------
# Check 11 — test_origin / original_intro consistency (SPEC §5.4)
# ---------------------------------------------------------------------------

_ORIGIN_STATUSES = ("resolved-in-list", "resolved-external", "pending", "synthesized")


def check_test_origin(fm: dict, rep: Report, where: str) -> None:
    """Structural §5.4 enforcement. Entirely offline — no network, runs identically under --offline."""
    refs = [r for r in fm.get("references") or [] if isinstance(r, dict)]
    by_key = {r.get("key"): r for r in refs}
    unverified_keys = {r.get("key") for r in fm.get("references_unverified") or []
                       if isinstance(r, dict)}
    flagged = [r for r in refs if r.get("original_intro") is True]
    flagged_unverified = [k for k in unverified_keys
                          if any((r.get("key") == k and r.get("original_intro") is True)
                                 for r in fm.get("references_unverified") or []
                                 if isinstance(r, dict))]
    using = _using_ref_keys(fm)
    origin = fm.get("test_origin") or {}
    status = origin.get("status")

    # 11a — one originator per test.
    if len(flagged) > 1:
        rep.err(where, 11, f"{len(flagged)} refs carry original_intro: true "
                           f"({', '.join(str(r.get('key')) for r in flagged)}) — at most one per "
                           f"entry (SPEC §5.4 rule 6)")
    # 11b — never on a quarantined ref.
    for k in flagged_unverified:
        rep.err(where, 11, f"references_unverified[{k}] carries original_intro: true — the "
                           f"originator must be a verified ref (SPEC §5.4 rule 6)")

    true_key = flagged[0].get("key") if len(flagged) == 1 else None
    true_year = _meta_year(flagged[0]) if len(flagged) == 1 else None

    # 11c / 11c' — nobody who ran the test may predate the credited originator.
    for k in sorted(using):
        ref = by_key.get(k)
        if ref is None:
            continue                      # membership is check 7's job
        year = _meta_year(ref)
        if year is None:
            # Only worth saying when a year would actually decide something: a lone using-ref
            # (or one with nothing dated to compare against) has no ordering to get wrong.
            if len(using) > 1 or true_year is not None:
                rep.warn(where, 11, f"using-ref {k} has no verification.meta.year — §5.4 ordering "
                                    f"is undecidable for it")
            continue
        if true_year is not None and k != true_key and year < true_year:
            rep.err(where, 11, f"using-ref {k} (meta.year {year}) predates the original_intro ref "
                               f"{true_key} (meta.year {true_year}) — SPEC §5.4 rule 3")
    # No citekey-year-vs-meta.year check: a citekey is a legal opaque label, `meta.year` is the
    # priority date, and the two disagree routinely (preprint year vs print issue). Reporting it
    # produced a permanent, unactionable warning on every run — dropped rather than muted.

    if status is not None and status not in _ORIGIN_STATUSES:
        rep.err(where, 11, f"test_origin.status {status!r} not one of {'|'.join(_ORIGIN_STATUSES)}")
    # 11e — resolved-in-list must name the flagged ref.
    if status == "resolved-in-list":
        ref_key = origin.get("ref")
        if not ref_key:
            rep.err(where, 11, "test_origin.status: resolved-in-list but no test_origin.ref")
        elif ref_key not in by_key:
            rep.err(where, 11, f"test_origin.ref '{ref_key}' is not in references[]")
        elif ref_key != true_key:
            rep.err(where, 11, f"test_origin.ref '{ref_key}' is not the original_intro: true ref "
                               f"({true_key!r}) — SPEC §5.4")
    # 11f — an external or synthesized origin credits no listed ref.
    if status in ("resolved-external", "synthesized") and flagged:
        rep.err(where, 11, f"test_origin.status: {status} but references[{true_key}] carries "
                           f"original_intro: true (SPEC §5.4 rules 2c, 5)")
    if fm.get("provenance") == "synthesized" and status not in (None, "synthesized"):
        rep.err(where, 11, f"provenance: synthesized requires test_origin.status: synthesized "
                           f"(got {status!r}) — SPEC §5.4 rule 5")
    # 11g — an unresolved origin with using-refs present is work left undone, not a verdict.
    if status in (None, "pending") and using:
        rep.warn(where, 11, f"test_origin {'absent' if status is None else 'pending'} while "
                            f"{len(using)} using-ref(s) exist — run /add-refs")


# ---------------------------------------------------------------------------
# Check 12 — wall_pressure_bc declared on conducting-wall entries (SPEC §5.3)
# ---------------------------------------------------------------------------


def check_wall_pressure_bc(fm: dict, rep: Report, where: str) -> None:
    """At a perfectly-conducting wall the physical pressure condition is force balance
    (`registry/bc-types/perfect-conductor.md`); references routinely substitute the naive
    homogeneous-Neumann approximation, which changes the near-wall solution. Every
    reference_results row on such an entry must say which it used — `not-stated` when the
    source is silent, so silence is recorded rather than assumed."""
    if not S.has_conducting_wall(fm):
        return
    for rr in fm.get("reference_results") or []:
        if isinstance(rr, dict) and not rr.get("wall_pressure_bc"):
            rep.err(where, 12, f"reference_results[{rr.get('key')}] missing wall_pressure_bc — "
                               f"the entry poses a perfectly-conducting wall (SPEC §5.3); use "
                               f"'not-stated' if the source does not say")


# ---------------------------------------------------------------------------
# Check 10 — verified-ref identifier resolvable (network; --offline downgrades)
# ---------------------------------------------------------------------------


def _norm_title(t: str) -> str:
    """Case/space/punctuation-insensitive title compare (publishers vary on both)."""
    return "".join(ch for ch in str(t).lower() if ch.isalnum())


def check_network_refs(fm: dict, offline: bool, rep: Report, where: str) -> None:
    if offline:
        # One line for the whole run (emitted by the driver), not one per ref: "--offline skipped
        # resolution" is the same fact 15 times over, and the per-ref list is not actionable.
        return
    for ref in fm.get("references") or []:
        if not isinstance(ref, dict):
            continue
        ident = (ref.get("verification") or {}).get("identifier") or {}
        if not ident:
            continue
        if verify_refs is None:
            rep.warn(where, 10, "verify_refs unavailable; skipping network resolution")
            return
        key = ref.get("key")
        r = verify_refs.resolve(ident)
        if r.state == "notfound":
            rep.err(where, 10, f"references[{key}] verified but identifier does not exist: "
                               f"{r.detail}")
            continue
        if r.state == "unreachable":
            # A socket timeout / 5xx must never red the build — existence is undecided,
            # not disproved (SPEC §8.3 check 10).
            rep.warn(where, 10, f"references[{key}] identifier resolution undecided "
                                f"(network): {r.detail}")
            continue
        # Stored `verification.meta` is resolver-derived by contract; the only mechanical
        # detector of hand-typed metadata is comparing it against the live resolution.
        stored = (ref.get("verification") or {}).get("meta") or {}
        if stored.get("year") and r.meta.year and stored["year"] != r.meta.year:
            rep.warn(where, 10, f"references[{key}] meta.year={stored['year']} but resolver "
                                f"reports {r.meta.year} ({r.resolver})")
        if stored.get("title") and r.meta.title and \
                _norm_title(stored["title"]) != _norm_title(r.meta.title):
            rep.warn(where, 10, f"references[{key}] meta.title differs from the resolved title "
                                f"({r.resolver}): {r.meta.title!r}")


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Validate the test-case database (SPEC §8.3).")
    ap.add_argument("--offline", action="store_true",
                    help="downgrade the network verified-ref check to a warning (SPEC §8.3 check 10)")
    args = ap.parse_args(argv)

    rep = Report()
    reg = load_registry_checked(rep)
    specs: list[S.SpecDoc] = []

    for path in S.find_specs():
        where = str(path.relative_to(S.REPO_ROOT))
        try:
            doc = S.load_spec(path)
        except Exception as e:
            rep.err(where, 1, f"failed to parse: {e}")
            continue
        specs.append(doc)
        fm = doc.frontmatter
        # slug == directory name (spec-schema §1.1)
        if fm.get("slug") != path.parent.name:
            rep.err(where, 1, f"slug '{fm.get('slug')}' != directory name '{path.parent.name}'")
        check_required(fm, rep, where)
        check_registry_ids(fm, reg, rep, where)
        check_scores(fm, rep, where)
        check_refs(fm, rep, where, args.offline)
        check_expressions(fm, rep, where)
        check_eos(fm, reg, rep, where)
        check_baseline(fm, rep, where)
        check_test_origin(fm, rep, where)
        check_wall_pressure_bc(fm, rep, where)
        check_network_refs(fm, args.offline, rep, where)

    check_index(specs, rep)
    if args.offline:
        rep.warn("all specs", 10, "identifier resolution skipped (--offline); run online to enforce")

    for w in rep.warnings:
        print(f"WARN  {w}")
    for e in rep.errors:
        print(f"ERROR {e}")
    n_specs = len(specs)
    if rep.errors:
        print(f"\nFAIL: {len(rep.errors)} error(s), {len(rep.warnings)} warning(s) "
              f"across {n_specs} spec(s).")
        return 1
    print(f"\nOK: {n_specs} spec(s) validated, {len(rep.warnings)} warning(s).")
    return 0


def load_registry_checked(rep: Report) -> S.Registry:
    try:
        return S.load_registry()
    except Exception as e:  # pragma: no cover
        rep.err("registry", 2, f"failed to load registry: {e}")
        return S.Registry()


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    sys.exit(main())
