---
# Authored via /add-test (NORMAL path) from Dematté, Farmakalides, Millmore & Nikiforakis,
# "An all Mach number scheme for visco-resistive magnetically-dominated MHD flows", JCP 514
# (2024) 113229 (citekey: dematte2024). Section 4.3.2 "Kelvin-Helmholtz instability", the IDEAL
# (eta=mu=0) re-run of the same IC, used to check discrete conservation of magnetic/cross
# helicity and div-B control.
#
# INTRA-PAPER DEDUP: see `kelvin-helmholtz-instability-vrmhd`'s header comment for the full
# reasoning. Same IC/geometry as that entry (source, verbatim: "we re-run the Kelvin-Helmholtz
# instability with the same initial condition as given in equation (68), but now with
# eta=mu=0"), but the resistivity/viscosity terms are absent here (a term-presence fork per the
# dedup skill's own worked case: "Inviscid KH vs visco-resistive KH -> NEW SIBLING"). Kept as a
# separate NEW-SIBLING entry, cross-linked via `related_to`, because the validation target is
# categorically different: this entry is not about dissipative accuracy but about whether an
# ideal-MHD discretisation spuriously creates/destroys magnetic helicity, cross helicity, and
# div-B in a genuinely turbulent (fully rolled-up, high-resolution) flow -- a question that is
# only meaningful for the non-dissipative (ideal) system.

slug: kelvin-helmholtz-instability-ideal-mhd
name: "Ideal-MHD Kelvin-Helmholtz Instability (Helicity/Div-B Conservation)"
provenance: literature
one_liner: "Ideal-MHD (eta=mu=0) re-run of the visco-resistive KH instability's IC, used to check discrete conservation of magnetic helicity and cross helicity and control of div-B in a turbulent flow, against an explicit reference scheme."

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
  has_internal_boundaries: false
geometry_stress: none

geometry:
  coord_system: cartesian
  domain: { x: [0, 2], y: [-1, 1] }
  regions:
    - id: inner
      shape: box
      params: { x: [0, 2], y: [-0.46, 0.46] }
    - id: mid_top
      shape: box
      params: { x: [0, 2], y: [0.46, 0.54] }
    - id: mid_bottom
      shape: box
      params: { x: [0, 2], y: [-0.54, -0.46] }
    - id: outer_top
      shape: box
      params: { x: [0, 2], y: [0.54, 1] }
    - id: outer_bottom
      shape: box
      params: { x: [0, 2], y: [-1, -0.54] }

units:
  system: nondimensional      # not named by the source; bare numbers
  b_field_convention: permeability-unity   # stated-here, global (Sect. 2)

initial_conditions:
  aux:
    - { name: U0, expr: "1.0" }
    - { name: delta_v, expr: "0.01" }
    - { name: a_w, expr: "1.0/25.0" }
    - { name: B0, expr: "0.07/sqrt(4*pi)" }
    - { name: chi_pos, expr: "(pi/2) * (y - 0.5 + a_w) / (2*a_w)" }   # valid in mid_top (y>0)
    - { name: chi_neg, expr: "(pi/2) * (-y - 0.5 + a_w) / (2*a_w)" }  # valid in mid_bottom (y<0), using |y|
  equilibrium:
    - region: inner
      fields: { rho: "1.0", vx: "-(1.0/2.0)*U0*tanh((abs(y)-0.5)/a_w)", vy: "delta_v*sin(2*pi*x)*sin(pi*abs(y))", vz: "0.0", Bx: "0.0", By: "0.0", Bz: "B0", p: "0.6" }
    - region: mid_top
      fields: { rho: "1.0", vx: "-(1.0/2.0)*U0*tanh((abs(y)-0.5)/a_w)", vy: "delta_v*sin(2*pi*x)*sin(pi*abs(y))", vz: "0.0", Bx: "B0*sin(chi_pos)", By: "0.0", Bz: "B0*cos(chi_pos)", p: "0.6" }
    - region: mid_bottom
      fields: { rho: "1.0", vx: "-(1.0/2.0)*U0*tanh((abs(y)-0.5)/a_w)", vy: "delta_v*sin(2*pi*x)*sin(pi*abs(y))", vz: "0.0", Bx: "B0*sin(chi_neg)", By: "0.0", Bz: "B0*cos(chi_neg)", p: "0.6" }
    - region: outer_top
      fields: { rho: "1.0", vx: "-(1.0/2.0)*U0*tanh((abs(y)-0.5)/a_w)", vy: "delta_v*sin(2*pi*x)*sin(pi*abs(y))", vz: "0.0", Bx: "B0", By: "0.0", Bz: "0.0", p: "0.6" }
    - region: outer_bottom
      fields: { rho: "1.0", vx: "-(1.0/2.0)*U0*tanh((abs(y)-0.5)/a_w)", vy: "delta_v*sin(2*pi*x)*sin(pi*abs(y))", vz: "0.0", Bx: "B0", By: "0.0", Bz: "0.0", p: "0.6" }
  perturbation:
    combine_rule: additive
    fields: []
  potentials: []

