# pending_extraction — lid-driven-cavity-mhd-visco-resistive

## Source
- entry: `lid-driven-cavity-mhd-visco-resistive`
- authored from: `dematte2024` (doi: 10.1016/j.jcp.2024.113229), Sect. 4.3.3
- authored offline: no (`dematte2024`'s DOI verified live; the primary PDF re-read directly for the two flags below)

## Parameters awaiting extraction
- `mu` (dynamic viscosity) — NOT stated anywhere in Sect. 4.3.3 for this specific test (confirmed
  by direct re-read of page 30; only "perfectly conductive walls are assumed" appears, no eta/mu
  numbers). Do NOT borrow the Kelvin-Helmholtz value (eta=mu=1e-3, Sect 4.3.2) or the
  shear-layer/current-sheet value (eta=mu=0.1, Sect 4.3.1) by analogy — those are different tests
  with their own stated values. Genuine gap in the source itself.
- `eta` (resistivity) — same gap, same caveat, same section.

## Convention checks
(none beyond the above — b_field_convention and gamma are both stated globally in Sect. 2/4)

## After resolution
1. Locate mu/eta for this test (author's supplementary material, code repository, or a direct
   author query) — a secondary/derived value is not acceptable per the no-fabrication contract.
2. Fill `parameters[].canonical` for `mu` and `eta` in `spec.md`; remove the `notes: needs-source`
   marker.
3. Run `scripts/validate.py`.
4. Run `scripts/reindex.py`.
5. Delete this file.
