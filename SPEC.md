# SPEC.md — Numerical Test-Case Database

Authoritative specification. Building happens in a later session; this document is the contract.
Nothing here is a suggestion — deviations require re-grilling.

---

## 0. Purpose & non-goals

A **git repo** holding a curated database of numerical test cases for computational-physics
method research (finite-volume / MHD / multi-material, etc.). Interacted with via **Claude Code
CLI** using slash commands backed by skills and a few Python scripts.

The repo lets a researcher:

- **add** a test from a paper / document / simulation settings file (`/add-test`);
- **find** tests matching a research need, including gaps in coverage (`/find-test`);
- **create** a new or derived test spec that does not yet exist (`/create-test`);
- **enrich** a test with literature references + their findings, enough to write a paper section
  (`/add-refs`).

**Non-goals:** no website, no web-app, no server, no database engine, no runtime for the physics
codes themselves. The DB stores *descriptions* sufficient to run and validate a test in an
external code; it does not run them.

**Prime directive:** stay consistent and machine-checkable forever. Every enum is registry-backed,
every entry is schema-validated, the lookup index is generated (never hand-edited), and references
are never fabricated. A **Sonnet-class model** must be able to execute every skill with high
accuracy — so procedures are prescriptive, mechanical, and template-driven, never relying on
cleverness.

---

## 1. Core concepts

### 1.1 Entry
A single test case = one directory `tests/<slug>/` containing one `spec.md`. The `spec.md` is
**one file**: YAML frontmatter (structured, filterable fields) + markdown body (prose fields).
Assets live beside it in `assets/`.

### 1.2 Slug
Human-readable, kebab-case, physically descriptive: `sod-shock-tube`, `orszag-tang-vortex`,
`brio-wu-shock-tube`, `theta-pinch-compression`. Slugs are the stable public key used in
`/find-test` output and `related_to` links.

### 1.3 Registry (controlled vocabulary)
Every enumerable field draws from a registry. Specs reference registry **ids**; `validate.py`
rejects any id not present in the registry. Extending vocabulary is the *only* sanctioned way to
grow the system's expressiveness, and it is a deliberate, logged, reviewed step
(§6, §7). This is the central anti-drift mechanism.

### 1.4 Reference vs reference-result
- `references[]` = canonical bibliography (bibtex), each with a **verification status**.
- `reference_results[]` = what a *specific* reference actually did with this test (params used,
  numerical method, resolution/AMR, findings). This is where all method/resolution provenance
  lives — never in the abstract problem statement.

### 1.5 Validation mode
A test carries one or more `validation_modes[]`. Each is a *specific* way to validate a method
against the test, with its own procedure reference, its own instructions, and its own **score /5**.
The entry's headline score = `max` over its modes.

### 1.6 Problem vs method (hard boundary)
The problem block describes the *physics problem only*: geometry, ICs, parameters, boundary
conditions **as physical statements**, unit conventions, times. It never prescribes a numerical
method (no "ghost fluid", no "cut cell", no resolution, no AMR, no grid type). Those are method
choices and appear only inside a `reference_result`. A spherical *coordinate frame the physics is
posed in* is problem; a spherical *grid* is method.

---

## 2. Entry identity & de-duplication (structural, value-blind)

The single most important rule for preventing a messy, duplicated DB. It must be executable by a
Sonnet-class model with near-zero subjectivity.

### 2.1 Identity signature
Two entries are "the same test" iff they share **all** of:

1. **physics_signature** — the set of materials, each with: base equation-set id, the **set of
   terms present** (see §2.3), and eos type id; plus the coupling/interface structure between
   materials.
2. **analysis_treatments** — the registry-backed set describing what extra analysis the problem
   demands (e.g. `none`, `oblique-to-grid`, `axis-singularity`, `multi-material-interface`).
   Members that merely *name kinds* of internal boundary are **searchable descriptors, not
   additional forks**; the fork is the binary `has_internal_boundaries` capability flag (§2.3).
3. **IC / geometry structural form** — the *form* of the initial condition, geometry, **and
   boundary-condition state expressions**, compared **modulo numeric constants**: expression
   structure, region topology, potential-defined fields, and the equilibrium+perturbation
   decomposition. Numeric values do **not** enter identity.
4. **capability_flags** — binary presence flags that gate which methods can run the test:
   `time_dependent_bc` (any domain-BC state expression references `t`) and
   `has_internal_boundaries` (≥1 internal material interface / internal boundary present). Like
   term-presence, these are **binary** and part of identity. They are capability *gates*, not
   forms: a method either supports a capability or not; the specific function or geometry does not
   further fork (§2.3).

### 2.2 Parameters are values, not identity
An entry stores a **canonical parameter set** (runnable defaults) plus a `parameters:` list
(name, canonical value, meaning, optional informational regime notes, optional `source_ref`).
Parameter *values* never affect identity. A reference that used different values of the *same
structural parameters* is recorded as a `reference_result` on the same entry, not a new entry.

### 2.3 Capability presence (the value-based forks)
A **capability** is present iff it is exercised by the **canonical** set. Capabilities that fork
identity are all **binary**:

