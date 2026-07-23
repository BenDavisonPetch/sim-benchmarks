---
id: elastoplastic
human_name: "Elastoplasticity (solid with yield / plastic flow)"
phase: fluid
requires_eos: true
velocity: evolved
evolves: [rho, v, E, sigma, ep] # mass, momentum, energy, stress, plastic-strain state
interchangeable_with: []
interchangeable_when: null
---
## Definition
Elastic–plastic solid dynamics: elastic stress response up to a yield surface, with plastic flow
(and hardening) beyond it, evolved as a convecting continuum. A **fluid-phase** base (velocity
evolved, `requires_eos: true`); the volumetric response is the `eos`, the deviatoric elastic/plastic
response is the equation set.

## Params schema
None intrinsic beyond the elastic-modulus + yield/hardening parameter set closing the constitutive
response (authored on the material; volumetric closure via `eos`). Physical `terms` toggles apply
when present.

## Notes
Yield/plasticity present ⇒ different `base` from `linear-elastic` and `hyperelastic` (both purely
elastic); a distinct physics_signature element that forks identity. Distinct from the non-convecting
solid-**phase** family.

## Refs
(none)
