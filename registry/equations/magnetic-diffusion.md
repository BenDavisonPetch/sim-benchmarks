---
id: magnetic-diffusion
human_name: "Magnetic diffusion (non-convecting conductor)"
phase: solid
requires_eos: false
velocity: fixed-zero            # v ≡ 0
evolves: [B]
interchangeable_with: []
interchangeable_when: null
---
## Definition
Non-convecting conducting body. Velocity is identically zero; the only evolved quantity is the
magnetic field, which obeys the induction equation reduced to pure diffusion:
`∂B/∂t = -(1/μ0) ∇×(η ∇×B)`, where `η` is the resistivity. A different *phase of matter* from the
fluid bases `hydro` / `mhd`.

## Params schema
None intrinsic. Resistivity enters via the `resistivity` term coefficient, which may be a scalar
or a spatial expression / `material_fields` entry (§4). No EoS (`requires_eos: false`).

## Notes
Used for planetary interiors and other solid conductors coupled to a plasma via
`electromagnetic-coupling`. A prescribed interior field (e.g. a dipole) is stored as this
material's initial condition, never as a bespoke boundary condition. Core-and-mantle style layered
conductors are one `magnetic-diffusion` material with a spatial `η(r)` (minimal-material
canonicalization, §2.4), not two materials.

## Refs
(none)
