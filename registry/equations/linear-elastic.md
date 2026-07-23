---
id: linear-elastic
human_name: "Linear elasticity (small-strain solid)"
phase: fluid
requires_eos: true
velocity: evolved
evolves: [rho, v, E, sigma]    # mass, momentum, energy, (small-strain) stress/deformation state
interchangeable_with: []
interchangeable_when: null
---
## Definition
Small-strain elastic-solid dynamics: the momentum equation closed by a linear (Hooke's-law) stress
response to the strain, evolved as a convecting continuum. A **fluid-phase** base in the §7.1 sense
(velocity is evolved, `requires_eos: true`) — the deviatoric/elastic response is an equation-set
property, the volumetric (pressure) response is the `eos`.

## Params schema
None intrinsic beyond the elastic-modulus set that closes the stress response (authored on the
material; volumetric closure via `eos`). Physical terms (e.g. `heat-conduction`) enter via the
independent `terms` toggles when present.

## Notes
Distinct from the solid-**phase** family (`magnetic-diffusion` / `perfect-conductor` / `rigid-body`,
which have `v ≡ 0`, `requires_eos: false`): those model a non-convecting conductor/obstacle, whereas
`linear-elastic` is a deforming, convecting solid. Small-strain regime; use `hyperelastic` for
large-deformation and `elastoplastic` when yield/plastic flow is present (different `base` ⇒
different physics_signature element).

## Refs
(none)
