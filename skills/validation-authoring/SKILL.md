---
name: validation-authoring
description: >
  Build validation_modes[] for an entry — choose a registry procedure, fill its slots, set a SPECIFIC
  purpose (never "compare with literature"), and score each mode against docs/scoring-rubric.md,
  including differential (baseline A/B) modes. Pulled in by /add-test and /create-test. Copy-and-fill
  against templates/validation-mode.worksheet.md; every entry needs >=1 mode or it is rejected.
---

# validation-authoring — validation_modes[] + scoring (SPEC §5.3, §6, §11.6/8)

Fills the validation half of an entry: `validation_modes[]`, the `## What this test actually tests`
and `## Validation notes` body sections, and (with `add-refs`) the `reference_results[]` a mode cites.
Every entry has **≥1** mode; a spec with no validation path is rejected (§9.3, §11.6).

Authorities: `docs/scoring-rubric.md` (the 1–5 table + rules), `docs/procedures.md` (norm/formula
definitions), `registry/procedures/*` (the procedure slots).

> **One-file rule (§11.9).** Fill these fields inside the single `spec.md` (from
> `templates/spec.template.md`). `templates/validation-mode.worksheet.md` is a per-mode decision
> worksheet — one pass per mode, then discard. Never freehand a second scaffold.

---

## Step 1. Find the quantitative anchors (do this before choosing a procedure)

List every quantitative, ideally **automatable**, way this problem can be checked. Prefer
quantitative over qualitative (§9.1 step 1). Candidate anchors:

- an exact / analytic solution (→ score 5 territory);
- a community-accepted canonical solution + a reliable automatable check (→ 4);
- a specific reference result to compare against (→ 3);
- specific named features that are meaningful even without an automatable check (→ 2);
- a single qualitative result only (→ 1).

Each distinct anchor is a **separate mode**. Do not collapse two genuinely different checks into one.

---

## Step 2. Choose a procedure per anchor (registry-backed, §6.1)

Map each anchor to a `registry/procedures` id and fill its slots (`inputs`). Seed procedures:

| Procedure | Use when the anchor is… |
|---|---|
| `exact-solution-compare` | an exact/analytic solution sampled at cell centroids |
| `convergence-order` | measured order p vs the theoretical order |
| `self-convergence` | Richardson vs a high-resolution reference (no exact soln) |
| `rankine-hugoniot-jump` | measured pre/post states vs analytic jump conditions |
| `feature-location` | positions of named shocks/contacts along cut-lines vs a reference |
| `well-balancing` | an equilibrium that must be preserved (+ perturbation preservation) |
| `norms` | L1/L2/Linf error magnitudes (volume-weighted; cut-cell ⇒ active-volume weighted) |
| `conservation-drift` | mass/flux drift vs time — **universal diagnostic** (§6.4) |
| `div-b` | ‖∇·B‖ vs a criterion — **universal diagnostic** (§6.4) |

**A mode may NOT invent an ad-hoc procedure.** If none fits, **vocab-extension** hard-stop: propose a
new `registry/procedures/<id>.md` (from `templates/procedure.template.md`) with its formula defined
once in `docs/procedures.md`, for one-word approval (§6.1, §7.2). Never inline a bespoke procedure.

**Universal-diagnostic rule (§6.4).** `div-b` and `conservation-drift` appear as a **scored** mode
**only** when genuinely discriminating for *this* problem — and the entry must state *why* it is
challenging here vs generic. Otherwise they are provenance metrics, **unscored** (do not add a
`score`).

---

## Step 3. Fill the mode

Per mode (see the worksheet for the field list):

- `id` — unique within the entry, kebab-case.
- `purpose` — a **SPECIFIC** capability statement. **NEVER** "compare with literature" (§11.6). Say
  *what* is being verified: "Verify positions of the named MHD shocks along stated cut-lines."
- `procedure` — the id from step 2.
- `inputs` — the procedure's slots: `at_time` (≤ `t_final`), `variables`, and procedure-specific
  slots (`cut_lines`, `features`, refinement ratio `r`, resolution sequence, `tolerance`), plus
  `reference: { kind: reference | reference-result, key: <key> }` where cited.
- `has_exact_solution` — bool.
- `score` (1–5) + `score_justification` (mandatory string).

**Reference key rule (§5.3, check 7).** A `reference_result` key, and any `inputs.reference` of
`kind: reference`, must be a **verified** `references[]` key online. Offline (§5.2B) it may resolve to
`references_unverified[]` — `validate.py --offline` downgrades check 7 accordingly (D-016); online
still enforces verified-only. Never invent a key.

---

## Step 4. Score against the rubric (docs/scoring-rubric.md)

| Score | Requires |
|------:|----------|
| **5** | Exact/analytic solution + quantitative convergence to the theoretical order. |
| **4** | No exact solution; community-canonical solution; reliable automatable quantitative check (self-convergence, RH-jump, growth-rate, feature-location). |
| **3** | Quantitative comparison to reference result(s); partial feature coverage. |
| **2** | No automatable check, but solution well-characterised (specific named features) and/or widely reproduced — qualitative match is meaningful and specific. |
| **1** | Single result, qualitative, no specific checkable features. |

Rules (§6.3):

- **No proxy is forced.** Use an automatable proxy only if reliable and cheap; otherwise score by
  characterisation quality + reproduction breadth (rows 2/1). Do **not** use symmetry as a proxy where
  AMR/gridding breaks it.
- Every mode carries a `score_justification`.
- Do not let prose richness inflate a score. An observation/model comparison (no exact solution) tops
  at **3**.
- Headline score = `max(validation_modes[].score)` — **set by `reindex.py`**, never hand-edited.

---

## Step 5. Differential (baseline A/B) modes (§6.3A)

When the meaningful measurand is the **difference** between the canonical run and a controlled variant
(e.g. standoff with vs without an inductive core), author it as **one mode on one entry** carrying:

- `baseline: { description: "...", config_delta: { "<dotted.path>": "<value>" } }` — the config delta
  serving as the differential reference;
- `measured: "<the difference being measured>"`.

Scoring reflects the **difference** measurement, not either run alone: a controlled quantitative A/B
tops at **3** absent an exact solution.

**Guard (check 9, §11.13).** `baseline.config_delta` may alter/zero a term **only** as the
differential reference. The entry's INDEX capability set (terms, `time_dependent_bc`,
`has_internal_boundaries`) is always computed from the **canonical** set, never the baseline — this
prevents smuggling a term-toggle into "baseline" to dodge a §2.3 fork. If the variant zeroes a term
the entry marks *present*, that control belongs on this entry only as a baseline; a standalone run of
it belongs on a **sibling** entry (see the dedup term-zeroing check, §2.4 step 4).

---

## Step 6. Prose body

- `## What this test actually tests` — the specific capability(ies). **NEVER** "compare with
  literature". Tie each sentence to a mode's `purpose`.
- `## Validation notes` — per-mode elaboration: expected convergence orders, known reference values
  **WITH units** (recorded verbatim, §11.10), tolerance rationale, differential-mode explanation.

---

## Done when

Every entry has ≥1 mode; each mode has a specific `purpose` (never "compare with literature"), a
registry procedure with filled slots, and a `score` ∈ 1..5 with justification; universal diagnostics
scored only when discriminating; differential modes carry `baseline` + `measured` and pass the check-9
guard; reference keys resolve per §5.3/check 7; `## Validation notes` records reference values with
units. `reindex.py` then sets `headline_score = max(modes)`.
