---
id: subsonic-inflow
human_name: "Subsonic inflow"
kind: bc-type
requires_state: true
physical: true
---
## Definition
Inflow boundary at subsonic speed: the incoming state is partly imposed and partly determined by
outgoing characteristics (physically, not all variables are free to prescribe at a subsonic inlet).
Stated as a physical inflow condition via `state` expressions.

## Params schema
- `state` — per-variable IC-expression-language expressions (§4) for the imposed inflow quantities.
  May reference `x,y,z` and `t`; a `t`-reference sets `time_dependent_bc = true` (§2.3).

## Notes
Subsonic vs supersonic inflow is a **physical** distinction (which characteristics are incoming),
not a method choice. Steady vs `t`-dependent inflow ⇒ **different entries** (`time_dependent_bc`
forks, §2.3); step vs ramp vs sinusoid ⇒ same entry (BC-state is a value).

## Refs
(none)
