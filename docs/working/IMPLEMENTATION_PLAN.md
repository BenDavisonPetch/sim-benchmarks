# Implementation Plan

Build sequence for the Numerical Test-Case Database. `SPEC.md` is the contract; this plan only
sequences the work already mandated there (README "Build status", SPEC §0). Nothing here overrides
the spec — if a stage reveals a spec ambiguity, stop and re-grill rather than improvise.

## State at start of build

Already authored (the seed drop):

- `SPEC.md`, `README.md`
- `registry/equations/{magnetic-diffusion,perfect-conductor,rigid-body}.md` (solid-phase family)
- `registry/internal-boundary-kinds/electromagnetic-coupling.md`
- `skills/add-test/triage.md`
- `templates/pending_extraction.template.md`
- `tests/mercury-magnetosphere-coupled-interior/spec.md` (worked example; will not pass
  `validate.py` until the registry and scripts exist)

Everything else in SPEC §10 is unbuilt.

## Sequencing principle

Later stages consume earlier ones, so the order is fixed by dependency, not preference:

```
docs (pin the details)
  └─> registry seeds (ids that specs reference; procedures cite doc formulae)
        └─> scripts + authoring templates (enforce the schema; scaffold entries)
              └─> index bring-up (generate INDEX.tsv; make the example entry validate green)
                    └─> support skills (shared authoring machinery)
                          └─> command skills (the four user commands compose the above)
```

Each stage is scoped to roughly one working session and ends at a checkable milestone. Stages 3 and
4 may merge if the scripts land cleanly; stages 5–6 may split further if the skills prove heavy.

## Deviation gate (mandatory, every stage)

Any deviation from `SPEC.md` — code the spec forbids, a filled gap, a forced elaboration — MUST be
logged in `docs/working/SPEC_DEVIATIONS.md` in the same commit. No silent deviations. **A stage cannot
proceed to the next until its logged deviations are resolved**, either by making the implementation
compliant or by improving the spec (re-grill + amend). See that file's phase-gate rule for the exact
blocking conditions. This gate is an implicit final clause of every stage's "Done when" below.

---

## Stage 1 — Docs (authoritative detail reference)

**Goal.** Pin every detail the scripts and registry entries must agree with, in prose, before any
code exists. No code dependencies; this stage defines the ground truth downstream stages implement.

**Deliverables** (`docs/`, per SPEC §10):

- `spec-schema.md` — the `spec.md` field reference (SPEC §3), authoritative for every frontmatter
  field and every body section, including which fields are required vs optional and their types.
- `ic-expression-language.md` — the expression grammar (SPEC §4): variables (`x,y,z,r,phi,theta,t`),
  the function allow-list, `step(t,a,b)`, aux-binding evaluation order, material-coefficient
  expressions, equilibrium/perturbation split, potentials. State the allow-list extension protocol
  (logged change to this file + `validate.py`).
- `scoring-rubric.md` — the 1–5 table (SPEC §6.3) verbatim, the max-over-modes headline rule, the
  "no forced proxy" and differential-mode (§6.3A) rules.
- `procedures.md` — the norm / convergence-order / seed-procedure formula definitions (SPEC §6.2),
  defined once so procedure registry files and modes reference rather than re-derive them.
- `conventions.md` — units-as-authored rule (SPEC §12), B-field conventions, naming/style, slug
  rules (SPEC §1.2).

**Done when.** All five files exist and are internally consistent with SPEC §3/§4/§6/§12. Cross-check
that every seed procedure named in SPEC §6.1 has a formula stub in `procedures.md`.

**Risks.** The expression allow-list and the norm formulae are the parts scripts will encode
literally — get them exact here to avoid churn in Stage 3.

---

## Stage 2 — Registry seed vocabulary + registry templates

**Goal.** Author every enum id the contract names and the example entry references. One markdown file
per id (`{id, human_name, definition, params-schema, notes, refs}`, matching the existing solid-phase
files). Mechanical, high-volume.

**Deliverables** (`registry/`, per SPEC §7.1):

- `equations/`: `hydro`, `mhd`, `linear-elastic`, `hyperelastic`, `elastoplastic` (fluid phase; each
  declares `requires_eos: true`). Solid-phase three already exist.
