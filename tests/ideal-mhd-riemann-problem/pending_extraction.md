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

## After resolution
1. Confirm the domain_bc convention against the cited primary sources (or the source paper's
   supplementary material).
2. Update `spec.md` domain_bc / Notes if a different convention is found.
3. Run `scripts/validate.py`.
4. Run `scripts/reindex.py`.
5. Delete this file.