- **term presence** — a physical term (viscosity, resistivity, heat-conduction, gravity, …) is
  present iff its coefficient is nonzero *anywhere* in the domain (a spatially-varying coefficient
  that is zero in part of the domain still counts as present).
- **time-dependent BC** (`time_dependent_bc`) — present iff any domain-BC state expression
  references `t`. Steady vs driven ⇒ different entries, `related_to`-linked. Step vs ramp vs
  sinusoid ⇒ **same entry** (the BC-state expression is a value): once a code implements
  `t`-dependence, arbitrary `f(t)` is trivial.
- **internal boundaries** (`has_internal_boundaries`) — present iff ≥1 internal boundary/interface
  exists. The *specific* internal geometry does **not** further fork; internal-boundary
  implementations are general.

Consequences (examples):
- viscosity `1` → `2`: present in both → **same entry** (record as `reference_result`).
- resistivity `0` → nonzero: absent vs present → **different entry** (+ `related_to` link).
- Mach subsonic → supersonic (same structure): **same entry**, parameter sweep.
- rotation `30°` → `45°` (same structure & treatments): **same entry**, `rotation_deg` parameter.
- steady inflow → time-dependent inflow: **different entry** (`time_dependent_bc` differs), linked.

**Searchable-tag exception.** Geometries *specifically constructed to stress-test an algorithm*
(not merely incidentally curved) carry a registry-backed `geometry_stress` tag so they are
findable. The tag is a searchable descriptor, not an extra identity fork (such geometries already
distinguish via IC/geometry structural form, §2.1 item 3).

Term-presence *is* the `/find-test` capability filter for free (inviscid-KH and viscous-KH are
legitimately different entries with different required terms); `time_dependent_bc` and
`has_internal_boundaries` are capability filters in the same way.

### 2.4 De-dup procedure (mechanical; run by `/add-test`, `/create-test`)
1. Query `INDEX.tsv`: candidate set = rows with the same `physics_signature` **and** the same
   `analysis_treatments` **and** the same `capability_flags`. (Cheap; narrows to ~0–3 entries.)
2. Open each candidate `spec.md`. Compare IC/geometry/BC-state **structural form ignoring numeric
   values**, and compare the canonical (aliased) name.
3. Decision:
   - **Structural match** (only numeric parameter values differ) → **not a new test**. Record a
     `reference_result` with `params_used`, and/or note the parameter range. Do **not** create an
     entry.
   - **Same physics_signature but different analysis_treatments or capability_flags** → **new
     entry** + `related_to` link to the sibling(s).
   - **No structural match** → **new entry**.
4. **Term-zeroing check:** if a candidate ref sets a coefficient of a term that the entry marks
   *present* to zero, that ref belongs to a **different (sibling) entry**, not this one. (Exception:
   a `validation_mode.baseline` that zeroes a term purely as a differential reference — §6.)
5. **Minimal-material canonicalization (convention, not a §11 invariant).** When a problem admits
   both a multi-material and a single-body-with-coefficient-field representation, choose the
   **minimum** material count: regions sharing an equation set become one material with a spatial
   coefficient; a material boundary exists only where the base equation set, EoS, or a genuine
   physical interface differs. Interchangeable solid-phase bases (§7.1) collapse to one signature
   element under their declared predicate. Not mechanically enforced; an optional lint may warn
   when an entry has ≥2 materials sharing a `base` (merge candidate; expect false positives).

Subjectivity is confined to step 2's structural compare over a tiny candidate set, with the above
explicit instructions. Everything else is mechanical.

### 2.5 Worked cases (must all hold)
- 1D Sod vs 2D Sod rotated 30° in an embedded rectangle → **different entries**
  (`analysis_treatments`: `none` vs `oblique-to-grid`; `has_internal_boundaries` differs),
  linked `related_to`.
- 2D Sod at 30° vs 2D Sod at 45° → **same entry**; `rotation_deg` parameter; two
  `reference_results`.
- 3D planar Sod with no new analysis requirement → **same entry** as its 2D form; the extra
  inert dimension is a parameter, not a fork.
- Inviscid Kelvin-Helmholtz vs visco-resistive Kelvin-Helmholtz → **different entries** (terms
  differ), `related_to` linked.
- Steady-inflow Sod vs step-inflow Sod → **different entries** (`time_dependent_bc` differs),
  linked; step-to-40 vs step-to-66 → **same entry** (parameter).
- Sod with a plain embedded rectangle vs the same physics with an adversarial spline-notch
  obstacle → both `has_internal_boundaries=true`; they differ only if their IC/geometry *form*
  differs; the adversarial one additionally carries `geometry_stress`.

---

## 3. `spec.md` schema

One file per entry: YAML frontmatter (all structured/filterable fields) + markdown body (prose).
Authoring skills copy `templates/spec.template.md` and fill it — never freehand.

### 3.1 Frontmatter (YAML)

