---
# Authored via /add-test (NORMAL path) from Jones, McNally & Reynolds, "A constrained-transport
# embedded boundary method for compressible resistive magnetohydrodynamics", J. Comput. Phys. 550
# (2026) 114641 (citekey: jones2026), Section 7.6 "Relaxation of axial field in cylindrical
# conductor".
#
# DEDUP: distinct physics_signature from tangential-field-soak-conducting-slab (same base+term,
# but different geometry/analysis_treatment: cylindrical+axis-singularity vs cartesian box) -- NOT
# a structural match (dedup step 1a/1b both miss: analysis_treatments differ) -> NEW ENTRY.

slug: axial-field-relaxation-cylindrical-conductor
name: "Relaxation of Axial Field in a Cylindrical Conductor"
provenance: literature
one_liner: "Inward resistive diffusion of an axial magnetic field from the boundary of a cylindrical conductor, verified against a Fourier-Bessel (J0) semi-analytic solution."

physics:
  materials:
    - name: conductor
      base: magnetic-diffusion
      terms: [resistivity]
      material_fields:
        - { name: eta, region: interior, expr: "1e-3", units: "cm^2/s" }
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
  domain: { r: [0, 0.4], phi: [0, 6.283185307179586] }   # a=0.4 cm cylindrical embedded boundary IS the domain edge
  regions:
    - id: interior
      shape: cylinder
      params: { center: [0, 0], r: 0.4 }

units:
  system: cgs-gaussian
  b_field_convention: sqrt-4pi   # consistent with Bz(a) = sqrt(4*pi)*1e-3 G as stated

initial_conditions:
  aux:
    - { name: a,    expr: "0.4" }            # conductor radius, cm
    - { name: eta,  expr: "1e-3" }            # resistivity, cm^2/s
    - { name: Bz_a, expr: "sqrt(4*pi)*1e-3" } # boundary axial field, G
  equilibrium:
    - region: interior
      fields:
        Bz: "0"   # "Initially, there is no field inside the conductor"
  perturbation:
    combine_rule: additive
    fields: {}
  potentials: []

parameters:
  - { name: a,    canonical: 0.4,                  meaning: "conductor (embedded boundary) radius, cm" }
  - { name: eta,  canonical: 1e-3,                 meaning: "magnetic diffusivity, cm^2/s (spatially uniform)" }
  - { name: Bz_a, canonical: 0.0035449077018110317, meaning: "boundary axial field magnitude, G (= sqrt(4*pi)*1e-3)" }

domain_bc:
  r_hi: { type: dirichlet, state: { Bz: "Bz_a" } }   # rigid, static wall; fixed axial field (source Sect. 4.1)

internal_boundaries: []

time:
  t_final: 1   # source: "results are compared at a final time of 1 s"
  snapshot_times: [1]

validation_modes:
  - id: axial-field-l1-convergence
    purpose: "Verify second-order spatial L1 convergence of the axial field toward the Fourier-Bessel semi-analytic inward-diffusion solution at t=1 s."
    procedure: convergence-order
    inputs:
      at_time: 1
      variables: [Bz]
      resolution_sequence: "not individually enumerated in the source (Fig. 7 log-log convergence plot gives no legend of Delta x values); the left-panel simulation shown alongside is 50x50"
      expected_order: 2
      reference: { kind: reference-result, key: jones2026 }
      tolerance: "measured L1(Bz) order approaches the theoretical 2nd order as Delta x -> 0 (Fig. 7, right panel)"
    has_exact_solution: true
    score: 5
    score_justification: "Semi-analytic Fourier-Bessel (J0) exact solution of the linear diffusion equation combined with a demonstrated 2nd-order L1(Bz) convergence sweep (Fig. 7) — rubric row 5."

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
    params_used: { a: 0.4, eta: 1e-3, Bz_a: 0.0035449077018110317, t: 1 }
    method: "resistive (eta!=0) MHD induction update; single-sided static-polyline embedded boundary; Dirichlet fixed-Bz enforcement"
    resolution: "50x50 (Fig. 7 left panel); a convergence sweep for the right panel, resolutions not individually enumerated"
    amr: "none"
    findings: "L1 error in Bz converges at second order in Delta x (Fig. 7, right panel), compared against the Fourier-Bessel semi-analytic solution (eq. 73)."
related_to: [azimuthal-field-relaxation-cylindrical-conductor]
headline_score: 5
---

## Physical problem
A cylindrical conductor of radius a=0.4 cm, with uniform magnetic diffusivity eta=1e-3 cm^2/s and
zero initial internal magnetic field, has an axial field Bz(a)=sqrt(4*pi)*1e-3 G imposed on its
(embedded, polyline-represented) boundary. The field diffuses purely resistively inward from the
boundary toward the axis; there is no fluid motion (v=0).

## What this test actually tests
Whether the scheme's resistive operator, combined with a Dirichlet-enforced fixed axial field at a
rigid, non-grid-conformal cylindrical embedded boundary (including the coordinate-axis singularity
at r=0), reproduces the correct inward-diffusion profile and its second-order spatial accuracy
(axial-field-l1-convergence).

## Qualitative behaviour
Bz rises monotonically from 0 at the axis (r=0) to Bz(a) at the boundary, the profile steepening
near the boundary and flattening toward the center as diffusion proceeds; by t=1 s the field has
substantially penetrated toward the axis (Fig. 7 left panel, log-scale color map).

## Validation notes
Fig. 7 (right panel) shows the L1(Bz) error at t=1 s converging at the theoretical second order
against the Fourier-Bessel series solution (eq. 73): Bz(r,t)=Bz(a)[1-sum_n c_n*J0(k_n*r)*
exp(-eta*k_n^2*t)], with k_n the positive roots of J0(k_n*a)=0 and c_n=2/(k_n*a*J1(k_n*a)) chosen
to satisfy Bz(r,0)=0 for r<a.

## Notes
`b_field_convention: sqrt-4pi` follows the same convention used throughout the paper. The specific
Delta x values underlying the Fig. 7 (right panel) convergence sweep are not individually
enumerated in the source text (unlike Figs. 2/3/4/6, which give explicit legends); only the
left-panel's 50x50 resolution is stated directly.
