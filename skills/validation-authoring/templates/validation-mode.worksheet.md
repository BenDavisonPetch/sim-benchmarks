# validation-mode worksheet (SPEC §5.3/§6) — one pass PER mode; a FILL-AID, not a scaffold

Run this worksheet once per anchor from step 1. Transcribe answers into a `validation_modes[]` element
inside the single `spec.md` (from `templates/spec.template.md`; §11.9). Discard the worksheet after.
Authorities: docs/scoring-rubric.md, docs/procedures.md, registry/procedures/*.

Entry MUST end with >=1 mode, else it is rejected (§11.6).

---

## Per-mode fill

- [ ] anchor (what quantitative/qualitative check does this problem admit?) → ____
- [ ] `id` (R) — unique within the entry, kebab-case → ____
- [ ] `purpose` (R) — SPECIFIC capability. NEVER "compare with literature" (§11.6). → "____"
- [ ] `procedure` (R) — registry/procedures id. None fits ⇒ vocab-extension hard-stop (§6.1/§7.2),
      never inline a bespoke procedure. → ____
- [ ] `inputs` (R) — the procedure's slots:
      - `at_time` (<= time.t_final) → ____
      - `variables` → [____]
      - procedure-specific slots (cut_lines / features / r / resolution seq / ...) → ____
      - `tolerance` → "____"
      - `reference` (where cited) → { kind: reference | reference-result, key: ____ }
        (key must be a VERIFIED references[] key online; offline may resolve to
         references_unverified[] — §5.3 / check 7 / D-016. Never invent a key.)
- [ ] `has_exact_solution` (R) → true/false
- [ ] `score` (R, 1..5) → ____   (see rubric below)
- [ ] `score_justification` (R) → "____"

### Differential (baseline A/B) mode? (§6.3A) — only if the measurand is a DIFFERENCE

- [ ] `baseline.description` → "____"
- [ ] `baseline.config_delta` → { "<dotted.path>": "<value>" }
- [ ] `measured` → "the difference in ____ , variant vs baseline"
- [ ] GUARD (check 9 / §11.13): config_delta must NOT change the INDEX capability set (terms,
      time_dependent_bc, has_internal_boundaries) — those come from the CANONICAL set. If the variant
      zeroes a term marked present, a STANDALONE run of it is a SIBLING entry, not this one (§2.4 step 4).
- [ ] A/B tops at score 3 absent an exact solution.

### Universal diagnostic (div-b / conservation-drift)? (§6.4)

- [ ] Genuinely discriminating for THIS problem? If yes → scored mode + state WHY it is challenging
      here vs generic. If no → provenance metric, UNSCORED (omit `score`).

---

## Scoring rubric (docs/scoring-rubric.md) — pick the highest row the mode HONESTLY meets

- 5 — exact/analytic solution + quantitative convergence to theoretical order.
- 4 — no exact soln; community-canonical soln + reliable automatable quantitative check.
- 3 — quantitative comparison to reference result(s); partial feature coverage. (obs/model compare
      caps here — no exact soln ⇒ never 4/5.)
- 2 — no automatable check, but well-characterised (specific named features) and/or widely reproduced.
- 1 — single qualitative result, no specific checkable features.

Rules: no proxy is forced; don't use symmetry as a proxy where AMR/gridding breaks it; don't let prose
richness inflate a score; headline = max(modes), set by reindex.py (never hand-edited).

---

## Prose (validation-owned sections)

- [ ] `## What this test actually tests` — specific capability(ies); NEVER "compare with literature".
- [ ] `## Validation notes` — per-mode elaboration; expected convergence orders; known reference
      values WITH units (verbatim, §11.10); differential-mode explanation.

## Pre-transcribe checklist

- [ ] >=1 mode total (§11.6).
- [ ] Every purpose specific, no "compare with literature".
- [ ] Every score has a justification; score honest to the rubric.
- [ ] Universal diagnostics scored only when discriminating (§6.4).
- [ ] Baseline modes pass the check-9 guard.
- [ ] Reference keys valid per §5.3 / check 7.
