---
# Authored via /add-test (NORMAL path) from Jones, McNally & Reynolds, "A constrained-transport
# embedded boundary method for compressible resistive magnetohydrodynamics", J. Comput. Phys. 550
# (2026) 114641 (citekey: jones2026), Section 7.11 "Compression of a parallel-pinch". Field form
# re-uses Section 7.3's construction (eqs. 68-69, citekey freidberg2014).
#
# DEDUP: sibling of theta-pinch-compression-embedded-boundary (source: "Otherwise all parameters
# and boundary conditions are the same as in the theta-pinch test") but the equilibrium field gains
# a nonzero in-plane (Bphi) component -- a structural IC difference -> NEW SIBLING.

slug: parallel-pinch-compression-embedded-boundary
name: "Sub-Alfvenic Compression of a Parallel Pinch by a Moving Embedded Boundary"
provenance: literature
one_liner: "A Freidberg parallel-pinch (Bphi(r), Bz(r)) plasma is adiabatically compressed by a moving, reflecting perfect-conductor embedded boundary; validated against the adiabatic P-rho relation and against mass/axial-flux/in-plane-flux conservation drift."

physics:
  materials:
    - name: plasma
      base: mhd
      terms: []
      eos:
        type: gamma-law
        params: { gamma: 1.6666666666666667 }
  coupling: none

dimension:
  intrinsic: 2
  runnable_in: [2]

analysis_treatments: [none]

capability_flags:
  time_dependent_bc: false
  has_internal_boundaries: true
geometry_stress: none

geometry:
  coord_system: cartesian
  domain: { x: [-0.5, 0.5], y: [-0.5, 0.5] }   # "square domain of side length unity" (source, same as the theta-pinch sibling)
  regions:
    - id: interior
      shape: cylinder
      params: { center: [0, 0], r: 0.4 }

units:
  system: cgs-gaussian
  b_field_convention: sqrt-4pi

initial_conditions:
  aux:
    - { name: a,       expr: "0.4" }
    - { name: rho0,    expr: "1" }
    - { name: P0,      expr: "10" }
    - { name: gamma,   expr: "1.6666666666666667" }
    - { name: Bphi_a,  expr: "sqrt(pi) / a" }    # Bphi(a) = sqrt(pi)/a G, source-restated (Sect. 7.11)
    - { name: Bz_a,    expr: "sqrt(4*pi)" }      # Bz(a) = sqrt(4*pi) G, source-restated
    - { name: alpha,   expr: "Bphi_a / Bz_a" }
  equilibrium:
    - region: interior
      fields:
        rho: "rho0"
        p: "P0"
        vx: "-(x/a)"    # v_r = -r/a, same motion profile as the theta-pinch sibling
        vy: "-(y/a)"
        vz: "0"
        # Bx, By from A_z(r) (source eq. 68, as in standing-magnetosonic-wave-parallel-pinch-cylinder)
        Bx: "-(Bphi_a / (2*a)) * y"
        By: "(Bphi_a / (2*a)) * x"
        Bz: "(Bz_a/alpha) * sqrt(1 + (2*alpha**2/3)*(1-(r/a)**2)**2*(5-2*(r/a)**2))"   # source eq. 69

  perturbation:
    combine_rule: additive
    fields: {}
  potentials:
    - name: A_z
      expr: "Bphi_a * (a/4) * (2 - (r/a)**2)"
      derives: "Bx = dA_z/dy, By = -dA_z/dx (B = curl(A_z*z_hat))"

parameters:
  - { name: a,      canonical: 0.4,   meaning: "initial cylinder (embedded boundary) radius, cm" }
  - { name: rho0,   canonical: 1,     meaning: "initial density, g/cm^3" }
  - { name: P0,     canonical: 10,    meaning: "initial thermal pressure, Ba" }
  - { name: gamma,  canonical: 1.6666666666666667, meaning: "ratio of specific heats (=5/3), global default" }
  - { name: Bphi_a, canonical: 4.430750558635426, meaning: "azimuthal field at r=a, G (= sqrt(pi)/a, a=0.4)" }
  - { name: Bz_a,   canonical: 3.5449077018110318, meaning: "axial field at r=a, G (= sqrt(4*pi))" }

domain_bc:
  x_lo: { type: outflow }
  x_hi: { type: outflow }
  y_lo: { type: outflow }
  y_hi: { type: outflow }

internal_boundaries:
  - kind: perfect-conductor-wall
    geometry: { region: interior, surface: boundary }
    motion: { type: prescribed-velocity, expr: "v_r = -r/a" }

time:
  t_final: 0.3   # "otherwise all parameters...are the same as in the theta-pinch test" (Sect. 7.10)
  snapshot_times: [0, 0.7, 1.4]   # Fig. 12/13-style snapshot pattern is not restated numerically for Fig. 12 alone; using the theta-pinch sibling's cadence as a placeholder -- see Notes

