# Vocabulary extension proposal (SPEC §7.2 hard-stop) — ONE batched message to the user

Emitted by the vocab-extension skill when an authoring pass needs id(s) or §4 function(s) not yet in
the registry. Present ALL proposals from the pass in a SINGLE message (never interrupt N times, §9.1).
Nothing below is referenced in a spec.md until the user approves it (§11.3).

Copy this block, fill one section per proposed item, delete unused sections, send. Ask for one-word
approval per item (or "approve all").

---

## Why I stopped
Authoring `<slug>` needs the following vocabulary that does not exist in the registry / §4 allow-list.
Per §7.2 I do not create vocabulary silently — approve each before I reference it.

(Confirm first: none of these is an existing id under another name, a term composition, an expression
over existing variables, or a solid-phase interchangeability — see vocab-extension step 2.)

---

## Proposal 1 — <kind>/<proposed-id>
- **Kind:** equation | term | eos | bc-type | coord-system | internal-boundary | analysis-treatment |
  geometry-stress | procedure | §4-function
- **Physical meaning (one line):** <what it is — PHYSICAL, never a method>
- **Why existing vocabulary can't express it:** <the specific gap; why step-2 alternatives fail>
- **Identity implication (§2.1/§2.3):** <does it fork identity? searchable tag only? affects
  physics_signature / capability_flags?>
- **Drafted file:** `registry/<kind>/<proposed-id>.md`  (from registry-term.template.md)
  — or `registry/procedures/<id>.md` (from procedure.template.md) + a formula in docs/procedures.md
  — or, for a §4 function: a logged change to docs/ic-expression-language.md allow-list +
    scripts/speclib.py arity (NOT a registry file).
  ```
  <paste the drafted file contents / the exact doc+code diff here so the user reviews the real thing>
  ```
- **Approve?** (one word: yes / no / rename-to <id>)

## Proposal 2 — <kind>/<proposed-id>
<same fields>

---

## Schema gaps (SEPARATE — do NOT self-heal; §12)
If this pass also hit a SCHEMA gap (no field/shape to hold the information at all — not merely a
missing id), list it here for re-grilling. Do NOT invent a field or overload an existing one.
- **Gap:** <what information has nowhere to live>
- **Why it's schema not vocab:** "there is no PLACE for X" (vocab would be "there is no id for X")
- **Tried coupled-physics framing?** <yes/no + result — triage.md A2.5>
- **Action:** escalate to user for spec re-grilling; entry stays un-authored for this field.

---

## On approval (vocab-extension step 5)
1. Write the approved registry file(s) / doc+code change to the repo.
2. Reference the new id(s) in `spec.md`.
3. Run `scripts/validate.py` (check 2) + `scripts/reindex.py`.
4. A §4-function addition is a logged docs + `validate.py` change (SPEC §4), one commit; a plain new
   registry id needs nothing further.
