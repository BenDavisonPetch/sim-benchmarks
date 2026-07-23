# pending_extraction — mercury-magnetosphere-coupled-interior

Fixed-format request handed to an internet/references-capable pass. Lists problem parameters
that are **defined only by reference** in the source and therefore recorded with
`status: needs-source`. This artifact exists because the authoring model must never fill such a
value from memory (SPEC §5 no-fabrication ethos, extended to problem parameters).

Delete this file once every row is resolved and the values are written into `spec.md`.

---

## Source
- entry: `mercury-magnetosphere-coupled-interior`
- authored from: `jia2015` (`doi:10.1002/2015JA021143`) + the MESSENGER-era refs below
- authored offline: `yes`

## Parameters awaiting extraction

For each row: confirm the value from the cited source, then write it into `spec.md`
`parameters:` (or the relevant IC/BC field), set the parameter's `source_ref: <citekey>`, and
remove the row here.

| param (spec field)                           | source ref (citekey) | what to extract exactly                                              | status       |
|----------------------------------------------|----------------------|----------------------------------------------------------------------|--------------|
| `physics.materials[plasma].eos.params.gamma` | `UNKNOWN`            | ratio of specific heats for the plasma (source gives `T_sw = 15 eV`, not γ) | needs-source |
| `parameters[dipole_eq_nT]`                   | `anderson2011`       | equatorial surface dipole strength (nT)                              | needs-source |
| `parameters[dipole_offset_RM]`               | `anderson2011`       | northward (+Z) dipole-center offset (R_M)                           | needs-source |
| `parameters[eta_mantle]`                     | `hauck2013`          | mantle resistivity (ohm·m)                                          | needs-source |
| `parameters[eta_core]`                       | `hauck2013`          | core-boundary resistivity (ohm·m)                                  | needs-source |
| `parameters[imf_B_nT]`                       | `slavin2009`         | upstream IMF vector, MSO frame (nT)                                 | needs-source |
| `validation_modes[boundary-standoff-locations].inputs.reference` | `winslow2013` | empirical magnetopause / bow-shock standoff model (pressure-scaled) | needs-source |

## Convention checks
List any unit / field-convention question the source left implicit (e.g. B-field convention,
unit system) that a resolving pass must pin down before the value is trustworthy.

- `units.b_field_convention`: not stated in source; confirm SI-with-μ0 vs sqrt-4π (Gaussian)
  before trusting any B value (surface dipole strength, IMF, `dipole(...)` moment normalization).
- `initial_conditions.equilibrium[interior].B`: the inline dipole moment uses `mu0/4pi = 1e-7`
  (SI). Confirm the source's field convention matches before relying on the moment magnitude.

## After resolution
1. Write each confirmed value into `spec.md`; set `source_ref`.
2. Run `scripts/validate.py`.
3. Run `scripts/reindex.py`.
4. Delete this file.
