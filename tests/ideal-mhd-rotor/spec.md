---
# Authored via /add-test (NORMAL path) from Dematté, Farmakalides, Millmore & Nikiforakis,
# "An all Mach number scheme for visco-resistive magnetically-dominated MHD flows", JCP 514
# (2024) 113229 (citekey: dematte2024), Sect. 4.1.4 "Ideal MHD rotor problem". The test itself
# is stated to originate with Balsara & Spicer [47] (test_origin below, status: pending --
# unresolved by this pass, per /add-test contract; a later /add-refs pass resolves the
# originating reference).

slug: ideal-mhd-rotor
name: "Ideal MHD Rotor Problem (Balsara & Spicer)"
provenance: literature
one_liner: "Rapidly rotating dense cylinder of fluid embedded in a uniform ambient plasma and magnetic field, launching strong torsional Alfven waves -- a classic stress test for div-B control under a steep density/velocity gradient."

physics:
  materials:
    - name: plasma
      base: mhd
      terms: []
      eos:
        type: gamma-law
        params: { gamma: 1.6666666666666667 }   # gamma = 5/3, global default ("unless otherwise stated"); not restated for this test
  coupling: none

dimension:
  intrinsic: 2
  runnable_in: [2]

analysis_treatments: [none]

capability_flags:
  time_dependent_bc: false
  has_internal_boundaries: false   # the rotor/transition/ambient split is a piecewise IC on ONE material, not a physical interface
geometry_stress: none

geometry:
  coord_system: cartesian
  domain: { x: [0, 1], y: [0, 1] }
  regions:
    - id: whole
      shape: box
      params: { x: [0, 1], y: [0, 1] }

units:
  system: nondimensional       # bare numbers as authored, not named by the source
  b_field_convention: permeability-unity   # global (Sect. 2): "the units of B are chosen such that the vacuum magnetic permeability is unity"

initial_conditions:
  aux:
    - { name: r, expr: "sqrt((x-0.5)**2 + (y-0.5)**2)" }
    - { name: u_r, expr: "5 - 10*y" }
    - { name: v_r, expr: "10*x - 5" }
    - { name: f_r, expr: "(23 - 200*r)/3" }
    - { name: H1, expr: "step(r, 0.1, 0.1)" }     # Heaviside at r=0.1: 0 for r<0.1 (rotor core), 1 for r>=0.1
    - { name: H2, expr: "step(r, 0.115, 0.115)" } # Heaviside at r=0.115: 0 for r<0.115 (transition), 1 for r>=0.115 (ambient)
    - { name: core, expr: "1 - H1" }
    - { name: trans, expr: "H1*(1 - H2)" }
    - { name: outer, expr: "H2" }
  equilibrium:
    - region: whole
      fields:
        rho: "10.0*core + (1.0 + 9.0*f_r)*trans + 1.0*outer"
        vx: "u_r*core + u_r*f_r*trans + 0.0*outer"
        vy: "v_r*core + v_r*f_r*trans + 0.0*outer"
        vz: "0.0"
        Bx: "2.5/sqrt(4*pi)"
        By: "0.0"
        Bz: "0.0"
        p: "1.0"
  perturbation:
    combine_rule: additive
    fields: []
  potentials: []

parameters:
  - { name: gamma, canonical: 1.6666666666666667, meaning: "ratio of specific heats (= 5/3), global default" }
  - { name: rotor_radius, canonical: 0.1, meaning: "radius of the rigidly-rotating dense core disk" }
  - { name: transition_radius, canonical: 0.115, meaning: "outer radius of the smeared (tapered) transition annulus" }
  - { name: B0x, canonical: 1.4104739588693907, meaning: "uniform background Bx = 2.5/sqrt(4*pi)" }

domain_bc:
  # NOT stated explicitly in Sect. 4.1.4 for this test (unlike some other Sect. 4 tests, e.g.
  # the shear-layer/current-sheet tests, which do state their BCs). Inferred as outflow/
  # zero-gradient -- standard practice for this benchmark since the Alfven fronts have not
  # reached the domain edge by t_final=0.25 -- and flagged needs-source in
  # pending_extraction.md pending confirmation against the retrievable Balsara & Spicer source.
  x_lo: { type: outflow }
  x_hi: { type: outflow }
  y_lo: { type: outflow }
  y_hi: { type: outflow }

internal_boundaries: []

time:
  t_final: 0.25
  snapshot_times: [0.25]

