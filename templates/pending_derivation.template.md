# pending_derivation — <slug>

Fixed-format request emitted by `/create-test` (SPEC §9.3) when a synthesized entry might admit
a stronger analytic / exact solution than the authoring model could derive. Until the derivation
lands, the entry carries its **provisional (low) score**; a resolved derivation can upgrade a
validation mode (e.g. to `exact-solution-compare`, raising the score per `scoring-rubric.md`).

Delete this file once the derivation is folded into `spec.md` and the mode/score updated.

---

## Source
- entry: `<slug>`
- provenance: synthesized
- current provisional score: `<n>` (mode `<mode-id>`)

## What to attempt
<The exact/analytic solution or closed-form reference sought: the governing reduction, the regime
 in which it is exact, and the variables it covers. State assumptions precisely.>

## Why it is provisional now
<What blocks an exact check today: no known closed form, derivation beyond the authoring model,
 or a reference that must be located. Be specific.>

## If derived
1. Add the derivation / exact solution to the relevant `validation_mode` (procedure, inputs,
   tolerance) in `spec.md`; adjust `score` + `score_justification` per `scoring-rubric.md`.
2. Run `scripts/reindex.py` (recomputes headline_score) + `scripts/validate.py`.
3. Delete this file.
