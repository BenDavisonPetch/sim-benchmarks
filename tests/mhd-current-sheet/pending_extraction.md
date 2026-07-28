# pending_extraction — mhd-current-sheet

## Source
- entry: `mhd-current-sheet`
- authored from: `dematte2024` (doi: 10.1016/j.jcp.2024.113229), Sect. 4.3.1
- authored offline: yes

## Parameters awaiting extraction
- `Bz0` (constant Bz component of the current-sheet IC): the source's displayed IC equation for
  B gives only a 2-component vector, `B = (0, +/-1.1e4)^T`, matching the stated fact that "the
  exact solution for By is the same as for v in the shear layer test given above." The
  surrounding prose separately states: "Also notice the strong, constant Bz component in the
  initial condition. This added component does not affect the solution for By, but it acts to
  increase the Alfvén wave speed by orders of magnitude..." No numeric value for Bz is given
  anywhere in the equation or the surrounding text on page 27 of the source (confirmed by direct
  re-read, not a transcription/OCR gap on our part). Recorded `canonical: null` /
  `notes: needs-source` in `spec.md`; the `Bz` key is omitted entirely from `initial_conditions`
  rather than guessed or set to 0.
  - Do NOT borrow the Kelvin-Helmholtz test's B0=0.07/sqrt(4*pi) (Sect. 4.3.2) or any other value
    by analogy -- these are unrelated tests with unrelated field-strength choices.
  - Candidate resolution paths for a future pass: (a) check if a companion/supplementary dataset
    or code repository for dematte2024 states this value; (b) check the immediate KH test's own
    text once more for any back-reference; (c) treat "strong" loosely and note that ANY value
    large enough to make v_Alfven >> the diffusion-driven characteristic speeds of this test would
    reproduce the qualitative claim, but this test's `exact-solution-erf-profile` validation mode
    does not require Bz at all (By's exact solution is independent of Bz per the source's own
    statement), so this gap does not block scoring the entry's only validation mode.

## Convention checks
- `domain_bc` (x: outflow/"transmissive"; y: periodic): both stated explicitly in the source
  ("transmissive boundary conditions ... in the x-direction," "Periodic boundary conditions ...
  in the y-direction") -- NOT a gap, recorded directly.

## After resolution
1. If a numeric Bz0 value is ever located in a primary or supplementary source, add it to
   `spec.md`'s `initial_conditions.equilibrium[*].fields.Bz` (as `"<Bz0>"` for x<=0 and `"-<Bz0>"`
   or `"<Bz0>"` for x>0 depending on what the recovered source states about its sign/constancy)
   and to the `Bz0` parameter (`canonical`, drop `needs-source`).
2. Run `scripts/validate.py`.
3. Run `scripts/reindex.py`.
4. Delete this file only if the Bz gap is resolved; otherwise leave it open (a genuine unresolved
   source gap, not an authoring omission).