validation_modes:
  - id: div-b-machine-precision
    purpose: "Verify the magnetic-field divergence-free constraint is maintained to (near-)machine precision throughout the strong Alfven-wave-launching evolution driven by the rotor's steep density/velocity gradient."
    procedure: div-b
    inputs:
      at_time: 0.25
      variables: [B]
      tolerance: "||div B||_L2 remains bounded, ranging ~1e-16 to ~1e-12 over t in [0,0.25], sampled every 10 time-steps (Fig. 8), for both staggered and unstaggered CT adaptations"
      reference: { kind: reference-result, key: dematte2024 }
    has_exact_solution: false
    score: 3
    score_justification: "Universal div-B diagnostic, scored here because the rotor's rapid rotation and steep central density/velocity gradient launching strong torsional Alfven waves is a well-known div-B stress case for CT-type schemes; the source reports an explicit quantitative bound (~1e-16 to ~1e-12) rather than an unscored provenance note -- capped at row 3 per the universal-diagnostic rule (not an exact-solution or literature-value comparison)."

  - id: pressure-density-contour-comparison
    purpose: "Characterize the density, gas-pressure, and magnetic-pressure contour patterns and the diagonal 1D pressure cross-section at t=0.25 against the reference simulation and the wider rotor-benchmark literature, as no exact solution exists for this problem."
    procedure: feature-location
    inputs:
      at_time: 0.25
      variables: [rho, p, Bmag]
      cut_lines: [{ from: [0, 0], to: [1, 1] }]
      reference: { kind: reference-result, key: dematte2024 }
      tolerance: "qualitative visual match to the contour patterns (50 equidistant contour lines, Figs. 6-7) and the diagonal pressure cross-section (Fig. 6 bottom-right); no numeric feature-location values stated in source"
    has_exact_solution: false
    score: 2
    score_justification: "No automatable numeric check stated (only 'good agreement is observed with... Balsara and Spicer [47]'), but the solution is well-characterised by specific named features (density/pressure/magnetic-pressure contour shapes, diagonal pressure profile) and this is a widely-reproduced canonical MHD benchmark -- rubric row 2."

references:
  - key: dematte2024
    original_intro: false
    verification:
      status: verified
      identifier: { doi: "10.1016/j.jcp.2024.113229" }
      source: "crossref: 10.1016/j.jcp.2024.113229 -> 200"
      checked: "2026-07-28"
      meta:
        year: 2024
        first_author: Dematté
        container: Journal of Computational Physics
        title: "An all Mach number scheme for visco-resistive magnetically-dominated MHD flows"
references_unverified: []
test_origin:
  # dematte2024 states this test "was originally proposed by Balsara and Spicer [47]" -- the
  # originating reference is NOT itself in references[] above (no DOI/arXiv id was located for
  # it in this pass; ref [47] is not resolved to a specific Balsara & Spicer paper here). Per
  # the /add-test contract, original_intro resolution is left to a later /add-refs pass; status
  # stays `pending` rather than guessed.
  status: pending
  authored_from: dematte2024
  attribution_claims:
    - stated_by: dematte2024
      quote: "the MHD rotor test which was originally proposed by Balsara and Spicer [47]"
reference_results:
  - key: dematte2024
    params_used: { domain: "[0,1]x[0,1]", t_final: 0.25, CT: "staggered (Fig 6) and unstaggered (Fig 7) adaptations both run" }
    method: "proposed semi-implicit FVS scheme; CFL=0.8; advective-eigenvalue timestep; GMRES tol 1e-15; Picard R=Q=S=2, sigma=1e-12 (all global defaults, not restated per-test)"
    resolution: "800x800 uniform Cartesian cells"
    amr: "none"
    findings: >
      Figs. 6-7: density, gas pressure, and magnetic pressure contours (50 equidistant lines) at
      t=0.25 for both staggered and unstaggered CT, plus a 1D diagonal pressure cross-section
      (Fig. 6 bottom-right); Fig. 8: ||div B||_L2 sampled every 10 time-steps, bounded ~1e-16 to
      ~1e-12 over t in [0,0.25] for both CT adaptations. "Good agreement is observed with
      numerical results published in the literature, see for example Balsara and Spicer [47]."
related_to: []
headline_score: 3
---

## Physical problem
A rapidly rotating, dense circular fluid region (the rotor) is embedded at the centre of a
square domain in a uniform ambient fluid, with a uniform pressure and magnetic field
(Bx=2.5/sqrt(4*pi)) filling the entire domain at t=0. The rotor spins with a linear (rigid-body)
velocity profile inside r<=0.1; density and toroidal velocity are smeared across a thin
transition annulus (0.1<r<=0.115) via a linear taper function to avoid start-up transients; the
ambient fluid (r>0.115) is at rest. The rapid rotation launches strong torsional Alfven waves
into the ambient plasma.

## What this test actually tests
(1) Whether the scheme maintains the divergence-free magnetic-field constraint to (near-)machine
precision under the strong Alfven-wave-launching, steep-gradient dynamics driven by the rotor
(div-b mode). (2) Whether the resulting density/pressure/magnetic-pressure field patterns and
diagonal pressure profile at t=0.25 qualitatively match the canonical rotor-benchmark literature
(feature-location mode).

## Qualitative behaviour
Strong torsional Alfven fronts propagate outward from the rotor into the ambient fluid; the
central dense core distorts under its own rotation and the confining magnetic tension. The
diagonal pressure cross-section develops the characteristic multi-peaked structure reported for
this benchmark (Fig. 6 bottom-right). No exact solution exists; comparison is by qualitative
pattern match against the literature.

## Validation notes
The div-B mode's tolerance (~1e-16 to ~1e-12, Fig. 8) is the one quantitative anchor in this
entry and is recorded verbatim from the source with units (dimensionless, as authored). The
feature-location mode carries no stated numeric tolerance -- the source's own validation is the
qualitative statement "good agreement is observed... see for example Balsara and Spicer [47]" --
so it is capped at rubric row 2 rather than inflated by prose richness.

## Notes
Domain boundary conditions are NOT stated explicitly for this test in Sect. 4.1.4; `outflow` is
recorded as an inferred convention (see `domain_bc` comment) and flagged needs-source in
`pending_extraction.md`. The piecewise IC (core/transition/ambient) is encoded here via
Heaviside-style `step(r,a,a)` indicator products rather than as separate `regions`, since it is a
single-material piecewise field, not a physical interface (`has_internal_boundaries: false`).