- `terms/`: `viscosity`, `resistivity`, `heat-conduction`, `gravity`.
- `eos/`: `gamma-law`, `stiffened`, `tabulated`.
- `tabulated-eos/`: seed the directory; author named entries only as needed (may stay empty this
  build — note it, don't force).
- `bc-types/`: `periodic`, `reflecting`, `outflow`, `dirichlet`, `neumann`, `perfect-conductor`,
  `subsonic-inflow`, `supersonic-inflow`.
- `coord-systems/`: `cartesian`, `cylindrical`, `spherical`, `axisymmetric`.
- `internal-boundary-kinds/`: `material-contact`, `free-surface`, `rigid-wall`,
  `perfect-conductor-wall`, `symmetry` (`electromagnetic-coupling` already exists).
- `analysis-treatments/`: `none`, `oblique-to-grid`, `axis-singularity`, `multi-material-interface`.
- `geometry-stress/`: seed the directory; author ids as real stress geometries appear (may stay
  empty this build — note it).
- `procedures/`: `norms`, `convergence-order`, `exact-solution-compare`, `self-convergence`,
  `rankine-hugoniot-jump`, `feature-location`, `well-balancing`, `conservation-drift`, `div-b`
  (each citing its formula in `docs/procedures.md`, filling the §6.1 schema).
- `templates/registry-term.template.md`, `templates/procedure.template.md` — copy-and-fill scaffolds
  for future vocab/procedure extension (SPEC §7.2, §10).

**Done when.** Every id referenced by the example spec exists
(`bc-types/{supersonic-inflow,outflow}`, `procedures/feature-location`, `coord-systems/cartesian`,
`eos/gamma-law`, `terms/resistivity`, `equations/mhd`, `analysis-treatments/none`), and every id
named in SPEC §7.1 is present. Equation files correctly declare `requires_eos`; solid-phase
interchangeability predicates unchanged.

**Risks.** Keep `base` semantics (SPEC §7.1: terms as independent toggles) exact — Euler = `hydro`
no terms, Navier–Stokes = `hydro`+`viscosity`, etc. Do not encode method concepts in any
internal-boundary-kind (physical only).

---

## Stage 3 — Scripts + authoring templates

**Goal.** Build the four Python scripts (the single source of truth for "not a mess", SPEC §8) plus
the templates two of them depend on. This is the heavy engineering stage.

**Deliverables:**

- `scripts/validate.py` — all ten SPEC §8.3 checks: parse + required fields; registry-id existence;
  score bounds + headline consistency; INDEX sync (regenerate in-memory, diff, fail on drift);
  ref rules (§5); expression-language parse + aux resolution + `time_dependent_bc` consistency;
  `reference_results[].key` membership + problem/method separation; `eos` iff `requires_eos`;
  `baseline.config_delta` capability-invariance (§6.3A guard); `--offline` downgrades the
  network-dependent identifier check to a warning.
- `scripts/reindex.py` — regenerate `INDEX.tsv` from all `spec.md`; recompute
  `headline_score = max(modes)` and the capability flags from the canonical set (SPEC §8.1/§8.2).
- `scripts/verify_refs.py` — SPEC §5.2A gate; `--offline` supported; hard-fail on a `verified` ref
  with no resolvable identifier.
- `scripts/new_test.py` — scaffold `tests/<slug>/` from `spec.template.md` + empty `assets/`.
- `templates/spec.template.md` — the copy-and-fill entry template mirroring SPEC §3 (frontmatter +
  fixed body-section order).
- `templates/pending_verification.template.md`, `templates/pending_derivation.template.md`.

**Deps.** Python 3 + `pyyaml` + `bibtexparser` (SPEC §8.5). Encodes docs from Stage 1 and validates
against registry from Stage 2.

**Done when.** All scripts run; `validate.py` and `reindex.py` execute against the repo without
crashing (the example entry may still report content gaps — fixed in Stage 4). Network calls remain
the only gated part; `--offline` works throughout.

**Risks.** The expression parser (SPEC §4) is the trickiest piece — numpy-evaluable on a grid, aux
resolution, capability derivation from BC-state `t`-references. Consider splitting the parser into a
shared module if `validate.py` grows large.

---

## Stage 4 — Index bring-up + green example entry

**Goal.** Prove the whole machine green end-to-end on the one seed entry. Generate the index; drive
the example spec to validation.

**Deliverables:**

- Generated `INDEX.tsv` (via `reindex.py`; never hand-edited).
- The example entry `tests/mercury-magnetosphere-coupled-interior/spec.md` passing
  `validate.py --offline`: resolve its residual vocab gaps (gap-C: `dipole` builtin + `step(t,a,b)`
  in the expression allow-list — a logged `docs/ic-expression-language.md` + `validate.py` change),
  and its `needs-source` markers (`gamma`, `b_field_convention`) recorded correctly via
  `pending_extraction.md` rather than fabricated.
- `tests/mercury-magnetosphere-coupled-interior/pending_extraction.md` (from the template) capturing
  the `needs-source` rows.

**Done when.** `validate.py --offline` and `reindex.py` both pass on the full repo; `INDEX.tsv`
matches the in-memory regeneration (no drift). The example entry is the reference for authoring.

**Risks.** The example spec was pressure-tested against the spec but predates the scripts; expect to
reconcile small format deltas. Do not weaken a check to make the entry pass — fix the entry (or, if a
genuine spec ambiguity surfaces, escalate).

**Note.** May fold into the tail of Stage 3 if the scripts land cleanly.

---

## Stage 5 — Support skills + authoring templates

**Goal.** The shared authoring machinery the command skills pull in (SPEC §9.5). Prescriptive,
copy-and-fill, Sonnet-executable, no cleverness.

**Deliverables** (`skills/`):

- `dedup/SKILL.md` — the mechanical §2.4 de-dup procedure (query INDEX → open candidates → structural
  compare modulo numeric values → decision → term-zeroing check → minimal-material canonicalization).
- `problem-authoring/{SKILL.md, templates/}` — filling the problem block within the §1.6 hard
  boundary (no method leakage).
- `validation-authoring/{SKILL.md, templates/}` — building `validation_modes[]`, choosing a
  procedure, scoring per the rubric, differential-mode handling.
- `vocab-extension/{SKILL.md, templates/}` — the §7.2 hard-stop-and-propose flow (draft registry file
  from `registry-term`/`procedure` template, one-word approval).

**Deps.** Stages 1–4 (skills reference docs, registry, scripts, and the worked example).

**Done when.** Each support skill is self-contained and testable by hand against the example entry
(e.g. run the dedup procedure against the seeded INDEX and get the right decision).

---

## Stage 6 — Command skills + commands

**Goal.** The four user-facing commands and their skills, composing the Stage 5 support skills
(SPEC §9.1–§9.4). Thin commands delegate to skills.

**Deliverables:**

- `skills/add-test/SKILL.md` (+ `templates/`) — the §9.1 procedure; `triage.md` already exists.
  Include the bulk orchestrator + subagent carve (§9.1 step 2) and the verbatim skill-contract line
  on no-fabrication (§5.2).
- `skills/find-test/SKILL.md` — §9.2; holds the alias table (§7.3: `Euler`, `Navier-Stokes`,
  `resistive MHD`, `VRMHD`, `θ-pinch`, …). INDEX-first, ranked slugs + coverage gaps.
- `skills/create-test/{SKILL.md, templates/}` — §9.3; dedup-first, mandatory `validation_modes[]`,
  optional `pending_derivation.md`.
- `skills/add-refs/{SKILL.md, templates/}` — §9.4/§5.5; verified-ref enrichment, `original_intro`
  rule (§5.4), resolves `pending_extraction.md`, runs `verify_refs.py` (or emits
  `pending_verification.md` offline).
- `.claude/commands/{add-test,find-test,create-test,add-refs}.md` — thin wrappers delegating to the
  skills.

**Deps.** All prior stages.

**Done when.** Each command runs end-to-end on a trial source and produces a spec that passes
`validate.py`; `/find-test` returns ranked results + coverage gaps against `INDEX.tsv`; the
no-fabrication contract line appears verbatim in `add-test` and `add-refs`.

**Risks.** Largest stage; likely splits. The bulk-consumption orchestrator (§9.1 step 2) is the most
complex single skill — may warrant its own session.

---

## Deferred (SPEC §12 — not built this build)

- `polyhedron` 3D geometry primitive.
- Automated unit-system conversion (deliberately excluded).
- `related_to` auto-linking for capability siblings (SPEC §12 TODO).
- Any GUI / web surface; running the physics codes.

Track these but do not schedule them into the stages above.
