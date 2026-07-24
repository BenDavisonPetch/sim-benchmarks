# enumeration worksheet (SPEC §9.1 step 2) — orchestrator fill-aid, not a scaffold

The orchestrator's pass over a multi-test source: enumerate tests, capture the user pick, build the
VERBATIM global-defaults block, resolve intra-paper de-dup, and group the picked set into subagents.
Fill it, act on it, then discard. One `spec.md` per authored test is still built from
`templates/spec.template.md` (§11.9) — this worksheet authors nothing.

---

## 0. Source
- path/URL: `<...>` (NOT committed — normalized to §3 form, §9.1 step 1)
- triage branch (from triage.md): NORMAL / APPLICATION
- authoring offline? yes/no

## 1. Enumerate every test the source defines
| # | test name (as in source) | one-line identity sketch (physics_signature + what forks it) | location (§/fig) |
|---|--------------------------|--------------------------------------------------------------|------------------|
| 1 |                          |                                                              |                  |
| 2 |                          |                                                              |                  |

## 2. User pick (§9.1 step 2a)
- [ ] Presented the enumeration and ASKED the user which to add.
- [ ] Picked set: [____].  Add-all ONLY on an explicit "all" — never assumed.

## 3. Global-defaults block — VERBATIM, never summarized (§9.1 step 2b)
Copy, word-for-word from the source (paraphrase = data loss):
- methods / setup text shared across tests (γ, unit system, common domain, common BCs, …);
- EVERY sentence with a quantifier: `all / each / every / throughout / unless otherwise / in all runs`.

```
<paste verbatim here — this block goes to EVERY subagent so a shared value is never dropped>
```

## 4. Intra-paper de-dup at enumeration (orchestrator only, §9.1 step 2d)
Parallel subagents can't see each other's writes. Collapse same-entry slices BEFORE dispatch.
- [ ] Tests in THIS paper that are the same entry (only params differ) → merge to one slice: [____]
- [ ] (Subagents still de-dup against the existing read-only INDEX in Step 3.)

## 5. Group picked tests into subagents (§9.1 step 2c)
Group by logical grouping (same physics_signature / siblings together). ~3–5 per subagent, capped by
count OR extracted-token budget, whichever first. Single-test subagent only for a heavy test.

| subagent | tests (from §1) | grouping rationale (shared physics_signature / siblings) |
|----------|-----------------|----------------------------------------------------------|
| A        |                 |                                                          |
| B        |                 |                                                          |

## 6. Dispatch (per subagent → templates/subagent-brief.template.md)
Each brief carries: the §3 global-defaults block + the subagent's per-test verbatim slice + read-only
full plaintext (grep-on-demand). Each subagent MUST return `inherited_from_global[]` +
`unresolved_references[]`.

## 7. Cross-check + serialized close (§9.1 step 2e/2f)
- [ ] For each returned draft: every value appears verbatim in the slice or the global block, else
      FLAG it (do not accept a value not seen verbatim).
- [ ] Batch ALL vocab proposals into ONE hard-stop (§7.2); ALL schema gaps into ONE ledger (§12).
- [ ] Serialize writes: drafts in parallel, then ONE `reindex.py` + ONE `validate.py` (`--offline` if
      offline). Never a parallel reindex (it races).
