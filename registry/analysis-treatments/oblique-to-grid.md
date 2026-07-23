---
id: oblique-to-grid
human_name: "Oblique to grid"
kind: analysis-treatment
---
## Definition
The problem's features (shocks, interfaces, flow direction) are deliberately oriented **oblique** to
the natural axes, so validating it demands analysis that accounts for the non-axis-aligned geometry
(e.g. a Sod tube rotated 30° in an embedded rectangle).

## Params schema
None. The rotation angle itself is a `parameters` value (e.g. `rotation_deg`), not part of identity;
only the *presence* of the oblique-analysis demand is (§2.1 item 2).

## Notes
Distinguishes sibling entries from their axis-aligned form (1D Sod `[none]` vs 2D-rotated Sod
`[oblique-to-grid]`, §2.5). Rotation 30° vs 45° on the same structure ⇒ **same entry**, parameter
sweep.

## Refs
(none)
