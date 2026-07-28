# pending_extraction — kelvin-helmholtz-instability-ideal-mhd

## Source
- entry: `kelvin-helmholtz-instability-ideal-mhd`
- authored from: `dematte2024` (doi: 10.1016/j.jcp.2024.113229), Sect. 4.3.2
- authored offline: yes

## Parameters awaiting extraction
(none — eta=mu=0 and lambda=0 are stated directly; all other IC parameters are inherited
unchanged from the shared equation (68) IC, also fully stated in the source.)

## Convention checks
- `domain_bc` (recorded as periodic on all four faces): same open convention gap as
  `kelvin-helmholtz-instability-vrmhd` (see that entry's `pending_extraction.md`) — shared IC/
  geometry, not independently re-derived here. **STATUS: open.**

## After resolution
1. Confirm the domain_bc convention against `dumbser2019vrmhd`'s primary text (same action item
   as the visco-resistive sibling entry — resolve both together).
2. Update `spec.md` domain_bc / Notes if a different convention is found.
3. Run `scripts/validate.py`.
4. Run `scripts/reindex.py`.
5. Delete this file.
