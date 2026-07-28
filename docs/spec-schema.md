# spec-schema.md — `spec.md` field reference

Authoritative field reference for a test entry's `spec.md` (SPEC §3). One file per entry:
**YAML frontmatter** (all structured/filterable fields) + **markdown body** (prose sections).
Authoring skills copy `templates/spec.template.md` and fill it — never freehand (SPEC §11.9).

Legend: **R** = required, **O** = optional. Types are the YAML types `validate.py` enforces.
"registry id" = a string that must resolve to a file `registry/<kind>/<id>.md` (SPEC §11.2).

---

## 1. Frontmatter

### 1.1 Top-level identity

| Field | R/O | Type | Notes |
|---|---|---|---|
| `slug` | R | string | kebab-case, physically descriptive; the stable public key (SPEC §1.2, `conventions.md`). Must equal the directory name `tests/<slug>/`. |
| `name` | R | string | Canonical display name. Quote if it contains punctuation. |
| `provenance` | R | enum | `literature` \| `synthesized`. `synthesized` for `/create-test` output. |
| `one_liner` | R | string | One-sentence summary; shown in `/find-test` output. |

### 1.2 `physics`

| Field | R/O | Type | Notes |
|---|---|---|---|
| `physics.materials` | R | list | ≥1 element. A single-material test uses a 1-element list. |
| `materials[].name` | R | string | Local material label, referenced by regions / material_fields. |
| `materials[].base` | R | registry id | `registry/equations/<id>`. |
| `materials[].terms` | R | list[registry id] | `registry/terms/<id>` set present (nonzero). `[]` = base with no terms (e.g. Euler, ideal MHD). Term presence is a value-based identity fork (SPEC §2.3). |
| `materials[].eos` | conditional | map | Present **iff** `base` declares `requires_eos: true` (SPEC §11.11, `validate.py` check 8). Omit otherwise. |
| `materials[].eos.type` | R (if eos) | registry id | `registry/eos/<id>`. |
| `materials[].eos.params` | R (if eos) | map | EoS parameters per the eos file's params-schema. |
| `materials[].material_fields` | O | list | Named spatial coefficients as expressions (`ic-expression-language.md`); e.g. a resistivity field `eta(r)`. Each `{name, region, expr, units?}`. |
| `physics.coupling` | R | registry id \| `none` | `registry/internal-boundary-kinds/<id>` or the literal `none`. Physical only — never a numerical method (SPEC §1.6). |

### 1.3 `dimension`

| Field | R/O | Type | Notes |
|---|---|---|---|
| `dimension.intrinsic` | R | int | Smallest dimension the problem is defined in. |
| `dimension.runnable_in` | R | list[int] | Dims requiring **no new analysis** (inert extra dims listed). A 3D-planar form of a 2D problem lists both — the extra inert dim is a parameter, not a fork (SPEC §2.5). |

### 1.4 Identity capability fields

| Field | R/O | Type | Notes |
|---|---|---|---|
| `analysis_treatments` | R | list[registry id] | `registry/analysis-treatments/<id>` set. `[none]` if no extra treatment. Part of identity (SPEC §2.1). Members that only *name* internal-boundary kinds are searchable descriptors, not forks. |
| `capability_flags.time_dependent_bc` | R | bool | `true` iff any `domain_bc[*].state` references `t`. Computed from the **canonical** set; `validate.py` check 6 enforces consistency. Binary identity fork (SPEC §2.3). |
| `capability_flags.has_internal_boundaries` | R | bool | `true` iff ≥1 internal material interface / internal boundary present. Binary identity fork. |
| `geometry_stress` | R | registry id \| `none` | `registry/geometry-stress/<id>` or `none`. Searchable tag for adversarial geometries (SPEC §2.3 exception), not an identity fork. |

### 1.5 `geometry`

| Field | R/O | Type | Notes |
|---|---|---|---|
| `geometry.coord_system` | R | registry id | `registry/coord-systems/<id>`. The **physical frame** the problem is posed in, never a grid (SPEC §1.6). |
| `geometry.domain` | R | map | Per-axis extents, e.g. `{ x: [0,1], y: [0,1] }`. |
| `geometry.regions` | R | list | Analytic predicate primitives + transforms. Each `{id, shape, params}`. |

Region primitives: `box`, `cylinder`, `sphere`, `shell{center, r:[r_inner,r_outer]}`, `halfspace`,
`polygon{vertices:[...]}`. (`polyhedron`, 3D, is deferred — SPEC §12.)
Transforms: `rotate{deg, about}`, `translate{by}`.

