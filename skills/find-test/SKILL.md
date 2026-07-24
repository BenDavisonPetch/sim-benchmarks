---
name: find-test
description: >
  Resolve a natural-language research need into structured INDEX filters, rank matching entries, and
  surface coverage gaps as a first-class result (SPEC §9.2). Holds the §7.3 alias table (slang ->
  canonical (base, terms) signature). Pulled in by /find-test. Read-only: never authors a spec; reads
  INDEX.tsv first and opens spec.md only for finalists. No templates/ (SPEC §10). No cleverness;
  runnable by a Sonnet-class model.
---

# find-test — need -> filters -> ranked matches + gaps (SPEC §9.2, §7.3, §2.3)

Translate a research need into the same structured filters the DB is indexed on, rank the entries that
match, and report **what is missing** as a first-class answer. This skill is read-only: it never
scaffolds or edits an entry (that is `/add-test` / `/create-test`). Subjectivity is confined to the
alias resolution in Step 1; everything after is a mechanical grep + rank over `INDEX.tsv`.

**Input.** The user's natural-language text after `/find-test` (a single need, or a suite request).
**Output.** Ranked slugs + one-line why-match + headline score, **plus coverage gaps** (Step 3); for a
suite, an ordered suite + a coverage table + explicit holes (Step 4).

---

## The alias table (SPEC §7.3 — slang lives HERE; specs stay canonical)

Specs never store slang. This table is the single place that knows informal names. Rows are
constructed from the §7.1 `base` semantics (SPEC gives the semantics, not literal rows — logged ELAB
in `SPEC_DEVIATIONS.md`). A slang term with **no** registry backing (e.g. "Hall MHD", "two-fluid",
"radiation MHD") is **not** an alias — it is a **coverage gap** to report in Step 3, never a silent
match onto the nearest base.

### (a) physics phrase -> `(base, terms)` signature

Maps to the `physics_signature` + `terms` INDEX columns. `base` semantics: terms are independent
toggles, each present iff its coefficient is nonzero anywhere (§2.3, §7.1).

| phrase (and common variants)              | base    | terms present                                  |
|-------------------------------------------|---------|------------------------------------------------|
| Euler / compressible Euler / inviscid gas | `hydro` | `[]`                                           |
| Navier–Stokes / viscous (compressible)    | `hydro` | `[viscosity]` (+`heat-conduction` if thermal)  |
| ideal MHD / MHD (unqualified)             | `mhd`   | `[]`                                           |
| resistive MHD                             | `mhd`   | `[resistivity]`                                |
| VRMHD / visco-resistive MHD               | `mhd`   | `[viscosity, resistivity]` (+`heat-conduction` if thermal) |

Notes:
- "MHD" unqualified defaults to **ideal** (`mhd`, no terms); only qualify with a term when the need
  names it ("resistive", "viscous", "with heat conduction").
- `heat-conduction` is a parenthetical add-on: include it only when the need mentions thermal
  conduction / a nonzero conductivity.
- The solid / non-convecting phase bases (`magnetic-diffusion`, `perfect-conductor`, `rigid-body`)
  have no slang aliases — name them directly if the need describes a frozen/diffusing/inert body.

### (b) canonical problem-name -> physics + slug hint

Maps a named test onto its likely physics family and a slug fragment to grep. A hint is a **search
seed, not a match** — still confirm against INDEX.

| name (and variants)                 | physics family        | slug hint / notes                              |
|-------------------------------------|-----------------------|------------------------------------------------|
| Sod / shock tube                    | `hydro` `[]`          | `sod` `shock-tube`                             |
| Brio–Wu                             | `mhd` `[]`            | `brio-wu`; MHD shock tube                      |
| Orszag–Tang                         | `mhd` `[]`            | `orszag-tang`                                  |
| KH / Kelvin–Helmholtz               | `hydro` or `mhd`      | `kelvin-helmholtz`; inviscid vs viscous FORK   |
| RT / Rayleigh–Taylor                | `hydro` (+`gravity`)  | `rayleigh-taylor`; gravity term present        |
| RM / Richtmyer–Meshkov              | `hydro` `[]`          | `richtmyer-meshkov`; shock-driven interface    |
| Sedov / blast / Sedov–Taylor        | `hydro` `[]`          | `sedov` `blast`; often axis-singularity        |
| θ-pinch / theta-pinch               | `mhd` family          | `theta-pinch`; often `axisymmetric`/cylindrical |

---

## Step 1. Resolve slang -> structured filters

Rewrite the need into the filter set the INDEX is keyed on. Use the alias table for physics phrases
and problem names; leave everything the user did not constrain **unfiltered** (do not invent
constraints).

Filters to fill (leave blank = unconstrained):

- **physics_signature** — `base(term|term)[/eostype]` per material, from alias table (a). For a
  problem-name need, seed the family + slug hint from (b).
- **terms / capabilities** — the required term set (viscosity, resistivity, heat-conduction, gravity).
  This is the presence filter (§2.3) — see Step 3a.
