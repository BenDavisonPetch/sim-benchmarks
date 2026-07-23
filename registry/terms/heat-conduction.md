---
id: heat-conduction
human_name: "Heat conduction"
kind: term
param_bearing: true
coefficient: kappa            # thermal conductivity (may be a spatial expression / material_field)
applies_to: [hydro, mhd, linear-elastic, hyperelastic, elastoplastic]
---
## Definition
Thermal energy diffusion (Fourier heat flux `q = -κ∇T`) in the energy equation. Present iff its
coefficient is nonzero **anywhere** in the domain (§2.3). Added to `hydro + viscosity` completes
Navier–Stokes; added to `mhd + viscosity + resistivity` completes VRMHD.

## Params schema
- `kappa` — thermal conductivity. Scalar or a position/aux expression / `material_fields` entry
  (§4).

## Notes
Independent toggle (§7.1). Adiabatic vs conducting ⇒ **different entries** (term presence forks
identity, §2.3).

## Refs
(none)