```yaml
slug: orszag-tang-vortex
name: "Orszag–Tang Vortex"              # canonical display name
provenance: literature                   # literature | synthesized
one_liner: "Smooth ICs developing MHD shocks + transition to 2D MHD turbulence."

physics:
  materials:
    - name: plasma                       # single-material tests still use a 1-element list
      base: mhd                          # registry/equations id
      terms: []                          # registry/terms ids present (nonzero). [] = ideal
      eos:                               # omit for bases with requires_eos: false
        type: gamma-law                  # registry/eos id
        params: { gamma: 1.6666666667 }
      material_fields: []                # optional named spatial coefficients (expressions);
                                         #   e.g. resistivity eta(r). See §4.
  coupling: none                          # registry/internal-boundary-kinds id, or 'none'
  # multi-material example:
  # materials: [ {name: metal, base: hydro, terms:[viscosity], eos:{...}},
  #              {name: plasma, base: mhd, terms:[resistivity], eos:{...}} ]
  # coupling: material-contact            # physical, NOT a method (never 'ghost-fluid')

dimension:
  intrinsic: 2                            # smallest dimension the problem is defined in
  runnable_in: [2]                        # dims requiring no new analysis (inert extra dims listed)

analysis_treatments: [none]               # registry/analysis-treatments ids (set)

capability_flags:                         # binary; computed from the CANONICAL set (§2.3)
  time_dependent_bc: false                # any domain_bc[*].state references t
  has_internal_boundaries: false          # >=1 internal material interface / internal boundary
geometry_stress: none                     # registry/geometry-stress id, or 'none'

geometry:
  coord_system: cartesian                 # registry/coord-systems id (physical frame; not a grid)
  domain: { x: [0,1], y: [0,1] }
  regions:                                # analytic predicate primitives + transforms
    - id: whole
      shape: box
      params: { x: [0,1], y: [0,1] }
  # primitives: box, cylinder, sphere, shell{center, r:[r_inner,r_outer]}, halfspace,
  #             polygon{vertices:[...]}   (polyhedron: 3D, TODO §12)
  # transforms: rotate{deg, about}, translate{by}

units:                                    # STORED AS AUTHORED — never auto-converted
  system: code                            # e.g. cgs-gaussian | si | code | nondimensional
  b_field_convention: permeability-unity  # permeability-unity | sqrt-4pi | ...

initial_conditions:
  aux:                                    # ordered top-down bindings, numpy-evaluable
    - { name: gamma, expr: "5/3" }
  equilibrium:                            # base state (may be trivial). Enables well-balancing.
    - region: whole
      fields:
        rho:  "gamma*gamma"
        p:    "gamma"
        vx:   "-sin(2*pi*y)"
        vy:   "sin(2*pi*x)"
        Bx:   "-sin(2*pi*y)"
        By:   "sin(4*pi*x)"
  perturbation:                            # added on top of equilibrium; [] if none
    combine_rule: additive                 # additive | replace
    fields: []
  potentials:                              # optional: potential-defined fields + derived rule
    - { name: A_z, expr: "...", derives: "B = curl(A)" }

parameters:                                # values only; never identity (except capabilities §2.3)
  - { name: gamma, canonical: 1.6666666667, meaning: "ratio of specific heats" }
  # optional per-parameter source_ref: a VERIFIED references[] key naming where the canonical
  # value is DEFINED (distinct from reference_results, which record what a ref DID with the test):
  # - { name: dipole_eq_nT, canonical: 195, meaning: "...", source_ref: anderson2011 }

domain_bc:                                 # PER FACE. {type, state}. registry/bc-types ids.
  x_lo: { type: periodic }
  x_hi: { type: periodic }
  y_lo: { type: periodic }
  y_hi: { type: periodic }
  # state fields are IC-expression-language expressions (may reference x,y,z,t). A face whose
  # state references t sets capability_flags.time_dependent_bc = true. Example driven inflow:
  # x_hi: { type: supersonic-inflow, state: { rho: "40 + 40*step(t,0,30)", vx: "-400 - 300*step(t,0,30)", ... } }
  # 3D: also z_lo, z_hi

internal_boundaries: []                    # physical only: material-contact | free-surface |
                                           # rigid-wall | perfect-conductor-wall | symmetry |
                                           # electromagnetic-coupling + geometry + motion.
                                           # NO numerical method here.

time:
  t_final: 0.5                             # time the sim must run to so EVERY mode can be evaluated
  snapshot_times: [0.08, 0.25]             # optional, qualitative

validation_modes:                          # >= 1 required. Each independently scored.
  - id: shock-feature-locations
    purpose: "Verify positions of the named MHD shocks along stated cut-lines."   # SPECIFIC
    procedure: feature-location            # registry/procedures id
    inputs:
      at_time: 0.5                         # sample time(s); must be <= t_final
      variables: [p]
      cut_lines: ["y=0.3125"]
      features: ["fast shock", "slow shock", "contact"]
      reference: { kind: reference-result, key: dahlburg1989 }
      tolerance: "positions within 2 cells"
    has_exact_solution: false
    score: 3
    score_justification: "Quantitative feature-location vs accepted reference; partial coverage."
    # optional differential (A/B) mode:
    # baseline:
    #   description: "same test with <effect> removed"
    #   config_delta: { "aux.eta_core": "eta_mantle" }   # a config delta serving as the reference
    # measured: "difference in the feature vs the baseline run"

references: []                             # verified refs (bibtex keys); see §5
references_unverified: []                  # quarantined until verify_refs.py upgrades; excluded
                                           # from INDEX + generated paper sections
reference_results: []                      # see §5.3
related_to: []                             # sibling slugs (same physics, different treatments/caps)
headline_score: 3                          # = max(validation_modes[].score); set by reindex.py
```

