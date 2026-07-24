---
name: dedup
description: >
  Mechanical, value-blind de-duplication of a candidate test against the existing database (SPEC
  §2.4). Pulled in by /add-test and /create-test BEFORE any new entry is scaffolded. Returns exactly
  one decision: existing-entry (record a reference_result / widen a parameter range), new-sibling
  (new entry + related_to link), or new-entry. No cleverness; runnable by a Sonnet-class model.
---

# dedup — structural, value-blind de-duplication (SPEC §2.4)

The single most important anti-mess rule. Two entries are "the same test" iff they share the whole
identity signature (§2.1); **parameter values never enter identity** (§2.2), except the binary
capability-presence flags (§2.3). This skill turns that into a fixed decision procedure. Subjectivity
is confined to step 3's structural compare over a tiny candidate set.

**Inputs.** The candidate test already normalized into the §3 problem form (physics_signature,
`analysis_treatments`, `capability_flags`, and the IC/geometry/BC-state expressions) — i.e. run
`problem-authoring` first, or at least have those fields drafted. Read-only `INDEX.tsv` must exist
(if absent, run `scripts/reindex.py` first).

**Output.** One of three decisions (step 4) + the concrete follow-up action. Never a partial answer.

---

## Step 0. Compute the candidate's three identity keys

From the drafted problem form, write down — for the **canonical** set only (never a
`baseline.config_delta`, §2.3 / §11.13):

- **physics_signature** — for each material: `base` id, the **set of terms present** (a term is
  present iff its coefficient is nonzero *anywhere* in the domain — a coefficient field that is zero
  in part of the domain still counts, §2.3), and `eos` type id; plus the coupling / interface
  structure between materials. Serialized as `INDEX.tsv` does it (D-009):
  `base(term1|term2)[/eostype]` per material, terms sorted, materials sorted, joined by `+`, with
  `@coupling` appended when `coupling != none`. This is the **raw** signature used to grep the index.
  - **Interchangeability is NOT baked into this string** (D-009: the mechanical index never collapses
    interchangeable solid-phase bases). If the candidate has a solid-phase base with a declared
    `interchangeable_with` partner whose `interchangeable_when` predicate **holds** (e.g.
    `perfect-conductor` ≡ `rigid-body` when the body carries no coupling field, §7.1), note the
    partner base as an **alias** — step 1a greps the raw signature *and* the aliased variants so an
    interchangeable duplicate is not missed. When the predicate does not hold, the bases fork (no
    alias).
- **analysis_treatments** — the registry-backed set (`none`, `oblique-to-grid`, `axis-singularity`,
  `multi-material-interface`, …).
- **capability_flags** — the two binary flags: `time_dependent_bc` (any `domain_bc[*].state`
  references `t`) and `has_internal_boundaries` (≥1 internal material interface / internal boundary).

> Members of `analysis_treatments` that merely *name kinds* of internal boundary are searchable
> descriptors, **not** forks (§2.1 item 2); the fork is the binary `has_internal_boundaries` flag.

---

## Step 1. Query INDEX — two passes (cheap; each narrows to ~0–3)

Grep `INDEX.tsv` twice. The **duplicate pass** finds true duplicates; the **sibling pass** finds
capability siblings for a `related_to` link. (SPEC §2.4 step 1 filters on all three keys; §2.4 step 3
and §2.5 also require identifying siblings that differ in exactly one identity component — the two
passes serve those two purposes.)

**1a — duplicate pass** (strict): rows matching **all three** keys from step 0:

```
same physics_signature (raw OR an aliased interchangeable variant)  AND
same analysis_treatments  AND  same capability_flags
```

Columns to match: `physics_signature`, `analysis_treatments`, `time_dependent_bc`,
`has_internal_boundaries` (the last two are the `capability_flags`). Grep both the raw signature and
any interchangeability alias from step 0 (the index does not collapse them, D-009). Set-valued cells
(`analysis_treatments`) are pipe-joined and order-insensitive — compare as sets. These slugs go to
step 2 for the structural compare.

**1b — sibling pass** (relaxed): rows with the **same physics_signature** but differing in exactly one
of `analysis_treatments` / `time_dependent_bc` / `has_internal_boundaries`. These are **not** duplicate
candidates (a differing capability flag or treatment is a fork, §2.3) — they are the siblings a
NEW-SIBLING decision links via `related_to`. Do not send them to the structural compare.

- **Both passes empty** → jump to **step 4, decision NEW-ENTRY** (nothing close).
- **1a non-empty** → carry those slugs to step 2 (may still resolve to existing-entry or new).
- **1a empty but 1b non-empty** → decision **NEW-SIBLING** (step 4): the physics matches but a
  capability/treatment differs; new entry + `related_to` to the 1b slugs. (This is the SPEC §2.5
  steady-inflow-vs-step-inflow / inviscid-vs-viscous / 1D-vs-oblique case.)

---

## Step 2. Open each candidate `spec.md`

For each candidate slug, open `tests/<slug>/spec.md`. You will compare, in step 3:

- the IC / geometry / **BC-state** structural form, **modulo numeric constants**;
- the canonical (aliased) name.

