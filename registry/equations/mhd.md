---
id: mhd
human_name: "Magnetohydrodynamics (ideal MHD base)"
phase: fluid
requires_eos: true
velocity: evolved
evolves: [rho, v, E, B]        # mass, momentum, total energy, magnetic field
interchangeable_with: []
interchangeable_when: null
---
## Definition
Single-fluid magnetohydrodynamics: the compressible fluid equations coupled to the induction
equation for the magnetic field `B`. Closed by an equation of state (`requires_eos: true`). With
**no terms** this base is **ideal MHD** (infinite conductivity, `∇·B = 0` constraint).

## Params schema
None intrinsic to the base. Thermodynamic closure is the material's `eos` (required). The magnetic
convention is declared per entry via `units.b_field_convention` (see `docs/conventions.md` §2).
Physical terms enter via independent `terms` toggles (§7.1 `base` semantics):
- `+ resistivity` = **resistive MHD** (finite η in the induction equation).
- `+ viscosity + resistivity` (+ optional `heat-conduction`) = **VRMHD**.

## Notes
Ideal MHD = `mhd` with `terms: []`. Resistive vs ideal are **different entries** (term presence
forks identity, §2.3); record a resistivity parameter sweep on the resistive entry, not a new one.
The `div-b` universal diagnostic (`docs/procedures.md` §9) applies. Distinct phase from the
solid-phase `magnetic-diffusion` / `perfect-conductor` conductors (those have `v ≡ 0`,
`requires_eos: false`); a conductor embedded in a plasma couples via `electromagnetic-coupling`.

## Refs
(none)
