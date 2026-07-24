---
name: create-test
description: >
  Synthesize a NEW or derived test spec that does not yet exist, from a free-text description (SPEC
  §9.3). De-dup FIRST (refuse + point if it exists), scaffold with provenance: synthesized, author the
  problem via problem-authoring, then MANDATORY validation-authoring (a spec with no validation path is
  rejected), optionally emit pending_derivation.md. Pulled in by /create-test. Copy-and-fill against
  templates/synthesis.worksheet.md; the canonical single-file scaffold is templates/spec.template.md.
---

# create-test — synthesize a new/derived spec (SPEC §9.3, §2.4, §6, §7.2)

Turn a free-text description into a canonical `spec.md` that did not exist before. Unlike `/add-test`
there is no source document — the physics comes from the description — so de-dup is the first gate
(never mint a duplicate) and a validation path is mandatory (a synthesized spec with no way to check
it is worthless and is rejected). This skill composes the support skills; it invents no procedure of
its own. Runnable by a Sonnet-class model.

**Input.** The user's free-text description after `/create-test` (e.g. "rotated Sod in an embedded
rectangle"). **Output.** Either a refusal + pointer to the existing entry (Step 1), or a new
`tests/<slug>/spec.md` with `provenance: synthesized`, ≥1 scored validation mode, and — if it admits a
stronger analytic solution than can be derived now — a `pending_derivation.md` (Steps 2–6).

---

## Step 0. Draft the identity-driving fields from the description

Copy `templates/synthesis.worksheet.md` and fill it from the description: the physics_signature
(materials `base` + terms present, coupling), `analysis_treatments`, `capability_flags`, and the
IC / geometry / BC-state **structural form** — enough to run `dedup`. Do **not** scaffold a file yet.
This is the same identity information `problem-authoring` Step 1–2 needs; the worksheet just front-loads
it so de-dup can run before any write.

---

## Step 1. De-dup FIRST — if it matches, REFUSE and point (SPEC §9.3 step 1, §2.4)

Run the **dedup** skill on the Step-0 draft (its `INDEX.tsv` must exist; run `reindex.py` first if
not). Act on its single decision:

- **existing-entry** (structural match, only numeric values differ) → **refuse to create.** Do not
  scaffold. Tell the user the matching slug and that their description is a parameter variation of it
  (offer to record a `reference_result` / widen a `parameters[]` range via `/add-test` instead).
- **new-sibling** (same physics_signature, differing `analysis_treatments`/`capability_flags`) →
  proceed to Step 2; note the sibling slug(s) for a manual `related_to` link (auto-linking deferred,
  §12 TODO).
- **new-entry** (no structural match) → proceed to Step 2.

Creating over a dedup match is the one thing this command must never do.

---

## Step 2. Scaffold with provenance: synthesized

Run `.venv/bin/python scripts/new_test.py <slug>` to scaffold `tests/<slug>/` from
`templates/spec.template.md` + an empty `assets/`. Pick a physically-descriptive kebab-case slug
(§1.2). In the scaffolded `spec.md` set `provenance: synthesized` (this is the field that marks a
`/create-test` entry, distinct from `literature`).

---

## Step 3. Author the problem (problem-authoring)

Run **problem-authoring** to fill the problem half from the description: `physics`, `dimension`,
`analysis_treatments`, `capability_flags`, `geometry`, `units`, `initial_conditions`, `parameters`,
`domain_bc`, `internal_boundaries`, `time`, and the problem-owned prose sections. Transcribe the
Step-0 worksheet answers straight in (they were already drafted for dedup). Honour the §1.6 hard
boundary — no method, resolution, AMR, or grid anywhere.

There is no source paper, so there are normally no reference-defined parameters and no
`pending_extraction.md`. If the description itself cites a value to a paper, treat it exactly as
`problem-authoring` Step 6 mandates (`needs-source` + `source_ref` + a `pending_extraction.md` row) —
never type it from memory.

---

## Step 4. Author validation — MANDATORY (SPEC §9.3 step 3, §11.6)

Run **validation-authoring** to build `validation_modes[]` + scores + the validation-owned prose
sections. This is **not optional**: a synthesized spec with no validation path is **rejected**. At
least one mode, each with a SPECIFIC `purpose` (never "compare with literature"), a registry procedure
with filled slots, and a `score` ∈ 1..5 with justification.

A freshly synthesized test often has no verified reference yet, so it scores on characterisation
quality + reproduction breadth (rubric rows 1–2) or on a self-check it admits (e.g.
`well-balancing`, `conservation-drift` **only if genuinely discriminating**, §6.4). If it admits an
exact/analytic solution you can state now, use `exact-solution-compare` and score accordingly;
otherwise the mode carries a **provisional low score** and Step 5 applies.

---

## Step 5. Optional — emit pending_derivation.md for a stronger analytic solution (SPEC §9.3 step 4)

If the test plausibly admits an **exact/analytic** solution (or a stronger closed-form reference) that
you cannot derive here, copy `templates/pending_derivation.template.md` (top-level) to
`tests/<slug>/pending_derivation.md` and fill it: what to attempt, the regime in which it is exact,
why it is provisional now. Until the derivation lands, the entry keeps its **provisional (low) score**;
a resolved derivation can later upgrade a mode (e.g. to `exact-solution-compare`) and raise the score.

Do not inflate the score in anticipation — the score reflects what is checkable **today**.

---

## Step 6. Vocab hard-stop / schema escalate; reindex + validate

- Any registry id or §4 function the description needs that does not exist → **vocab-extension**
  hard-stop-and-propose (§7.2): draft the file, batch into one message, one-word approval, never
  reference before approval.
- A genuine **schema gap** (no field/shape to hold the information — not merely a missing id) →
  escalate to the user for re-grilling (§12); do not invent a field. (Try the coupled-physics framing
  first, triage.md A2.5.)
- Then run **one** `.venv/bin/python scripts/reindex.py` (sets `headline_score`, computes flags +
  INDEX) and **one** `.venv/bin/python scripts/validate.py` (`--offline` when authoring offline). Fix
  any check failure before finishing.

---

## Done when

De-dup ran **before** any scaffold and a match caused a refusal-with-pointer (never a duplicate);
`provenance: synthesized` is set; the problem block is method-free and every expression parses; there
is ≥1 scored validation mode (validation was mandatory, not skipped); a `pending_derivation.md` exists
iff a stronger analytic solution is plausible-but-underived and the score stays provisional until then;
all vocab was approved before reference and schema gaps escalated; `reindex.py` + `validate.py`
(`--offline` if offline) pass.
