# /add-test — source triage (prepended to the main procedure)

Runs BEFORE §9.1 step 1. Decides which extraction path a source takes. Mechanical;
Sonnet-executable; no cleverness.

---

## T0. Classify the source

Score the source against both signal sets. Pick the branch with more hits; on a tie, take
the **application** branch (it is strictly more cautious).

**Benchmark / method source → NORMAL path (§9.1):**
- States initial conditions as explicit closed-form expressions in this document.
- Names a canonical test problem (Sod, Orszag–Tang, Brio–Wu, …).
- Problem statement is resolution-independent and self-contained.
- Provides or cites an exact / analytic / community-canonical reference solution.

**Application / modeling source → APPLICATION branch (below):**
- Problem is a driven, real-body or real-experiment scenario.
- Validation is comparison to *observations* or to *other models*, not to an exact solution.
- Key problem parameters are cited to other papers ("the dipole of [ref]", "conductivity
  from [ref]").
- Numbers are scattered through prose/figures rather than a setup block.

**Decision rule (overrides the score):** if the problem **cannot be fully specified from the
quantities stated in *this* document alone**, it is an application source. Needing to open a
cited paper to fill a required field is the defining symptom.

---

## Application branch

### A1. Harvest, verbatim, with provenance
Extract every quantitative statement into a candidate parameter table. For each row record:
`name | value-as-stated | units-as-stated | location (section/fig) | origin`, where
`origin ∈ {stated-here, stated-by-reference:<citekey>}`. Copy values verbatim — never
normalize, never convert (SPEC §12), never paraphrase.

### A2. Problem / method split (SPEC §1.6, hard)
Route each harvested item:
- **Physical statement** (geometry, ICs, material properties, boundary *physics*, drive,
  times) → problem block.
- **Method choice** (code, grid type, resolution, AMR, solver, scheme, CFL, div-B cleaning) →
  `reference_result` on **this** paper. Never in the problem block.
A spherical *grid* is a method; a spherical *coordinate frame the physics is posed in* is
problem. When in doubt, it is method.

### A3. Reference-defined parameters — never fill from memory
For every row with `origin = stated-by-reference`: write the parameter with a `source_ref`
pointer and `status: needs-source`. **Do not** type the value from training knowledge even if
you believe you know it. This mirrors the §5 no-fabrication rule: a value you did not read in a
supplied source is a claim, not a fact.

### A2.5. Try the coupled-material representation BEFORE crying schema-gap
Most "the schema can't hold this" reactions are premature. Before flagging any schema gap, try to
represent embedded / frozen / constrained / conducting interior conditions as **coupled physics**:

- Model any interior or embedded region as a **material with its own base equation set** + its own
  IC + an **interface coupling** to the surrounding material. A region where the fluid is frozen
  (`v≡0`) and only the field evolves is base `magnetic-diffusion`, not a bespoke boundary
  condition. A prescribed field there is that material's **IC**, not a magic BC.
- **Minimal-material canonicalization (SPEC §11.14):** merge regions that share an equation set
  into ONE material with a **spatial coefficient field** (e.g. core+mantle → one body with
  `eta(r)`). Introduce a material boundary only where the base equation set, EoS, or a genuine
  physical interface differs. Do not mint a material per named region.
- Only escalate a **schema gap** if the condition is **not derivable from an equation evolved in
  the domain** — an externally imposed condition with no backing evolved equation. That, and only
  that, is out of scope (SPEC §12) and needs re-grilling.

This step alone resolved the Mercury pressure-test's apparent GAP-1/3/8 (interior = a
`magnetic-diffusion` material with `eta(r)` + electromagnetic coupling; the dipole is its IC).

### A2.6. Set capability flags (drives identity + INDEX)
Compute, from the **canonical** set only:
- `time_dependent_bc` = any `domain_bc[*].state` expression references `t`.
- `has_internal_boundaries` = ≥1 internal material interface / internal boundary present.
- `geometry_stress` = a registry id only if the geometry is *purpose-built* to stress an
  algorithm; otherwise `none`.
These are **binary** capability forks (SPEC §2.3): never fork on the specific `f(t)` or the
specific internal geometry — fork only on presence. A `baseline.config_delta` never changes these
flags (they come from the canonical set).

### A4. Gap classification — the split that matters
When a required physical statement STILL will not fit after A2.5, decide **which kind of gap**:

- **Vocabulary gap** — a missing *enum id* (equation, term, eos, bc-type, coord-system,
  internal-boundary-kind, analysis-treatment, procedure). → §7.2 hard-stop-and-propose: draft
  the registry file, one-word approval. The system is designed to self-heal here.
- **Schema gap** — a missing *field or structural shape* (the spec has nowhere to put this kind
  of information at all). → the extension machinery does **not** cover this. Do **not** invent a
  field, do **not** overload an existing one. Record the gap in the gap ledger (A7) and escalate
  to the user for re-grilling (SPEC preamble: "deviations require re-grilling"). Stop trying to
  make the entry validate.

Rule of thumb: "there is no id for X" = vocab. "There is no place for X" = schema.

### A5. Validation from stated anchors only
Build `validation_modes[]` only from quantitative anchors actually present. Score per the
rubric (§6.3) — an observation/model comparison tops out at 3; no exact solution ⇒ never 4/5.
Do not let prose richness inflate a score. If the paper's key validation is a **controlled
A/B against its own variant run** (e.g. with vs without an effect), note that the control run
lives on a *sibling entry* if the variant zeroes a term marked present (§2.3): such a
comparison is cross-entry (see gap ledger — flag if the schema has no differential mode).

### A6. Emit deferral artifacts
- `pending_extraction.md` (template) — every `needs-source` parameter, and exactly which paper
  to pull each from. This is the mechanical to-do handed to a refs-capable pass.
- `pending_verification.md` — for any unverified references (§5.2B), as normal.

### A7. Batch, don't drip
Collect **all** vocabulary proposals into a single hard-stop-and-propose. Collect **all**
schema gaps into one ledger presented to the user together. Never interrupt N times.

### A8. Prefer two-phase
Application sources are heavy and reference-entangled. Default to: `/add-test` produces the
skeleton + harvested in-text params + `pending_extraction.md`; a later `/add-refs` pass pulls
the reference-defined parameters and the result comparisons. Do not attempt to finish a
reference-entangled application entry in one pass.
