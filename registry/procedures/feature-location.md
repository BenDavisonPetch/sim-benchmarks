---
id: feature-location
human_name: "Feature location"
kind: procedure
formula_ref: "docs/procedures.md §6"
---
## Applies to
Problems with named, locatable features (shocks, contacts, rarefaction heads, standoff surfaces,
X-lines).

## Inputs (slots)
- sample time(s) (≤ `t_final`).
- `variables`, `cut_lines`, `features`.
- `reference` (exact, canonical, or a `reference_result`) + positional `tolerance`
  (e.g. "positions within 2 cells").

## Steps / formula
Defined in `docs/procedures.md` §6. Locate the named features along the stated cut-lines at the
stated times; compare positions against the reference within the positional tolerance.

## Output form
Measured position per named feature.

## Pass-criterion
Each position within tolerance of the reference.

## Refs
(none)
