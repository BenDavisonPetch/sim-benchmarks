---
id: perfect-conductor-wall
human_name: "Perfect-conductor wall (internal conducting surface)"
kind: internal-boundary
physical: true
---
## Definition
Surface of a perfectly-conducting internal body: the magnetic field cannot penetrate the surface
(normal B and tangential E vanish there), for a conductor embedded in an MHD domain. A physical
electromagnetic interior surface, never a numerical treatment.

## Params schema
Geometry of the conducting surface + (optional) motion. No method fields.

## Notes
The **internal**-boundary analogue of the `perfect-conductor` domain-face BC. Distinct from
`electromagnetic-coupling`, which couples two **evolved** bodies via field continuity; use
`perfect-conductor-wall` when the conductor interior is not itself evolved. Presence sets
`has_internal_boundaries = true`.

## Refs
(none)
