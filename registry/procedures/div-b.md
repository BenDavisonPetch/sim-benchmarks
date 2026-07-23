---
id: div-b
human_name: "Div-B"
kind: procedure
formula_ref: "docs/procedures.md §9"
universal_diagnostic: true
---
## Applies to
MHD problems. A **universal diagnostic** (SPEC §6.4): **scored** only when the entry asserts why
controlling `∇·B` is specifically challenging for that problem; otherwise an **unscored** provenance
metric.

## Inputs (slots)
- norm choice.
- sample time(s).
- criterion.

## Steps / formula
Defined in `docs/procedures.md` §9. Compute a norm of `∇·B` (per §1, over the domain) and compare
against the criterion.

## Output form
`norm(∇·B)` (per §1).

## Pass-criterion
Below the stated criterion.

## Refs
(none)