- **dims** — 1 / 2 / 3 if the need constrains dimensionality.
- **analysis_treatments** — `oblique-to-grid`, `axis-singularity`, `multi-material-interface`, … if
  the need implies extra analysis ("rotated", "at the axis", "across a material interface").
- **bc types** — a `registry/bc-types` id if named ("periodic", "inflow", …).
- **multi_material** — true if the need describes ≥2 distinct materials/equation sets.
- **time_dependent_bc** — true if the need describes a driven / time-varying boundary ("driven
  inflow", "pressure step"), false if it explicitly wants a steady problem.
- **has_internal_boundaries** — true if the need describes an embedded obstacle / internal interface.
- **geometry_stress** — set if the need asks for an adversarial / purpose-built stress geometry.
- **min score** — a floor if the need asks for "well-validated" / "score ≥ N".
- **exact-solution-required?** — true if the need demands an analytic/exact reference (maps to the
  INDEX `has_exact_solution` column).

Any slang with no registry backing → note it now; it becomes a Step-3 coverage gap.

---

## Step 2. Query INDEX.tsv first; open spec.md only for finalists

1. Read `INDEX.tsv` (generated; grep-cheap, token-economical — §8.1). Columns:
   `slug, physics_signature, terms, dims, analysis_treatments, bc_types_present, coupling,
   multi_material, time_dependent_bc, has_internal_boundaries, headline_score, has_exact_solution`.
   Set-valued cells (`terms`, `analysis_treatments`, `bc_types_present`) are pipe-joined — compare as
   sets, order-insensitive.
2. Filter rows against Step 1. Apply the capability presence rule (Step 3a) for term / capability
   filters. Drop rows below `min score` or lacking an exact solution when required.
3. Open `tests/<slug>/spec.md` **only for the finalists** (the handful that pass the INDEX filter) —
   to confirm the structural match and to write the why-match line. Never open every spec.

---

## Step 3. Output — ranked matches + coverage gaps (BOTH are first-class)

Emit, in this order:

1. **Ranked matches.** For each finalist, one row:
   `<slug> — <one-line why it matches> — headline score <n>/5`.
   Rank by: filter completeness (matches more of the constrained filters first), then headline score,
   then exact-solution availability. Keep the why-match to one line tied to the filters that hit.
2. **Coverage gaps (always present, even when matches exist).** Report, explicitly:
   - filters with **zero** matching entries ("no viscous KH entry exists");
   - slang with **no registry backing** from Step 1 ("Hall MHD has no `base` — vocabulary gap, not
     in scope without a §7.2 extension");
   - near-misses that fork on **one** capability (a sibling exists inviscid but not viscous, or steady
     but not driven) — name the sibling slug and the missing fork.

   Gaps are the answer to "what should I add next", so never omit them because matches were found.

### Step 3a. Capability filter = presence (§2.3)

Term/capability filters test **presence**, not value:

- **"my method has no heat-conduction / no resistivity / …"** (a capability the method lacks) ⇒
  **exclude** every entry whose **required terms ⊄ the method's capabilities**. An entry that requires
  `resistivity` is unrunnable by an ideal-only method; drop it.
- **"my method has no time-dependent BCs"** ⇒ exclude entries with `time_dependent_bc = true`.
- **"no internal boundaries"** ⇒ exclude entries with `has_internal_boundaries = true`.
- Conversely, **"I want a viscous test"** keeps only entries whose `terms` include `viscosity`.

Presence is why inviscid-KH and viscous-KH are legitimately different entries (§2.3): the filter tells
them apart for free.

---

## Step 4. Suite queries -> ordered suite + coverage table + explicit holes

A suite request ("an MHD convergence suite", "a robustness ladder from smooth to adversarial") returns
more than a flat ranking:

1. **Ordered suite** — the chosen slugs in a sensible progression (e.g. smooth → discontinuous →
   adversarial; or increasing dimensionality; or ascending headline score). State the ordering axis.
2. **Coverage table** — rows = suite members, columns = the capabilities/analysis the suite is meant
   to span (dims, terms, analysis_treatments, has_exact_solution, score). Shows at a glance what each
   member exercises.
3. **Explicit holes** — cells the suite **cannot** fill from the current DB (e.g. "no 3D oblique MHD
   entry", "no exact-solution mode above 2D"). These are `/create-test` / `/add-test` targets. A suite
   answer is incomplete without its holes.

Apply the Step-3a presence filter across the whole suite (a suite for an ideal-only method excludes
every entry requiring a term the method lacks).

---

## Done when

The need is resolved into explicit Step-1 filters (unconstrained fields left blank, no invented
constraints); `INDEX.tsv` was read first and only finalist specs opened; the output carries ranked
slugs + one-line why-match + headline score **and** first-class coverage gaps (including
no-registry-backing slang and one-capability-fork near-misses); a suite request additionally returns an
ordered suite + coverage table + explicit holes; every capability filter used presence (§2.3), not
value.
