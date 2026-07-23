# scoring-rubric.md — validation-mode scoring

The 1–5 rubric applied **per `validation_mode`** (SPEC §6.3). Every mode carries a `score` and a
`score_justification`. The entry's `headline_score` is the max over its modes.

---

## Rubric (SPEC §6.3, verbatim)

| Score | Requires |
|------:|----------|
| **5** | Exact/analytic solution + quantitative convergence to the theoretical order. |
| **4** | No exact solution; community-accepted canonical solution; reliable automatable quantitative check (self-convergence, RH-jump, growth-rate, feature-location). |
| **3** | Quantitative comparison to reference result(s); partial feature coverage. |
| **2** | No automatable check, BUT solution well-characterised (specific named features) and/or widely reproduced across refs — qualitative match is meaningful and specific. |
| **1** | Single result, qualitative, no specific checkable features. |

---

## Rules

- **Headline rule.** `headline_score = max(validation_modes[].score)`, set by `reindex.py`
  (SPEC §8.2, §11.8). Never hand-authored to a different value; `validate.py` check 3 fails on
  mismatch.
- **Justification.** Every mode has a `score_justification` string stating why the row applies.
- **No forced proxy.** Use an automatable proxy **only** if it is reliable and cheap. Otherwise
  score by characterisation quality + reproduction breadth (rows 2/1). Do not fabricate an
  automatable check to inflate a score.
- **Symmetry caveat.** Do not use symmetry as a proxy where AMR/gridding breaks it. Where such a
  trap exists, note it in the body `## Qualitative behaviour` section and score honestly (row 2/1).

---

## Differential (baseline) modes — SPEC §6.3A

A mode may carry an optional `baseline` (a `config_delta` serving as the differential reference).
The `measured` quantity is then the **difference** between the canonical run and the baseline run
(e.g. magnetopause standoff with vs without an inductive core).

- Scoring reflects the **difference** measurement, not either run alone.
- A controlled quantitative A/B **tops at 3** absent an exact solution.
- The reason such a case is **one mode on one entry** (not two entries) is precisely that a single
  run without the comparison is not itself a strong check.

**Guard (enforced by `validate.py` check 9, SPEC §11.13):** a `baseline.config_delta` may alter or
zero a term **only** as the differential reference. The entry's INDEX capability set (terms,
`time_dependent_bc`, `has_internal_boundaries`) is always computed from the **canonical** set,
never the baseline — this prevents smuggling a term-toggle into "baseline" to dodge the §2.3
identity fork.

---

## Universal diagnostics — SPEC §6.4

`div-b` and `conservation-drift` appear as a **scored** `validation_mode` **only** when genuinely
discriminating for that problem — the entry must assert *why* the diagnostic is challenging here
versus generic. Otherwise they are provenance metrics, recorded **unscored**.
