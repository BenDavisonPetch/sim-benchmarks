# pending_extraction — orszag-tang-vortex

No `needs-source` parameter values (gamma and all IC state values are stated directly in Sect.
4.1.5 of the source). One convention gap requires confirmation.

---

## Source
- entry: `orszag-tang-vortex`
- authored from: `dematte2024` (doi: 10.1016/j.jcp.2024.113229), Sect. 4.1.5
- authored offline: no (online pass; crossref reachable)

## Parameters awaiting extraction
(none -- all numeric state values are stated directly in Sect. 4.1.5 of the source)

## Convention checks
- `domain_bc.*.type`: not stated explicitly for this test beyond "the computational domain is
  the square [0,1]x[0,1]". Recorded as `periodic` (inferred -- the near-universal, IC-consistent
  convention for this canonical benchmark). Confirm against the originating source once
  identified/retrievable: Orszag & Tang [71] (cited by dematte2024 as the test's originator; not
  resolved to a specific DOI/arXiv id in this pass -- see `test_origin.status: pending` in
  `spec.md`), or Dahlburg & Picone [72,73] (cited for the underlying physics).

## After resolution
1. Confirm the `periodic` domain_bc convention against Orszag & Tang [71] / Dahlburg & Picone
   [72,73] once resolved.
2. Update `spec.md` domain_bc / Notes if a different convention is found.
3. Run `scripts/validate.py`.
4. Run `scripts/reindex.py`.
5. Delete this file.
