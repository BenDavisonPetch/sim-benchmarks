---
name: add-refs
description: >
  Enrich an existing entry with literature references + their findings until a paper section is
  writable (SPEC §9.4 -> §5.5). Per verified ref: fill findings (quantitative numbers verbatim WITH
  units), params_used, method, resolution; resolve test_origin + original_intro (§5.4, chasing a stated
  attribution with cite_chain.py); run verify_refs.py online or
  emit pending_verification.md offline; resolve any pending_extraction.md parameter whose defining ref
  is retrievable. Pulled in by /add-refs. Copy-and-fill against templates/refs-enrichment.worksheet.md.
  NEVER fabricates a citation; never writes "compares with literature".
---

# add-refs — enrich an entry to paper-section quality (SPEC §9.4, §5.3–§5.5)

Fill the reference-provenance half of an existing entry: for each **verified** ref, what it actually
did with this test (`reference_results[]`), where the test came from (`test_origin` +
`original_intro`), and any reference-defined problem parameter now retrievable. Method / resolution /
AMR provenance lives here and **only** here (§1.6) — never in the problem block. Runnable by a
Sonnet-class model.

**Input.** A `<slug>` after `/add-refs`. **Output.** The entry's `reference_results[]`, `references[]`
/ `references_unverified[]`, `test_origin`, and `original_intro` flags filled; offline a
`pending_verification.md`; any resolvable `pending_extraction.md` rows written back.

---

## No-fabrication contract (VERBATIM, SPEC §5.2 — the prime safety rule)

> "If you cannot retrieve a source, you MUST NOT emit a `verified` bibtex entry. Record
> `verification.status: unverified` and write what needs checking. A DOI you read off a PDF is a
> claim to be checked, not a verification. Fabricating a citation is the worst failure mode of this
> repo."

Verification is a **script job with internet** (`verify_refs.py`), never a model judgement. A model
without internet emits `unverified` + a `pending_verification.md` — never a `verified` citation. The
same discipline extends to problem parameters defined only by reference (Step 5): a value you did not
read in a retrieved source is a claim, not a fact.

---

## Step 0. Read the entry; list its refs by status

Open `tests/<slug>/spec.md`. Enumerate `references[]` (verified), `references_unverified[]`
(quarantined), and existing `reference_results[]`. Note whether you are authoring **online** (can
retrieve + run `verify_refs.py`) or **offline** (§5.2B) — it decides Steps 4 and 6.

Copy `templates/refs-enrichment.worksheet.md` — one pass per ref.

---

## Step 1. Per VERIFIED ref, fill the reference_result (SPEC §5.3, §5.5)

A `reference_result` records what a **specific** ref did with **this** test. Fill, per ref (must be a
`references[]` key — online: verified; offline it may resolve to `references_unverified[]`, §5.3 /
check 7 / D-016):

- `key` — the citekey.
- `params_used` — the structural parameters, **values as the ref used them**.
- `method` — the numerical method, provenance ONLY (e.g. "second-order Godunov, unstaggered CT"). This
  is the correct and only home for method language (§1.6).
- `resolution` — grid/AMR as reported.
- `amr` — as reported, or "none".
- `findings` — **specific and quantitative where the ref reports it. Numbers verbatim WITH units**
  (convergence orders, jump sizes, growth rates, resolution thresholds, timings, standoff distances).
  §11.10: quantitative findings are recorded verbatim with units wherever a reference reports them.
- `figure_asset` — optional; if a figure is reproduced, cite it and describe the reproduction.

Never inflate or paraphrase a number. If the ref states "L1 converges at order 1.97", write `1.97`,
not "~2" and not "second order".

**Fetch discipline (cost gate).** Extract findings from the **abstract + the results / convergence
tables + the figure captions** for this test — do **not** pull the full PDF into context. Fetch the
full text only when a specific number you must record is absent from those sections. Pulling whole
papers is the dominant token cost of this skill and is almost never needed for `findings`.