### 3.2 Body (markdown, prose)
Fixed section order (template-enforced):

```markdown
## Physical problem
<what is physically happening>

## What this test actually tests
<specific capability(ies): NEVER "compare with literature">

## Qualitative behaviour
<used only where no exact solution: SPECIFIC named features — "fast shock reaches x≈…,
contact at …". Note known traps, e.g. AMR gridding breaks IC symmetry — do not use symmetry
as a proxy where this occurs.>

## Validation notes
<per-mode elaboration, expected convergence orders, known reference values with units>

## Notes
<edge cases, gotchas, unit-convention warnings>
```

---

## 4. IC / geometry / BC expression language

Documented once in `docs/ic-expression-language.md`; parsed/checked by `validate.py`.

- **Variables:** `x, y, z, r, phi, theta` (coordinate-system aware) and `t` (time). `t` appears
  only in `domain_bc` state expressions and any explicitly time-dependent field; a steady problem
  never references `t`.
- **Functions:** `sin, cos, tan, exp, log, sqrt, tanh, erf, abs, min, max, J0, J1, Jn(n,·)`,
  `step(t, a, b)` (transition helper, defined once in docs), standard arithmetic, `pi`. Extendable
  via `docs/` + `validate.py` allow-list (logged change).
- **Aux bindings:** ordered list, evaluated top-down; later expressions may reference earlier aux
  names (e.g. `K = <complex>`, `rho = exp(-K)`, `p = K`).
- **Material coefficients** (term params and `material_fields`) accept expressions in position +
  aux variables exactly like ICs, not only scalars (enables e.g. a resistivity field `eta(r)`).
- **Equilibrium + perturbation:** ICs split into `equilibrium` and `perturbation` with a
  `combine_rule`. Enables the `well-balancing` validation procedure and perturbation-on-equilibrium
  tests.
- **Potentials:** author may define a potential (e.g. `A_z`) + a `derives` rule (`B = curl(A)`);
  the derivation rule is stated, not method-specific.
- Everything must be numpy-evaluable on a coordinate grid; `validate.py` parses and (aux-)resolves
  every expression.

---

## 5. References & hallucination-proof verification (CRITICAL)

**Prime safety rule:** references are never fabricated. A model without internet must never emit a
`verified` citation. Verification is a **script job with internet**, not a model judgement.

### 5.1 Verification model
Each ref carries:
```yaml
verification:
  status: verified | unverified | user-supplied
  identifier: { doi: ... }        # or { arxiv: ... } or { url: ... }
  source: <how it was checked>    # tool / retrieval artifact; empty until checked
  checked: <date | null>
```
- Nothing enters `references[]` (the trusted, indexed list) unless `status: verified`.
- `unverified` / `user-supplied` refs sit in `references_unverified[]`, **excluded from INDEX and
  from any generated paper section**, until upgraded.

### 5.2 Two ingest paths (both safe)

**A. In-repo script gate — `scripts/verify_refs.py` (has internet, authoritative trust boundary):**
- Parse bibtex; every ref must have a resolvable identifier (DOI / arXiv / URL).
- Attempt live resolution → on success set `status: verified`, cache resolved metadata; on failure
  set `unverified`.
- **Hard fail** the build if any ref has `status: verified` with no identifier or an unresolvable
  one. (A verified ref with no resolvable id is a contradiction.)
- `--offline`: skip the live network call (warns, leaves statuses untouched); the script still
  runs and still forbids fabricated `verified`.

**B. No-internet model path (e.g. enterprise Claude Code):**
- The model records refs as `status: unverified` in `references_unverified[]`, **never** `verified`.
- Any DOI/arXiv id is extracted **verbatim from the source document**, treated as a *claim to be
  checked*, not a verification. (A DOI read off a PDF is a claim, not proof.)
- The model additionally emits `tests/<slug>/pending_verification.md` — a fixed-format artifact
  (candidate bibtex + exactly what to confirm) — handed to an internet-capable model or fed to
  `verify_refs.py`.
- Upgrade path: on successful verification, entries move `references_unverified[] → references[]`;
  `reindex.py` regenerates `INDEX.tsv`.

**Skill contract line (verbatim in `/add-test`, `/add-refs`):**
> "If you cannot retrieve a source, you MUST NOT emit a `verified` bibtex entry. Record
> `verification.status: unverified` and write what needs checking. A DOI you read off a PDF is a
> claim to be checked, not a verification. Fabricating a citation is the worst failure mode of this
> repo."

The same no-fabrication discipline applies to **problem parameters defined only by reference**:
record them with a `source_ref` pointer + a `pending_extraction.md` entry (§9.1), never a
value typed from memory.

