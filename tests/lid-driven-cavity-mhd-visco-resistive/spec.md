---
# Authored via /add-test (NORMAL path) from Dematté, Farmakalides, Millmore & Nikiforakis,
# "An all Mach number scheme for visco-resistive magnetically-dominated MHD flows", JCP 514
# (2024) 113229 (citekey: dematte2024). Section 4.3.3 "Lid-driven cavity with magnetic field
# (visco-resistive)".
#
# DEDUP NOTE (dedup skill, SPEC 2.2/2.4): the source studies two cases, Bx0=0.5 and Bx0=1.0,
# on an otherwise IDENTICAL geometry, IC structure, BC structure and method (§2.1 item 3:
# parameter values never enter identity). This mirrors the ideal-mhd-riemann-problem
# RP1-RP4 fold precedent: ONE canonical entry with Bx0 as a parameter; Bx0=0.5 (the case with
# the full streamline figure, Fig 17) is the canonical preset, Bx0=1.0 is recorded as an
# additional reference_result (params_used).

slug: lid-driven-cavity-mhd-visco-resistive
name: "Lid-Driven Cavity with Horizontal Magnetic Field (Visco-Resistive MHD)"
provenance: literature
one_liner: "Classical lid-driven cavity for visco-resistive MHD with an imposed uniform horizontal magnetic field Bx0 (canonical preset Bx0=0.5; Bx0=1.0 as a second preset); steady-state streamlines and 1D B-field slices compared to Fambri et al.'s hybrid FV/FE reference solution."

physics:
  materials:
    - name: plasma
      base: mhd
      terms: [viscosity, resistivity]
      eos:
        type: gamma-law
        params: { gamma: 1.6666666666666667 }   # gamma = 5/3, global default ("unless otherwise stated"), not overridden here
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
  domain: { x: [-0.5, 0.5], y: [-0.5, 0.5] }
  regions:
    - id: whole
      shape: box
      params: { x: [-0.5, 0.5], y: [-0.5, 0.5] }

units:
  system: nondimensional     # not named by the source; values given as bare numbers
  b_field_convention: permeability-unity   # stated-here, global (Sect. 2): "the units of B are chosen such that the vacuum magnetic permeability is unity"

initial_conditions:
  aux:
    - { name: beta_hat, expr: "40" }
  equilibrium:
    - region: whole
      fields: { rho: "1.0", vx: "0.0", vy: "0.0", vz: "0.0", Bx: "Bx0", By: "0.0", Bz: "0.0", p: "1e5" }
  perturbation:
    combine_rule: additive
    fields: []
  potentials: []

parameters:
  - { name: gamma, canonical: 1.6666666666666667, meaning: "ratio of specific heats (= 5/3), global default 'unless otherwise stated'" }
  - { name: Bx0, canonical: 0.5, meaning: "uniform initial/boundary horizontal magnetic field magnitude (canonical preset). Second studied value Bx0=1.0 (see reference_results)." }
  - { name: beta_hat, canonical: 40, meaning: "sharpness parameter of the tanh-tapered lid-velocity profile (dimensionless)" }
  - name: mu
    canonical: null
    meaning: "dynamic viscosity coefficient for this test (units consistent with the VRMHD viscous term)"
    notes: needs-source
  - name: eta
    canonical: null
    meaning: "resistivity coefficient for this test (units consistent with the VRMHD resistive term)"
    notes: needs-source

