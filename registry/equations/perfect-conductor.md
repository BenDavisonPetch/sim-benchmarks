---
id: perfect-conductor
human_name: "Perfect conductor (frozen-flux rigid body)"
phase: solid
requires_eos: false
velocity: fixed-zero            # v ≡ 0
evolves: [B]                    # frozen; no interior diffusion
interchangeable_with: [rigid-body]
interchangeable_when: "no coupling magnetic field is present / the body carries no field"
---
## Definition
Non-convecting body of infinite conductivity: the magnetic field is frozen, there is no interior
diffusion, and currents are confined to the surface. Equivalent to a rigid body that additionally
carries a magnetic field. Phase of matter: solid.

## Params schema
None. No resistivity (infinite conductivity); no EoS (`requires_eos: false`).

## Notes
Interchangeable with `rigid-body` when no coupling field is present (then the two are physically
indistinguishable and must not fork identity, §2.3 / §2.4). When a field interacts, frozen-flux vs
no-interaction distinguishes them and they fork. A carried field (e.g. a dipole) is stored as this
material's initial condition. Couples to a plasma via `electromagnetic-coupling`.

## Refs
(none)
