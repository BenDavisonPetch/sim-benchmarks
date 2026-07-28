# pending_extraction — theta-pinch-equilibrium-force-balance

No `needs-source` parameter values (B0, R, rho0, p_bg, and the two velocity cases are all stated
directly in Sect. 4.2.2/4.2.3 of the source). One convention gap requires confirmation.

---

## Source
- entry: `theta-pinch-equilibrium-force-balance`
- authored from: `dematte2024` (doi: 10.1016/j.jcp.2024.113229), Sect. 4.2.2 + 4.2.3
- authored offline: yes

## Parameters awaiting extraction
(none)

## Convention checks
- `domain_bc.*.type`: not explicitly stated for either the static (4.2.2) or advected (4.2.3)
  theta-pinch test in the source (checked directly against the full normalized extract — no
  boundary-condition sentence appears in either subsection, unlike Sect. 4.3.1's explicit
  "transmissive boundary conditions ... in the x-direction" or Sect. 4.1.1's Riemann-problem
  entries). Recorded as `outflow` (inferred; standard practice for a compact structure, R=0.9,
  centered well inside a [-3,3]x[-3,3] domain that should not be reached by the (near-)static
  solution before t_final). Confirm against Freidberg [75] or a re-read of the primary source
  if a domain-edge BC statement is later located.
- `b_field_convention: permeability-unity`: inferred from B0=8.0 being stated directly with no
  `sqrt(4*pi)` factor (unlike Sect. 4.1.6/4.2.1 of the same paper), consistent with the paper's
  stated global default (Sect. 2: "the units of B are chosen such that the vacuum magnetic
  permeability is unity"). Not itself flagged as uncertain, but noted here for completeness.

## After resolution
1. Confirm the `domain_bc` convention (or find an explicit statement) on a further read of
   dematte2024 or Freidberg [75].
2. Update `spec.md` `domain_bc` / `## Notes` if a different convention is found.
3. Run `scripts/validate.py`.
4. Run `scripts/reindex.py`.
5. Delete this file.
