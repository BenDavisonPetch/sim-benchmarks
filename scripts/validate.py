#!/usr/bin/env python3
"""validate.py — single source of truth for "not a mess" (SPEC §8.3).

Runs the ten SPEC §8.3 checks across every tests/*/spec.md and the generated
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
# Check 10 — verified-ref identifier resolvable (network; --offline downgrades)
# ---------------------------------------------------------------------------


def check_network_refs(fm: dict, offline: bool, rep: Report, where: str) -> None:
    for ref in fm.get("references") or []:
        if not isinstance(ref, dict):
            continue
        ident = (ref.get("verification") or {}).get("identifier") or {}
        if not ident:
            continue
        if offline:
            rep.warn(where, 10, f"references[{ref.get('key')}] identifier not resolved (--offline)")
            continue
        if verify_refs is None:
            rep.warn(where, 10, "verify_refs unavailable; skipping network resolution")
            return
        ok, detail = verify_refs.resolve_identifier(ident)
        if not ok:
            rep.err(where, 10, f"references[{ref.get('key')}] verified but identifier "
                               f"unresolvable: {detail}")


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
        check_network_refs(fm, args.offline, rep, where)

    check_index(specs, rep)

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
