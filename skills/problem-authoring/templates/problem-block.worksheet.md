# problem-block worksheet (SPEC §1.6/§2/§3/§4) — a FILL-AID, not a scaffold

Answer every line below, then transcribe the answers into the single `spec.md` scaffolded from
`templates/spec.template.md` (§11.9 — do NOT create a competing file). Delete this worksheet after.
Each line names the target spec field + the rule that governs it. `R` = required, `O` = optional.

Golden rule for EVERY line: PHYSICAL statement only. No method / resolution / AMR / grid (§1.6).

---

## Identity-driving fields (feed the dedup skill — fill these FIRST)

- [ ] `physics.materials[]`  (R) — per material: `base` (registry/equations id), `terms` (set present,
      nonzero anywhere), `eos` (iff base.requires_eos), `material_fields` (O). Minimize material count
      (§2.4 step 5): merge same-equation regions into one body + coefficient field.
      → material 1: base=____  terms=[____]  eos=____  fields=____
      → material N: ...
- [ ] `physics.coupling`  (R) — registry/internal-boundary-kinds id, or `none`. Physical only.
      → ____
- [ ] `analysis_treatments`  (R) — registry/analysis-treatments set; `[none]` if plain. → [____]
- [ ] `capability_flags.time_dependent_bc`  (R) — any domain_bc[*].state references t? → true/false
- [ ] `capability_flags.has_internal_boundaries`  (R) — coupling!=none OR >1 material OR
      internal_boundaries non-empty? → true/false
- [ ] `geometry_stress`  (R) — registry/geometry-stress id ONLY if purpose-built to stress an
      algorithm; else `none`. → ____

> After these six: run `dedup` (§2.4). If it returns existing-entry, STOP — record a
> reference_result / widen a parameter range instead of authoring a new spec.

## Dimension

- [ ] `dimension.intrinsic`  (R) — smallest dim the problem is defined in. → ____
- [ ] `dimension.runnable_in`  (R) — dims needing NO new analysis (inert extra dims listed). → [____]

## Geometry (physical frame, not a grid)

- [ ] `geometry.coord_system`  (R) — registry/coord-systems id. → ____
- [ ] `geometry.domain`  (R) — per-axis extents in authored units. → { }
- [ ] `geometry.regions[]`  (R) — primitives (box/cylinder/sphere/shell/halfspace/polygon) +
      transforms (rotate/translate). No cell size. → ...

## Units (STORED AS AUTHORED — never convert, §12)

- [ ] `units.system`  (R) — cgs-gaussian|si|code|nondimensional|... → ____
- [ ] `units.b_field_convention`  (R key) — permeability-unity|sqrt-4pi|...|null.
      `null` ONLY with a needs-source row in pending_extraction.md. → ____

## Initial conditions (grammar: docs/ic-expression-language.md; §4)

- [ ] `initial_conditions.aux[]`  (O) — ordered {name, expr, units?}, top-down. → ...
- [ ] `initial_conditions.equilibrium[]`  (R) — base state (may be trivial). {region, fields:{var:expr}}
- [ ] `initial_conditions.perturbation`  (R) — {combine_rule: additive|replace, fields: [] if none}
- [ ] `initial_conditions.potentials[]`  (O) — {name, expr, derives:"B = curl(A)"}
      → Every expr numpy-evaluable? t only in domain_bc/time-dependent fields? functions all on the
        §4 allow-list (else vocab-extension hard-stop)?

## Parameters (values only — never identity, §2.2)

- [ ] `parameters[]`  (R, may be []) — each {name, canonical, meaning WITH units}.
      Reference-defined value ⇒ `canonical: null` + `notes: needs-source` + `source_ref` + a
      pending_extraction.md row. NEVER typed from memory (§5.2). → ...

## Boundary conditions (physical)

- [ ] `domain_bc`  (R) — per face {type (registry/bc-types id), state?}. A face whose state
      references t ⇒ time_dependent_bc=true. Multi-variable-group face ⇒ ONE composite id
      (conducting wall = perfect-conductor, state { vx, vy, vz, Bn }). → ...
- [ ] `internal_boundaries`  (R, may be []) — physical kinds + geometry + motion; no method. → [____]

## Time

- [ ] `time.t_final`  (R) — run-to time so EVERY validation mode can be evaluated. → ____
- [ ] `time.snapshot_times`  (O) — qualitative. → [____]

## Prose body (problem-owned sections)

- [ ] `## Physical problem` — what is physically happening; problem only.
- [ ] `## Qualitative behaviour` — SPECIFIC named features where no exact solution; note symmetry/AMR
      traps.
- [ ] `## Notes` — edge cases, gotchas, unit-convention warnings.

(`## What this test actually tests` + `## Validation notes` → validation-authoring skill.)

---

## Pre-transcribe checklist

- [ ] No method / resolution / AMR / grid anywhere (§1.6, §11.1).
- [ ] eos present IFF base.requires_eos (§11.11 / check 8).
- [ ] capability_flags computed from the CANONICAL set only (§2.3, §11.13).
- [ ] Any new id or function → batched into ONE vocab-extension hard-stop (§7.2), not silently used.
- [ ] Any needs-source parameter → row in pending_extraction.md (§5.2).