### 1.6 `units` (stored as authored — never auto-converted, SPEC §12)

| Field | R/O | Type | Notes |
|---|---|---|---|
| `units.system` | R | string | e.g. `cgs-gaussian` \| `si` \| `code` \| `nondimensional`. See `conventions.md`. |
| `units.b_field_convention` | R | string \| `null` | e.g. `permeability-unity` \| `sqrt-4pi`. `null` only with a `needs-source`/pending row (SPEC §5). See `conventions.md`. |

### 1.7 `initial_conditions`

Grammar and evaluation order are defined in `ic-expression-language.md`; `validate.py` check 6
parses and aux-resolves every expression here.

| Field | R/O | Type | Notes |
|---|---|---|---|
| `initial_conditions.aux` | O | list | Ordered `{name, expr, units?}` bindings, evaluated top-down; later may reference earlier. |
| `initial_conditions.equilibrium` | R | list | Base state (may be trivial). `{region, fields:{var: expr}}`. Enables `well-balancing`. |
| `initial_conditions.perturbation` | R | map | `{combine_rule, fields}`. `combine_rule` ∈ `additive` \| `replace`. `fields: []` if none. |
| `initial_conditions.potentials` | O | list | `{name, expr, derives}` — potential-defined fields + a stated derivation rule (e.g. `B = curl(A)`). Rule is physical, not method-specific. |

### 1.8 `parameters`

Values only; never identity except capability presence (SPEC §2.2/§2.3).

| Field | R/O | Type | Notes |
|---|---|---|---|
| `parameters[].name` | R | string | Parameter name. |
| `parameters[].canonical` | R | scalar \| list \| `null` | The runnable default. `null` only paired with `notes: needs-source` + a `pending_extraction.md` row (SPEC §5.2, §11.5). |
| `parameters[].meaning` | R | string | Human meaning, with units. |
| `parameters[].notes` | O | string | Informational regime notes; `needs-source` marker. |
| `parameters[].source_ref` | O | references key | A **verified** `references[]` key naming where the canonical value is *defined* (distinct from `reference_results`, which record what a ref *did*). |

### 1.9 `domain_bc` (per face)

Each face key (`x_lo, x_hi, y_lo, y_hi`, plus `z_lo, z_hi` in 3D) maps to `{type, state?}`.

| Field | R/O | Type | Notes |
|---|---|---|---|
| `domain_bc.<face>.type` | R | registry id | `registry/bc-types/<id>`. |
| `domain_bc.<face>.state` | O | map | `{var: expr}` IC-expression-language expressions (may reference `x,y,z,t`). Any face whose state references `t` sets `capability_flags.time_dependent_bc = true` (SPEC §2.3, `validate.py` check 6). A bc-type declaring `state_keys` accepts only those keys (check 2). |

One `type` per face: a boundary constraining several variable groups at once is a single
**composite** bc-type, not a per-variable face shape (SPEC §7.1). A rigid conducting wall — velocity
+ normal/tangential B + density + pressure — is `perfect-conductor`, whose optional `state` carries
a moving wall's velocity (`vx, vy, vz`) and a non-zero normal field (`Bn`); see
`registry/bc-types/perfect-conductor.md`.

### 1.10 `internal_boundaries`

List; physical only (SPEC §1.6, §11.1). `[]` when none. Each entry names an
`internal-boundary-kinds` id (`material-contact`, `free-surface`, `rigid-wall`,
`perfect-conductor-wall`, `symmetry`, `electromagnetic-coupling`, …) + geometry + optional motion.
**No numerical method here.** (A plasma/solid material interface expressed via `physics.coupling`
need not be repeated here.)

### 1.11 `time`

| Field | R/O | Type | Notes |
|---|---|---|---|
| `time.t_final` | R | number | Time the sim must run to so **every** mode can be evaluated. |
| `time.snapshot_times` | O | list[number] | Qualitative snapshot times. |

### 1.12 `validation_modes` (≥1 required — SPEC §11.6)

Each element is one independently-scored validation mode.