**Verified-but-unreadable ref (deadlock escape).** A ref whose identifier resolves (so it is legitimately
`verified`) but whose text is genuinely inaccessible (paywalled + no free/arXiv copy) gets **no**
`reference_result` — leave it out and add a one-line YAML comment saying why. Never type
findings/method/resolution from a secondary summary or memory to satisfy "Done when" — the
no-fabrication contract wins over completeness.

---

## Step 2. Resolve the test's origin (SPEC §5.4 — `test_origin` + `original_intro`)

`test_origin` is entry-level (one originator per test); `original_intro` is the per-ref boolean that
marks it when the originator is in `references[]`. Both are set **only** here — `/promote-refs` never
touches them, `/add-test` only records `authored_from` + `attribution_claims[]`.

**Definitions (verbatim, SPEC §5.4 rule 1).** A **using-ref** is a `references[]` entry with a
`reference_results[]` row (it ran this test), plus `test_origin.authored_from`. A ref cited only as a
`parameters[].source_ref`, or only as a mode `inputs.reference` of `kind: reference` (an empirical
model / data source), is **not** a using-ref. **Publication year** = `verification.meta.year`, never a
citekey year.

**2a. Read what the using-refs *state* about provenance.** A bare citation is not a statement; "the
vortex of [X]", "the test introduced by [X]", "we use the setup of [X]" is. Copy the sentence
**verbatim** into `test_origin.attribution_claims[]` with `stated_by`. Never paraphrase.

**2b. Chase a stated attribution to an identifier.**

```bash
.venv/bin/python scripts/cite_chain.py --citing <the stating ref's doi> --match <author surname>
```

This greps the citing work's publisher-deposited Crossref reference list and prints
`DOI | author | year | title | journal`. Two honest no-answers: **no deposited reference list** (common
for books) and **DOI-only rows** (AGU/Wiley deposit bare DOIs, so a surname cannot match — the script
says how many). Neither means the citation is absent: fall back to `WebSearch`, or match a DOI fragment
and confirm it with `verify_refs.py --lookup <doi>`. Never guess an identifier.

**2c. Apply the rule, in precedence order.**

1. **Stated attribution beats dates.** (a) The attributed work is already in `references[]` → it is
   `original_intro: true`, `status: resolved-in-list`. (b) It is **not** in the list → chase it, and
   once its identifier verifies, **add** it and set it `true`; this is the one sanctioned case of
   add-refs adding a ref purely for provenance, and an unreadable originator correctly carries no
   `reference_results` row. (c) The chase does not verify → **no** ref is `true`;
   `status: resolved-external` + `external: {author, year, doi?}` recording what the claim says.
2. **Otherwise the earliest using-ref** by `meta.year` is `true`; every other using-ref is `false`.
3. **Unknown stays unknown.** Missing years, tied years, or an unfinished chase → **no**
   `original_intro` anywhere, `status: pending` + a note. `pending` is a correct answer; a guess is not.
4. **`provenance: synthesized` → `status: synthesized`** (optional `derived_from`), never any `true` —
   a synthesized entry has no literature originator.
5. At most **one** `true` per entry, and only on a verified key. For a **dedup-folded** multi-preset
   entry "the test" is the fold-level test — one `true` across all folded presets, never per-preset.

Beware near-misses: "similar to [X]" is **not** origination. Without a verbatim sentence in hand the
honest result is `status: pending`.

**2d. Write it.**

```yaml
test_origin:
  status: resolved-in-list          # | resolved-external | pending | synthesized
  ref: brio1988                     # required iff resolved-in-list; the original_intro: true key
  authored_from: dematte2024        # the ref this entry was ingested from (set by /add-test)
  external: { author: Balsara, year: 2004, doi: "10.1086/381377" }   # iff resolved-external
  attribution_claims:
    - stated_by: dematte2024
      quote: "<verbatim sentence stating where the test came from>"
```

`validate.py` check 11 enforces this structurally (one `true`; `true` only on a verified key; no
using-ref older than the `true` ref; no `true` under `resolved-external`/`synthesized`).

