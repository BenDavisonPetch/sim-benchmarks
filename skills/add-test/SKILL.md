---
name: add-test
description: >
  Add test case(s) from a source (PDF | doc | HTML | settings file) into the DB (SPEC §9.1). Runs
  triage.md FIRST (benchmark/NORMAL vs application branch), then normalizes to §3 form, enumerates +
  lets the user pick, carves the picked set to subagents with a verbatim global-defaults block, de-dups
  each, and authors via problem-authoring + validation-authoring + the §5 verification path. Pulled in
  by /add-test. Composes triage.md, dedup, problem-authoring, validation-authoring, vocab-extension.
  Copy-and-fill against templates/. NEVER fabricates a citation. Sonnet-executable; no cleverness.
---

# add-test — source -> normalized -> enumerated -> de-duped -> authored (SPEC §9.1)

Ingest a source document into one or more canonical entries. The source is **never committed** —
everything is converted to the §3 problem form. A full paper holds many tests, so this skill is an
**orchestrator**: it enumerates, lets the user pick, and carves the picked set across subagents without
losing shared parameters. It composes the support skills and invents nothing of its own. Runnable by a
Sonnet-class model.

**Input.** A source path/URL after `/add-test`. **Output.** For each picked test: an existing-entry
pointer (dedup match) or a new `tests/<slug>/spec.md` authored + reindexed + validated, with vocab
proposals batched and schema gaps escalated.

---

## No-fabrication contract (VERBATIM, SPEC §5.2 — the prime safety rule)

> "If you cannot retrieve a source, you MUST NOT emit a `verified` bibtex entry. Record
> `verification.status: unverified` and write what needs checking. A DOI you read off a PDF is a
> claim to be checked, not a verification. Fabricating a citation is the worst failure mode of this
> repo."

This governs every ref and every reference-defined parameter (a value not read in a supplied source is
a `needs-source` claim, never typed from memory — §5.2 extended to parameters).

---

## Step 0. Triage FIRST (run `skills/add-test/triage.md` BEFORE Step 1)

Before anything else, run the source triage in **`triage.md`** (same directory). It classifies the
source as a **benchmark/method** source (NORMAL path — Steps 1–5 below) or an **application/modeling**
source (the APPLICATION branch defined in `triage.md`: harvest quantitatives verbatim, try the
coupled-material representation before crying schema-gap, record reference-defined params as
`needs-source` + `pending_extraction.md`, prefer two-phase `/add-test` then `/add-refs`). Do not
duplicate `triage.md` here — read and follow it, then return to the matching path. The
`## Physical problem` / method split (§1.6) that `triage.md` A2 sets up applies to every step below.

---

## Step 1. Read + normalize the source into §3 problem form

Read the source and convert it to the common problem form (§3). The PDF / settings file is **not**
committed; produce canonical plaintext/structured form. Actively seek **quantitative, automatable**
validation anchors, not merely qualitative description (they drive the score in
`validation-authoring`). Keep the source's own plaintext available for grep-on-demand in Step 2.

---

## Step 2. Bulk consumption — orchestrator + subagents (SPEC §9.1 step 2, in full)

A full paper (many tests) on one Sonnet context risks lost shared parameters and enumeration errors
(14+ at once is an error risk). Orchestrate:

### 2a. Enumerate + let the user pick
List every test the source defines (name + one-line identity sketch). **Let the user pick.** Add-all
only on an **explicit "all"** — never assume it. Single obviously-small sources (one test) skip the
carve and go straight to Step 3.

### 2b. Build the global-defaults block — VERBATIM, never summarized
Extract into one block, **copied verbatim** from the source (never paraphrased):
- the **methods / setup** text (shared γ, unit system, common domain, common BCs, …);
- **every sentence carrying a quantifier**: `all / each / every / throughout / unless otherwise / in
  all runs` (and equivalents). These carry shared parameters that a per-test carve would otherwise
  drop.
This block is passed to **every** subagent so a common value (e.g. one γ used by all tests) is never
lost in the slice.

### 2c. Group the picked tests into subagents
Group by **logical grouping** — same `physics_signature` / siblings together — not strictly one per
test. **~3–5 tests per subagent**, capped by **count OR extracted-token budget, whichever comes
first**. Single-test subagents only for unusually heavy tests.

### 2d. Resolve intra-paper de-dup at enumeration (orchestrator only)
Parallel subagents cannot see each other's in-flight writes. **The orchestrator** resolves de-dup
*between tests in this same paper* at enumeration time (collapse two slices that are the same entry
before dispatch). Subagents de-dup only against the existing **read-only INDEX** (Step 3).

