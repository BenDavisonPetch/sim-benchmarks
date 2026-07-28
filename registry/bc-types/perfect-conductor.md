---
id: perfect-conductor
human_name: "Perfect-conductor wall (composite: velocity + B + thermodynamic)"
kind: bc-type
requires_state: optional
state_keys: [vx, vy, vz, Bn]
physical: true
---
## Definition
A rigid, perfectly-conducting **domain face**. This is a *composite* physical wall condition: it
states, in one id, the condition every variable group takes at such a wall, so a face needs exactly
one `type` (SPEC §3 `domain_bc` carries one type per face).

Per variable group, at the face with outward normal `n`:

- **Velocity** — the fluid moves with the wall. The wall velocity is the `state` velocity
  components (`vx`, `vy`, `vz`); absent ⇒ **0** (stationary wall). When `viscosity` is present the
  condition is no-slip (the full velocity vector equals the wall velocity); with no viscous term it
  degrades to impermeability (`v·n = v_wall·n`, tangential velocity free) — the wall is the same
  physical object either way, and which components the equations can constrain is set by the terms
  present, not by a different boundary.
- **Magnetic field** — Dirichlet on the **normal** component, `B·n = Bn` (`state.Bn`; absent ⇒
  **0**, i.e. field excluded from the wall). The tangential electric field vanishes, so the normal
  flux is frozen and field lines are pinned to the wall's material points. The **tangential**
  components are not prescribed by the physics — a perfect conductor supports a surface current, so
  `B·t` is whatever the interior solution gives. References close it numerically (homogeneous
  Neumann `∂B_t/∂n = 0`, or `B·t = 0` where the wall interior is field-free); that closure is a
  method choice and belongs in `reference_results[].method`.
- **Density** — homogeneous Neumann, `∂ρ/∂n = 0`.
- **Pressure** — wall-normal **force balance**, `n·∇p = n·(J × B)`. This is the physically correct
  condition at a conducting wall carrying a field, and it is what this id asserts. The commonly-used
  naive `n·∇p = 0` is an *approximation of it*, i.e. a method choice: which one a given reference
  used is recorded per reference in `reference_results[].wall_pressure_bc`
  (`registry/wall-pressure-treatments/`), never here (SPEC §1.6).

## Params schema
- `state` — **optional** (`requires_state: optional`). Allowed keys: `vx`, `vy`, `vz` (wall
  velocity components) and `Bn` (prescribed normal magnetic-field component, in the entry's
  `b_field_convention`). Values are IC-expression-language expressions (§4) and may reference
  `x,y,z` and `t`; a `state` expression referencing `t` sets `capability_flags.time_dependent_bc =
  true` (§2.3, `validate.py` check 6). Any other key is a validation error (check 2).
- Omitting `state` entirely means a stationary wall with `Bn = 0`.

`Bn` is the component along the face normal — `Bx` on `x_lo`/`x_hi`, `By` on `y_lo`/`y_hi`, `Bz` on
`z_lo`/`z_hi` — named normal-relative so one id serves every face.

## Notes
Distinct from the `perfect-conductor` **equation-set** base (a solid-phase conducting body) and from
the `perfect-conductor-wall` **internal**-boundary kind (an interior conducting surface). This id is
a `domain_bc` face type. Both this id and the internal `perfect-conductor-wall` kind trigger
`validate.py` check 12 (every `reference_results` row must declare `wall_pressure_bc`).

A wall that is rigid and no-slip but *not* conducting is not this id — use `reflecting` or
`dirichlet`.

## Refs
(none)
