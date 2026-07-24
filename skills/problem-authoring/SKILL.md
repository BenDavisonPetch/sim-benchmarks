---
name: problem-authoring
description: >
  Fill the PROBLEM half of a spec.md — physics, geometry, units, initial conditions, boundary
  conditions, parameters — strictly within the §1.6 problem/method hard boundary (no method, no
  resolution, no grid, no AMR ever). Pulled in by /add-test and /create-test. Copy-and-fill against
  templates/problem-block.worksheet.md; the canonical single-file scaffold is templates/spec.template.md.
---

# problem-authoring — the physics problem, method-free (SPEC §1.6, §2, §3, §4)

Fills the problem-describing fields of an entry: `physics`, `dimension`, `analysis_treatments`,
`capability_flags`, `geometry`, `units`, `initial_conditions`, `parameters`, `domain_bc`,
`internal_boundaries`, `time`, and the `## Physical problem` / `## Qualitative behaviour` / `## Notes`
body sections. Everything here is a **physical statement**. Method/resolution/AMR/grid provenance
belongs in a `reference_result` (handled by `add-refs`), never here.

> **One-file rule (§11.9).** You do not create a file here. Fill these fields **inside the single
> `spec.md` scaffolded from `templates/spec.template.md`**. `templates/problem-block.worksheet.md` is
> a decision worksheet listing each problem field with its rules — fill the worksheet's answers
> straight into the spec, then discard it. Never freehand a second scaffold.

---

## The hard boundary (SPEC §1.6 / §11.1) — apply to EVERY field

Problem = geometry, ICs, parameters, boundary conditions **as physical statements**, unit
conventions, times. It **never** names a numerical method, resolution, AMR setting, or grid type.

- A spherical **coordinate frame the physics is posed in** = problem (`geometry.coord_system`).
- A spherical **grid** = method → `reference_result`.
- "ghost fluid", "cut cell", "1000×1000", "block-adaptive", "CFL 0.4", "div-B cleaning" = method.
- When in doubt, it is method — leave it out of the problem block.

`validate.py` check 7 enforces this structurally (method/resolution/amr keys must not appear at the
spec top level); prose leakage in `## Physical problem` is not keyword-scanned (D-014) — it is your
discipline.

---

## Step 1. Materials & physics_signature (§2.1, §7.1)

For each material (single-material tests use a 1-element list):

- `base` — a `registry/equations` id. Fluid phase (`requires_eos: true`): `hydro`, `mhd`,
  `linear-elastic`, `hyperelastic`, `elastoplastic`. Solid / non-convecting phase
  (`requires_eos: false`, `v≡0`): `magnetic-diffusion`, `perfect-conductor`, `rigid-body`.
- `terms` — the set of `registry/terms` ids **present** (coefficient nonzero anywhere, §2.3).
  Independent toggles: Euler = `hydro` + no terms; Navier–Stokes = `hydro`+`viscosity`(+`heat-conduction`);
  ideal MHD = `mhd` + no terms; resistive MHD = `mhd`+`resistivity`; VRMHD =
  `mhd`+`viscosity`+`resistivity`(+`heat-conduction`).
- `eos` — present **iff** the base declares `requires_eos: true` (check 8). Omit entirely for
  solid-phase bases.
- `material_fields` — optional named spatial coefficients as expressions (§4), e.g. a resistivity
  field `eta(r)`. Use these to keep the material count minimal (below).
- `coupling` — a `registry/internal-boundary-kinds` id or `none`. **Physical only** — never a method
  (never `ghost-fluid`). A conductor bounding a plasma couples via `electromagnetic-coupling`.

**Minimal-material canonicalization (§2.4 step 5).** Merge regions that share an equation set into
**one** material with a spatial coefficient field; introduce a material boundary only where the base
equation set, EoS, or a genuine physical interface differs. Do not mint a material per named region
(core+mantle → one body with `eta(r)`).

A prescribed interior field (e.g. a dipole) is a solid-phase material's **initial condition**, never a
bespoke boundary condition (§7.1).

---

## Step 2. Dimension, analysis_treatments, capability_flags

- `dimension.intrinsic` = smallest dimension the problem is defined in; `runnable_in` lists dims
  requiring **no new analysis** (an inert extra dimension is a parameter, not a fork — §2.5).
- `analysis_treatments` = the `registry/analysis-treatments` set (`none`, `oblique-to-grid`,
  `axis-singularity`, `multi-material-interface`, …). Descriptors of what extra analysis the problem
  demands; kinds-of-internal-boundary members are searchable, not forks (§2.1 item 2).
- `capability_flags` — **binary, from the CANONICAL set only** (§2.3, §11.13):
  - `time_dependent_bc` = any `domain_bc[*].state` references `t`.
  - `has_internal_boundaries` = `coupling != none`, or >1 material, or non-empty `internal_boundaries`.
  Never fork on the specific `f(t)` or the specific internal geometry — only on presence.