validation_modes:
  - id: central-adiabat-tracking
    purpose: "Verify the central (geometric-center) pressure and density trace the expected adiabatic relation P/P0=(rho/rho0)^gamma throughout the sub-Alfvenic compression of the parallel-pinch equilibrium."
    procedure: exact-solution-compare
    inputs:
      at_time: [0, 0.3]
      variables: [rho, p]
      cut_lines: ["geometric center of the mesh cell containing the domain center"]
      reference: { kind: reference-result, key: jones2026 }
      tolerance: "central (rho,P) trace lies on the adiabat P/P0=(rho/rho0)^gamma to within plotting precision (Fig. 12, panel d)"
    has_exact_solution: false
    score: 3
    score_justification: "Quantitative comparison to a well-motivated reference relation (the adiabatic invariant, valid in the stated strongly sub-Alfvenic limit), not an exact solution of the full compressible MHD equations at finite radius — rubric row 3, matching the theta-pinch sibling."

  - id: mass-axial-flux-conservation-drift
    purpose: "Verify total mass and total z-direction magnetic flux enclosed within the moving embedded compressing boundary, comparing conservation behavior against the theta-pinch sibling which has no in-plane field."
    procedure: conservation-drift
    inputs:
      conserved_quantity: "total mass and total Bz flux within the compressing interior region (active-volume/area-fraction weighted)"
      evolve_time: [0, 0.3]
      drift_form: relative
      tolerance: "source reports mass and Bz-flux relative errors that are similar early (high resolution) but diverge and become non-monotonic later (low resolution) (Fig. 12, panel e)"
    has_exact_solution: false
    score: 3
    score_justification: "Automatable, quantitative drift-vs-time diagnostic, genuinely discriminating for a moving, non-grid-conformal embedded boundary — rubric row 3 (SPEC §6.4 universal-diagnostic rule), matching the theta-pinch sibling."

  - id: inplane-flux-conservation-drift
    purpose: "Verify conservation of the in-plane (azimuthal, Bphi) magnetic flux enclosed within the moving embedded boundary -- a conservation check that does not exist for the theta-pinch sibling test, which has zero in-plane field."
    procedure: conservation-drift
    inputs:
      conserved_quantity: "line integral of Bphi around the compressing interior region (source: integral of B_phi dr)"
      evolve_time: [0, 0.3]
      drift_form: relative
      tolerance: "source: 'a conservation error of this component of magnetic flux due to the boundary condition is again present' (Fig. 12, panel e)"
    has_exact_solution: false
    score: 3
    score_justification: "Automatable, quantitative drift-vs-time diagnostic; explicitly discriminating because this is the one component the source singles out as newly non-conserved relative to the theta-pinch sibling (its in-plane field is identically zero there) — rubric row 3."

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
  - key: freidberg2014
    verification:
      status: verified
      identifier: { doi: "10.1017/CBO9780511795046" }
      source: "crossref: 10.1017/CBO9780511795046 -> 200"
      checked: "2026-07-27"
      meta:
        year: 2014
        first_author: Freidberg
        container: Cambridge University Press
        title: "Ideal MHD"
references_unverified: []
test_origin:
  status: pending
  authored_from: jones2026
  attribution_claims: []
reference_results:
  - key: jones2026
    params_used: { a: 0.4, rho0: 1, P0: 10, gamma: 1.6666666666666667, Bphi_a: 4.430750558635426, Bz_a: 3.5449077018110318, t_final: 0.3 }
    method: "ideal MHD; moving-polyline embedded boundary, reflecting perfect-conductor wall, velocity = v_r=-r/a; same 128^2 mesh as the theta-pinch sibling"
    resolution: "128^2 Cartesian mesh"
    amr: "none"
    wall_pressure_bc: not-stated   # "the cylindrical boundary is a reflecting [wall]"; no pressure condition given
    findings: "Central density/pressure trace the adiabat (Fig. 12d); mass and Bz-flux conservation errors are similar early but diverge and become non-monotonic later (Fig. 12e); a new in-plane (Bphi) flux conservation error is present, absent in the theta-pinch sibling."
related_to: [theta-pinch-compression-embedded-boundary, standing-magnetosonic-wave-parallel-pinch-cylinder]
headline_score: 3
---

## Physical problem
A cylindrical plasma of initial radius a=0.4 cm, density rho0=1 g/cm^3, thermal pressure P0=10 Ba,
threaded by a Freidberg parallel-pinch equilibrium field (azimuthal Bphi(r) from a vector potential,
axial Bz(r) direct, per standing-magnetosonic-wave-parallel-pinch-cylinder's eqs. 68-69, here with
Bphi(a)=sqrt(pi)/a G and Bz(a)=sqrt(4*pi) G at a=0.4 cm), is adiabatically compressed by a moving,
reflecting perfect-conductor embedded boundary contracting with radial velocity v_r=-r/a. Otherwise
identical to the theta-pinch compression sibling test.

## What this test actually tests
Whether the scheme's moving-embedded-boundary MHD treatment correctly captures adiabatic
compressional heating of a *sheared* (parallel-pinch) equilibrium as its internal structure evolves
under compression (central-adiabat-tracking), and whether the moving cut-cell representation
introduces non-conservation of mass, axial flux (mass-axial-flux-conservation-drift), and — newly,
relative to the theta-pinch sibling — in-plane azimuthal flux (inplane-flux-conservation-drift).

## Qualitative behaviour
The radial profiles of density, azimuthal field, and axial field all evolve as the pinch is
compressed (unlike the theta-pinch sibling's simpler quasi-uniform compression), reflecting the
changing internal structure of the sheared equilibrium; the central pressure-density trace still
lies on the adiabat (Fig. 12d).

## Validation notes
As in the theta-pinch sibling, no grid-convergence sweep is reported for this test (a single
resolution is used), capping all modes at rubric row 3. The key qualitative distinction from the
sibling is the nonzero in-plane field, which the source explicitly identifies as introducing an
additional conservation error not present when Bphi=0.

## Notes
`snapshot_times` here is a placeholder (the source does not restate a numeric snapshot cadence for
Fig. 12 specifically); `t_final=0.3` is carried over from the explicit statement that "all
parameters and boundary conditions are the same as in the theta-pinch test" (Section 7.10).
`internal_boundaries[0].motion` uses the same free-text convention as the theta-pinch sibling (see
its Notes) since the schema does not yet define a strict structured form for boundary motion.
