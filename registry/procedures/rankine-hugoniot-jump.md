---
id: rankine-hugoniot-jump
human_name: "Rankine–Hugoniot jump"
kind: procedure
formula_ref: "docs/procedures.md §5"
---
## Applies to
Problems with well-defined shocks whose jump conditions are analytic (incl. MHD magnetic jump
relations).

## Inputs (slots)
- shock identity.
- pre/post sampling locations or method.
- `variables`, tolerance.

## Steps / formula
Defined in `docs/procedures.md` §5. Measure pre- and post-shock states and compare against the
analytic jump conditions (mass, momentum, energy; MHD magnetic relations) for the measured shock
speed, within tolerance.

## Output form
Measured jumps vs analytic jumps per conserved quantity.

## Pass-criterion
Each jump within tolerance.

## Refs
(none)
