# pending_verification — permeable-core-thin-shell-diffusion

Offline authoring (SPEC §5.2B). The single reference is the source web page itself; its identifier
(URL) was read verbatim from the saved HTML. No DOI/author/year is asserted (that would be a
memory-fabricated bibliographic claim). Hand this to an internet-capable pass or `verify_refs.py`.

Delete this file once the reference is verified and moved to `references[]`.

---

## Candidate references (unverified)

| citekey | claimed identifier | to confirm |
|---|---|---|
| `mit6013-ch10-4` | url: https://web.mit.edu/6.013_book/www/chapter10/10.4.html | Resolve the URL; confirm it is MIT 6.013 course notes ch.10.4 Example 10.4.1. Record the canonical author/title/year (Haus & Melcher, *Electromagnetic Fields and Energy*, or the course-notes citation) ONLY from the resolved page — do not fill from memory. |

## After resolution
1. On successful resolution set `verification.status: verified`, fill `source` + `checked`, move to `references[]`.
2. Run `scripts/verify_refs.py` then `scripts/reindex.py` + `scripts/validate.py`.
3. Delete this file.
