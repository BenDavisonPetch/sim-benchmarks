# pending_extraction — ideal-mhd-rotor

No `needs-source` parameter values (all numeric IC state values are stated directly in Sect.
4.1.4 of the source). One convention gap requires confirmation.

---

## Source
- entry: `ideal-mhd-rotor`
- authored from: `dematte2024` (doi: 10.1016/j.jcp.2024.113229), Sect. 4.1.4
- authored offline: no (online pass; crossref reachable)

## Parameters awaiting extraction
(none -- all numeric state values are stated directly in Sect. 4.1.4 of the source)

## Convention checks
- `domain_bc.*.type`: not stated explicitly for this test in Sect. 4.1.4 (the excerpt notes
  "Boundary conditions not explicitly restated for this test in the body text"). Recorded as
  `outflow` (inferred, standard practice for this benchmark since the Alfven fronts have not
  reached the domain edge by t_final=0.25). Confirm against the originating source once
  identified/retrievable: Balsara & Spicer [47] (cited by dematte2024 as the test's originator;
  not resolved to a specific DOI/arXiv id in this pass -- see `test_origin.status: pending` in
  `spec.md`).

## After resolution
1. Confirm the domain_bc convention against Balsara & Spicer [47] once resolved (or against any
   other primary rotor-benchmark source).
2. Update `spec.md` domain_bc / Notes if a different convention is found.
3. Run `scripts/validate.py`.
4. Run `scripts/reindex.py`.
5. Delete this file.
