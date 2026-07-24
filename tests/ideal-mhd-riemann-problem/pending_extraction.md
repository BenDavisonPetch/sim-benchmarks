# pending_extraction — ideal-mhd-riemann-problem

No `needs-source` parameter values (gamma and b_field_convention are both stated directly in
the source, Sect. 4/Sect. 2). One convention gap requires confirmation.

---

## Source
- entry: `ideal-mhd-riemann-problem`
- authored from: `dematte2024` (doi: 10.1016/j.jcp.2024.113229), Sect. 4.1.1
- authored offline: yes

## Parameters awaiting extraction
(none — all numeric state values for RP1-RP4 are stated directly in Table 1 of the source)

## Convention checks
- `domain_bc.x_lo/x_hi.type`: not explicitly stated for the Riemann-problem tests in Sect. 4.1.1
  (unlike Sect. 4.3.1, which states "transmissive boundary conditions ... in the x-direction").
  Recorded as `outflow` (inferred, standard practice for a shock tube whose waves do not reach the
  boundary by t_final). Confirm against the primary sources: Brio & Wu (1988), J. Comput. Phys.
  75, 400-422; Ryu & Jones (1995), Astrophys. J. 442, 228.
  **STATUS (2026-07-24, /add-refs online pass): partially checked, still open.**
  - `ryujones1995` (verified, arXiv:astro-ph/9404074) full text was retrieved and searched
    (`boundary`, `outflow`, `extrapolat*`, etc.) — no domain-edge boundary-condition statement of
    any kind appears anywhere in the paper for its 1D shock-tube tests (the only "boundary" hit
    concerns the *internal* Riemann discontinuity, not the domain edges). This source cannot
    confirm or refute the `outflow` convention.
  - `brio1988` could not be checked: the paper is paywalled (ScienceDirect returns HTTP 403 to
    automated fetch) and predates arXiv, so no free full text was locatable. Per the no-fabrication
    contract, the convention stays `outflow` (inferred), and this row stays open rather than being
    resolved from memory or a secondary source.

## After resolution
1. Confirm the domain_bc convention against the cited primary sources (or the source paper's
   supplementary material) — `brio1988` specifically still needs a retrievable copy.
2. Update `spec.md` domain_bc / Notes if a different convention is found.
3. Run `scripts/validate.py`.
4. Run `scripts/reindex.py`.
5. Delete this file.
