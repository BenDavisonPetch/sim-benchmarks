# pending_verification — ideal-mhd-riemann-problem

Fixed-format artifact emitted by an **offline** authoring pass (SPEC §5.2B). A DOI read off a PDF
is a claim to be checked, not a verification.

---

## Source
- entry: `ideal-mhd-riemann-problem`
- authored offline: yes

## References awaiting verification

| citekey          | identifier (as claimed)                    | what to confirm                                                        | status     |
|-------------------|--------------------------------------------|--------------------------------------------------------------------------|------------|
| `dematte2024`     | `doi: 10.1016/j.jcp.2024.113229` (read off the PDF's own metadata/header) | Title "An all Mach number scheme for visco-resistive magnetically-dominated MHD flows"; Dematté, Farmakalides, Millmore, Nikiforakis; JCP 514 (2024) 113229 | unverified |
| `brio1988`        | none stated (paper's ref [64], no DOI given) | M. Brio, C.C. Wu, "An upwind differencing scheme for the equations of ideal magnetohydrodynamics", J. Comput. Phys. 75 (1988) 400-422 | unverified |
| `ryujones1995`    | none stated (paper's ref [65], no DOI given) | D. Ryu, T.W. Jones, "Numerical magnetohydrodynamics in astrophysics: algorithm and tests for one-dimensional flow", Astrophys. J. 442 (1995) 228 | unverified |
| `dumbser2024vrmhd`| none stated (paper's ref [41], no DOI given) | M. Dumbser, D. Balsara, M. Tavelli, F. Fambri, "A divergence-free semi-implicit finite volume scheme for ideal, viscous, and resistive magnetohydrodynamics" | unverified |
| `fambri2023`      | none stated (paper's ref [42], no DOI given) | F. Fambri, "A novel structure preserving semi-implicit finite volume method for viscous and resistive magnetohydrodynamics", Int. J. Numer. Methods Fluids | unverified |

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
@article{brio1988,
  title   = {An upwind differencing scheme for the equations of ideal magnetohydrodynamics},
  author  = {Brio, M. and Wu, C.C.},
  journal = {Journal of Computational Physics},
  volume  = {75},
  pages   = {400--422},
  year    = {1988}
}
@article{ryujones1995,
  title   = {Numerical magnetohydrodynamics in astrophysics: algorithm and tests for one-dimensional flow},
  author  = {Ryu, D. and Jones, T.W.},
  journal = {Astrophysical Journal},
  volume  = {442},
  pages   = {228},
  year    = {1995}
}
```

## After resolution
1. Run `scripts/verify_refs.py` (online) to resolve each identifier.
2. Move each verified ref `references_unverified[] -> references[]`; stamp `verification`.
3. Run `scripts/reindex.py` (unverified refs are excluded from INDEX until upgraded).
4. Run `scripts/validate.py`.
5. Delete this file.
