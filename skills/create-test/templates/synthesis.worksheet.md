# synthesis worksheet (SPEC §9.3) — free-text -> identity fields BEFORE de-dup; a FILL-AID

Fill from the `/create-test` description. Purpose: front-load the identity-driving fields so `dedup`
(§2.4) can run **before** anything is scaffolded, and mark this as a synthesized entry. Transcribe the
answers into the single `spec.md` (scaffolded from `templates/spec.template.md`, §11.9) once dedup
clears — do NOT create a competing file. Delete this worksheet after.

Golden rule for every line: PHYSICAL statement only. No method / resolution / AMR / grid (§1.6).

---

## 0. The description
- Free-text need (verbatim): `<paste>`
- Proposed slug (kebab-case, physically descriptive, §1.2): `<slug>`
- `provenance`: **synthesized**  (this is what marks a /create-test entry, not `literature`)

## 1. Identity-driving fields (feed dedup — fill these FIRST, §2.1/§2.3)

- [ ] `physics.materials[]` — per material: `base` (registry/equations id), `terms` (set present,
      nonzero anywhere), `eos` (iff base.requires_eos). Minimize material count (§2.4 step 5).
      → material 1: base=____  terms=[____]  eos=____
      → material N: ...
- [ ] `physics.coupling` — registry/internal-boundary-kinds id, or `none`. → ____
- [ ] `analysis_treatments` — registry/analysis-treatments set; `[none]` if plain. → [____]
- [ ] `capability_flags.time_dependent_bc` — any domain_bc[*].state references t? → true/false
- [ ] `capability_flags.has_internal_boundaries` — coupling!=none OR >1 material OR
      internal_boundaries non-empty? → true/false
- [ ] `geometry_stress` — registry/geometry-stress id ONLY if purpose-built to stress an algorithm;
      else `none`. → ____
- [ ] IC / geometry / BC-state **structural form** (modulo numeric constants — dedup compares FORM):
      region topology, expression shapes, equilibrium+perturbation split. → `<sketch>`

## 2. Run dedup NOW (§2.4) — before scaffolding

- [ ] dedup decision → **existing-entry** / **new-sibling** / **new-entry**
- [ ] existing-entry ⇒ **STOP. Refuse to create.** Point the user to slug `<____>`; their description
      is a parameter variation (offer /add-test to record a reference_result / widen a range).
- [ ] new-sibling ⇒ proceed; note sibling slug(s) for a manual related_to link: [____]
- [ ] new-entry ⇒ proceed.

## 3. Derivation-candidate check (§9.3 step 4) — decide if pending_derivation.md is needed

- [ ] Does this test plausibly admit an EXACT/analytic solution (or a stronger closed-form reference)
      that you CANNOT derive here? → yes/no
- [ ] If yes → emit tests/<slug>/pending_derivation.md (top-level template); the entry keeps a
      PROVISIONAL low score until derived. Do NOT inflate the score in anticipation.
- [ ] If no → score on what is checkable today (rubric rows 1–2, or a self-check it admits).

---

## Hand-off
- Problem fields (§1 above + geometry/units/ICs/params/BCs/time) → **problem-authoring** skill.
- validation_modes[] + scores + prose → **validation-authoring** skill (MANDATORY, §11.6).
- Any new id/function → **vocab-extension** hard-stop (§7.2). Schema gap → escalate (§12).

## Pre-transcribe checklist
- [ ] De-dup ran BEFORE scaffolding; a match caused a refusal (never a duplicate).
- [ ] `provenance: synthesized` set.
- [ ] Will end with >=1 scored validation mode (§11.6) — else the spec is rejected.
- [ ] pending_derivation.md emitted iff an underived exact solution is plausible; score stays provisional.
- [ ] capability_flags from the CANONICAL set only (§2.3, §11.13).
