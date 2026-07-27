---
# Authored via /add-test (NORMAL path) from Jones, McNally & Reynolds, "A constrained-transport
# embedded boundary method for compressible resistive magnetohydrodynamics", J. Comput. Phys. 550
# (2026) 114641 (citekey: jones2026), Section 7.2 "Standing magnetosonic wave in a cylinder - a
# perturbed theta-pinch".
#
# DEDUP: sibling of standing-acoustic-wave-cylinder (same cylinder/eigenmode geometry and rigid
# wall) but the base equation set forks hydro -> mhd (an added uniform axial field), so this is a
# NEW SIBLING, not the same entry (SPEC dedup worked case: differing terms/base fork identity).
# related_to links both ways.

slug: standing-magnetosonic-wave-theta-pinch-cylinder
name: "Standing Fast Magnetosonic Wave in a Cylinder (Perturbed Theta-Pinch)"
provenance: literature
one_liner: "A standing fast-magnetosonic-wave normal mode inside a rigid-walled cylindrical embedded boundary threaded by a uniform axial field (a perturbed theta-pinch), with an analytic solution; used for a spatial second-order convergence study."

physics:
  materials:
    - name: plasma
      base: mhd
      terms: []
      eos:
        type: gamma-law
        params: { gamma: 1.6666666666666667 }   # gamma=5/3, source-stated global default
  coupling: none

dimension:
  intrinsic: 2
  runnable_in: [2]

analysis_treatments: [axis-singularity]

capability_flags:
  time_dependent_bc: false
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
  system: cgs-gaussian
  b_field_convention: sqrt-4pi   # source: "Bz,0 = sqrt(4*pi) G (1 in code units)" -- the sqrt(4pi) CGS-Gaussian <-> code-units factor

initial_conditions:
  aux:
    - { name: a,     expr: "1" }
    - { name: f,     expr: "1e-8" }
    - { name: J11,   expr: "3.8317059702" }
    - { name: k,     expr: "J11 / a" }
    - { name: rho0,  expr: "1" }
    - { name: P0,    expr: "1" }
    - { name: gamma, expr: "1.6666666666666667" }
    - { name: Bz0,   expr: "sqrt(4*pi)" }               # theta-pinch axial field, G (=1 in code units)
    - { name: cs,    expr: "sqrt(gamma * P0 / rho0)" }
    - { name: cA,    expr: "Bz0 / sqrt(rho0)" }          # Alfven speed
    - { name: cp,    expr: "sqrt(cA**2 + cs**2)" }       # fast magnetosonic speed, replaces cs (source: "cp is used in place of the sound speed")
    - { name: omega, expr: "cp * k" }
  equilibrium:
    - region: interior
      fields:
        rho: "rho0"
        p: "P0"
        vx: "0"
        vy: "0"
        vz: "0"
        Bx: "0"
        By: "0"
        Bz: "Bz0"
  perturbation:
    combine_rule: additive
    # t=0 slice: the density/Bz perturbations are proportional to sin(omega*t) (vanishing at t=0,
    # by direct analogy with the acoustic-wave sibling test), leaving only the radial-velocity kick,
    # same functional form as standing-acoustic-wave-cylinder but with omega=cp*k (fast-magnetosonic
    # frequency) replacing the sound-wave omega=cs*k.
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
  - { name: Bz0,   canonical: 3.5449077018110318, meaning: "uniform axial (theta-pinch) field strength, G (= sqrt(4*pi), 1 in code units)" }

domain_bc:
  r_hi: { type: dirichlet, state: { Bz: "Bz0", vx: "0", vy: "0" } }   # rigid, static wall; fixed axial field (source Sect. 4.1, Eq. 42 current-free-preserving Dirichlet enforcement)

internal_boundaries: []

time:
  t_final: 3.0425445024378415   # 7 oscillation periods = 7*(2*pi/omega) (source: "after 7 oscillation periods")
  snapshot_times: [3.0425445024378415]