### 5.3 `reference_results[]`
```yaml
reference_results:
  - key: dahlburg1989              # must be a verified references[] key (online); offline it may
                                   # resolve to references_unverified[] — see §8.3 check 7
    params_used: { gamma: 1.6666666667 }   # only structural params, values as used
    method: "second-order Godunov, unstaggered CT"   # provenance ONLY (never in problem block)
    resolution: "1000x1000"
    amr: "none"
    findings: >
      Specific, quantitative where reported. Numbers verbatim WITH UNITS
      (orders, jump sizes, growth rates, resolution thresholds, timings).
    figure_asset: assets/dahlburg1989-pressure.png    # optional; cited + reproduction described
```

### 5.4 `original_intro`
Per-ref boolean `original_intro`. Default `unknown`. Set only during `/add-refs`, by rule: among
**verified** refs using the test, the earliest publication is `original_intro` — **unless** a ref
states it took the test from elsewhere, in which case follow that attribution. Never guess beyond
this rule.

### 5.5 `/add-refs`
Enriches an existing entry so a paper section is writable: for each verified ref, fills specific
`findings` (with mandatory quantitative numbers where the ref reports them), `params_used`,
`method`, `resolution`. Resolves `original_intro` per §5.4. Runs `verify_refs.py` (or emits
`pending_verification.md` if offline). Also resolves any `pending_extraction.md` parameter whose
defining reference it can retrieve. Never emits "compares with literature".

---

## 6. Validation procedures & scoring

### 6.1 Procedure registry `registry/procedures/<id>.md`
Each: `{ id, human name, applies_to, inputs (slots), steps/formula, output form, pass-criterion }`.
`validation_modes` reference a procedure by id and fill its slots. Registry-backed and extensible
(§7): a mode may not invent an ad-hoc procedure; if none fits, add-test/create-test **proposes** a
new procedure file for review.

**Seed procedures (a seed, not a fixed set):**
- `norms` — L1 / L2 / Linf, **volume-weighted**; on embedded/cut-cell geometry, weighted by active
  volume fraction (documented once).
- `convergence-order` — pairwise `p = log(E_coarse/E_fine)/log(r)` and LSQ log-log slope.
- `exact-solution-compare` — sample exact solution at cell centroids; norm(numeric − exact) per var.
- `self-convergence` — Richardson vs high-resolution reference (ratio stated).
- `rankine-hugoniot-jump` — measured pre/post states vs analytic jump conditions + tolerance.
- `feature-location` — positions of named shocks/contacts along stated cut-lines vs reference +
  tolerance.
- `well-balancing` — init equilibrium, evolve, deviation-norm < tol; + perturbation-preservation.
- `conservation-drift` — total mass / flux vs time. (Universal diagnostic; see §6.4.)
- `div-b` — norm of ∇·B vs criterion. (Universal diagnostic; see §6.4.)

### 6.2 Norm/formula definitions
`docs/` defines norms, convergence-order formulae, and every seed procedure once, so models
reference them and never re-derive.

### 6.3 Scoring rubric (`docs/scoring-rubric.md`) — per validation_mode

| Score | Requires |
|------:|----------|
| **5** | Exact/analytic solution + quantitative convergence to the theoretical order. |
| **4** | No exact solution; community-accepted canonical solution; reliable automatable quantitative check (self-convergence, RH-jump, growth-rate, feature-location). |
| **3** | Quantitative comparison to reference result(s); partial feature coverage. |
| **2** | No automatable check, BUT solution well-characterised (specific named features) and/or widely reproduced across refs — qualitative match is meaningful and specific. |
| **1** | Single result, qualitative, no specific checkable features. |

Rules:
- Headline score = `max(validation_modes[].score)` (set by `reindex.py`).
- Every mode has a `score_justification` string.
- **No proxy is forced.** Use an automatable proxy only if reliable and cheap; otherwise score by
  characterisation quality + reproduction breadth (rows 2/1). Do not use symmetry as a proxy where
  AMR/gridding breaks it.

### 6.3A Differential (baseline) validation modes
A mode may carry an optional `baseline` (a config delta serving as the differential reference); the
`measured` quantity is then the **difference** between the canonical run and the baseline run
(e.g. magnetopause standoff with vs without an inductive core). Scoring reflects the difference
measurement, not either run alone — a controlled quantitative A/B tops at 3 absent an exact
solution. A single run without the comparison being poor is exactly why such a case is **one mode
on one entry**, not two entries.

**Guard (enforced by `validate.py`, §8.3):** a `baseline.config_delta` may alter or zero a term
**only** as the differential reference. The entry's INDEX capability set (terms,
`time_dependent_bc`, `has_internal_boundaries`) is always computed from the **canonical** set,
never the baseline (prevents smuggling a term-toggle into "baseline" to dodge §2.3).

### 6.4 Universal diagnostics (`div-b`, `conservation-drift`)
Present on an entry as a **scored** `validation_mode` **only** when genuinely discriminating for
that problem (the entry must assert *why* it is challenging here vs generic). Otherwise they are
provenance metrics, **unscored**.

---

## 7. Registry & vocabulary extension (anti-drift engine)

