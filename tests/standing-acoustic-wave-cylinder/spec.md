---
# Authored via /add-test (NORMAL path) from Jones, McNally & Reynolds, "A constrained-transport
# embedded boundary method for compressible resistive magnetohydrodynamics", J. Comput. Phys. 550
# (2026) 114641 (citekey: jones2026), Section 7.1 "Standing acoustic wave in a cylinder".

slug: standing-acoustic-wave-cylinder
name: "Standing Acoustic Wave in a Cylinder"
provenance: literature
one_liner: "A standing sound-wave normal mode inside a rigid-walled cylindrical embedded boundary, with a closed-form Bessel-function solution at all times; used for a spatial second-order convergence study."

physics:
  materials:
    - name: gas
      base: hydro
      terms: []
      eos:
        type: gamma-law
        params: { gamma: 1.6666666666666667 }   # gamma=5/3, source-stated global default ("Unless otherwise mentioned... a gamma=5/3 material is used")
  coupling: none

dimension:
  intrinsic: 2                # (r,phi) plane; z-invariant
  runnable_in: [2]

analysis_treatments: [axis-singularity]   # domain includes r=0

capability_flags:
  time_dependent_bc: false    # rigid wall, no state expression at all
  has_internal_boundaries: false
geometry_stress: none

geometry:
  coord_system: cylindrical
  domain: { r: [0, 1], phi: [0, 6.283185307179586] }   # a=1 cm cylindrical embedded boundary IS the domain edge
  regions:
    - id: interior
      shape: cylinder
      params: { center: [0, 0], r: 1 }

units:
  system: cgs-gaussian        # rho in g/cm^3, P in Ba (barye) as stated
  b_field_convention: null    # no magnetic field in this hydro test

initial_conditions:
  aux:
    - { name: a,     expr: "1" }                 # cylinder radius, cm
    - { name: f,     expr: "1e-8" }               # perturbation magnitude (source: f=10^-8)
    - { name: J11,   expr: "3.8317059702" }       # first zero of the first-order Bessel function J1
    - { name: k,     expr: "J11 / a" }            # wave number
    - { name: rho0,  expr: "1" }                  # background density, g/cm^3
    - { name: P0,    expr: "1" }                  # background pressure, Ba
    - { name: gamma, expr: "1.6666666666666667" }
    - { name: cs,    expr: "sqrt(gamma * P0 / rho0)" }   # sound speed
    - { name: omega, expr: "cs * k" }             # mode frequency
  equilibrium:
    - region: interior
      fields:
        rho: "rho0"
        p: "P0"
        vx: "0"
        vy: "0"
  perturbation:
    combine_rule: additive
    # t=0 slice of the exact time-dependent solution v_r(r,t) = -(f*omega/k)*J1(k*r)*cos(omega*t):
    # at t=0, cos(omega*t)=1 and the density/pressure perturbations (proportional to sin(omega*t))
    # vanish, leaving only a radial-velocity kick as the t=0 IC.
    fields:
      vx: "-(f*omega/k) * J1(k*r) * (x/r)"
      vy: "-(f*omega/k) * J1(k*r) * (y/r)"
  potentials: []

parameters:
  - { name: a,     canonical: 1,    meaning: "cylinder (embedded boundary) radius, cm" }
  - { name: f,     canonical: 1e-8, meaning: "perturbation magnitude (dimensionless)" }
  - { name: rho0,  canonical: 1,    meaning: "background density, g/cm^3" }
  - { name: P0,    canonical: 1,    meaning: "background pressure, Ba" }
  - { name: gamma, canonical: 1.6666666666666667, meaning: "ratio of specific heats (=5/3), global default" }

domain_bc:
  r_hi: { type: reflecting }   # rigid wall at r=a; standing-wave eigenmode k=J11/a makes v_r(a,t)=0 automatically (J1(J11)=0)

internal_boundaries: []

time:
  t_final: 1.2701742902559663   # one full wave period T = 2*pi/omega (source: "results...after one wave period")
  snapshot_times: [1.2701742902559663]

