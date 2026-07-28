# pending_extraction — kelvin-helmholtz-instability-vrmhd

## Source
- entry: `kelvin-helmholtz-instability-vrmhd`
- authored from: `dematte2024` (doi: 10.1016/j.jcp.2024.113229), Sect. 4.3.2
- authored offline: yes

## Parameters awaiting extraction
(none — all IC parameter values (U0, delta_v, a, B0, eta, mu, lambda) are stated directly in the
quoted text.)

## Convention checks
- `domain_bc` (recorded as periodic on all four faces): NOT explicitly (re-)stated in the quoted
  slice of Sect. 4.3.2 for this specific test. x-periodicity is strongly implied by the
  `sin(2*pi*x)` perturbation term (only sensible as a periodic mode on [0,2]); y-periodicity is
  the standard convention for this Dumbser-et-al.-type KH benchmark (the IC already approaches
  uniform states at |y|=1, so periodic and outflow would behave identically to first order, but
  the identity of the *stated* convention is still unconfirmed). Attributed origin `dumbser2019vrmhd`
  is already `verified` in this entry's `references[]` but its own BC statement for this specific
  test was not read in this authoring pass (only `dematte2024`'s Sect. 4.3.2 text was in scope).
  **STATUS: open.** Confirm against `dumbser2019vrmhd`'s full text (arXiv:1801.06592) on a future
  `/add-refs` pass.

## After resolution
1. Confirm the domain_bc convention against `dumbser2019vrmhd`'s primary text.
2. Update `spec.md` domain_bc / Notes if a different convention is found.
3. Run `scripts/validate.py`.
4. Run `scripts/reindex.py`.
5. Delete this file.
