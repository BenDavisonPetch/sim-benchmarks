---
name: add-refs
description: >
  Enrich an existing entry with literature references + their findings until a paper section is
  writable (SPEC §9.4 -> §5.5). Per verified ref: fill findings (quantitative numbers verbatim WITH
  units), params_used, method, resolution; resolve original_intro (§5.4); run verify_refs.py online or
  emit pending_verification.md offline; resolve any pending_extraction.md parameter whose defining ref
  is retrievable. Pulled in by /add-refs. Copy-and-fill against templates/refs-enrichment.worksheet.md.
  NEVER fabricates a citation; never writes "compares with literature".
---

# add-refs — enrich an entry to paper-section quality (SPEC §9.4, §5.3–§5.5)

Fill the reference-provenance half of an existing entry: for each **verified** ref, what it actually
did with this test (`reference_results[]`), the earliest-user attribution (`original_intro`), and any
reference-defined problem parameter now retrievable. Method / resolution / AMR provenance lives here
and **only** here (§1.6) — never in the problem block. Runnable by a Sonnet-class model.

**Input.** A `<slug>` after `/add-refs`. **Output.** The entry's `reference_results[]`, `references[]`
/ `references_unverified[]`, and `original_intro` flags filled; offline a `pending_verification.md`;
any resolvable `pending_extraction.md` rows written back.

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

---

## Step 2. Resolve original_intro (SPEC §5.4 — by RULE, never guessed)

`original_intro` is per-ref, default `unknown`. Set it **only** here, by this rule:

- Among the **verified** refs that use this test, the **earliest publication** is
  `original_intro: true` — **unless** a ref states it took the test from elsewhere, in which case
  follow that stated attribution.
- Every other using ref is `original_intro: false`.
- **Never guess beyond this rule.** If you cannot order the refs by date (e.g. all unverified
  offline), leave `unknown` and note it — do not invent a priority.

---

## Step 3. Prose fit — write for a paper section, never "compares with literature"

The point of enrichment is a writable paper section. In `## Validation notes` (and any per-mode
elaboration) tie the ref findings to the entry's validation modes with **specific** numbers and units.
**Never** write "compares with literature" or any equivalent vague filler (§11.6 spirit); state *what*
each ref found and *how* it validates the test.

---

## Step 4. Verify — online run verify_refs.py; offline emit pending_verification.md (SPEC §5.2)

- **Online:** run `.venv/bin/python scripts/verify_refs.py`. On success it resolves identifiers and
  the ref may move `references_unverified[] -> references[]` with `verification.status: verified` +
  `source` + `checked`. A `verified` ref with no resolvable identifier **hard-fails** — fix or
  downgrade it, never fake an identifier.
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
the problem block) and quantitative `findings` **verbatim with units**; `original_intro` set by the
§5.4 rule (or left `unknown` with a note, never guessed); no "compares with literature" anywhere;
online `verify_refs.py` ran (offline emitted `pending_verification.md` and zero `verified` entries);
every retrievable `pending_extraction.md` row was written back with a `source_ref` (unretrievable rows
left `needs-source`, never fabricated); `reindex.py` + `validate.py` pass.
