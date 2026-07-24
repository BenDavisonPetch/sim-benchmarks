---
name: promote-refs
description: >
  Verify the identifiers of an entry's already-listed references_unverified[] and, for each that
  resolves online, move it references_unverified[] -> references[] with a verification stamp — so
  verify_refs.py / validate.py pass in online mode (verified-only). The shallow counterpart to
  add-refs: it NEVER adds a new reference, NEVER writes reference_results/findings, and NEVER pulls
  full paper text. Identifier discovery + the unverified->verified move ONLY. Pulled in by
  /promote-refs. NEVER fabricates a citation or an identifier.
---

# promote-refs — verify + promote existing refs (SPEC §5.2A, §5.3)

Take the refs an entry **already lists** in `references_unverified[]`, resolve their identifiers
online, and move the ones that resolve into `references[]` with a `verification` stamp. Nothing else.
This is the fast path when an offline authoring pass (or `add-test`) left `references_unverified[]`
populated and the only thing blocking an online `validate.py` is that `reference_results[]` / mode
`inputs.reference` keys point at not-yet-verified refs (check 7 / check 10). Runnable by a
Sonnet-class model.

**Input.** A `<slug>` after `/promote-refs`, or **blank = sweep every entry** that has a non-empty
`references_unverified[]`. **Output.** Resolved refs moved to `references[]` with stamps; unresolvable
refs left in `references_unverified[]`; `reindex.py` + online `validate.py` pass (or the remaining
failures are pre-existing and unrelated).

---

## No-fabrication contract (VERBATIM, SPEC §5.2 — the prime safety rule)

> "If you cannot retrieve a source, you MUST NOT emit a `verified` bibtex entry. Record
> `verification.status: unverified` and write what needs checking. A DOI you read off a PDF is a
> claim to be checked, not a verification. Fabricating a citation is the worst failure mode of this
> repo."

Verification is a **script job with internet** (`verify_refs.py`), never a model judgement. A
`verified` ref with no resolvable identifier hard-fails the build. Never stamp `verified` on an
identifier that resolves nowhere, and never invent an identifier to make a ref pass.

---

## Scope — what this skill does NOT do

Hard boundaries (they are `add-refs`'s job, not this skill's):

- **Never add a reference** that is not already in `references_unverified[]`. If a needed citation is
  missing entirely, stop and tell the user to run `/add-refs` — do not author one here.
- **Never write or edit `reference_results[]`, `findings`, `params_used`, `method`, `resolution`, or
  `amr`.** No enrichment.
- **Never pull full paper text.** Identifier discovery only — see Step 1.
- **Never touch `pending_extraction.md`** or the problem block.

The one derived field this skill does set is `original_intro`, and only by the mechanical §5.4 rule
(Step 3) — never by research.

---

## Step 0. Read the entry; list unverified refs

Open `tests/<slug>/spec.md` (or each spec, if sweeping). Enumerate `references_unverified[]`. If it is
empty, there is nothing to do — report and stop. Confirm you are **online**; this skill cannot promote
offline (Step 4).

---

## Step 1. Ensure each unverified ref has an identifier (discovery only)

For every ref in `references_unverified[]`:

- If it already carries an identifier (`verification.identifier.doi` / `arxiv` / `url`), use it.
- If the identifier is **empty**, find it with `WebSearch` on the ref's title + authors (from its
  `bibtex` block or the entry's `pending_verification.md` "what to confirm" column). `WebFetch` a
  single candidate landing page (DOI page, arXiv `/abs/` page, publisher record) **only to confirm
  the title + authors + journal match** — this is identifier confirmation, **not** content
  extraction. Do NOT fetch the PDF or read the body. Write the confirmed identifier into
  `verification.identifier`.
- If you cannot find a matching identifier, leave the ref in `references_unverified[]` — never guess
  one.

---

## Step 2. Resolve + move (verify_refs.py is report-only — you hand-edit)

Run `.venv/bin/python scripts/verify_refs.py`. The script is **report-only**: its `--write` upgrade is
deliberately not implemented (PyYAML would strip authored inline comments, D-012). It prints
`RESOLVED`/`UNRESOLVED` per identifier but moves nothing.

For each ref that printed **RESOLVED**, hand-edit the frontmatter:

- Move the entry from `references_unverified[]` into `references[]`.
- Stamp `verification: { status: verified, identifier: {...}, source: "<what resolved it>",
  checked: "<YYYY-MM-DD>" }`.

Leave every `UNRESOLVED` ref in `references_unverified[]` with `status: unverified`.

**Valid-but-bot-blocked identifier.** Some publishers (e.g. Wiley) return HTTP 403 to the script's
non-browser requests even for a valid DOI. If the identifier is corroborated (title/authors matched a
retrieved landing page in Step 1), record a **resolvable** identifier — prefer the arXiv id, which
resolves 200 — as the `verified` identifier and note the blocked DOI in `source`. Do **not** hard-fail
and do **not** fabricate.

Re-run `verify_refs.py`; every ref now in `references[]` must print `RESOLVED`.

---

## Step 3. Set original_intro for newly-verified using-refs (§5.4 rule only)

Only if a promoted ref is a **using-ref** (it has a matching `reference_result[]` or a mode
`inputs.reference` pointing at it) and its `original_intro` is unset. Apply the §5.4 rule mechanically,
using **actual publication dates** (not citekey years): among the verified using-refs, the earliest
publication is `original_intro: true`, every other is `false`; if a ref states it took the test from
elsewhere, follow that. If dates cannot be ordered, leave `unknown` and note it. **Never** research
beyond the date ordering. For a dedup-folded multi-preset entry, "the test" is the fold-level test —
one `true` across all folded presets.

---

## Step 4. Reindex + validate

Run `.venv/bin/python scripts/reindex.py`, then online `.venv/bin/python scripts/validate.py`. Newly
verified refs now satisfy check 7 (`reference_results[]` / mode keys resolve to `references[]`) and
check 10 (identifiers resolve). Fix any failure **that this entry introduced**; pre-existing failures
in other entries are out of scope — report them, do not touch them.

Offline (`--offline`): promotion is impossible (no live resolution). Run only the static gate to
confirm nothing regressed, report that promotion needs an online run, and stop.

---

## Done when

Every `references_unverified[]` ref whose identifier resolves online has moved to `references[]` with a
`verification` stamp (`status: verified` + identifier + `source` + `checked`); unresolvable refs remain
`unverified`; **zero** new references, `reference_results`, or findings were authored; `original_intro`
set by the §5.4 rule only where a promoted using-ref needed it; `reindex.py` + online `validate.py`
pass for this entry (any remaining errors are pre-existing and in unrelated entries).