### 7.1 Layout
```
registry/
  equations/            # base eqn-set ids. Fluid phase: hydro, mhd, linear-elastic,
                        #   hyperelastic, elastoplastic. Solid / non-convecting phase (v==0,
                        #   requires_eos:false): magnetic-diffusion, perfect-conductor, rigid-body
  terms/                # viscosity, resistivity, heat-conduction, gravity, ...
  eos/                  # gamma-law, stiffened, tabulated
  tabulated-eos/        # canonical named tabulated EoS + provenance + refs (id-referenced)
  bc-types/             # periodic, reflecting, outflow, dirichlet, neumann, perfect-conductor,
                        #   subsonic-inflow, supersonic-inflow, ...   (extensible)
  coord-systems/        # cartesian, cylindrical, spherical, axisymmetric
  internal-boundary-kinds/  # material-contact, free-surface, rigid-wall, perfect-conductor-wall,
                            #   symmetry, electromagnetic-coupling   (physical, never methods)
  analysis-treatments/  # none, oblique-to-grid, axis-singularity, multi-material-interface, ...
  geometry-stress/      # ids for adversarial/stress geometries (searchable tag, §2.3 exception)
  procedures/           # §6.1
```
One markdown file per entry: `{ id, human name, definition, params-schema, notes, refs }`.
Readable, diffable, single-file edits for a Sonnet-class model.

**`base` semantics.** Fluid phase: `hydro` with no terms = Euler; `hydro` + `viscosity`
(+`heat-conduction`) = Navier–Stokes; `mhd` with no terms = ideal MHD; `mhd` + `resistivity` =
resistive MHD; `mhd` + `viscosity` + `resistivity`(+`heat-conduction`) = VRMHD. Terms are
**independent toggles**, each param-bearing when present. Each equation file declares
`requires_eos` (true for fluid bases; false for solid-phase bases).

**Solid / non-convecting phase family.** A different *phase of matter* from the fluid bases; all
have `v ≡ 0`, `requires_eos: false`:
- `magnetic-diffusion` — field diffuses with finite η (`resistivity` coefficient, may be a spatial
  field); evolves only `∂B/∂t = -(1/μ0)∇×(η∇×B)`.
- `perfect-conductor` — infinite conductivity: field frozen, no interior diffusion; a rigid body
  that carries a magnetic field.
- `rigid-body` — non-deforming body with no magnetic-field interaction (inert obstacle).
Each solid-phase file declares `interchangeable_with: [<ids>]` + `interchangeable_when:
"<predicate>"`. `perfect-conductor` and `rigid-body` declare each other interchangeable **when no
coupling magnetic field is present / the body carries no field** — then they are the same
physics_signature element and do not fork; when a field interacts (frozen-flux vs no-interaction)
they differ and fork. The dedup step (§2.4) collapses an interchangeable pair to one signature
element only when the declared predicate holds; ambiguous cases fall to §2.4 step-2.

A prescribed interior field (e.g. a dipole) is stored as the solid-phase material's **initial
condition**, never as a bespoke boundary condition. A conductor embedded in or bounding a plasma
couples via `electromagnetic-coupling` (field continuity across the interface).

### 7.2 Extension = hard-stop-and-propose
When `/add-test` or `/create-test` needs a vocabulary term not in the registry, the skill **STOPS**
and proposes a draft registry file to the user for one-word approval; only after approval is the id
referenced. Never auto-create silently. Same for a needed-but-missing procedure. This is the
*vocabulary* extension mechanism; it does **not** cover missing schema *fields* (see §12).

### 7.3 Aliases
Common informal names (`Euler`, `Navier-Stokes`, `resistive MHD`, `VRMHD`, `θ-pinch`) are resolved
by an alias table inside the `/find-test` skill, mapping phrase → `(base, terms)` signature.
Specs stay canonical; only find-test knows the slang.

---

## 8. Index & validation scripts

### 8.1 `INDEX.tsv` (generated; never hand-edited)
One row per entry. Columns = the filterable subset only:
```
slug \t physics_signature \t terms \t dims \t analysis_treatments \t bc_types_present \t
coupling \t multi_material \t time_dependent_bc \t has_internal_boundaries \t headline_score \t
has_exact_solution
```
Set-valued cells (`terms`, `analysis_treatments`, `bc_types_present`) are pipe-joined.
Grep-cheap and token-economical. Regenerated by `reindex.py`. `time_dependent_bc` and
`has_internal_boundaries` are capability filters used by `/find-test` to exclude methods lacking a
capability (§9.2).

### 8.2 `scripts/reindex.py`
Rebuilds `INDEX.tsv` from all `spec.md`. Recomputes `headline_score = max(modes)` and the
capability flags from the canonical set. The index is a pure derived artifact; source of truth is
the per-test specs.

### 8.3 `scripts/validate.py` (single source of truth for "not a mess")
Checks:
1. Every `spec.md` parses; all required fields present.
2. Every registry id used exists in the registry.
3. Each mode `score` ∈ 1..5; `headline_score == max(modes)`.
4. `INDEX.tsv` in sync (regenerate in-memory, diff, fail on drift), including capability flags.
5. Ref rules: trusted `references[]` all `verified`; `verified` ⇒ resolvable identifier present;
   unverified refs only in `references_unverified[]` and absent from INDEX.
6. IC/BC expression language parses; aux bindings resolve; `units` tags present; any BC state
   referencing `t` ⇒ `time_dependent_bc == true`.
