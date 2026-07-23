---
id: exact-solution-compare
human_name: "Exact-solution compare"
kind: procedure
formula_ref: "docs/procedures.md §3"
---
## Applies to
Problems with an exact or analytic solution.

## Inputs (slots)
- exact-solution reference.
- sample time(s) (≤ `t_final`).
- `variables`, norm choice(s), tolerance.

## Steps / formula
Defined in `docs/procedures.md` §3. Sample the exact solution at cell **centroids**; form
`e_i = u_i − u*_i` and reduce with the `norms` definitions (§1) per variable.

## Output form
`norm(numeric − exact)` per variable.

## Pass-criterion
Norms below tolerance; combined with `convergence-order` this is the route to a score of 5.

## Refs
(none)