validation_modes:
  - id: density-l1-convergence
    purpose: "Verify second-order spatial L1 convergence of density toward the exact standing-wave Bessel-function solution after one wave period."
    procedure: convergence-order
    inputs:
      at_time: 1.2701742902559663
      variables: [rho]
      resolution_sequence: [0.12, 0.0545, 0.0286, 0.0146, 0.00741]   # Delta x in cm, from Fig. 2b
      expected_order: 2
      reference: { kind: reference-result, key: jones2026 }
      tolerance: "measured L1(rho) order approaches the theoretical 2nd order as Delta x -> 0 (Fig. 2b)"
    has_exact_solution: true
    score: 5
    score_justification: "Exact closed-form analytic solution (Bessel-function standing wave) at all times, combined with a demonstrated 2nd-order L1(rho) convergence sweep (Fig. 2b) — rubric row 5."

references:
  - key: jones2026
    original_intro: false
    verification:
      status: verified
      identifier: { doi: "10.1016/j.jcp.2025.114641" }
      source: "crossref: 10.1016/j.jcp.2025.114641 -> 200"
      checked: "2026-07-27"
      meta:
        year: 2026
        first_author: Jones
        container: Journal of Computational Physics
        title: "A constrained-transport embedded boundary method for compressible resistive magnetohydrodynamics"
references_unverified: []
test_origin:
  status: pending
  authored_from: jones2026
  attribution_claims: []
reference_results:
  - key: jones2026
    params_used: { a: 1, f: 1e-8, gamma: 1.6666666666666667, t: 1.2701742902559663 }
    method: "HLLD Riemann solver; single-sided static-polyline embedded boundary (Forrer & Jeltsch cut-cell)"
    resolution: "Delta x in {0.12, 0.0545, 0.0286, 0.0146, 0.00741} cm"
    amr: "none"
    findings: "L1 error in density converges at second order in Delta x (Fig. 2b); radial-velocity profile matches the exact solution at all shown resolutions (Fig. 2a)."
related_to: [standing-magnetosonic-wave-theta-pinch-cylinder]
headline_score: 5
---

## Physical problem
A standing acoustic (sound) wave normal mode is initialized inside a cylindrical embedded
boundary of radius a=1 cm containing a gas at rest (rho0=1 g/cm^3, P0=1 Ba, gamma=5/3). The wave
number k is chosen as the first zero of J1 divided by a, so the analytic radial-velocity solution
automatically satisfies a rigid (reflecting) wall at r=a. The exact solution at all times is
rho(r,t)=rho0+f*rho0*J0(k*r)*sin(omega*t), P(r,t)=P0+gamma*P0*(rho1/rho0), v_r(r,t)=
-(f*omega/k)*J1(k*r)*cos(omega*t), with omega=cs*k and cs=sqrt(gamma*P0/rho0).

## What this test actually tests
Whether the scheme's cut-cell embedded-boundary treatment (a non-grid-conformal rigid wall) can
support and evolve a smooth Bessel-function eigenmode without degrading the underlying second-order
spatial accuracy of the base finite-volume Godunov scheme (density-l1-convergence).

## Qualitative behaviour
The radial velocity profile is a smooth cosine-in-time, J1(kr)-in-radius curve, symmetric about
r=0, vanishing at r=a by construction; density and pressure perturbations are J0(kr)-shaped and
vanish at t=0, 90 degrees out of phase with velocity.

## Validation notes
Fig. 2b shows the L1(rho) error at t = one wave period T=2*pi/omega across five resolutions
(Delta x = 0.12 down to 0.00741 cm), converging at the theoretical second order (dashed
Delta x^2 reference line closely tracked). Fig. 2a overlays the radial-velocity profile at each
resolution against the exact solution, visually converging as Delta x decreases.

## Notes
`b_field_convention` is null (not applicable, not a needs-source gap) since this is a pure
hydrodynamic test. The embedded boundary radius a=1 cm exactly equals the domain's outer
coordinate extent `r_hi`, so the wall is represented here as `domain_bc.r_hi` rather than an
`internal_boundaries` entry (the fluid occupies the entire coordinate domain up to the wall).