domain_bc:
  # Physical BC, verbatim (Sect. 4.3.3): no-slip (u=0) on left/right/bottom walls; lid velocity
  # u=(u_Lid(x),0) on the top wall with u_Lid = tanh(beta_hat*(0.5-x)) + tanh(beta_hat*(0.5+x)) - 1.0.
  # Homogeneous Neumann on rho, p everywhere. Perfectly-conducting walls: normal B fixed
  # (Bx=Bx0 on x_lo/x_hi, By=0 on y_lo/y_hi) PLUS homogeneous Neumann on the tangential B
  # component at each face (dBx/dy=0 on y_lo/y_hi; dBy/dx=0 on x_lo/x_hi) -- i.e. exactly the
  # composite `perfect-conductor` face condition, whose Bn state carries the stated normal field.
  # The source's pressure treatment (homogeneous Neumann, not the force balance this bc-type
  # asserts) is a method choice, recorded per row in reference_results[].wall_pressure_bc.
  x_lo: { type: perfect-conductor, state: { vx: "0.0", vy: "0.0", Bn: "Bx0" } }
  x_hi: { type: perfect-conductor, state: { vx: "0.0", vy: "0.0", Bn: "Bx0" } }
  y_lo: { type: perfect-conductor, state: { vx: "0.0", vy: "0.0", Bn: "0.0" } }
  y_hi: { type: perfect-conductor, state: { vx: "tanh(beta_hat*(0.5-x)) + tanh(beta_hat*(0.5+x)) - 1.0", vy: "0.0", Bn: "0.0" } }

internal_boundaries: []

time:
  t_final: 20.0   # source: "at time t=20, by which the solution has reached steady-state" (Fig 17, Bx0=0.5 case)
  snapshot_times: []

validation_modes:
  - id: bfield-slices-vs-fambri-reference
    purpose: "Compare 1D slices of Bx and By along the x- and y-axes at steady state against Fambri et al.'s hybrid FV/FE reference solution, for both studied Bx0 values."
    procedure: norms
    inputs:
      at_time: 20.0
      variables: [Bx, By]
      reference: { kind: reference, key: fambri2023 }
      tolerance: "visual/qualitative agreement as reported (Fig. 18); no numeric tolerance stated in source"
    has_exact_solution: false
    score: 3
    score_justification: "Quantitative reference profiles exist (Fambri et al.'s hybrid FV/FE steady-state solution) but the comparison as reported is visual 1D-slice agreement, not a stated numeric norm; tops at 3 per the rubric (no exact solution, reference-result comparison)."

references:
  - key: fambri2023
    original_intro: false   # NOT set here — only /add-refs resolves original_intro (§5.4); attribution recorded via test_origin.attribution_claims below instead
    verification:
      status: verified
      identifier: { doi: "10.1016/j.jcp.2023.112493" }
      source: "crossref: 10.1016/j.jcp.2023.112493 -> 200"
      checked: "2026-07-28"
      meta:
        year: 2023
        first_author: Fambri
        container: Journal of Computational Physics
        title: "A well-balanced and exactly divergence-free staggered semi-implicit hybrid finite volume / finite element scheme for the incompressible MHD equations"
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
  status: pending
  authored_from: dematte2024
  attribution_claims:
    - stated_by: dematte2024
      quote: "we consider a variant of the classical lid-driven cavity test for the incompressible Navier-Stokes equations, in which an additional horizontal magnetic field is imposed, as carried out by Fambri et al. [78]."
reference_results:
  - key: dematte2024
    params_used: { Bx0: 0.5, resolution_grid: "512x512", CFL: 0.4, t_final: 20.0 }
    method: "tangential-B wall closure: homogeneous Neumann (dBx/dy=0 on y_lo/y_hi, dBy/dx=0 on x_lo/x_hi); proposed semi-implicit finite volume scheme; second-order-accurate MUSCL-Hancock-type TVD reconstruction for the explicit advective terms; implicit treatment of visco-resistive terms; time step chosen according to the velocity (CFL=0.4), not the fast magnetosonic speed"
    resolution: "512x512 uniform Cartesian cells"
    amr: "none"
    wall_pressure_bc: homogeneous-neumann   # "homogeneous Neumann boundary condition applied everywhere for the density and pressure"
    findings: >
      Streamlines of velocity and magnetic field at t=20 (steady state) shown in Fig 17 for
      Bx0=0.5. 1D slices of Bx, By along the x- and y-axes (Fig 18) for both Bx0=0.5 and
      Bx0=1.0 show "very good agreement" with Fambri et al.'s hybrid FV/FE reference solution.
  - key: dematte2024
    params_used: { Bx0: 1.0, resolution_grid: "512x512", CFL: 0.4, t_final: 20.0 }
    method: "same as Bx0=0.5 entry above"
    resolution: "512x512 uniform Cartesian cells"
    amr: "none"
    wall_pressure_bc: homogeneous-neumann
    findings: "1D Bx, By slices (Fig 18) show very good agreement with the Fambri et al. reference solution for this Bx0 value also."