7. `reference_results[].key` (and any `validation_mode.inputs.reference` of `kind: reference`) ∈
   `references[]`; provenance-only fields (method/resolution/amr) never appear in the problem block.
   `--offline` ⇒ these keys may instead resolve to `references_unverified[]`, since offline
   authoring (§5.2B) cannot produce a `verified` ref; the verified-only requirement is enforced
   online (same downgrade principle as check 10).
8. `eos` present iff the material's base declares `requires_eos: true`.
9. `baseline.config_delta` does not change the entry's INDEX capability set (computed from the
   canonical set only).
10. `verified`-ref identifier resolvable (network-dependent). `--offline` ⇒ downgrade this to a
    warning, not a failure.

### 8.4 `scripts/verify_refs.py`
§5.2A. `--offline` supported.

### 8.5 `scripts/new_test.py`
Scaffolds `tests/<slug>/` from `templates/spec.template.md` + empty `assets/`.

All scripts: Python 3, deps `pyyaml`, `bibtexparser`. Runnable by the model (network calls are the
only gated part).

---

## 9. Commands & skills

Commands are thin (`.claude/commands/<n>.md`) and delegate to `skills/<n>/SKILL.md`. Skills
are prescriptive enough for a Sonnet-class model, use copy-and-fill templates, and never rely on
cleverness. One `templates/` dir per authoring skill, copy-and-fill only, no nested logic.

### 9.1 `/add-test <source>`  (PDF | doc | HTML | settings file)
Begins with the **source triage** (`skills/add-test/triage.md`): classify the source as a
benchmark/method paper (normal path) or an application/modeling paper (a driven, observation- or
model-validated scenario whose full spec may require pulling parameters from cited papers). The
application branch harvests in-text quantitatives verbatim, tries the coupled-material
representation before flagging any gap, distinguishes vocabulary gaps (§7.2, self-heal) from schema
gaps (§12, escalate), records reference-defined parameters with `source_ref` + `status:
needs-source` and emits `pending_extraction.md`, and prefers a two-phase `/add-test` then
`/add-refs`.

Procedure:
1. Read + normalize the source into the common problem form (§3). The source PDF/settings file is
   **not** committed; everything is converted to canonical plaintext/structured form. Actively seek
   **quantitative, automatable** validation, not merely qualitative.
