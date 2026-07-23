---
id: supersonic-inflow
human_name: "Supersonic inflow"
kind: bc-type
requires_state: true
physical: true
---
## Definition
Inflow boundary at supersonic speed: all characteristics are incoming, so the **entire** state is
imposed on the face. Stated as a physical inflow condition via `state` expressions (e.g. the
solar-wind inlet of the worked Mercury example).

## Params schema
- `state` — per-variable IC-expression-language expressions (§4) for the fully-imposed inflow
  state. May reference `x,y,z` and `t`; a `t`-reference sets `time_dependent_bc = true` (§2.3).

## Notes
Supersonic vs subsonic inflow is a **physical** distinction (all vs some incoming characteristics).
Mach subsonic → supersonic on the same structure is a parameter sweep (**same entry**, §2.3), but
the imposed-state completeness differs by id; author the id matching the canonical regime. Steady vs
driven inflow forks via `time_dependent_bc`.

## Refs
(none)
