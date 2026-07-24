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

### D-005 [ELAB] `tabulated-eos/` and `geometry-stress/` seeded empty via `.gitkeep`
- Stage/date: Stage 2, 2026-07-23
- Spec: §7.1 (registry layout: `tabulated-eos/`, `geometry-stress/` directories)
- Code: registry/tabulated-eos/.gitkeep, registry/geometry-stress/.gitkeep
- What: SPEC §7.1 lists both directories; the plan (Stage 2) permits them empty this build
  ("author named entries only as needed — may stay empty this build — note it, don't force"). Git
  does not track empty directories, so each is seeded with a `.gitkeep` placeholder (not a registry
  entry — no frontmatter, no `id`).
- Why: forced by git's inability to track empty dirs; no real `tabulated-eos`/`geometry-stress` id
  is referenced by any current entry (incl. the worked example), so none is authored.
- Impact: none. Stage 3 `validate.py` must glob registry entries as `*.md` (so `.gitkeep` is
  ignored) — noted for that stage.
- Status: OPEN

### D-006 [ELAB] Extended machine-readable frontmatter on registry entries
- Stage/date: Stage 2, 2026-07-23
- Spec: §7.1 (per-id file `{ id, human name, definition, params-schema, notes, refs }`)
- Code: registry/{equations,terms,eos,bc-types,coord-systems,internal-boundary-kinds,
  analysis-treatments,procedures}/*.md
- What: SPEC §7.1 names a minimal id schema; entries additionally carry structured frontmatter keys
  beyond `id`/`human_name` — e.g. `kind`, `phase`, `requires_eos`, `velocity`, `evolves`,
  `interchangeable_with/when` (equations); `param_bearing`, `coefficient`, `applies_to` (terms);
  `params` (eos); `requires_state`, `physical` (bc-types); `variables`, `axis_singularity`
  (coord-systems); `formula_ref`, `universal_diagnostic` (procedures). The body keeps the mandated
  `## Definition / ## Params schema / ## Notes / ## Refs` sections (procedures use the §6.1 section
  set: Applies to / Inputs / Steps-formula / Output form / Pass-criterion / Refs).
- Why: the seed solid-phase + `electromagnetic-coupling` files already established extended
  frontmatter; scripts (Stage 3) consume these as machine-readable aids (e.g. `requires_eos` drives
  `validate.py` check 8, §8.3). Additive metadata, filterable and diffable.
- Impact: none (additive; §11.2 registry-id existence and §7.1 body schema unaffected — a superset,
  not a change).
- Status: OPEN

### D-007 [ELAB] Expression check is AST-based, not numeric numpy grid evaluation
- Stage/date: Stage 3, 2026-07-23
- Spec: §4 ("numpy-evaluable on a coordinate grid; validate.py parses and (aux-)resolves"), §8.3
  check 6 ("IC/BC expression language parses; aux bindings resolve"), §8.5 (deps `pyyaml`,
  `bibtexparser`)
- Code: scripts/speclib.py (`check_expr`, `_ExprWalker`, `FUNCTIONS`)
- What: `validate.py` check 6 enforces the §4 grammar via Python's stdlib `ast` — parse, allow-list
  of function names, call arity, permitted operators/nodes, aux top-down ordering (no forward
  refs), and the `t`-scope rule — rather than numerically evaluating each expression on a numpy
  grid. numpy is therefore **not** a dependency.
- Why: §8.5 pins deps to `pyyaml` + `bibtexparser` only; importing numpy (and scipy, for
  `J0/J1/Jn/erf`) to numerically evaluate would violate §8.5. §8.3 check 6's own wording is
  "parses; aux bindings resolve" — exactly what the AST checker delivers. `docs/ic-expression-language.md`
  §7 point 4 phrases the guarantee as "numpy-evaluable on a coordinate grid"; that is delivered
  **structurally** (grammar + allow-list + arity guarantee an expression *would* evaluate), not by
  running an evaluation.
- Impact: none. §11 unaffected; §8.3 check 6 satisfied as written. Doc §7 point 4 wording is
  marginally stronger than the mechanism; left as-is (structural enforcement) — flag for a future
  doc softening if a reviewer prefers, not blocking.
- Status: OPEN

### D-008 [ELAB] `has_internal_boundaries` structural derivation + authored==computed check
- Stage/date: Stage 3, 2026-07-23
- Spec: §2.3 (has_internal_boundaries "present iff ≥1 internal boundary/interface"), §8.3 check 6
  (explicit biconditional given only for `time_dependent_bc`)
- Code: scripts/speclib.py (`compute_has_internal_boundaries`), scripts/validate.py (`check_expressions`)
- What: SPEC gives an explicit `t`⇔`time_dependent_bc` check but no mechanical rule for deriving
  `has_internal_boundaries` from structure. Defined: `true` iff `physics.coupling != none` **or**
  `internal_boundaries` non-empty **or** `>1` material (two materials must meet at an interface).
  `validate.py` additionally enforces `capability_flags.has_internal_boundaries == computed`
  (a check the spec mandates explicitly only for `time_dependent_bc`).
- Why: spec gap — reindex must compute the flag for INDEX (§8.2), so a deterministic rule is
  required; enforcing authored==computed prevents a silently inconsistent identity flag (§11.7).
- Impact: none (a stricter, not looser, consistency check; matches the mercury example
  coupling+multi-material ⇒ true).
- Status: OPEN

### D-009 [ELAB] INDEX `physics_signature` serialization; no interchangeable-base collapsing
- Stage/date: Stage 3, 2026-07-23
- Spec: §2.1 item 1 (physics_signature = materials{base, term-set, eos} + coupling), §2.4
  (interchangeable solid-phase bases collapse under a declared predicate), §8.1
- Code: scripts/speclib.py (`physics_signature`)
- What: SPEC defines physics_signature conceptually but not a string form. Serialized as
  `base(term1|term2)[/eostype]` per material (terms sorted), materials sorted, joined by `+`, with
  `@coupling` appended when coupling != none. Interchangeable-base collapsing (§2.4, e.g.
  perfect-conductor/rigid-body) is **not** applied in the INDEX signature.
- Why: a deterministic string is needed for the grep-cheap INDEX candidate query (§2.4 step 1).
  §2.4/§11 note interchangeability collapsing is a **dedup convention, not a §11 invariant** and
  requires predicate evaluation ("no coupling field present") — handled by the dedup skill
  (Stage 5), not the mechanical index.
- Impact: none (§11 unaffected; dedup step 1 narrows candidates, step 2 does the structural compare).
- Status: OPEN

### D-010 [ELAB] INDEX `has_exact_solution` column = OR over modes
- Stage/date: Stage 3, 2026-07-23
- Spec: §3.1 (`has_exact_solution` is per validation_mode), §8.1 (INDEX has one `has_exact_solution` column)
- Code: scripts/speclib.py (`has_exact_solution`)
- What: `has_exact_solution` is per-mode in the schema but a single INDEX column. Defined as the
  disjunction (true iff **any** mode has an exact solution).
- Why: §8.1 provides one column; find-test's "exact-solution required?" filter (§9.2) wants "does
  this entry offer an exact-solution mode at all" — the OR answers that.
- Impact: none.
- Status: OPEN

### D-011 [ELAB] `reindex.py` writes INDEX.tsv + single-line headline_score write-back only
- Stage/date: Stage 3, 2026-07-23
- Spec: §8.2 (reindex "recomputes headline_score = max(modes) and the capability flags"; §3.1
  headline_score "set by reindex.py"), §11.4 (INDEX generated), §11.8 (headline = max)
- Code: scripts/reindex.py (`_rewrite_headline`, `main`); scripts/validate.py (`check_index`)
- What: `reindex.py` regenerates INDEX.tsv (the derived artifact) and writes the recomputed
  `headline_score` back into each spec.md via a single-line, comment-preserving regex edit of the
  frontmatter. It does **not** rewrite the rest of the frontmatter, and does not write the
  capability flags back into specs. Flags remain authored and are enforced by `validate.py`
  (`time_dependent_bc` check 6 biconditional; `has_internal_boundaries` per D-008); the INDEX flag
  values are computed fresh by reindex per §8.2.
- Why: a full PyYAML round-trip of the frontmatter would destroy authored inline comments — and the
  worked example (mercury) is heavily commented and is the authoring reference. INDEX still carries
  reindex-computed flags (§8.2 satisfied for the derived artifact); validate enforces spec-vs-computed
  consistency, so §11.4/§11.7/§11.8 all hold.
- Impact: none.
- Status: OPEN

### D-012 [ELAB] `verify_refs.py` report-only by default; automated write-back deferred
- Stage/date: Stage 3, 2026-07-23
- Spec: §5.2A (on success "set status: verified"; "entries move references_unverified[] → references[]"),
  §8.4
- Code: scripts/verify_refs.py
- What: `verify_refs.py` performs the §5.2A static gate (a `verified` ref with no resolvable
  identifier HARD-FAILS) and, online, live-resolves identifiers and reports RESOLVED/UNRESOLVED,
  hard-failing an unresolvable `verified` ref. It does **not** mutate spec.md frontmatter to upgrade
  `references_unverified[] → references[]` by default; a `--write` flag is reserved but not yet
  implemented.
- Why: same comment-preservation reason as D-011 — refs are nested multi-key frontmatter entries
  (per §5.1) and PyYAML round-trip is lossy. Stage 3's goal is "scripts run; --offline works; the
  verified-without-identifier contradiction hard-fails" — all satisfied. The upgrade write is a
  skill/manual step (Stage 6 `/add-refs`) or a future `--write`.
- Why-not-INTERIM: no current stage depends on automated write-back; not a scheduled debt this build.
- Impact: none (§11.5 no-fabrication + verified⇒identifier gate fully enforced).
- Status: OPEN

### D-013 [ELAB] INDEX.tsv format details (header row, `dims`, set-cell join, bool spelling)
- Stage/date: Stage 3, 2026-07-23
- Spec: §8.1 (column list; "set-valued cells pipe-joined")
- Code: scripts/speclib.py (`render_index`, `index_row`, `_bool`, `_join_set`)
- What: choices §8.1 leaves open — a leading TSV **header row** naming the columns; the `dims`
  column = `dimension.runnable_in` ints pipe-joined; set cells (`terms`, `analysis_treatments`,
  `bc_types_present`) sorted then `|`-joined (empty set ⇒ empty cell); bools rendered lowercase
  `true`/`false`; rows sorted by slug. `validate.py` regenerates via the same serializer and diffs
  byte-for-byte (check 4).
- Why: §8.1 specifies columns and pipe-joining but not header/ordering/bool spelling; a single
  serializer shared by reindex + validate guarantees they never disagree.
- Impact: none.
- Status: OPEN

### D-014 [ELAB] `parameters` classified required-present; check 7 method-in-prose not scanned
- Stage/date: Stage 3, 2026-07-23
- Spec: §3.1 / spec-schema §1.8 (parameters), §8.3 check 7 ("provenance-only fields never appear in
  the problem block"), D-004 (required-vs-optional classification)
- Code: scripts/validate.py (`_REQUIRED_PATHS`, `check_refs`)
- What: (a) D-004 did not classify `parameters`; `validate.py` treats it as **required-present**
  (empty list allowed), consistent with the schema always showing it. (b) Check 7's "method/
  resolution/amr never in the problem block" is enforced **structurally** — those keys must not
  appear at the spec top level (they belong under `reference_results`) plus `reference_results[].key`
  ∈ `references[]` — but the prose of `## Physical problem` is **not** keyword-scanned for method
  language (unreliable / false-positive prone).
- Why: (a) closes a D-004 gap on the stricter side. (b) a reliable mechanical check covers the
  structural placement; prose method-leakage is an authoring-discipline / review concern, not
  mechanically decidable.
- Impact: none for (a) (stricter). (b): §11.1 is enforced for structured fields; prose method
  leakage is not mechanically caught — a known, accepted limit of check 7.
- Status: OPEN

### D-015 [ELAB] `dipole` field builtin allow-listed; example B-IC written inline (gap-C)
- Stage/date: Stage 4, 2026-07-23
- Spec: §4 (allow-list extension protocol), docs/ic-expression-language.md §2.2/§8, IMPLEMENTATION_PLAN
  Stage 4 (gap-C: "dipole builtin + step(t,a,b) in the allow-list")
- Code: scripts/speclib.py (`FUNCTIONS["dipole"] = 6`); docs/ic-expression-language.md §2.2;
  tests/mercury-magnetosphere-coupled-interior/spec.md (`initial_conditions.equilibrium[interior].B`)
- What: added ONE general, vector-valued field builtin `dipole(mx,my,mz, cx,cy,cz)` to the §4
  allow-list (doc §2.2). The worked example's B IC was rewritten from
  `dipole(moment_from_surface_eq(195e-9, R_M), center=[0,0,0.2*R_M])` (which used a second,
  problem-specific builtin + a keyword argument + a list literal, none in the §4 grammar) to
  `dipole(0, 0, dipole_eq_nT * 1e-9 * R_M**3 / 1e-7, 0, 0, dipole_offset_RM)` — six positional
  scalar args, the moment written **inline** from the surface-equatorial field (no helper builtin,
  no agent-precomputed number, per the user's Stage-4 direction). The center offset `0.2*R_M`
  (≈488 in R_M-unit coords — a units error) was corrected to the declared param `dipole_offset_RM`
  (0.2 R_M). `step(t,a,b)` was already allow-listed (D-001), completing gap-C.
- Why: gap-C is a mandated Stage-4 deliverable; the doc §8 protocol explicitly anticipated a
  `dipole` field builtin. User declined both a precomputed-moment aux and adding a
  `moment_from_surface_eq` builtin (former = error-prone hand derivation; latter = problem-specific
  bloat), directing the moment be defined inline.
- Impact: none. §11.2/§11 unaffected; check 6 passes structurally (AST-only per D-007 — the builtin
  has arity only, no numpy impl). Field convention / units of the moment are units-as-authored
  (§12) and flagged in the entry's pending_extraction.md, not enforced by validate.
- Status: RESOLVED-Stage4

### D-016 [DEV] `validate.py --offline` downgrades check-7 ref-membership to accept unverified refs
- Stage/date: Stage 4, 2026-07-23
- Spec: §5.3 (reference_result key "must be a verified references[] key"), §8.3 check 7
- Code: scripts/validate.py (`check_refs(..., offline)`); SPEC §8.3 check 7 + §5.3 amended
- What: §5.3/§8.3-check-7 require `reference_results[].key` (and a mode `inputs.reference` of
  `kind: reference`) to be a **verified** `references[]` key. Offline authoring (§5.2B) can never
  produce a `verified` ref, so a fully-offline entry that cites a reference_result could never pass
  `validate.py --offline` — contradicting IMPLEMENTATION_PLAN Stage 4's "Done when: --offline
  passes". Resolution (user-approved via Stage-4 grill): amend the spec so `--offline` downgrades
  the check-7 membership target to `references[] ∪ references_unverified[]` (mirroring check 10's
  offline downgrade); **online** still enforces verified-only. `validate.py` threads the `offline`
  flag into `check_refs`. The example's cited refs (winslow2013, anderson2011, hauck2013,
  slavin2009) were added to `references_unverified[]` as unverified claims (no fabricated
  identifiers). Online `validate.py` (no `--offline`) still fails the example on check 7 by design,
  until Stage 6 `/add-refs` verifies the refs online and moves them to `references[]`.
- Why: genuine spec tension between §5.2B (offline ⇒ unverified) and §5.3 (reference_result ⇒
  verified); escalated per the plan's "stop and re-grill on ambiguity" gate rather than improvised.
  User chose the offline-downgrade amendment.
- Impact: none to §11 invariants. §11.5 (no fabricated refs) intact — refs stay unverified and
  INDEX-excluded; the trust boundary (verified⇒indexed) is preserved online. A deliberately looser
  offline reading of §8.3 check 7, now written into the spec.
- Status: RESOLVED-Stage4

### D-017 [ELAB] Stage-5 support-skill templates are fill-worksheets, not competing spec scaffolds
- Stage/date: Stage 5, 2026-07-24
- Spec: §9.5 (support skills `problem-authoring`, `validation-authoring`, `vocab-extension` each carry
  `templates/`), §10 (layout names the `templates/` dirs, not their contents), §11.9 (spec.md is one
  file, template-derived, fixed section order)
- Code: skills/problem-authoring/templates/problem-block.worksheet.md,
  skills/validation-authoring/templates/validation-mode.worksheet.md,
  skills/vocab-extension/templates/proposal.template.md
- What: SPEC names a `templates/` dir per authoring support skill but not what they hold. Rather than a
  second full-file `spec.md` scaffold (which would compete with `templates/spec.template.md` and risk
  divergent section order), each support-skill template is a **fill-aid**: problem-authoring and
  validation-authoring ship *worksheets* (a checklist of the fields they own + the governing rule per
  field, transcribed into the single spec.md), and vocab-extension ships a *proposal message* template
  for the §7.2 hard-stop. The authoritative single-file entry scaffold stays `templates/spec.template.md`.
- Why: preserve §11.9 (one authoritative scaffold, one fixed section order) while still giving each
  support skill the copy-and-fill material §9.5 calls for. `dedup` carries no `templates/` per §10.
- Impact: none. §11.9 preserved (no second entry scaffold); worksheets point back to spec.template.md.
- Status: OPEN

### D-018 [ELAB] dedup step 1 is a two-pass query (strict duplicate + relaxed sibling)
- Stage/date: Stage 5, 2026-07-24
- Spec: §2.4 step 1 (candidate set = same physics_signature AND analysis_treatments AND
  capability_flags), §2.4 step 3 (NEW-SIBLING decision for same physics_signature but differing
  treatments/capability_flags), §2.5 (worked cases requiring sibling identification), §12 TODO
  (related_to auto-linking deferred), D-009 (INDEX signature not interchangeable-collapsed)
- Code: skills/dedup/SKILL.md (steps 0–1)
- What: §2.4 step 1 literally filters the candidate set on all three keys, which alone can never feed
  step 3's NEW-SIBLING branch (a differing capability flag/treatment is excluded from the set). The
  dedup skill therefore runs step 1 as **two passes**: (1a) strict all-three match → duplicate
  candidates for the structural compare; (1b) relaxed same-physics_signature, differing in exactly one
  identity component → siblings for a `related_to` link. 1a also greps interchangeability aliases
  because D-009 leaves the INDEX signature uncollapsed. related_to linking stays manual this build
  (§12 TODO not implemented).
- Why: without 1b the skill returns NEW-ENTRY where §2.5 requires NEW-SIBLING (steady-vs-driven
  inflow, inviscid-vs-viscous KH, 1D-vs-oblique Sod). Faithful to §2.4 step 3 + §2.5 outcomes.
- Impact: none to §11 (dedup convention, not a mechanical invariant; §2.4/§11 note identity structural
  compare is a skill step). Produces the SPEC §2.5 worked-case answers on the seeded INDEX.
- Status: OPEN