related_to: []
headline_score: 3
---

## Physical problem
A variant of the classical lid-driven cavity test for the incompressible Navier-Stokes
equations, extended to visco-resistive MHD by imposing an additional uniform horizontal
magnetic field B0=(Bx0,0,0) throughout the square domain [-0.5,0.5]x[-0.5,0.5]. The fluid
starts at rest (rho=1, p=1e5, u=0). A smoothly-tapered lid velocity profile
u_Lid = tanh(beta_hat*(0.5-x)) + tanh(beta_hat*(0.5+x)) - 1.0 (beta_hat=40) drives the top
boundary; no-slip walls elsewhere. Perfectly-conducting-wall conditions are imposed on the
magnetic field: the normal component of B is fixed at its initial value on each wall
(Bx=Bx0 left/right, By=0 top/bottom), with a companion homogeneous-Neumann condition on the
tangential B-component derived from the ideal-Ohm's-law wall condition Ez=0. Two initial
field magnitudes are studied: Bx0=0.5 (canonical preset) and Bx0=1.0.

## What this test actually tests
Coupled viscous + resistive momentum/induction transport in a driven shear flow that
magnetically couples to a background field threading the domain, including the ability of
the scheme to reach a physically correct MHD steady state (streamline topology and B-field
distribution) under implicit visco-resistive treatment with a velocity-dictated (not
magnetosonic-dictated) time step.

## Qualitative behaviour
By t=20 the flow/field configuration has reached steady state (source: "by which the
solution has reached steady-state"). No exact solution is available; the qualitative shape
comparison is against Fambri et al.'s own hybrid FV/FE steady-state streamlines (Fig 17,
Bx0=0.5) and 1D Bx/By slices along the domain axes (Fig 18, both Bx0 cases).

## Validation notes
The only quantitative anchor is the paper's own comparison to Fambri et al.'s hybrid FV/FE
reference solution via 1D slices of Bx and By at t=20; the source states only "very good
agreement", with no numeric tolerance — this caps the mode at score 3 (rubric: reference-
result comparison, no exact solution, no stated numeric tolerance).

## Notes
- FLAG (source gap, confirmed by direct re-read of page 30 of the PDF): the numeric values
  of the dynamic viscosity mu and resistivity eta for THIS specific test are never stated
  anywhere in Sect. 4.3.3 — only "perfectly conductive walls are assumed" is given, with no
  eta/mu numbers. Do NOT borrow eta=mu=1e-3 (the Kelvin-Helmholtz test, Sect 4.3.2) or
  eta=mu=0.1 (the shear-layer/current-sheet test, Sect 4.3.1) by analogy; both are recorded
  here as `needs-source` (see pending_extraction.md).
- The source imposes homogeneous Neumann on density and pressure at every wall (verbatim:
  "homogeneous Neumann boundary condition applied everywhere for the density and pressure").
  For pressure that is the naive approximation of the `perfect-conductor` force-balance
  condition, recorded per row as `wall_pressure_bc: homogeneous-neumann`. With `Bx0` normal to
  the x-walls and the resistive layer next to them, `n·(J×B)` need not vanish there, so the two
  conditions are not equivalent for this test — expect a near-wall pressure difference against
  any code that applies force balance.
- The source states the simulation time step is chosen according to the velocity (CFL=0.4),
  overriding the paper's global default (CFL=0.8, advective-eigenvalue time stepping already
  matches the global default in kind but the CFL number itself is overridden) — this is a
  method/time-stepping detail, out of scope for the problem-only fields here, but recorded
  in `reference_results.method` above.
- Units are stored as authored (bare, nondimensional numbers); b_field_convention
  (permeability-unity) is a global, paper-wide statement (Sect. 2), not a needs-source item.
