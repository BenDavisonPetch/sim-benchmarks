---
# Copy-and-fill scaffold for a NEW validation procedure (SPEC §6.1/§7.2).
# One markdown file per id at registry/procedures/<id>.md. id MUST equal the filename.
# A mode may NOT invent an ad-hoc procedure; add-test/create-test PROPOSES a new file for review
# (hard-stop-and-propose, §7.2). Define any new formula ONCE in docs/procedures.md and cite it here.
# Delete every comment line before committing the filled file.
id: <kebab-case-id>                 # == filename
human_name: "<Human Readable Name>"
kind: procedure
formula_ref: "docs/procedures.md §<n>"   # the single formula definition this procedure references
# universal_diagnostic: true        # ONLY for div-b / conservation-drift style diagnostics (§6.4):
#                                    #   scored only when genuinely discriminating, else unscored
---
## Applies to
<Problem class this procedure validates. If a universal diagnostic, state the scored-vs-unscored
rule (§6.4).>

## Inputs (slots)
<The slots a validation_mode fills: sample time(s) (≤ t_final), variables, reference, tolerance,
and any procedure-specific slots (cut_lines, resolution sequence, refinement ratio r, ...).>

## Steps / formula
<The procedure, referencing the formula defined once in docs/procedures.md §<n>. Do NOT re-derive
formulae here — cite them.>

## Output form
<What the procedure emits (e.g. one scalar per (variable, norm); order p; measured position per
feature).>

## Pass-criterion
<The condition for a pass (e.g. value below the stated tolerance; order within tolerance of the
theoretical order).>

## Refs
(none)
