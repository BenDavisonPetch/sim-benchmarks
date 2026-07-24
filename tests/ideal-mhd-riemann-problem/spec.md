---
# Authored via /add-test (NORMAL path) from Dematté, Farmakalides, Millmore & Nikiforakis,
# "An all Mach number scheme for visco-resistive magnetically-dominated MHD flows", JCP 514
# (2024) 113229 (citekey: dematte2024). Section 4.1.1 "Riemann problem tests".
#
# INTRA-PAPER DEDUP (orchestrator, SPEC 9.1 step 2d): the source names four Riemann problems
# (RP1-RP4). All four share an IDENTICAL structural form (two constant states W_L, W_R
# separated by a single discontinuity at x=x0, on domain [0,1], ideal MHD, gamma-law EoS,
# no terms) and differ ONLY in the numeric state values, x0, and output time (dedup 2.1
# item 3: parameter values never enter identity). Per the dedup worked-case precedent ("2D
# Sod at 30 vs 45 -> existing entry; parameter; two reference_results"), RP1-RP4 fold into
# ONE canonical entry. RP1 (Brio & Wu) is authored as the canonical numeric preset; RP2-4
# are recorded as additional reference_results (params_used) on this same paper.

slug: ideal-mhd-riemann-problem
name: "1D Ideal MHD Riemann Problem (Shock-Tube Family)"
provenance: literature
one_liner: "1D ideal-MHD Riemann problem: two constant states separated by a discontinuity; canonical preset is the Brio-Wu shock tube (RP1), with RP2 (Ryu-Jones seven-wave), RP3, RP4 as parameter presets on the same entry."

physics:
  materials:
    - name: plasma
      base: mhd
      terms: []
      eos:
        type: gamma-law
        params: { gamma: 1.6666666666666667 }   # gamma = 5/3, global default ("unless otherwise stated"), stated-here
  coupling: none

dimension:
  intrinsic: 1
  runnable_in: [1]

analysis_treatments: [none]

capability_flags:
  time_dependent_bc: false
  has_internal_boundaries: false
geometry_stress: none

geometry:
  coord_system: cartesian
  domain: { x: [0, 1] }
  regions:
    - id: left
      shape: box
      params: { x: [0, x0] }
    - id: right
      shape: box
      params: { x: [x0, 1] }

units:
  system: nondimensional      # not named by the source; values given as bare numbers (standard shock-tube convention)
  b_field_convention: permeability-unity   # stated-here, global (Sect. 2): "the units of B are chosen such that the vacuum magnetic permeability is unity"

initial_conditions:
  aux:
    - { name: x0, expr: "0.5" }   # RP1 (Brio-Wu, canonical preset); RP4 uses x0=0.4 (see reference_results)
  equilibrium:
    - region: left
      fields: { rho: "1.0", vx: "0.0", vy: "0.0", vz: "0.0", Bx: "0.75", By: "1.0", Bz: "0.0", p: "1.0" }
    - region: right
      fields: { rho: "0.125", vx: "0.0", vy: "0.0", vz: "0.0", Bx: "0.75", By: "-1.0", Bz: "0.0", p: "0.1" }
  perturbation:
    combine_rule: additive
    fields: []
  potentials: []

parameters:
  - { name: gamma, canonical: 1.6666666666666667, meaning: "ratio of specific heats (= 5/3), global default 'unless otherwise stated'" }
  - { name: x0, canonical: 0.5, meaning: "initial discontinuity location (RP1-3); RP4 uses x0=0.4" }
  - { name: rho_L, canonical: 1.0, meaning: "left-state density (RP1/Brio-Wu)" }
  - { name: rho_R, canonical: 0.125, meaning: "right-state density (RP1/Brio-Wu)" }
  - { name: Bx_shared, canonical: 0.75, meaning: "normal B-field component, uniform L/R (RP1/Brio-Wu; div-B compatibility)" }
  - { name: By_L, canonical: 1.0, meaning: "left-state tangential B_y (RP1/Brio-Wu)" }
  - { name: By_R, canonical: -1.0, meaning: "right-state tangential B_y (RP1/Brio-Wu)" }
  - { name: p_L, canonical: 1.0, meaning: "left-state gas pressure (RP1/Brio-Wu)" }
  - { name: p_R, canonical: 0.1, meaning: "right-state gas pressure (RP1/Brio-Wu)" }