Read only these fields: `geometry.regions`, `initial_conditions` (`aux`, `equilibrium`,
`perturbation`, `potentials`), `domain_bc[*].state`, `internal_boundaries`, and `name`.

---

## Step 3. Structural compare, ignoring numeric values

Compare candidate ⟷ each existing entry on **form only**. Replace every numeric literal with a
placeholder before comparing (`0.75` ≈ `0.5` ≈ any number; but `0` is structural where it means a
term/field is *absent* — see the term-zeroing check, step 5). Compare:

1. **Expression structure** — the parse shape of each IC / BC-state / coefficient expression with
   numeric constants blanked. `rho: "gamma*gamma"` matches `rho: "a*a"`-shaped; `vx: "-sin(2*pi*y)"`
   matches any `c1*sin(c2*y)`. Function calls, operator tree, and variable references must match;
   the constants need not.
2. **Region topology** — same set of region shapes and their spatial relationship (a box split into
   two halves ≠ a shell-in-box), modulo the numeric extents/coordinates.
3. **Potential-defined fields** — same potentials + same `derives` rule (`B = curl(A)`), if any.
4. **Equilibrium + perturbation decomposition** — same split shape and `combine_rule`; a
   perturbation-on-equilibrium test ≠ a plain-IC test even if the equilibrium expressions coincide.

Two forms **match** iff all four coincide under numeric-blanking. Numeric values do not enter this
comparison (§2.1 item 3).

---

## Step 4. Decision (exactly one)

| Situation | Decision | Action |
|---|---|---|
| **Structural match** (only numeric parameter values differ) | **NOT a new test** | Record a `reference_result` (with `params_used`) on the matched entry, and/or widen a `parameters[]` range note. **Point the user to the existing slug.** Do **not** create an entry. |
| Same physics_signature **but** different `analysis_treatments` **or** different `capability_flags` (the step-1b sibling pass hit; 1a empty) | **NEW SIBLING** | Create a new entry; add `related_to` links to the sibling(s) (manual this build — §12). |
| No structural match (both step-1 passes empty, or 1a candidates all differ structurally) | **NEW ENTRY** | Create a new entry; no `related_to` unless a sibling is later identified. |

> `related_to` for capability siblings is authored manually this build; automatic reciprocal linking
> is deferred (SPEC §12 TODO). When you take the NEW-SIBLING branch, write the link yourself.

---

## Step 5. Term-zeroing check (guards against a mis-filed reference_result)

Before finalizing an **existing-entry** decision that would attach a `reference_result`: if that
candidate reference sets the coefficient of a term the entry marks **present** to **zero**, the
reference belongs to a **different (sibling) entry**, not this one (§2.4 step 4). Re-route it: it is
NEW-SIBLING material, linked via `related_to`.

**Exception.** A `validation_mode.baseline` that zeroes a term *purely as a differential reference*
(§6.3A) stays on the same entry — that is the A/B control run, not a separate physics. The tell: the
zeroing lives in `baseline.config_delta`, and the entry's INDEX capability set is still computed from
the canonical (un-zeroed) set (§11.13). If in doubt, `validate.py` check 9 enforces the guard.

---

## Step 6. Minimal-material canonicalization (convention, not a §11 invariant)

When the candidate admits both a multi-material and a single-body-with-coefficient-field
representation, choose the **minimum** material count before comparing signatures:

- regions sharing an equation set → **one** material with a spatial coefficient field
  (e.g. core+mantle → one body with `eta(r)`);
- a material boundary exists **only** where the base equation set, EoS, or a genuine physical
  interface differs;
- interchangeable solid-phase bases (§7.1) collapse to one signature element under their declared
  predicate.

This is a de-dup convention (§2.4 step 5), **not** mechanically enforced. An optional lint may warn
when an entry has ≥2 materials sharing a `base` (merge candidate; expect false positives). Canonicalize
*before* step 0 so signatures compare on the same footing.

---

## Worked cases (must all hold — SPEC §2.5; use to self-check)

- 1D Sod vs 2D Sod rotated 30° in an embedded rectangle → **NEW SIBLING** (`analysis_treatments`
  `none` vs `oblique-to-grid`; `has_internal_boundaries` differs), `related_to`-linked.
- 2D Sod at 30° vs 2D Sod at 45° → **existing entry**; `rotation_deg` parameter; two
  `reference_results`.
- 3D planar Sod with no new analysis requirement → **existing entry** as its 2D form; the inert extra
  dimension is a parameter, not a fork.
- Inviscid KH vs visco-resistive KH → **NEW SIBLING** (terms differ), `related_to`-linked.
- Steady-inflow Sod vs step-inflow Sod → **NEW SIBLING** (`time_dependent_bc` differs); step-to-40 vs
  step-to-66 → **existing entry** (parameter).
- Sod + plain embedded rectangle vs same physics + adversarial spline-notch obstacle → both
  `has_internal_boundaries=true`; same entry unless the IC/geometry *form* differs; the adversarial
  one additionally carries a `geometry_stress` tag (searchable, not a fork).