- `geometry_stress` = a `registry/geometry-stress` id **only** if the geometry is purpose-built to
  stress an algorithm; else `none` (searchable tag, §2.3 exception — not a fork).

---

## Step 3. Geometry (physical frame, not a grid)

- `coord_system` — a `registry/coord-systems` id: the physical frame the problem is posed in.
- `domain` — per-axis extents in the authored units.
- `regions` — analytic predicate primitives (`box`, `cylinder`, `sphere`, `shell{center, r:[ri,ro]}`,
  `halfspace`, `polygon{vertices}`) + transforms (`rotate{deg, about}`, `translate{by}`). No grid,
  no resolution, no cell size. (`polyhedron` is deferred, §12.)

---

## Step 4. Units (STORED AS AUTHORED — never convert, §12)

- `units.system` — `cgs-gaussian | si | code | nondimensional | …` as authored in the source.
- `units.b_field_convention` — `permeability-unity | sqrt-4pi | …`, or `null` **only** when the
  source does not state it — and then it MUST have a `needs-source` row in `pending_extraction.md`
  (§5.2, never guessed). No automated conversion (§12).

---

## Step 5. Initial conditions & expression language (§4)

Grammar authority: `docs/ic-expression-language.md`. All expressions numpy-evaluable on a grid;
`validate.py` check 6 parses and aux-resolves every one.

- Variables `x, y, z, r, phi, theta` (coordinate-aware) and `t` (time). `t` appears **only** in
  `domain_bc` state and any explicitly time-dependent field; a steady problem never references `t`.
- Functions: the allow-list in the doc (`sin, cos, …, J0, J1, Jn`, `step(t,a,b)`, `dipole(...)`, …).
  A needed function not on the list ⇒ **vocab-extension** hard-stop (logged doc + `validate.py`
  change), never silently used.
- `aux` — ordered bindings, evaluated top-down; later may reference earlier names.
- `equilibrium` + `perturbation` (with `combine_rule`) — split the ICs so `well-balancing` and
  perturbation-on-equilibrium modes are expressible. Equilibrium may be trivial but the key is present.
- `potentials` — optional potential (e.g. `A_z`) + a stated `derives` rule (`B = curl(A)`);
  the rule is physical, not a method.
- Material coefficients / `material_fields` accept the same expressions (not only scalars).

---

## Step 6. Parameters (values only — never identity, §2.2)

Each `{ name, canonical, meaning (with units) }`. Optional `source_ref` = a **verified** `references[]`
key that *defines* the value (distinct from a `reference_result`, which records what a ref *did*).

**No-fabrication for reference-defined parameters (§5.2).** A parameter whose value is defined only by
a cited reference is recorded with `canonical: null`, `notes: needs-source` (or `status: needs-source`)
+ a `source_ref` pointer, **and** a row in `pending_extraction.md`. Never type a value from memory.

---

## Step 7. Boundary conditions (per face, physical) & internal boundaries

- `domain_bc` — per face `{type, state?}`, `type` a `registry/bc-types` id. `state` fields are
  expressions (may reference `x,y,z,t`). Any face whose `state` references `t` ⇒
  `capability_flags.time_dependent_bc = true` (check 6). Step vs ramp vs sinusoid ⇒ **same entry**
  (the BC-state expression is a value, §2.3); steady vs driven ⇒ **different entries**, linked.
- `internal_boundaries` — physical only (`material-contact`, `free-surface`, `rigid-wall`,
  `perfect-conductor-wall`, `symmetry`, `electromagnetic-coupling`) + geometry + motion. **No
  numerical method.** Often empty when the interface is already carried by `physics.coupling`.

---

## Step 8. Time & prose body

- `time.t_final` — run-to time so **every** validation mode can be evaluated; `snapshot_times`
  optional/qualitative.
- `## Physical problem` — what is physically happening. Problem only.
- `## Qualitative behaviour` — where no exact solution: SPECIFIC named features ("fast shock reaches
  x≈…, contact at …"). Note traps (e.g. AMR gridding breaks IC symmetry — do not rely on symmetry as
  a proxy there).
- `## Notes` — edge cases, gotchas, unit-convention warnings.

(`## What this test actually tests` and `## Validation notes` are filled by `validation-authoring`.)

---

## Step 9. Vocabulary check (hard-stop, don't improvise)

Any id you reach for that is **not** already in the registry, or any function not on the §4
allow-list, triggers **vocab-extension** (§7.2 hard-stop-and-propose). Batch all such proposals into
one hard-stop. Distinguish a **vocabulary** gap (missing enum id — self-healing) from a **schema** gap
(no field to hold the information at all — escalate to the user, §12). "No id for X" = vocab; "no place
for X" = schema.

---

## Done when

Every problem field of `spec.md` is filled from physical statements only; capability flags computed
from the canonical set; every expression parses (`validate.py --offline` check 6 clean); every
reference-defined parameter carries `needs-source` + a `pending_extraction.md` row; no method,
resolution, AMR, or grid anywhere in the problem block.
