---
id: convergence-order
human_name: "Convergence order"
kind: procedure
formula_ref: "docs/procedures.md §2"
---
## Applies to
Methods with a known theoretical order and a refinable error measure. Combined with
`exact-solution-compare` this is the route to a score of 5 (`docs/scoring-rubric.md`).

## Inputs (slots)
- error measure — usually a `norms` output per variable.
- resolution sequence + refinement ratio `r = h_coarse/h_fine`.
- expected (theoretical) order.

## Steps / formula
Defined in `docs/procedures.md` §2. Pairwise order `p = log(E_coarse/E_fine)/log(r)`; and/or the
least-squares slope of a line fit to `(log h, log E)`.

## Output form
`p` (pairwise per pair and/or LSQ slope) reported with the resolution sequence.

## Pass-criterion
`p` within tolerance of the theoretical order.

## Refs
(none)