| Field | R/O | Type | Notes |
|---|---|---|---|
| `id` | R | string | Mode label, unique within the entry. |
| `purpose` | R | string | **Specific** capability statement. Never "compare with literature" (SPEC §11.6). |
| `procedure` | R | registry id | `registry/procedures/<id>`; fills that procedure's slots. A mode may not invent an ad-hoc procedure (SPEC §6.1). |
| `inputs` | R | map | The procedure's slot fills (sample times, variables, cut-lines, features, reference, tolerance, …). `inputs.at_time` (and any sample time) must be ≤ `time.t_final`. |
| `inputs.reference` | O | map | `{kind, key}`; `kind` ∈ `reference` \| `reference-result`; `key` must resolve (see §5 rules). |
| `has_exact_solution` | R | bool | Feeds `INDEX.tsv` and scoring. |
| `score` | R | int | 1..5 (`validate.py` check 3). See `scoring-rubric.md`. |
| `score_justification` | R | string | Required for every mode (SPEC §11.6). |
| `baseline` | O | map | Differential (A/B) mode: `{description, config_delta}`. `config_delta` may alter/zero a term **only** as a differential reference and must **not** change the entry's INDEX capability set (SPEC §6.3A, §11.13, `validate.py` check 9). |
| `measured` | conditional | string | Present with `baseline`: the difference quantity being measured. |

Universal diagnostics (`div-b`, `conservation-drift`) appear as a **scored** mode only when
genuinely discriminating for the problem (the entry must assert *why*); otherwise they are
unscored provenance metrics (SPEC §6.4).

### 1.13 References & links

| Field | R/O | Type | Notes |
|---|---|---|---|
| `references` | R | list | Verified refs only (`status: verified`, SPEC §5.1). `[]` allowed. Each carries `verification{status, identifier, source, checked, meta?}`. `meta{year, first_author, container, title}` is **resolver output pasted from `verify_refs.py --meta`, never typed** — `meta.year` (the priority date over a doi+arxiv pair) is what SPEC §5.4 orders attribution by; check 5 requires it on a using-ref with a doi/arxiv, check 10 warns when it disagrees with the live resolution. See §5 rules and `conventions.md`. |
| `references_unverified` | R | list | Quarantined refs (`unverified`/`user-supplied`); excluded from INDEX and generated paper sections. `[]` allowed. |
| `test_origin` | O | map | Entry-level attribution (SPEC §5.4): `{status: resolved-in-list\|resolved-external\|pending\|synthesized, ref?, authored_from?, external?, derived_from?, attribution_claims[]{stated_by, quote}}`. `/add-test` fills `authored_from` + verbatim `attribution_claims[]`; only `/add-refs` resolves `status`/`ref`/`external`; `/promote-refs` never touches it. `validate.py` check 11. |
| `reference_results` | R | list | What a specific ref *did* (SPEC §5.3). `[]` allowed. `key` must be in `references[]`. Fields: `key, params_used, method, resolution, amr, findings, figure_asset?, wall_pressure_bc?`. Method/resolution/amr are provenance-only — never in the problem block (`validate.py` check 7). `wall_pressure_bc` (a `registry/wall-pressure-treatments/` id) is **required** on every row of an entry posing a perfectly-conducting wall — a `perfect-conductor` face or a `perfect-conductor-wall` internal boundary (`validate.py` check 12); `not-stated` when the source is silent. |
| `related_to` | R | list[slug] | Sibling slugs (same physics, different treatments/capabilities). `[]` allowed. |
| `headline_score` | R | int | `= max(validation_modes[].score)`; **set by `reindex.py`** (SPEC §8.2, §11.8). Hand value must equal the recomputed max or `validate.py` check 3 fails. |

Per-ref `original_intro` (bool, `unknown` = key absent) marks the one ref that introduced the test. Set
only during `/add-refs` by the SPEC §5.4 rule: a **stated** attribution wins over dates; otherwise the
earliest **using-ref** (one with a `reference_results[]` row) by `verification.meta.year`; unresolved
stays unresolved (`test_origin.status: pending`, no flag anywhere); a `provenance: synthesized` entry
never carries one. At most one `true` per entry, and only on a verified key.

---

## 2. Body (markdown, prose)

Fixed section order, template-enforced (SPEC §3.2, §11.9). All five headings present in this order:

```markdown
## Physical problem
<what is physically happening — problem only, no method>

## What this test actually tests
<specific capability(ies); NEVER "compare with literature">

## Qualitative behaviour
<used where no exact solution: SPECIFIC named features ("fast shock reaches x≈…, contact at …").
 Note known traps, e.g. AMR gridding breaks IC symmetry — do not use symmetry as a proxy there.>

## Validation notes
<per-mode elaboration, expected convergence orders, known reference values WITH units>

## Notes
<edge cases, gotchas, unit-convention warnings>
```

The problem-block prose (`Physical problem`, and the physical parts of the others) is bound by the
§1.6 hard boundary: no numerical method, resolution, AMR, or grid type. All such provenance lives
in `reference_results` (`validate.py` check 7).
