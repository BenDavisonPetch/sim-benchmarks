---
id: norms
human_name: "Volume-weighted norms (L1 / L2 / Linf)"
kind: procedure
formula_ref: "docs/procedures.md §1"
---
## Applies to
Any validation mode measuring an error field against a reference (exact, canonical, or a
`reference_result`). Foundation for `exact-solution-compare`, `convergence-order`, `self-convergence`,
`well-balancing`.

## Inputs (slots)
- `variables` — variable(s) whose error field is normed.
- `reference` — exact solution or reference-result the error is taken against.
- norm choice(s) — L1, L2, and/or Linf.

## Steps / formula
Volume-weighted discrete norms over active cells with weight `w_i = f_i·V_i` (active volume
fraction `f_i`), **defined once** in `docs/procedures.md` §1:
`L1 = Σw|e|/Σw`, `L2 = sqrt(Σw e²/Σw)`, `Linf = max|e|` over active cells (`f_i>0`),
`e_i = u_i − u*_i`. Computed per variable unless a combined norm is stated.

## Output form
One scalar per (variable, norm).

## Pass-criterion
Each value below the mode's stated tolerance.

## Refs
(none)
