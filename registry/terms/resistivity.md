---
id: resistivity
human_name: "Resistivity"
kind: term
param_bearing: true
coefficient: eta              # magnetic resistivity/diffusivity (may be a spatial expression)
applies_to: [mhd, magnetic-diffusion]
---
## Definition
Finite magnetic diffusion in the induction equation. Present iff its coefficient is nonzero
**anywhere** in the domain (§2.3). `mhd + resistivity` = resistive MHD. Also the coefficient of the
solid-phase `magnetic-diffusion` base (`∂B/∂t = -(1/μ0)∇×(η∇×B)`).

## Params schema
- `eta` — resistivity / magnetic diffusivity. Scalar or a position/aux expression /
  `material_fields` entry (§4); e.g. a radial field `eta(r)` for a layered conductor.

## Notes
Independent toggle (§7.1). Ideal (η=0) vs resistive (η≠0) ⇒ **different entries** (term presence
forks identity, §2.3); a resistivity sweep is a parameter on the resistive entry. Interpreted under
the entry's declared `b_field_convention` (`docs/conventions.md` §2).

## Refs
(none)
