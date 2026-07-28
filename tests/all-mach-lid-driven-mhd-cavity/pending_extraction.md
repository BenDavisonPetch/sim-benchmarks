# pending_extraction — all-mach-lid-driven-mhd-cavity

## Source
- entry: `all-mach-lid-driven-mhd-cavity`
- authored from: `dematte2024` (doi: 10.1016/j.jcp.2024.113229), Sect. 4.4
- authored offline: no (`dematte2024`'s DOI verified live; the primary PDF re-read directly, twice, for the two flags below)

## Parameters awaiting extraction
- `x_norm` — used in the lid-velocity profile `u_lid = 4*A*(x_norm - x_norm^2)`; never defined
  anywhere in the visible text of Sect. 4.4 (confirmed by direct re-read of page 30). Presumably a
  normalisation of `x` onto `[0,1]`, but no formula is stated. Do not guess a normalisation —
  genuine gap in the source itself.

## Convention checks
- Ramp-amplitude exponent: the source literally prints
  `A = u_max * exp( -(1 - t_peak)^2 / (2*sigma^2) )` (constant "1", not the time variable "t").
  Taken literally this makes A time-independent, contradicting the described Gaussian-in-time
  ramp (Fig 19 shows Mach number peaking near t=10 in a bump shape) and the surrounding prose
  ("ramped up... ramped down"). Near-certainly a typesetting error for `(t - t_peak)^2`, confirmed
  by direct re-read of page 30 (twice) as printed exactly this way — NOT an OCR/transcription
  artifact on our part. Recorded AS PRINTED in `spec.md` `domain_bc.y_hi.state`; the corrected form
  is NOT substituted and must not be presented as verified source content until independently
  confirmed (e.g. against a companion code repository, if the authors have one, or a published
  erratum).

## After resolution
1. Determine `x_norm`'s definition (author's supplementary material, code repository, or a direct
   author query) and confirm/deny the `(1-t_peak)` vs `(t-t_peak)` reading.
2. Update `domain_bc.y_hi.state` in `spec.md` accordingly; remove the `needs-source` marker on
   `x_norm`; update the FLAG notes in `## Notes` to record the resolution (do not simply delete the
   history of the flag — note what was found and how).
3. Run `scripts/validate.py`.
4. Run `scripts/reindex.py`.
5. Delete this file.
