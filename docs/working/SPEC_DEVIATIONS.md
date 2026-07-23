# SPEC_DEVIATIONS — implementation vs SPEC.md

Running catalogue of every place the implementation does not STRICTLY follow `SPEC.md`. Mandatory:
any agent writing code, scripts, registry entries, skills, or docs that deviates from, adds to, or
fills a gap in the spec MUST append an entry in the same commit/stage. No silent deviations.
Reviewers check this file against the diff.

`SPEC.md` is the contract (`SPEC.md` preamble: "deviations require re-grilling"). This file is how a
deviation is surfaced instead of silently absorbed. A stage is not complete while it has unresolved
deviations (see phase-gate rule below).

## What counts (log it)

- **DEV** — deviation: the implementation does something the spec forbids or prescribes differently
  (e.g. a `validate.py` check looser than SPEC §8.3, a schema field renamed, a body-section order
  changed).
- **ELAB** — elaboration: the spec is silent or ambiguous and the implementation had to choose
  (a tolerance, a tie-break, an INDEX column ordering detail, an expression-parser edge case, a
  template wording).
- **INTERIM** — temporary non-compliance scheduled to be fixed in a later stage. Must name the
  removing stage.

Not logged: pure refactors, naming, formatting, or comment changes with identical behaviour; work
that already matches the spec exactly.

## Entry format

One entry per item, newest last:

```
### <ID> [DEV|ELAB|INTERIM] <one-line title>
- Stage/date: Stage <n>, YYYY-MM-DD
- Spec: <section, e.g. §8.3 check 6 / §4>
- Code: <file:lines>
- What: <what the implementation does vs what the spec says / leaves open>
- Why: <forcing reason — spec gap, dependency on a later stage, tooling limit, test failure>
- Impact: <which SPEC §11 invariant(s) affected? state "none" explicitly if none>
- Status: OPEN | SPEC-UPDATE-NEEDED | ACCEPTED (user signed off) | RESOLVED-Stage<n>
```

IDs are sequential: `D-001, D-002, …`.

- **INTERIM** entries start `Status: OPEN` with a named target stage; flip to `RESOLVED-Stage<n>`
  when removed.
- **SPEC-UPDATE-NEEDED** = the resolution is to improve `SPEC.md`, not the code; the user must amend
  the spec, after which the entry flips to `RESOLVED-Stage<n>` (or `ACCEPTED`).
- **ACCEPTED** only after user sign-off. Agents never self-accept a DEV.

The `Impact` line names invariants by their SPEC §11 number where possible, e.g. "§11.1 (no method
in problem block)", "§11.2 (every enum a registry id)", "§11.4 (INDEX generated / not stale)",
"§11.5 (no fabricated refs)", "§11.8 (headline = max of modes)", "§11.9 (one-file, fixed section
order)". State "none" explicitly when nothing is affected.

## Phase-gate rule

Writing to this list is mandatory, and **implementation cannot proceed to the next stage
(IMPLEMENTATION_PLAN.md Stages 1–6) until every deviation logged in the current stage is resolved**,
by one of exactly two routes:

1. **Make the implementation compliant** — change the code/artifact to strictly follow the spec;
   flip the entry to `RESOLVED-Stage<n>`.
2. **Improve the spec** — if the deviation reveals a genuine spec gap or error, re-grill the user
   and amend `SPEC.md`; flip the entry to `RESOLVED-Stage<n>` (or `ACCEPTED` on sign-off).

Concretely, a stage is **not done** while it has:

- any **OPEN DEV** entry;
- any **OPEN INTERIM** entry whose named target stage is the current one or earlier;
- any **SPEC-UPDATE-NEEDED** entry not yet folded into `SPEC.md` or `ACCEPTED`.

Allowed to cross a stage boundary: an **INTERIM** entry whose target stage is strictly later (it is a
pre-registered, tracked debt), and an **ELAB** entry whose `Impact` is `none`. Everything else blocks
the gate.

Final build exit (after Stage 6): zero OPEN entries; every SPEC-UPDATE-NEEDED folded into the spec or
ACCEPTED; every INTERIM flipped to RESOLVED.

---

## Entries

### D-001 [ELAB] `step(t,a,b)` defined as clamped linear ramp
- Stage/date: Stage 1, 2026-07-23
- Spec: §4 ("`step(t, a, b)` (transition helper, defined once in docs)")
- Code: docs/ic-expression-language.md §2.1
- What: SPEC names `step(t,a,b)` and mandates it be defined once in docs but gives no formula.
  Defined as `clip((t-a)/(b-a), 0, 1)`: 0 for t≤a, linear for a<t<b, 1 for t≥b; `a==b` ⇒ Heaviside.
- Why: spec gap — the formula must exist for `validate.py` to implement it (Stage 3) and for the
  worked example's driven inflow (`step(t, step_start_s, step_start_s+step_ramp_s)`) to evaluate.
  Chosen form matches the example's ramp usage.
- Impact: none. Consistent with §2.3 (step/ramp/sinusoid do not fork; BC-state is a value).
- Status: OPEN

### D-002 [ELAB] Volume-weighted norm normalization + Linf active-cell rule
- Stage/date: Stage 1, 2026-07-23
- Spec: §6.1 (`norms` — "L1/L2/Linf, volume-weighted; ... weighted by active volume fraction
  (documented once)")
- Code: docs/procedures.md §1
- What: SPEC says "volume-weighted" without a formula. Defined normalized norms
  `L1 = Σw|e|/Σw`, `L2 = sqrt(Σw e²/Σw)`, `Linf = max|e|` over active cells, with weight
  `w_i = f_i·V_i` (`f_i` = active volume fraction). Normalized (divide by Σw) chosen over
  unnormalized sums; Linf restricted to `f_i>0` cells.
- Why: spec gap — the norm formula is what `validate.py` and every procedure encode literally
  (Stage 3). Normalized form makes norms comparable across resolutions/geometries.
- Impact: none.
- Status: OPEN

### D-003 [ELAB] `conservation-drift` absolute/relative drift forms
- Stage/date: Stage 1, 2026-07-23
- Spec: §6.1 (`conservation-drift` — "total mass / flux vs time")
- Code: docs/procedures.md §8
- What: SPEC names the diagnostic without a drift formula. Defined
  `drift(t) = |Q(t)−Q(0)|` (absolute) or `|Q(t)−Q(0)|/|Q(0)|` (relative, when Q(0)≠0).
- Why: spec gap — a concrete measure is needed for the procedure registry file (Stage 2) and
  `validate.py` (Stage 3).
- Impact: none.
- Status: OPEN

### D-004 [ELAB] Frontmatter required-vs-optional classification
- Stage/date: Stage 1, 2026-07-23
- Spec: §3.1 (schema example with `[]`/default values), §8.3 check 1 ("all required fields present")
- Code: docs/spec-schema.md §1
- What: SPEC §3.1 shows the frontmatter by example but does not enumerate which fields are
  required. Classified each field R/O for `validate.py` check 1: `references`,
  `references_unverified`, `reference_results`, `related_to` marked **required-present** (empty list
  allowed); `eos` conditional on `requires_eos`; `material_fields`, `aux`, `potentials`,
  `snapshot_times`, `baseline`, `source_ref` optional.
- Why: spec gap — check 1 ("all required fields present") needs an explicit required set. Chosen so
  list fields are always present (grep/reindex never key-misses) while allowing `[]`.
- Impact: none (a stricter, not looser, reading of §8.3 check 1; §11 unaffected).
- Status: OPEN
