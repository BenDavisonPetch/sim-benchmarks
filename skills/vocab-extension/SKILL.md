---
name: vocab-extension
description: >
  The §7.2 hard-stop-and-propose flow for growing controlled vocabulary. When an authoring skill needs
  a registry id (equation/term/eos/bc-type/coord-system/internal-boundary/analysis-treatment/
  geometry-stress/procedure) or a §4 expression function that does not yet exist, STOP, draft the
  registry file(s) from templates/procedure.template.md or templates/registry-term.template.md, and
  present a batched one-word-approval proposal. Never auto-create silently. Distinguish vocab gaps
  (self-healing) from schema gaps (escalate, §12).
---

# vocab-extension — hard-stop-and-propose (SPEC §7.2, §6.1, §12)

The **only** sanctioned way to grow the system's expressiveness, and it is deliberate, logged, and
reviewed. Extending vocabulary is the central anti-drift mechanism (§1.3). This skill is pulled in by
`problem-authoring`, `validation-authoring`, `/add-test`, and `/create-test` whenever they reach for a
term that is not already in the registry.

**Prime rule:** never reference an id until it exists **and** the user has approved it. No silent
auto-creation (§11.3).

---

## Step 1. Is it a VOCABULARY gap or a SCHEMA gap? (the split that matters)

Before proposing anything, classify — they route completely differently (triage.md A4, §12):

- **Vocabulary gap** — a missing *enum id* or a missing §4 *function*: no `registry/<kind>/<id>.md`
  for the physical concept, or a function not on the `docs/ic-expression-language.md` allow-list. The
  system is **designed to self-heal** here → continue this skill (hard-stop-and-propose).
- **Schema gap** — a missing *field or structural shape*: the spec has **nowhere to put** this kind of
  information at all. The extension machinery does **not** cover this. Do **not** invent a field, do
  **not** overload an existing one. Record it in the gap ledger and **escalate to the user for
  re-grilling** (SPEC preamble; §12). Stop trying to make the entry validate.

> Rule of thumb: **"there is no id for X" = vocab. "There is no place for X" = schema.**
> A borderline case worth trying first: an embedded/frozen/constrained interior condition is usually
> **coupled physics**, not a schema gap — model it as a material with its own base equation set + IC +
> interface coupling (triage.md A2.5) before declaring either kind of gap.

Only vocabulary gaps proceed past this step.

---

## Step 2. Try harder to avoid the extension (don't bloat the vocabulary)

A registry id is a permanent, reviewed commitment. Before drafting one, confirm none of these already
covers the need:

- an **existing id** under a different name (check the registry dir + the `/find-test` alias table for
  slang, §7.3);
- **term composition** — the concept is `base` + existing `terms`, not a new base (Navier–Stokes is
  `hydro`+`viscosity`, not a new equation id);
- **an expression** — the concept is a `material_fields` / IC expression over existing variables, not
  a new function;
- **solid-phase interchangeability** — the physics collapses onto an existing base under a declared
  predicate (§7.1).

If one of these covers it, use it — no proposal. Otherwise continue.

---

## Step 3. Draft the registry file(s) — copy-and-fill, physical only

Draft, don't commit-and-reference yet. Pick the scaffold by kind:

- a new **procedure** → copy `templates/procedure.template.md` → `registry/procedures/<id>.md`;
  define its formula **once** in `docs/procedures.md` and cite it (never re-derive in the file).
- any other **vocabulary id** → copy `templates/registry-term.template.md` →
  `registry/<kind>/<id>.md`; keep only the kind-specific frontmatter block (mirror a sibling file in
  the same dir).
- a new **§4 function** → this is a logged change to `docs/ic-expression-language.md` (add to the
  allow-list, §2) **and** `scripts/speclib.py`/`validate.py` (register arity); note it in the proposal
  as a doc+code change, not a registry file.

Hard constraints while drafting:

- `id` == filename, kebab-case, **physical descriptor only** — never a method name (no `ghost-fluid`,
  `cut-cell`, grid, resolution). `internal-boundary-kinds` and `bc-types` are PHYSICAL conditions.
- Equation ids declare `requires_eos`; solid-phase ids declare `interchangeable_with` +
  `interchangeable_when`.
- Cite the SPEC section the id encodes; state identity implications (does it fork? §2.1/§2.3).

---

## Step 4. Hard-stop with a BATCHED proposal (never interrupt N times)

Collect **all** vocabulary proposals discovered in this authoring pass into **one** hard-stop message
(§9.1: batch all vocab proposals into a single hard-stop; batch all schema gaps into one ledger).
Present via `templates/proposal.template.md`: for each proposed id, the drafted file, the one-line
justification, and the identity/fork implication. Ask for **one-word approval** per proposal (or a
single "approve all").

Do **not** proceed, and do **not** write any `spec.md` field that references a proposed id, until the
user approves.

---

## Step 5. On approval — commit the id, then reference it

Only after approval:

1. Write the drafted registry file(s) (and any `docs/procedures.md` / allow-list change) to the repo.
2. Now the authoring skill may reference the new id in the `spec.md`.
3. Run `scripts/validate.py` (check 2 confirms every used id now exists) + `scripts/reindex.py`.
4. Log the extension in `docs/working/SPEC_DEVIATIONS.md` **only** if it also touches code/docs beyond
   a pure new registry file (a §4-function addition is a logged doc+code change; a plain new registry
   id that the spec already anticipates is normal vocabulary growth, not a deviation).

On a schema gap (from step 1): do none of the above — the entry stays un-authored for that field; hand
the gap ledger to the user for re-grilling.

---

## Done when

Every id an entry references either already existed or was drafted, batched into one hard-stop,
approved, committed, and validated (check 2 clean); no id was referenced before approval; schema gaps
were escalated (not papered over with an invented field); any §4-function addition is logged in docs +
code + SPEC_DEVIATIONS.