parameters:
  - { name: gamma, canonical: 1.6666666666666667, meaning: "ratio of specific heats (= 5/3), global default" }
  - { name: eta, canonical: 0.0, meaning: "resistivity coefficient, explicitly zeroed ('now with eta=mu=0') -- resistivity term therefore ABSENT" }
  - { name: mu, canonical: 0.0, meaning: "dynamic viscosity coefficient, explicitly zeroed -- viscosity term therefore ABSENT" }
  - { name: lambda_heat, canonical: 0.0, meaning: "heat conduction coefficient, explicitly zeroed ('neglect the heat conduction by setting lambda=0') -- heat-conduction term therefore ABSENT" }
  - { name: U0, canonical: 1.0, meaning: "shear-layer velocity amplitude" }
  - { name: delta_v, canonical: 0.01, meaning: "perturbation velocity amplitude" }
  - { name: a_w, canonical: 0.04, meaning: "shear-layer transition half-width parameter (source symbol 'a' = 1/25)" }
  - { name: B0, canonical: 0.019755057825980868, meaning: "magnetic field magnitude (source: B0 = 0.07/sqrt(4*pi))" }
  - { name: rho0, canonical: 1.0, meaning: "uniform initial density" }
  - { name: p0, canonical: 0.6, meaning: "uniform initial gas pressure (source: 3/5)" }

domain_bc:
  # Same convention gap as kelvin-helmholtz-instability-vrmhd — see that entry's
  # pending_extraction.md. Recorded identically (periodic, inferred) for consistency since both
  # runs share the identical IC/geometry.
  x_lo: { type: periodic }
  x_hi: { type: periodic }
  y_lo: { type: periodic }
  y_hi: { type: periodic }

internal_boundaries: []

time:
  t_final: 4.0
  snapshot_times: [4.0]

validation_modes:
  - id: magnetic-helicity-conservation-error
    purpose: "Verify the time evolution of the magnetic helicity conservation error Delta H_M = H_M(t) - H_M(0), with H_M = (1/2)*integral_Omega A.B dOmega, against an explicit reference divergence-free Godunov-type scheme, over t in [0,4]."
    procedure: conservation-drift
    inputs:
      at_time: 4.0
      variables: [A_dot_B]
      reference: { kind: reference-result, key: dematte2024 }
      tolerance: "conservation errors comparable in magnitude to the explicit divergence-free Godunov-type reference scheme's errors (Fig. 16); no explicit numeric tolerance is stated in the source"
    has_exact_solution: false
    score: 3
    score_justification: "Magnetic helicity is genuinely discriminating here: no standard ideal-MHD scheme enforces its exact discrete conservation (source, verbatim), so a fully rolled-up, high-resolution (1024x1024) turbulent KH flow is a stringent, purpose-built stress test for this specific failure mode -- warranting a SCORED universal-diagnostic mode (SPEC §6.4). It is quantitative (a full time-series comparison against an explicit named reference scheme) but the source states no numeric tolerance, capping it at rubric row 3 rather than 4."

  - id: cross-helicity-conservation-error
    purpose: "Verify the time evolution of the cross helicity conservation error Delta H_C = H_C(t) - H_C(0), with H_C = (1/2)*integral_Omega u.B dOmega, against an explicit reference divergence-free Godunov-type scheme, over t in [0,4]."
    procedure: conservation-drift
    inputs:
      at_time: 4.0
      variables: [u_dot_B]
      reference: { kind: reference-result, key: dematte2024 }
      tolerance: "conservation errors comparable in magnitude to the explicit divergence-free Godunov-type reference scheme's errors (Fig. 16); no explicit numeric tolerance is stated in the source"
    has_exact_solution: false
    score: 3
    score_justification: "Same discriminating-challenge argument as the magnetic-helicity mode, for the distinct conserved quantity H_C (a genuinely different physical invariant, kept as its own mode per validation-authoring step 1: 'do not collapse two genuinely different checks into one'). Quantitative time-series comparison against an explicit named reference scheme, no stated numeric tolerance -- rubric row 3."

  - id: div-b-time-series
    purpose: "Verify ||div B||_L2 remains controlled over t in [0,4] for the fully rolled-up (turbulent) ideal-MHD KH flow, against an explicit reference divergence-free Godunov-type scheme."
    procedure: div-b
    inputs:
      at_time: 4.0
      variables: [B]
      reference: { kind: reference-result, key: dematte2024 }
      tolerance: "comparable in magnitude to the explicit divergence-free Godunov-type reference scheme's div-B error (Fig. 16); no explicit numeric criterion is stated in the source for this specific test"
    has_exact_solution: false
    score: 3
    score_justification: "Genuinely discriminating here: this KH flow reaches full nonlinear turbulence at high resolution (1024x1024), a substantially more demanding div-B stress test than a smooth/laminar problem, and the source explicitly compares it against a named reference scheme -- warranting a SCORED universal-diagnostic mode (SPEC §6.4). Quantitative time series, no stated numeric criterion for this specific test -- rubric row 3 (contrast the rotor test, Sect. 4.1.4, which does give bounding values for its own div-B time series but is a separate entry-in-waiting, not this one)."

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
  - key: dumbser2019vrmhd
    original_intro: true            # stated attribution (§5.4 rule 2a) -- see test_origin below (attribution is to the SHARED IC, equation (68), not to this ideal re-run specifically)
    verification:
      status: verified
      identifier: { doi: "10.1002/fld.4681", arxiv: "1801.06592" }
      source: "crossref: 10.1002/fld.4681 -> 200"
      checked: "2026-07-28"
      meta:
        year: 2018
        first_author: Dumbser
        container: International Journal for Numerical Methods in Fluids
        title: "A divergence-free semi-implicit finite volume scheme for ideal, viscous, and resistive magnetohydrodynamics"