---

## Step 3. Prose fit — write for a paper section, never "compares with literature"

The point of enrichment is a writable paper section. In `## Validation notes` (and any per-mode
elaboration) tie the ref findings to the entry's validation modes with **specific** numbers and units.
**Never** write "compares with literature" or any equivalent vague filler (§11.6 spirit); state *what*
each ref found and *how* it validates the test.

---

## Step 4. Verify — online run verify_refs.py; offline emit pending_verification.md (SPEC §5.2)

- **Online:** run `.venv/bin/python scripts/verify_refs.py --meta`. The script is **report-only** — an
  in-place `--write` upgrade is deliberately not implemented (PyYAML would strip the authored inline
  comments, D-012). It prints `RESOLVED` / `UNRESOLVED` / `UNDECIDED` per identifier plus a
  paste-ready `meta:` block, but does **not** move anything: **you hand-edit** the frontmatter to move
  each `RESOLVED` ref `references_unverified[] -> references[]`, stamp `verification.status: verified`
  + `source` (the printed detail) + `checked` (date), and **paste** the printed `meta:` block under
  `verification:`. Never type `meta` by hand — check 10 compares it against the live resolution.
  Re-run the script after editing; a `verified` ref that prints `UNRESOLVED` **hard-fails** — fix or
  downgrade it, never fake an identifier. `UNDECIDED` means the network could not decide (timeout /
  5xx): retry later, promote nothing.
- **A DOI that does not resolve does not exist.** The resolver never contacts a publisher landing
  page: DOIs go to Crossref, then DataCite, then the DOI Handle API, none of which bot-block or
  captcha. A DOI that 404s on **all three** does not exist. Never substitute an arXiv id to make a DOI
  "pass" — that records the wrong canonical identifier; when a ref has both, record **both** under
  `identifier` (the resolver then reports the priority date as `meta.year`).
- **Offline:** record every candidate ref as `status: unverified` in `references_unverified[]` with
  its claimed identifier extracted **verbatim** from the source (a claim, not proof). Emit
  `tests/<slug>/pending_verification.md` from `templates/pending_verification.template.md` (top-level):
  candidate bibtex + exactly what to confirm. Do **not** emit any `verified` entry.

---

## Step 5. Resolve pending_extraction.md rows whose defining ref is retrievable (SPEC §5.5)

If `tests/<slug>/pending_extraction.md` exists, for each `needs-source` row whose defining ref you can
**actually retrieve**:

- Read the value from the retrieved source; write it into the named `spec.md` field; set the
  parameter's `source_ref: <citekey>`; remove the row.
- A value you **cannot** retrieve stays `needs-source` — **never** typed from memory (the contract
  line applies to parameters too). Leave its row.
- Answer any convention check (b-field convention, unit system) only from a retrieved source.

Delete `pending_extraction.md` only once **every** row is resolved.

---

## Step 6. Reindex + validate

Run **one** `.venv/bin/python scripts/reindex.py` (unverified refs stay excluded from INDEX until
upgraded) then `.venv/bin/python scripts/validate.py` (`--offline` when offline — check 7 then accepts
a `references_unverified[]` key, check 10 downgrades to a warning; online enforces verified-only). Fix
any failure before finishing.

---

## Done when

Every verified ref has a `reference_result` with `method`/`resolution`/`amr` (provenance-only, never in
the problem block) and quantitative `findings` **verbatim with units** — **except** a
verified-but-unreadable ref, which correctly carries no `reference_result` plus a comment saying why;
`test_origin` written with any attribution sentence quoted **verbatim**, and `original_intro` set by
the §5.4 rule (or left unset with `status: pending`, never guessed); no "compares with literature" anywhere;
online `verify_refs.py` ran (offline emitted `pending_verification.md` and zero `verified` entries);
every retrievable `pending_extraction.md` row was written back with a `source_ref` (unretrievable rows
left `needs-source`, never fabricated); `reindex.py` + `validate.py` pass.
