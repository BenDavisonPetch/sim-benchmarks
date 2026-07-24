# subagent-brief template (SPEC §9.1 step 2e) — one brief PER subagent

The orchestrator fills one of these per subagent (from the enumeration worksheet §5–§6) and dispatches
it. The subagent authors its assigned test(s) into `spec.md` draft(s) via problem-authoring +
validation-authoring, de-dups against the read-only INDEX, and RETURNS the two contract lists below.
The subagent NEVER runs reindex.py (the orchestrator serializes that — a parallel reindex races).

---

## Your assignment
- test(s) to author: `<names from the enumeration>`
- triage branch: NORMAL / APPLICATION (follow triage.md for APPLICATION)
- authoring offline? yes/no

## Global-defaults block (VERBATIM — shared across the paper; treat as authoritative for shared params)
```
<the orchestrator's §3 global-defaults block, pasted verbatim>
```

## Your per-test verbatim slice (NOT the whole source)
```
<the exact source text for this subagent's test(s), verbatim>
```

## Read-only full source plaintext (grep-on-demand)
- path: `<absolute path to the normalized full plaintext>`
- Use it ONLY to grep a referenced-but-unsupplied quantity you detect in your slice — NEVER to author
  a different test, and NEVER to hallucinate a value. If a needed quantity is nowhere in the slice,
  the global block, or a grep hit, it is `unresolved` (see return contract) or a `needs-source`
  reference-defined parameter (§5.2) — never typed from memory.

## What to do
1. problem-authoring — fill the problem half, method-free (§1.6). Reference-defined params →
   `needs-source` + `source_ref` + a pending_extraction.md row.
2. dedup — against the read-only INDEX only. existing-entry ⇒ report it (record a reference_result),
   don't scaffold a duplicate.
3. validation-authoring — >=1 scored mode from the quantitative anchors (§11.6).
4. Emit the `spec.md` draft(s). Do NOT run reindex.py / validate.py — the orchestrator does, once.

## RETURN CONTRACT (mandatory — the orchestrator cross-checks these, §9.1 step 2e)
- `inherited_from_global[]` — every value you took from the global-defaults block (param name + value).
  Lets the orchestrator confirm you did not silently invent a shared value.
- `unresolved_references[]` — every quantity your slice referenced that you could NOT find verbatim in
  the slice, the global block, or a grep hit. Flag, don't fill.
- vocab proposals (ids/functions not in the registry) — list them; the orchestrator BATCHES all
  subagents' proposals into ONE hard-stop (§7.2). Do not hard-stop the user yourself.
- schema gaps (no field/shape for the information — not a missing id) — list them; the orchestrator
  collects into ONE ledger (§12). Try the coupled-physics framing first (triage.md A2.5).
