---
id: self-convergence
human_name: "Self-convergence"
kind: procedure
formula_ref: "docs/procedures.md §4"
---
## Applies to
Canonical problems with no closed form: use a high-resolution run as the reference.

## Inputs (slots)
- resolution sequence + high-resolution reference level.
- refinement ratio `r` (stated explicitly).
- `variables`, tolerance / expected order.

## Steps / formula
Defined in `docs/procedures.md` §4. Measure Richardson-style convergence of successively refined
runs toward the high-resolution reference, using the `convergence-order` formulae (§2) with the
high-resolution run in place of the exact solution. `r` between levels is stated explicitly.

## Output form
Self-convergence order per variable.

## Pass-criterion
Order within tolerance of the expected value.

## Refs
(none)
