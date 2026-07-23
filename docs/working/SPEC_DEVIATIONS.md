# SPEC_DEVIATIONS — implementation vs SPEC.md

Running catalogue of every place the implementation does not STRICTLY follow `SPEC.md`. Mandatory:
any agent writing code, scripts, registry entries, skills, or docs that deviates from, adds to, or
fills a gap in the spec MUST append an entry in the same commit/stage. No silent deviations.
Reviewers check this file against the diff.

`SPEC.md` is the contract (`SPEC.md` preamble: "deviations require re-grilling"). This file is how a
deviation is surfaced instead of silently absorbed. A stage is not complete while it has unresolved
deviations (see phase-gate rule below).

## What counts (log it)

- **DEV** — deviation: the implementation does something the spec forbids or prescribes differently
  (e.g. a `validate.py` check looser than SPEC §8.3, a schema field renamed, a body-section order
  changed).
- **ELAB** — elaboration: the spec is silent or ambiguous and the implementation had to choose
  (a tolerance, a tie-break, an INDEX column ordering detail, an expression-parser edge case, a
  template wording).
- **INTERIM** — temporary non-compliance scheduled to be fixed in a later stage. Must name the
  removing stage.

Not logged: pure refactors, naming, formatting, or comment changes with identical behaviour; work
that already matches the spec exactly.

## Entry format

One entry per item, newest last:

```
### <ID> [DEV|ELAB|INTERIM] <one-line title>
- Stage/date: Stage <n>, YYYY-MM-DD
- Spec: <section, e.g. §8.3 check 6 / §4>
- Code: <file:lines>
- What: <what the implementation does vs what the spec says / leaves open>
- Why: <forcing reason — spec gap, dependency on a later stage, tooling limit, test failure>
- Impact: <which SPEC §11 invariant(s) affected? state "none" explicitly if none>
- Status: OPEN | SPEC-UPDATE-NEEDED | ACCEPTED (user signed off) | RESOLVED-Stage<n>
```

IDs are sequential: `D-001, D-002, …`.

- **INTERIM** entries start `Status: OPEN` with a named target stage; flip to `RESOLVED-Stage<n>`
  when removed.
- **SPEC-UPDATE-NEEDED** = the resolution is to improve `SPEC.md`, not the code; the user must amend
  the spec, after which the entry flips to `RESOLVED-Stage<n>` (or `ACCEPTED`).
- **ACCEPTED** only after user sign-off. Agents never self-accept a DEV.

The `Impact` line names invariants by their SPEC §11 number where possible, e.g. "§11.1 (no method
in problem block)", "§11.2 (every enum a registry id)", "§11.4 (INDEX generated / not stale)",
"§11.5 (no fabricated refs)", "§11.8 (headline = max of modes)", "§11.9 (one-file, fixed section
order)". State "none" explicitly when nothing is affected.

## Phase-gate rule

Writing to this list is mandatory, and **implementation cannot proceed to the next stage
(IMPLEMENTATION_PLAN.md Stages 1–6) until every deviation logged in the current stage is resolved**,
by one of exactly two routes:

1. **Make the implementation compliant** — change the code/artifact to strictly follow the spec;
   flip the entry to `RESOLVED-Stage<n>`.
2. **Improve the spec** — if the deviation reveals a genuine spec gap or error, re-grill the user
   and amend `SPEC.md`; flip the entry to `RESOLVED-Stage<n>` (or `ACCEPTED` on sign-off).

Concretely, a stage is **not done** while it has:

- any **OPEN DEV** entry;
- any **OPEN INTERIM** entry whose named target stage is the current one or earlier;
- any **SPEC-UPDATE-NEEDED** entry not yet folded into `SPEC.md` or `ACCEPTED`.

Allowed to cross a stage boundary: an **INTERIM** entry whose target stage is strictly later (it is a
pre-registered, tracked debt), and an **ELAB** entry whose `Impact` is `none`. Everything else blocks
the gate.

Final build exit (after Stage 6): zero OPEN entries; every SPEC-UPDATE-NEEDED folded into the spec or
ACCEPTED; every INTERIM flipped to RESOLVED.

---

## Entries

(none yet — build not started)
