---
# Authored via /add-test (NORMAL path) from Dematté, Farmakalides, Millmore & Nikiforakis,
# "An all Mach number scheme for visco-resistive magnetically-dominated MHD flows", JCP 514
# (2024) 113229 (citekey: dematte2024). Section 4.3.2 "Kelvin-Helmholtz instability", the
# visco-resistive (eta=mu=1e-3) half of the pair.
#
# INTRA-PAPER DEDUP: this test and `kelvin-helmholtz-instability-ideal-mhd` share the IDENTICAL
# initial condition and geometry (source, verbatim: "we re-run the Kelvin-Helmholtz instability
# with the same initial condition as given in equation (68), but now with eta=mu=0"). Per the
# dedup skill's own worked case ("Inviscid KH vs visco-resistive KH -> NEW SIBLING (terms
# differ), related_to-linked"), a term-presence difference (viscosity+resistivity present here,
# absent there) forks identity even with identical IC/geometry -- these are NOT folded into one
# entry. Kept as two NEW-SIBLING entries, cross-linked via `related_to`, because they test
# fundamentally different physics: this entry probes visco-resistive dissipation fidelity
# (density-field qualitative agreement with a real diffusive KH roll-up); the ideal sibling
# probes discrete conservation properties (magnetic/cross helicity, div-B) of an ideal-MHD
# scheme applied to the same turbulent flow -- a capability question that is meaningless for
# a dissipative (visco-resistive) run, where helicity and div-B are not expected to be
# conserved in the first place.

slug: kelvin-helmholtz-instability-vrmhd
name: "Visco-Resistive Kelvin-Helmholtz Instability (VRMHD)"
provenance: literature
one_liner: "2D magnetised Kelvin-Helmholtz instability with visco-resistive dissipation (eta=mu=1e-3), as investigated by Dumbser et al.; validated via qualitative density-field agreement with the literature at t=4."

physics:
  materials:
    - name: plasma
      base: mhd
      terms: [viscosity, resistivity]
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
  - { name: eta, canonical: 0.001, meaning: "resistivity coefficient (VRMHD resistive term)" }
  - { name: mu, canonical: 0.001, meaning: "dynamic viscosity coefficient (VRMHD viscous term)" }
  - { name: lambda_heat, canonical: 0.0, meaning: "heat conduction coefficient, explicitly set to zero ('neglect the heat conduction by setting lambda=0') -- heat-conduction term therefore ABSENT" }
  - { name: U0, canonical: 1.0, meaning: "shear-layer velocity amplitude" }
  - { name: delta_v, canonical: 0.01, meaning: "perturbation velocity amplitude" }
  - { name: a_w, canonical: 0.04, meaning: "shear-layer transition half-width parameter (source symbol 'a' = 1/25)" }
  - { name: B0, canonical: 0.019755057825980868, meaning: "magnetic field magnitude (source: B0 = 0.07/sqrt(4*pi))" }
  - { name: rho0, canonical: 1.0, meaning: "uniform initial density" }
  - { name: p0, canonical: 0.6, meaning: "uniform initial gas pressure (source: 3/5)" }

domain_bc:
  # NOT explicitly stated in the quoted slice of Sect. 4.3.2. x-periodicity is strongly implied
  # by the sin(2*pi*x) perturbation form (a standard periodic-in-x KH setup); y-periodicity is
  # the conventional choice for this specific Dumbser-et-al.-type KH benchmark (the IC is
  # y-symmetric and approaches uniform states at |y|=1) but is NOT independently confirmed here.
  # Recorded as periodic on all faces as an inferred convention; flagged in pending_extraction.md.
  x_lo: { type: periodic }
  x_hi: { type: periodic }
  y_lo: { type: periodic }
  y_hi: { type: periodic }

internal_boundaries: []

time:
  t_final: 4.0
  snapshot_times: [4.0]

