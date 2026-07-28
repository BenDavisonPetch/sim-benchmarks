# pending_verification — mhd-shear-layer

## Source
- entry: `mhd-shear-layer`
- authored offline: no (online authoring pass; `dematte2024` and `dumbser2019vrmhd`/`fambri2021`-
  style refs verify live via `verify_refs.py`, but this entry cites no other numeric reference —
  only the textbook below)

## References awaiting verification

| citekey                  | identifier (as claimed) | what to confirm                                                          | status     |
|---------------------------|--------------------------|---------------------------------------------------------------------------|------------|
| `schlichting-gersten1955` | none (textbook, no DOI)  | H. Schlichting, K. Gersten, "Boundary-Layer Theory" (Springer; the 2005 8th/German "Grenzschicht-Theorie" edition is the one dematte2024 cites as ref [76]); confirm this book states/derives the erf shear-layer solution v(x,t) = -erf(x/(2*sqrt(mu*t))) | unverified |

`scripts/verify_refs.py --lookup` requires a doi/arxiv/url identifier, which this textbook
(a well-known fluid-mechanics reference with many editions/ISBNs and no single canonical DOI)
does not straightforwardly provide. Not fabricated as `verified`; kept in
`references_unverified[]` with `status: pending`.

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
1. Locate an ISBN/DOI (e.g. via the publisher's catalogue or a library-metadata API) and confirm
   via `scripts/verify_refs.py` (or a manual identifier lookup if the tool does not support ISBN).
2. Move to `references[]` with `verification.status: verified` once resolved.
3. Run `scripts/reindex.py`.
4. Run `scripts/validate.py`.
5. Delete this file.
