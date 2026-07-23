# pending_verification — <slug>

Fixed-format artifact emitted by an **offline** authoring pass (SPEC §5.2B). Lists candidate
references recorded as `status: unverified` that an internet-capable pass — or
`scripts/verify_refs.py` — must confirm before they may move into `references[]`.

> A DOI you read off a PDF is a **claim to be checked, not a verification**. Fabricating a
> citation is the worst failure mode of this repo (SPEC §5.2).

Delete this file once every ref is verified and moved `references_unverified[] -> references[]`.

---

## Source
- entry: `<slug>`
- authored offline: `<yes|no>`

## References awaiting verification

For each: resolve the identifier live; on success set `verification.status: verified`, fill
`source` + `checked`, and move the entry into `references[]`; then remove the row here.

| citekey        | identifier (as claimed)      | what to confirm                                  | status     |
|----------------|------------------------------|--------------------------------------------------|------------|
| `<citekey>`    | `doi/arxiv/url: <value>`     | `<title / authors / year to match against>`      | unverified |

## Candidate bibtex
```bibtex
@article{<citekey>,
  title   = {<title>},
  author  = {<authors>},
  journal = {<journal>},
  year    = {<year>},
  doi     = {<doi>}
}
```

## After resolution
1. Run `scripts/verify_refs.py` (online) to resolve each identifier.
2. Move each verified ref `references_unverified[] -> references[]`; stamp `verification`.
3. Run `scripts/reindex.py` (unverified refs are excluded from INDEX until upgraded).
4. Run `scripts/validate.py`.
5. Delete this file.
