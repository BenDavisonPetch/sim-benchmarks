---
# Copy-and-fill entry scaffold (SPEC §3; docs/spec-schema.md is the authoritative field
# reference). One file per test at tests/<slug>/spec.md. Frontmatter = all structured /
# filterable fields; body = prose in the FIXED section order below (SPEC §11.9).
# Authoring skills copy this file and fill it — never freehand. Delete guidance comments
# and every unused OPTIONAL field before committing. R = required, O = optional.

slug: <kebab-case-slug>              # R; == directory name tests/<slug>/ (conventions §3)
name: "<Canonical Display Name>"     # R
provenance: literature               # R; literature | synthesized (synthesized = /create-test)
one_liner: "<one-sentence summary>"  # R; shown in /find-test output

physics:                             # R
  materials:                         # R; >=1 element (single-material tests use a 1-list)
    - name: <material>               # R; local label referenced by regions / material_fields
      base: <equation-id>            # R; registry/equations id
      terms: []                      # R; registry/terms ids present (nonzero). [] = no terms.
      eos:                           # present IFF base declares requires_eos: true (check 8)
        type: <eos-id>               #   registry/eos id
        params: { }                  #   per the eos file's params-schema
      material_fields: []            # O; named spatial coefficients as expressions (§4):
                                     #   - { name: eta, region: <id>, expr: "...", units: "..." }
  coupling: none                     # R; registry/internal-boundary-kinds id, or 'none'

dimension:                           # R
  intrinsic: <int>                   # R; smallest dimension the problem is defined in
  runnable_in: [<int>]               # R; dims requiring no new analysis (inert extra dims listed)

analysis_treatments: [none]          # R; registry/analysis-treatments ids (set); [none] if plain

capability_flags:                    # R; BINARY, computed from the CANONICAL set (§2.3)
  time_dependent_bc: false           # R; true iff any domain_bc[*].state references t (check 6)
  has_internal_boundaries: false     # R; true iff coupling != none, >1 material, or internal_boundaries
geometry_stress: none                # R; registry/geometry-stress id, or 'none' (searchable tag)

geometry:                            # R
  coord_system: cartesian            # R; registry/coord-systems id (physical frame, NOT a grid)
  domain: { }                        # R; per-axis extents, e.g. { x: [0,1], y: [0,1] }
  regions:                           # R; analytic predicate primitives + transforms
    - id: whole                      #   primitives: box, cylinder, sphere,
      shape: box                     #     shell{center, r:[r_inner,r_outer]}, halfspace, polygon{vertices}
      params: { }                    #   transforms: rotate{deg, about}, translate{by}

units:                               # R; STORED AS AUTHORED — never auto-converted (§12)
  system: code                       # R; cgs-gaussian | si | code | nondimensional | ...
  b_field_convention: null           # R (key present); permeability-unity | sqrt-4pi | ... | null
                                     #   null only with a needs-source row in pending_extraction.md

initial_conditions:                  # R; grammar in docs/ic-expression-language.md
  aux: []                            # O; ordered { name, expr, units? }, evaluated top-down
  equilibrium:                       # R; base state (may be trivial). Enables well-balancing.
    - region: whole
      fields: { }                    #   { var: "expr" } — numpy-evaluable expressions (§4)
  perturbation:                      # R
    combine_rule: additive           #   additive | replace
    fields: []                       #   [] if none
  potentials: []                     # O; { name, expr, derives: "B = curl(A)" }

parameters:                          # R (may be []); values only, never identity (§2.2)
  - { name: <name>, canonical: <value>, meaning: "<meaning with units>" }
  # canonical: null ONLY with notes: needs-source + a pending_extraction.md row (§5.2)
  # optional source_ref: <verified references[] key defining the value>

domain_bc: { }                       # R; PER FACE {type, state?}. registry/bc-types ids.
  # x_lo: { type: periodic }
  # x_hi: { type: supersonic-inflow, state: { rho: "40 + 40*step(t,0,30)", vx: "..." } }
  #   a face whose state references t sets capability_flags.time_dependent_bc = true
  # 3D adds z_lo, z_hi

internal_boundaries: []              # R (may be []); physical only (§1.6). Each: kind + geometry + motion.

time:                                # R
  t_final: <number>                  # R; run-to time so EVERY mode can be evaluated
  snapshot_times: []                 # O; qualitative

validation_modes:                    # R; >=1. Each independently scored (§6.3, scoring-rubric.md).
  - id: <mode-id>                    # R; unique within the entry
    purpose: "<SPECIFIC capability>" # R; NEVER "compare with literature" (§11.6)
    procedure: <procedure-id>        # R; registry/procedures id; fills its slots
    inputs:                          # R; the procedure's slot fills
      at_time: <t <= t_final>
      variables: []
      reference: { kind: reference-result, key: <key> }   # kind: reference | reference-result
      tolerance: "<tolerance>"
    has_exact_solution: false        # R
    score: <1..5>                    # R; see scoring-rubric.md
    score_justification: "<why this row>"   # R
    # optional differential (A/B) mode (§6.3A) — config_delta must NOT change the capability set:
    # baseline: { description: "...", config_delta: { "aux.<name>": "<value>" } }
    # measured: "<the difference being measured>"

references: []                       # R (may be []); verified refs only (status: verified, §5.1)
  # ref shape (§5.1): key + optional original_intro (set ONLY by /add-refs, §5.4) + verification;
  # `meta` is resolver output pasted from `verify_refs.py --meta` — NEVER typed from memory:
  # - key: <citekey>
  #   original_intro: true
  #   verification:
  #     status: verified
  #     identifier: { doi: "<10.x/y>", arxiv: "<id>" }   # record BOTH when both exist
  #     source: "crossref: <doi> -> 200"
  #     checked: "<YYYY-MM-DD>"
  #     meta: { year: <YYYY>, first_author: <Surname>, container: "<journal>", title: "<title>" }
references_unverified: []            # R (may be []); quarantined (unverified | user-supplied)
# test_origin: entry-level attribution (§5.4). /add-test fills authored_from + attribution_claims[];
# only /add-refs resolves `status`/`ref`/`external`. `pending` is a correct answer; a guess is not.
# test_origin:
#   status: pending                  # resolved-in-list | resolved-external | pending | synthesized
#   ref: <the original_intro: true key>          # iff resolved-in-list
#   authored_from: <ref this entry was ingested from>
#   external: { author: <Surname>, year: <YYYY>, doi: "<10.x/y>" }   # iff resolved-external
#   derived_from: <ref>              # optional, synthesized entries
#   attribution_claims:
#     - stated_by: <citekey>
#       quote: "<VERBATIM sentence stating where the test came from>"
reference_results: []                # R (may be []); what a specific ref DID (§5.3); key in references[]
related_to: []                       # R (may be []); sibling slugs (§2.3 forks)
headline_score: 0                    # R; = max(validation_modes[].score); set by reindex.py (§8.2)
---

## Physical problem
<What is physically happening. Problem ONLY — no numerical method, resolution, AMR, or grid (§1.6).>

## What this test actually tests
<The specific capability(ies). NEVER "compare with literature".>

## Qualitative behaviour
<Used where no exact solution: SPECIFIC named features ("fast shock reaches x≈…, contact at …").
 Note known traps, e.g. AMR gridding breaks IC symmetry — do not use symmetry as a proxy there.>

## Validation notes
<Per-mode elaboration, expected convergence orders, known reference values WITH units.>

## Notes
<Edge cases, gotchas, unit-convention warnings.>