references_unverified: []
test_origin:
  status: resolved-in-list
  ref: dumbser2019vrmhd
  authored_from: dematte2024
  attribution_claims:
    - stated_by: dematte2024
      quote: "we re-run the Kelvin-Helmholtz instability with the same initial condition as given in equation (68), but now with eta=mu=0 (IDEAL MHD variant)"
reference_results:
  - key: dematte2024
    params_used: { domain: "[0,2]x[-1,1]", eta: 0.0, mu: 0.0, lambda: 0.0, t_final: 4.0 }
    method: "proposed semi-implicit FVS scheme (ideal-MHD limit, no visco-resistive implicit sub-system); unstaggered CT adaptation; compared against an explicit second-order-accurate divergence-free Godunov-type scheme with staggered CT"
    resolution: "1024x1024 cells"
    amr: "none"
    findings: >
      Fig 16: time evolution of Delta H_C (cross helicity error), Delta H_M (magnetic helicity
      error), and ||div B||_L2 for both the semi-implicit (SI, unstaggered CT) and explicit (Exp,
      staggered CT) schemes over t in [0,4]. "We note that, although magnetic helicity and cross
      helicity should be conserved in the continuum limit, no standard ideal MHD scheme is set up
      to enforce their exact conservation at the discrete level, and so they are not exactly
      conserved numerically. This is reflected in the obtained results, where it is observed that
      the conservation errors from the present scheme are comparable to those obtained using an
      explicit divergence-free Godunov-type scheme."
related_to: [kelvin-helmholtz-instability-vrmhd]
headline_score: 3
---

## Physical problem
The ideal-MHD (eta=mu=0, lambda=0) limit of the same magnetised Kelvin-Helmholtz instability IC
used in `kelvin-helmholtz-instability-vrmhd` (equation (68) of the source): a tanh-profile shear
layer perturbed sinusoidally, embedded in a rotating helical magnetic field (Bx-to-Bz transition
across the mid bands). With all dissipative terms removed, the flow develops fully nonlinear
(turbulent) structure, and the discrete conservation of magnetic helicity, cross helicity, and
div-B become the quantities of interest rather than dissipative accuracy.

## What this test actually tests
Discrete conservation-error behaviour of an ideal-MHD scheme's magnetic helicity and cross
helicity, and its control of the div-B constraint, under a genuinely turbulent 2D MHD flow, all
benchmarked against an explicit reference scheme over the full time history t in [0,4] -- three
independently scored modes for three distinct conserved/controlled quantities.

## Qualitative behaviour
As in the visco-resistive sibling, the shear layer rolls up into a KH vortex/braid structure, but
here undamped (no dissipative terms), leading to fully developed 2D MHD turbulence by t=4. Neither
magnetic nor cross helicity is expected to be exactly conserved at the discrete level by any
standard ideal-MHD scheme (source, verbatim); the benchmark question is whether the proposed
scheme's conservation errors are comparable to (not necessarily smaller than) an established
explicit reference scheme's errors.

## Validation notes
All three modes are quantitative time-series comparisons against an explicitly named reference
scheme (an explicit, second-order, divergence-free Godunov-type method with staggered CT), but the
source states no explicit numeric tolerance/criterion for any of the three curves in Fig. 16 --
each mode is therefore scored 3, not 4, per docs/scoring-rubric.md. All three are treated as
SCORED universal diagnostics (not the default unscored provenance-metric treatment) because this
specific test is purpose-built by the source to stress exactly these failure modes in a turbulent
regime (SPEC §6.4 discriminating-challenge requirement) -- contrast a generic problem where div-B
tracking would be an unscored provenance metric.

## Notes
This entry and `kelvin-helmholtz-instability-vrmhd` share the exact same IC/geometry (equation
(68)) and are linked via `related_to` as a deliberate NEW-SIBLING pair (dedup skill worked case:
term-presence difference forks identity even under an identical IC) -- see that entry's header
comment for the full dedup reasoning. `domain_bc` (periodic all faces) is an inferred convention
shared with the visco-resistive sibling -- see `pending_extraction.md`.