validation_modes:
  - id: density-l1-convergence
    purpose: "Verify second-order spatial L1 convergence of density toward the analytic standing fast-magnetosonic-wave solution after 7 oscillation periods."
    procedure: convergence-order
    inputs:
      at_time: 3.0425445024378415
      variables: [rho]
      resolution_sequence: [0.12, 0.0667, 0.0353, 0.0182, 0.00923]   # Delta x in cm, from Fig. 3b
      expected_order: 2
      reference: { kind: reference-result, key: jones2026 }
      tolerance: "measured L1(rho) order approaches the theoretical 2nd order as Delta x -> 0 (Fig. 3b)"
    has_exact_solution: true
    score: 5
    score_justification: "Analytic standing fast-magnetosonic-wave solution (source states the problem 'converges to the analytic one at second order') combined with a demonstrated 2nd-order L1(rho) convergence sweep (Fig. 3b) — rubric row 5."

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
    params_used: { a: 1, f: 1e-8, gamma: 1.6666666666666667, Bz0: 3.5449077018110318, t: 3.0425445024378415 }
    method: "HLLD Riemann solver; single-sided static-polyline embedded boundary; staggered constrained transport"
    resolution: "Delta x in {0.12, 0.0667, 0.0353, 0.0182, 0.00923} cm"
    amr: "none"
    findings: "L1 error in density converges at second order in Delta x (Fig. 3b); axial-field profile matches the analytic solution at all shown resolutions (Fig. 3a)."
related_to: [standing-acoustic-wave-cylinder, standing-magnetosonic-wave-parallel-pinch-cylinder]
headline_score: 5
---

## Physical problem
A standing fast-magnetosonic-wave normal mode inside a cylindrical embedded boundary of radius
a=1 cm containing a magnetized plasma at rest (rho0=1 g/cm^3, P0=1 Ba, gamma=5/3) threaded by a
uniform axial field Bz,0=sqrt(4*pi) G (a "theta-pinch" configuration). This is the acoustic-wave
sibling test extended with a magnetic field: the wave number k is again the first zero of J1
divided by a, and the frequency uses the fast magnetosonic speed cp=sqrt(cA^2+cs^2) in place of
the sound speed cs, where cA=Bz0/sqrt(rho0) is the Alfven speed.

## What this test actually tests
Whether the scheme's MHD extension of the cut-cell embedded boundary (Dirichlet enforcement of a
fixed axial field at a rigid, non-grid-conformal wall, Sect. 4.1 Eq. 42) preserves the base
scheme's second-order spatial accuracy for a magnetized standing-wave eigenmode
(density-l1-convergence).

## Qualitative behaviour
The axial-field perturbation (Bz - sqrt(4*pi)) is a smooth, sign-changing radial profile
(Fig. 3a) analogous in shape to the acoustic wave's density perturbation, vanishing at r=a and
converging visually to the analytic curve as resolution increases.

## Validation notes
Fig. 3b shows the L1(rho) error at t = 7 oscillation periods across five resolutions
(Delta x = 0.12 down to 0.00923 cm), converging at the theoretical second order. The source gives
the frequency substitution omega=cp*k explicitly but does not spell out the extended closed-form
coefficients for the density/Bz perturbation amplitudes at t>0 (only the acoustic-wave sibling's
rho1=f*rho0*J0(kr)*sin(omega*t) form is given explicitly) — not needed for the t=0 IC here since
those perturbations are proportional to sin(omega*0)=0 regardless of their coefficient, but a
reader wanting the full t>0 analytic curve should consult Fig. 3a or re-derive it from the linear
fast-magnetosonic eigenmode.

## Notes
`b_field_convention: sqrt-4pi` follows the source's explicit "Bz,0 = sqrt(4*pi) G (1 in code
units)" annotation. As in the acoustic-wave sibling, the embedded wall coincides exactly with the
domain's outer coordinate extent (`domain_bc.r_hi`), not a separate `internal_boundaries` entry.
