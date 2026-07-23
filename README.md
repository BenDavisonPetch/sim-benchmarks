# Numerical Test-Case Database

A git repo holding a curated database of numerical test cases for computational-physics method
research (finite-volume / MHD / multi-material, etc.), interacted with via the Claude Code CLI
through `/add-test`, `/find-test`, `/create-test`, and `/add-refs`.

The DB stores *descriptions* sufficient to run and validate a test in an external code; it does not
run the physics codes, and it is not a website, server, or database engine.

**`SPEC.md` is the contract.** Every design rule — entry identity and de-duplication, the `spec.md`
schema, the reference-verification (no-fabrication) model, validation scoring, the registry /
vocabulary-extension anti-drift engine, the index and validation scripts, and the commands/skills —
is defined there and is authoritative. Read it first.

## Layout

The full intended tree is in `SPEC.md` §10. This drop contains the finalized contract plus the
concrete seed artifacts that were designed against it:

```
SPEC.md                                             # the contract (authoritative)
README.md
registry/
  equations/magnetic-diffusion.md                   # solid-phase base eqn sets (§7.1)
  equations/perfect-conductor.md
  equations/rigid-body.md
  internal-boundary-kinds/electromagnetic-coupling.md
skills/
  add-test/triage.md                                # source triage sub-procedure (§9.1)
templates/
  pending_extraction.template.md                    # reference-defined problem params (§9.1 / §5)
tests/
  mercury-magnetosphere-coupled-interior/spec.md    # worked example entry (Jia 2015)
```

## Build status

Per `SPEC.md` §0, the implementation is a follow-on build. Still to be authored against the
contract: the scripts (`validate.py`, `reindex.py`, `verify_refs.py`, `new_test.py`), the remaining
`docs/` (schema reference, expression language, scoring rubric, procedures, conventions), the
command/skill `SKILL.md` files and their templates, the generated `INDEX.tsv`, and the seed
registry entries for the vocabulary the contract already names (`hydro`, `mhd`, the terms, EoS,
bc-types, coord-systems, analysis-treatments, procedures).

The example entry `tests/mercury-magnetosphere-coupled-interior/spec.md` references registry ids
(e.g. `bc-types/supersonic-inflow`, `procedures/feature-location`, `coord-systems/cartesian`,
`eos/gamma-law`, `terms/resistivity`) that must exist once the seed registry is populated; it will
pass `validate.py` only after that step. It is included as the worked reference for authoring.