domain_bc:
  # NOT explicitly stated in Sect. 4.1.1 (unlike the shear-layer/current-sheet tests, which do
  # state "transmissive... x-direction"). Inferred as outflow/zero-gradient, standard practice
  # for a shock tube whose waves do not reach the domain boundary by t_final; flagged in
  # pending_extraction.md as a convention needing confirmation against the Brio & Wu (1988) /
  # Ryu & Jones (1995) primary sources.
  x_lo: { type: outflow }
  x_hi: { type: outflow }

internal_boundaries: []

time:
  t_final: 0.1     # RP1 T_out; RP2=0.2, RP3=0.15, RP4=0.16 (see reference_results)
  snapshot_times: []

validation_modes:
  - id: rh-jump-shocks
    purpose: "Verify measured pre/post-shock jumps across the MHD shocks and discontinuities against the analytic Rankine-Hugoniot jump conditions for the ideal MHD system, for each named Riemann preset (RP1-RP4)."
    procedure: rankine-hugoniot-jump
    inputs:
      at_time: 0.1
      variables: [rho, vx, vy, Bx, By, p]
      tolerance: "measured jump within a few percent of the analytic MHD RH relations (grid-resolution dependent)"
    has_exact_solution: false
    score: 4
    score_justification: "No exact full-profile solution, but the MHD Rankine-Hugoniot jump conditions are analytic and give a reliable, automatable, resolution-independent check (rubric row 4); this is a community-canonical benchmark family (Brio & Wu; Ryu & Jones; Dumbser et al.; Fambri)."

  - id: profile-vs-high-res-reference
    purpose: "Compare density and B_y profiles at the stated output time against the paper's own high-resolution reference solution, for each Riemann preset."
    procedure: norms
    inputs:
      at_time: 0.1
      variables: [rho, By]
      reference: { kind: reference-result, key: dematte2024 }
      tolerance: "visual/qualitative agreement as reported (Fig. 2); no numeric tolerance stated in source"
    has_exact_solution: false
    score: 3
    score_justification: "Quantitative reference profile exists (paper's own high-resolution MUSCL/HLLC run) but comparison as reported is visual, not a stated numeric norm; tops at 3 (rubric)."

references: []
references_unverified:
  - key: dematte2024
    verification: { status: unverified, identifier: { doi: "10.1016/j.jcp.2024.113229" }, source: "", checked: null }
  - key: brio1988
    verification: { status: unverified, identifier: {}, source: "", checked: null }
  - key: ryujones1995
    verification: { status: unverified, identifier: {}, source: "", checked: null }
  - key: dumbser2024vrmhd
    verification: { status: unverified, identifier: {}, source: "", checked: null }
  - key: fambri2023
    verification: { status: unverified, identifier: {}, source: "", checked: null }
