# pending_verification — smooth-mhd-vortex

Fixed-format artifact emitted by an **offline** authoring pass (SPEC §5.2B). A DOI read off a PDF
is a claim to be checked, not a verification.

---

## Source
- entry: `smooth-mhd-vortex`
- authored offline: yes

## References awaiting verification

| citekey           | identifier (as claimed)                                     | what to confirm                                                                                   | status     |
|---------------------|---------------------------------------------------------------|-------------------------------------------------------------------------------------------------------|------------|
| `dematte2024`       | `doi: 10.1016/j.jcp.2024.113229` (read off the PDF's own metadata/header) | Title "An all Mach number scheme for visco-resistive magnetically-dominated MHD flows"; Dematté, Farmakalides, Millmore, Nikiforakis; JCP 514 (2024) 113229 | unverified |
| `dumbser2024vrmhd`  | none stated (paper's ref [41], no DOI given)                   | M. Dumbser, D. Balsara, M. Tavelli, F. Fambri, "A divergence-free semi-implicit finite volume scheme for ideal, viscous, and resistive magnetohydrodynamics" (source of this vortex setup) | unverified |
| `fambri2023`        | none stated (paper's ref [42], no DOI given)                   | F. Fambri, "A novel structure preserving semi-implicit finite volume method for viscous and resistive magnetohydrodynamics", Int. J. Numer. Methods Fluids (source of the long-time re-run) | unverified |

## Candidate bibtex
```bibtex
@article{dematte2024,
  title   = {An all Mach number scheme for visco-resistive magnetically-dominated MHD flows},
  author  = {Dematt\'e, Riccardo and Farmakalides, Alexander A. and Millmore, Stephen and Nikiforakis, Nikos},
  journal = {Journal of Computational Physics},
  volume  = {514},
  pages   = {113229},
  year    = {2024},
  doi     = {10.1016/j.jcp.2024.113229}
}
```

## After resolution
1. Run `scripts/verify_refs.py` (online) to resolve each identifier.
2. Move each verified ref `references_unverified[] -> references[]`; stamp `verification`.
3. Run `scripts/reindex.py` (unverified refs are excluded from INDEX until upgraded).
4. Run `scripts/validate.py`.
5. Delete this file.
