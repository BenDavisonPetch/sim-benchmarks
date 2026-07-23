---
id: gravity
human_name: "Gravity"
kind: term
param_bearing: true
coefficient: g                # gravitational acceleration / potential (may be a spatial expression)
applies_to: [hydro, mhd, linear-elastic, hyperelastic, elastoplastic]
---
## Definition
Gravitational body force (and its energy coupling) as a source term in the momentum/energy
equations. Present iff its coefficient is nonzero **anywhere** in the domain (§2.3). Enables
hydrostatic-equilibrium problems and the `well-balancing` validation procedure
(`docs/procedures.md` §7).

## Params schema
- `g` — gravitational acceleration (constant, directional) or a potential/field expression; scalar
  or a position/aux expression / `material_fields` entry (§4). Self-gravity, if applicable, is
  stated as a field derived from the density.

## Notes
Independent toggle (§7.1). With vs without gravity ⇒ **different entries** (term presence forks
identity, §2.3). A nontrivial hydrostatic `equilibrium` is authored in `initial_conditions`
(§4 split) to enable well-balancing.

## Refs
(none)