validation_modes:
  - id: density-field-qualitative-agreement
    purpose: "Verify the fluid density field at t=4 reproduces the visco-resistive KH roll-up/braid structure reported in the literature (Dumbser et al.) for the same IC."
    procedure: norms
    inputs:
      at_time: 4.0
      variables: [rho]
      reference: { kind: reference-result, key: dematte2024 }
      tolerance: "qualitative visual agreement only ('very good agreement... with results in the literature, see for example Dumbser et al.'); no numeric error norm or tolerance is stated in the source"
    has_exact_solution: false
    score: 3
    score_justification: "A specific, quantitative reference result exists (dematte2024's own 1024x1024 run, itself compared against Dumbser et al.'s published density field for the identical IC), but the comparison as reported is a visual figure match with no stated numeric norm or tolerance -- same situation as ideal-mhd-riemann-problem's profile-vs-high-res-reference mode, capped at rubric row 3 (quantitative reference exists; qualitative reporting)."

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
    original_intro: true            # stated attribution (§5.4 rule 2a) — see test_origin below
    verification:
      status: verified
      identifier: { doi: "10.1002/fld.4681", arxiv: "1801.06592" }
      source: "crossref: 10.1002/fld.4681 -> 200"
      checked: "2026-07-28"
      meta:
        year: 2018                  # priority date; print issue 2019 (citekey year)
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
      quote: "we simulate the Kelvin-Helmholtz instability forming in a visco-resistive fluid, as investigated in Dumbser [41]"
reference_results:
  - key: dematte2024
    params_used: { domain: "[0,2]x[-1,1]", eta: 0.001, mu: 0.001, lambda: 0.0, t_final: 4.0 }
    method: "proposed semi-implicit FVS scheme; VRMHD viscous/resistive terms treated implicitly; second-order-accurate MUSCL-Hancock-type TVD reconstruction for the explicit advective sub-system (star quantities U*)"
    resolution: "1024x1024 cells"
    amr: "none"
    findings: >
      "The numerical solution for fluid density at the final time is shown in Fig 15 where we
      observe very good agreement with results in the literature (see for example Dumbser et
      al. [41])."
related_to: [kelvin-helmholtz-instability-ideal-mhd]
headline_score: 3
---

## Physical problem
A 2D magnetised Kelvin-Helmholtz instability: a tanh-profile shear layer in vx (centred at
|y|=0.5) with a small sinusoidal vy perturbation, embedded in a magnetic field that rotates
smoothly (via the chi angle) from purely Bx (outer bands, |y|>0.54) through a helical transition
(mid bands) to purely Bz (inner band, |y|<0.46). Evolved under the full visco-resistive MHD
(VRMHD) system with eta=mu=1e-3 and heat conduction neglected (lambda=0).

## What this test actually tests
Qualitative fidelity of the scheme's combined advective + visco-resistive treatment in producing
the correct nonlinear roll-up/braid structure of a magnetised KH instability, benchmarked against
an established literature result (Dumbser et al.) for the identical IC.

## Qualitative behaviour
The shear layer rolls up into the characteristic KH vortex/braid structure by t=4, with the
magnetic field's helical mid-band structure influencing (but not suppressing, at this weak
B0=0.07/sqrt(4*pi)) the roll-up; density develops the associated mixing-layer structure. No
specific quantitative feature positions are given in the source -- only a qualitative "very good
agreement" claim for the density field.

## Validation notes
No automatable numeric check is available from the source (no error norm, no tolerance, no
digitizable reference curve is described in the text) -- the mode is capped at score 3 by the
existence of a specific, named quantitative reference result (dematte2024's own run, itself
checked against Dumbser et al.) even though the reported comparison is visual only.

## Notes
This entry and `kelvin-helmholtz-instability-ideal-mhd` share the exact same IC/geometry
(equation (68) in the source) and are linked via `related_to` as a deliberate NEW-SIBLING pair
(dedup skill worked case: term-presence difference forks identity even under an identical IC).
`domain_bc` (periodic all faces) is an inferred convention, not explicitly restated in the quoted
slice for this test -- see `pending_extraction.md`.