### 2e. Brief each subagent (copy `templates/subagent-brief.template.md`)
Pass each subagent:
- the **global-defaults block** (2b), verbatim;
- its **per-test verbatim slice** (not the whole PDF);
- **read-only** access to the full source plaintext so it can **grep on demand** when it detects a
  referenced-but-unsupplied quantity — instead of hallucinating.
Require each subagent to **return** `inherited_from_global[]` (which values it took from the global
block) + `unresolved_references[]` (referenced-but-unfound quantities). The orchestrator cross-checks:
any value not seen verbatim in the slice or the global block is flagged, not accepted.

### 2f. Batch interruptions; serialize writes
- **Batch all vocabulary proposals into ONE hard-stop** (§7.2) and **all schema gaps into ONE ledger**
  (§12). Never interrupt the user N times.
- **Serialize the write side:** subagents emit `spec.md` drafts in parallel, then the orchestrator runs
  **one** `reindex.py` + **one** `validate.py`. A parallel reindex would race.

---

## Step 3. Per chosen test — de-dup (SPEC §2.4, §9.1 step 3)

Run the **dedup** skill on each chosen test against the read-only `INDEX.tsv`:

- **existing-entry** → do **not** duplicate. Record a `reference_result` (with `params_used`) and/or
  widen a `parameters[]` range on the matched entry, and **point the user to the existing slug**.
- **new-sibling** → new entry (Step 4) + a manual `related_to` link to the sibling(s) (§12 TODO).
- **new-entry** → new entry (Step 4).

---

## Step 4. New entry — author it (SPEC §9.1 step 4)

For a new-entry / new-sibling test:

1. `.venv/bin/python scripts/new_test.py <slug>` — scaffold from `templates/spec.template.md` + empty
   `assets/`. `provenance: literature` (this came from a source).
2. **problem-authoring** — fill the problem half (method-free, §1.6). Reference-defined params →
   `needs-source` + `source_ref` + a `pending_extraction.md` row (never from memory).
3. **validation-authoring** — build `validation_modes[]` + scores from the quantitative anchors found
   in Step 1. ≥1 mode or the entry is rejected (§11.6).
4. **Refs via the verification path (§5).** Online: run `verify_refs.py --meta`; a ref moves to
   `references[]` only when verified, with the printed `meta:` block pasted under `verification:`
   (never typed). Offline: record `references_unverified[]` + emit `pending_verification.md`; emit
   zero `verified` entries. Method/resolution/AMR go in `reference_results[]`, never the problem
   block. (A reference-entangled application source: prefer two-phase — skeleton now, `/add-refs`
   later, per `triage.md` A8.)
   **Record the attribution trail, do not resolve it (§5.4).** Set
   `test_origin.authored_from: <the ref this entry was read from>`, and if the source states where the
   test itself came from ("the vortex of [X]", "the test introduced by [X]"), copy that sentence
   **VERBATIM** into `test_origin.attribution_claims[] {stated_by, quote}` — never paraphrase, never
   chase the identifier here, and **never** set `original_intro` or `test_origin.status` to anything
   but `pending`. `/add-refs` resolves it later; `status: pending` **is** the to-do marker (no extra
   pending-artifact file). A sentence not recorded now is a sentence lost — the reader had the source
   open, `/add-refs` may not.
5. Then the serialized **one** `reindex.py` + **one** `validate.py` (`--offline` if offline).

---

## Step 5. Vocab hard-stop / schema escalate (SPEC §7.2, §12)

- Any registry id or §4 function not yet present → **vocab-extension** hard-stop-and-propose, **batched**
  (§7.2): draft the file, one message, one-word approval, never reference before approval.
- A genuine **schema gap** (no field/shape to hold the information — not a missing id) → record in the
  **one** schema-gap ledger and escalate to the user for re-grilling (§12). Try the coupled-physics
  framing first (`triage.md` A2.5). Do not invent a field.

---

## Done when

Triage ran first and routed to the right path; the source was normalized to §3 form and not committed;
tests were enumerated and the user picked (add-all only on explicit "all"); a verbatim global-defaults
block was built and every subagent returned `inherited_from_global[]` + `unresolved_references[]`;
intra-paper dedup was resolved by the orchestrator; each chosen test was de-duped against INDEX
(existing-entry pointed, not duplicated); new entries authored method-free with ≥1 scored mode and refs
through the §5 verification path (zero fabricated citations); `test_origin.authored_from` +
any verbatim `attribution_claims[]` recorded with `status: pending` and no `original_intro` set; vocab proposals batched into one
hard-stop and schema gaps into one ledger; a single `reindex.py` + single `validate.py` pass.