reference_results:
  - key: dematte2024
    params_used: { preset: "RP1 (Brio-Wu)", x0: 0.5, rho_L: 1.0, rho_R: 0.125, Bx: 0.75, By_L: 1.0, By_R: -1.0, p_L: 1.0, p_R: 0.1, t_final: 0.1 }
    method: "proposed semi-implicit FVS scheme (Rusanov advective flux, nested-Picard implicit pressure sub-system); staggered CT for div-B; MUSCL-Hancock TVD 2nd-order reconstruction"
    resolution: "1000 cells on [0,1]"
    amr: "none"
    findings: >
      Good agreement with a high-resolution reference (2nd-order MUSCL-type TVD scheme with the
      HLLC Riemann solver), for both a purely-advective and an Alfvenic time step; artificial
      compound wave in the density profile is present, consistent with standard finite-volume MHD
      schemes in the literature.
  - key: dematte2024
    params_used: { preset: "RP2 (Ryu-Jones seven-wave)", x0: 0.5, rho_L: 1.08, rho_R: 0.9891, vx_L: 1.2, vx_R: -0.0131, vy_L: 0.01, vy_R: 0.0269, vz_L: 0.5, vz_R: 0.010037, Bx: 0.564190, By_L: 1.015541, By_R: 1.135262, Bz_L: 0.564190, Bz_R: 0.564923, p_L: 0.95, p_R: 0.97159, t_final: 0.2 }
    method: "same as RP1 entry above"
    resolution: "1000 cells on [0,1]"
    amr: "none"
    findings: "Good agreement with high-resolution reference; wave pattern correctly reproduced."
  - key: dematte2024
    params_used: { preset: "RP3", x0: 0.5, rho_L: 1.7, rho_R: 0.2, vz_R: -1.496891, Bx: 1.1, By_L: 1.0, By_R: 0.785887, Bz_R: 0.618370, p_L: 1.7, p_R: 0.2, t_final: 0.15 }
    method: "same as RP1 entry above"
    resolution: "1000 cells on [0,1]"
    amr: "none"
    findings: "Purely-advective dt less accurate than Alfvenic dt due to lower time resolution; re-run at multiple CFL numbers (Fig. 3) shows accuracy improves as CFL (and dt) decreases."
  - key: dematte2024
    params_used: { preset: "RP4", x0: 0.4, rho_L: 1.0, rho_R: 0.4, Bx: 1.3, By_L: 1.0, By_R: -1.0, p_L: 1.0, p_R: 0.4, t_final: 0.16 }
    method: "same as RP1 entry above"
    resolution: "1000 cells on [0,1]"
    amr: "none"
    findings: "Purely-advective dt less accurate than Alfvenic dt (same effect as RP3); re-run at multiple CFL numbers (Fig. 3)."
related_to: []
headline_score: 4
---

## Physical problem
A 1D ideal-MHD Riemann problem: two uniform constant states (density, velocity, magnetic field,
gas pressure) separated by a single discontinuity at x=x0 on the domain [0,1], evolved under the
ideal MHD equations with an ideal-gas EoS. The canonical numeric preset (RP1) is the classical
Brio-Wu shock tube; RP2-RP4 are alternate presets of the same structural problem.

## What this test actually tests
Shock-capturing and wave-pattern fidelity of a numerical MHD scheme across the seven ideal-MHD
wave families (fast/slow shocks, rotational discontinuities, contact, entropy wave), including
correct reproduction of the artificial compound wave known to appear in RP1's density profile.

## Qualitative behaviour
RP1 (Brio-Wu): fast rarefaction, compound wave, contact discontinuity, slow shock, fast
rarefaction (left to right); a numerically-generated compound wave is a known, expected feature
in the density profile of standard finite-volume MHD schemes. RP2-RP4: analogous multi-wave
structures at their respective states (see reference_results for each preset's findings).

## Validation notes
RH-jump conditions provide a resolution-independent, analytic check across all four presets.
The paper's own comparison (Fig. 2/3) is against a high-resolution reference solution (its own
explicit HLLC run), not an exact solution — this caps the reference-comparison mode at score 3,
while the RH-jump mode (analytic conditions) reaches score 4.

## Notes
domain_bc type (outflow) is an inferred convention, not explicitly stated for this subsection —
see pending_extraction.md. Bx is uniform across the discontinuity in every preset (required for
div-B compatibility of a 1D normal field). Units are stored as authored (bare, nondimensional
numbers); b_field_convention (permeability-unity) IS stated in the source (Sect. 2), so is not a
needs-source item.
