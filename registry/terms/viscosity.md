---
id: viscosity
human_name: "Viscosity"
kind: term
param_bearing: true
coefficient: mu               # dynamic viscosity (may be a spatial expression / material_field)
applies_to: [hydro, mhd, linear-elastic, hyperelastic, elastoplastic]
---
## Definition
Momentum diffusion via the viscous stress tensor. Present iff its coefficient is nonzero **anywhere**
in the domain (§2.3). `hydro + viscosity` (+ optional `heat-conduction`) = Navier–Stokes;
`mhd + viscosity + resistivity` (+ optional `heat-conduction`) = VRMHD.

## Params schema
- `mu` — dynamic viscosity. Scalar or a position/aux expression / `material_fields` entry (§4). A
  spatially-varying coefficient that is zero in part of the domain still counts as **present**.

## Notes
Independent toggle (§7.1). Inviscid vs viscous ⇒ **different entries** (term presence forks
identity, §2.3); a viscosity value sweep (`1 → 2`) is a parameter on the same entry, not a fork.

## Refs
(none)
