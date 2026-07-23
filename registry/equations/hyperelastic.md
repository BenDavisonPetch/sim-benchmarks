---
id: hyperelastic
human_name: "Hyperelasticity (large-deformation solid)"
phase: fluid
requires_eos: true
velocity: evolved
evolves: [rho, v, E, F]        # mass, momentum, energy, deformation-gradient state
interchangeable_with: []
interchangeable_when: null
---
## Definition
Finite-strain elastic-solid dynamics: momentum coupled to a nonlinear (finite-deformation) elastic
stress response derived from a strain-energy density, typically carrying a deformation-gradient
state `F`. A **fluid-phase** base (velocity evolved, `requires_eos: true`); the volumetric response
is the `eos`, the elastic response is the equation set.

## Params schema
None intrinsic beyond the strain-energy / elastic-parameter set closing the stress response
(authored on the material; volumetric closure via `eos`). Physical `terms` toggles apply when
present.

## Notes
Large-deformation regime — different `base` from `linear-elastic` (small strain) and
`elastoplastic` (yield present); each is a distinct physics_signature element and forks identity.
Distinct from the non-convecting solid-**phase** family (`rigid-body` etc.).

## Refs
(none)
