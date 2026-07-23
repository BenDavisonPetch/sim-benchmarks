# pending_extraction — <slug>

Fixed-format request handed to an internet/references-capable pass. Lists problem parameters
that are **defined only by reference** in the source and therefore recorded with
`status: needs-source`. This artifact exists because the authoring model must never fill such a
value from memory (SPEC §5 no-fabrication ethos, extended to problem parameters).

Delete this file once every row is resolved and the values are written into `spec.md`.

---

## Source
- entry: `<slug>`
- authored from: `<citekey of the source paper>` (`<doi/arxiv/url>`)
- authored offline: `<yes|no>`

## Parameters awaiting extraction

For each row: confirm the value from the cited source, then write it into `spec.md`
`parameters:` (or the relevant IC/BC field), set the parameter's `source_ref: <citekey>`, and
remove the row here.

| param (spec field)        | source ref (citekey) | what to extract exactly                         | status      |
|---------------------------|----------------------|-------------------------------------------------|-------------|
| `<field path>`            | `<citekey>`          | `<the precise quantity, units, any convention>` | needs-source |
| `physics.eos.params.gamma`| `<citekey|UNKNOWN>`  | ratio of specific heats used for the plasma     | needs-source |

## Convention checks
List any unit / field-convention question the source left implicit (e.g. B-field convention,
unit system) that a resolving pass must pin down before the value is trustworthy.

- `<field>`: `<question>` — e.g. "b_field_convention not stated; confirm SI-with-μ0 vs
  sqrt-4π before recording dipole strength."

## After resolution
1. Write each confirmed value into `spec.md`; set `source_ref`.
2. Run `scripts/validate.py`.
3. Run `scripts/reindex.py`.
4. Delete this file.
