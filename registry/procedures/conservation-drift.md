---
id: conservation-drift
human_name: "Conservation drift"
kind: procedure
formula_ref: "docs/procedures.md §8"
universal_diagnostic: true
---
## Applies to
Any conservative system. A **universal diagnostic** (SPEC §6.4): **scored** only when genuinely
discriminating for the problem (the entry must assert why it is challenging here); otherwise recorded
as an **unscored** provenance metric.

## Inputs (slots)
- conserved quantity `Q` (total mass, momentum, energy, or a stated flux balance).
- evolve time, drift form (absolute/relative), tolerance / criterion.

## Steps / formula
Defined in `docs/procedures.md` §8. Track `Q` vs time; drift `= |Q(t)−Q(0)|` (absolute) or
`|Q(t)−Q(0)|/|Q(0)|` (relative, `Q(0)≠0`).

## Output form
Drift vs time.

## Pass-criterion
Drift below the stated criterion.

## Refs
(none)