2. **Bulk consumption (orchestrator + subagents).** On a **full paper** (many tests), a Sonnet
   orchestrator enumerates the tests and **lets the user pick** (bulk add-all only on explicit
   "all"; 14+ at once on a single Sonnet context is an error risk). To process the picked set the
   orchestrator:
   - builds, **verbatim** (never summarized), a *global-defaults block* — the methods/setup text
     plus every sentence carrying a quantifier (`all / each / every / throughout / unless
     otherwise / in all runs`) — so shared parameters (e.g. a common γ) are never lost in the
     carve;
   - passes each subagent the global-defaults block **plus its per-test verbatim slice** (not the
     whole PDF), and read-only access to the full plaintext so a subagent can **grep on demand**
     when it detects a referenced-but-unsupplied quantity instead of hallucinating;
   - groups tests by logical grouping (same `physics_signature` / siblings together) rather than
     strictly one-per-test, ~3–5 per subagent, capped by count **or** extracted-token budget,
     whichever first; single-test subagents only for unusually heavy tests;
   - resolves **intra-paper** de-dup itself at enumeration (parallel subagents cannot see each
     other's in-flight writes); subagents de-dup only against the existing read-only INDEX;
   - requires each subagent to return `inherited_from_global[]` + `unresolved_references[]` so a
     cross-check flags any value not seen verbatim;
   - **batches** all vocabulary proposals into one hard-stop and all schema gaps into one ledger
     (never interrupt N times);
   - serializes the write side: subagents emit `spec.md` drafts in parallel, then the orchestrator
     runs **one** `reindex.py` + **one** `validate.py` (parallel reindex would race).
3. For each chosen test: run **de-dup** (§2.4). If it exists → record a `reference_result` /
   widen a parameter range and **point the user to the existing entry**; do not duplicate.
4. If new: scaffold, fill `spec.md` from template, add refs via the verification path (§5),
   `reindex.py`, `validate.py`.
5. Hard-stop-and-propose for any missing vocabulary/procedure (§7.2); escalate any schema gap (§12).

### 9.2 `/find-test <natural-language need>`
1. Resolve slang via the alias table; translate the need into structured filters
   (physics signature, terms/capabilities, dims, analysis_treatments, bc types, multi-material,
   `time_dependent_bc`, `has_internal_boundaries`, `geometry_stress`, min score,
   exact-solution required?).
2. Read `INDEX.tsv` first; open `spec.md` only for finalists.
3. Output = **ranked slugs + one-line why-match + headline score**, and — as a first-class result —
   **coverage gaps**.
4. Suite queries → return an **ordered suite + a coverage table + explicit holes**. Capability
   filter uses presence (§2.3): e.g. "method has no heat-conduction" ⇒ exclude entries whose
   required terms ⊄ the method's capabilities; "method has no time-dependent BCs" ⇒ exclude
   `time_dependent_bc` entries.

### 9.3 `/create-test <description>`  (e.g. rotated Sod in embedded rectangle)
1. Run **de-dup first** (§2.4). If it matches an existing entry → refuse to create and point to it.
2. Emit a `spec.md` with `provenance: synthesized`.
3. **Must** populate `validation_modes[]` + score(s): a spec with no validation path is rejected.
4. May emit `tests/<slug>/pending_derivation.md` — a fixed-format request for a stronger model to
   attempt an exact/analytic solution. Until then the test carries its **provisional (low) score**.
5. Hard-stop-and-propose for missing vocabulary (§7.2); escalate any schema gap (§12).

### 9.4 `/add-refs <slug>`
§5.5.

### 9.5 Support skills
`dedup`, `problem-authoring`, `validation-authoring`, `vocab-extension` (shared procedures pulled
in by the command skills).

---

## 10. Repository layout

```
INDEX.tsv                              # generated; never hand-edited
README.md
SPEC.md
registry/
  equations/*.md
  terms/*.md
  eos/*.md
  tabulated-eos/*.md
  bc-types/*.md
  coord-systems/*.md
  internal-boundary-kinds/*.md
  analysis-treatments/*.md
  geometry-stress/*.md
  procedures/*.md
tests/
  <slug>/
    spec.md
    assets/                            # cited + reproduction-described reference figures
    pending_verification.md            # only when offline refs await verification
    pending_extraction.md              # only when problem params are defined-by-reference
    pending_derivation.md              # only when a synthesized test awaits analytic derivation
skills/
  add-test/{SKILL.md, triage.md, templates/}
  find-test/{SKILL.md}                 # holds the alias table
  create-test/{SKILL.md, templates/}
  add-refs/{SKILL.md, templates/}
  dedup/SKILL.md
  problem-authoring/{SKILL.md, templates/}
  validation-authoring/{SKILL.md, templates/}
  vocab-extension/{SKILL.md, templates/}
.claude/commands/
  add-test.md  find-test.md  create-test.md  add-refs.md
scripts/
  validate.py  reindex.py  verify_refs.py  new_test.py
docs/
  spec-schema.md                       # the schema (§3), authoritative field reference
  ic-expression-language.md            # §4
  scoring-rubric.md                    # §6.3
  procedures.md                        # norm/formula definitions (§6.2)
  conventions.md                       # units canonical convention, naming, style
templates/
  spec.template.md
  pending_verification.template.md
  pending_extraction.template.md
  pending_derivation.template.md
  registry-term.template.md
  procedure.template.md
```

---

## 11. Invariants (must always hold; enforced by `validate.py` where mechanical)

1. Problem block never names a numerical method, resolution, AMR setting, or grid type.
2. Every enum value is a registry id; unknown id ⇒ validation failure.
3. Vocabulary grows only by hard-stop-and-propose, never silently.
4. `INDEX.tsv` is generated; a stale index fails validation.
5. No `verified` reference without a resolvable identifier; no fabricated references, ever;
   offline models emit `unverified` + a `pending_verification.md`. Problem parameters defined only
   by reference are `needs-source`, never typed from memory.
6. Every entry has ≥1 `validation_mode`; every mode has a specific `purpose`
   (never "compare with literature") and a `score` with justification.
7. Entry identity is structural + value-blind, except **capability presence** (§2.3).
8. Headline score = max over modes.
9. `spec.md` is one file, template-derived, fixed section order.
10. Quantitative findings are recorded verbatim with units wherever a reference reports them.
11. `eos` present iff the material's base declares `requires_eos: true`.
12. The only value-based identity forks are capability-presence flags: term presence,
    `time_dependent_bc`, `has_internal_boundaries` (all binary). Form (BC-state function, internal
    geometry) never forks.
13. A `baseline.config_delta` never alters the entry's INDEX capability set (computed from the
    canonical set only).

(Minimal-material canonicalization is a **dedup convention**, §2.4, not a §11 invariant: it is not
mechanically checkable.)

---

## 12. Deferred / explicitly out of scope (this build)

- `polyhedron` geometry primitive (3D) — noted, not yet specified.
- Automated conversion between unit systems — deliberately excluded (conversion = error risk;
  store as authored, tag conventions, dedup on the canonical signature).
- Any GUI / web surface.
- Running the physics codes.
- An internal or boundary condition **not derivable from an equation evolved in the domain** (an
  externally imposed condition with no backing evolved equation) — out of scope for now. A
  condition that *is* so derivable is represented as a material with its own equation set + IC +
  interface coupling (never a bespoke BC). This is the fence between "represent it as coupled
  physics" and "genuine schema extension required." Schema *field* additions (as opposed to
  *vocabulary*, §7.2) are not self-healing and require re-grilling.
- **TODO: `related_to` auto-linking for capability siblings.** When a capability-presence fork
  spawns sibling entries (steady vs `time_dependent_bc`; with vs without a term; internal-boundary
  present vs absent; interchangeable-vs-forked solid-phase base), `/add-test` and `/create-test`
  should emit reciprocal `related_to` links automatically, and `/find-test` should surface the
  sibling set. Rule to specify: on entry creation, query INDEX for rows identical in every identity
  component **except one** capability flag, and link those. Not built this build.
