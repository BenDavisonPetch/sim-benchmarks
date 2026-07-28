# pending_verification — mhd-current-sheet

## Source
- entry: `mhd-current-sheet`
- authored offline: no

## References awaiting verification

| citekey                  | identifier (as claimed) | what to confirm                                                          | status     |
|---------------------------|--------------------------|---------------------------------------------------------------------------|------------|
| `schlichting-gersten1955` | none (textbook, no DOI)  | H. Schlichting, K. Gersten, "Boundary-Layer Theory" (Springer; 2005 edition cited by dematte2024 as ref [76]); confirm this book states/derives the erf profile shared with mhd-shear-layer's exact solution | unverified |

Same gap as `mhd-shear-layer`'s identical row (this book is cited jointly for both tests in the
source). `scripts/verify_refs.py --lookup` requires a doi/arxiv/url identifier, which this
textbook does not straightforwardly provide. Kept `references_unverified[]` / `status: pending`.

## Candidate bibtex
```bibtex
@book{schlichting-gersten1955,
  title  = {Boundary-Layer Theory},
  author = {Schlichting, Hermann and Gersten, Klaus},
  publisher = {Springer},
  year   = {2005},
  note   = {Cited by dematte2024 (JCP 514, 2024, 113229) as ref [76], German title "Grenzschicht-Theorie"}
}
```

## After resolution
1. Resolve jointly with `mhd-shear-layer`'s identical row (same book, same gap).
2. Move to `references[]` with `verification.status: verified` once resolved.
3. Run `scripts/reindex.py`.
4. Run `scripts/validate.py`.
5. Delete this file.
