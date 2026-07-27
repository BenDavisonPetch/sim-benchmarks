---
# Authored via /add-test (NORMAL path) from Jones, McNally & Reynolds, "A constrained-transport
# embedded boundary method for compressible resistive magnetohydrodynamics", J. Comput. Phys. 550
# (2026) 114641 (citekey: jones2026), Section 7.7 "Relaxation of azimuthal field in cylindrical
# conductor".
#
# DEDUP: sibling of axial-field-relaxation-cylindrical-conductor (same base/term, same cylindrical
# conductor geometry) but the imposed/evolved field component differs (azimuthal Bphi(r,t) vs axial
# Bz(r,t)) -- a structurally different IC/BC-state form (different field component driven, +
# different eta, a numeric parameter) -> dedup structural-compare (step 3) finds the boundary-state
# expression shape differs (Bphi tangential-vector form vs a plain scalar Bz Dirichlet) -> NEW
# SIBLING, related_to linked both ways.

slug: azimuthal-field-relaxation-cylindrical-conductor
name: "Relaxation of Azimuthal Field in a Cylindrical Conductor"
provenance: literature
one_liner: "Inward resistive diffusion of an azimuthal (toroidal) magnetic field from the boundary of a cylindrical conductor, verified against a Fourier-Bessel (J1) semi-analytic solution."

physics:
  materials:
    - name: conductor
      base: magnetic-diffusion
      terms: [resistivity]
      material_fields:
        - { name: eta, region: interior, expr: "1", units: "cm^2/s" }
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
  b_field_convention: sqrt-4pi   # consistent with Bphi(a) = sqrt(4*pi)*1e-3 G as stated

initial_conditions:
  aux:
    - { name: a,      expr: "0.4" }            # conductor radius, cm
    - { name: eta,    expr: "1" }               # resistivity, cm^2/s
    - { name: Bphi_a, expr: "sqrt(4*pi)*1e-3" } # boundary toroidal field, G
  equilibrium:
    - region: interior
      fields:
        Bx: "0"   # "we initialize a cylindrical conductor with zero magnetic flux density"
        By: "0"
  perturbation:
    combine_rule: additive
    fields: {}
  potentials: []

parameters:
  - { name: a,      canonical: 0.4,                   meaning: "conductor (embedded boundary) radius, cm" }
  - { name: eta,    canonical: 1,                      meaning: "magnetic diffusivity, cm^2/s (spatially uniform)" }
  - { name: Bphi_a, canonical: 0.0035449077018110317,  meaning: "boundary toroidal field magnitude, G (= sqrt(4*pi)*1e-3)" }

domain_bc:
  r_hi: { type: dirichlet, state: { Bx: "-Bphi_a*sin(phi)", By: "Bphi_a*cos(phi)" } }   # rigid, static wall; fixed toroidal field of magnitude Bphi_a, tangential everywhere on the boundary

internal_boundaries: []

time:
  t_final: 0.03   # source: "The result at t=0.03 s"
  snapshot_times: [0.03]

validation_modes:
  - id: azimuthal-field-l1-convergence
    purpose: "Verify second-order spatial L1 convergence of the azimuthal field toward the Fourier-Bessel semi-analytic inward-diffusion solution at t=0.03 s."
    procedure: convergence-order
    inputs:
      at_time: 0.03
      variables: [Bphi]
      resolution_sequence: "not individually enumerated in the source (Fig. 8 log-log convergence plot gives no legend of Delta x values); the left-panel simulation shown alongside is 24x24"
      expected_order: 2
      reference: { kind: reference-result, key: jones2026 }
      tolerance: "measured L1(Bphi) order approaches the theoretical 2nd order as Delta x -> 0 (Fig. 8, right panel)"
    has_exact_solution: true
    score: 5
    score_justification: "Semi-analytic Fourier-Bessel (J1) exact solution of the linear diffusion equation combined with a demonstrated 2nd-order L1(Bphi) convergence sweep (Fig. 8) — rubric row 5."

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
    params_used: { a: 0.4, eta: 1, Bphi_a: 0.0035449077018110317, t: 0.03 }
    method: "resistive (eta!=0) MHD induction update; single-sided static-polyline embedded boundary; Dirichlet fixed-Bphi enforcement"
    resolution: "24x24 (Fig. 8 left panel); a convergence sweep for the right panel, resolutions not individually enumerated"
    amr: "none"
    findings: "L1 error in Bphi converges at second order in Delta x (Fig. 8, right panel), compared against the Fourier-Bessel semi-analytic solution (eq. 74)."
related_to: [axial-field-relaxation-cylindrical-conductor]
headline_score: 5
---

## Physical problem
A cylindrical conductor of radius a=0.4 cm, with uniform magnetic diffusivity eta=1 cm^2/s and
zero initial internal magnetic field, has a toroidal (azimuthal) field Bphi(a)=sqrt(4*pi)*1e-3 G
imposed on its (embedded, polyline-represented) boundary. The field diffuses purely resistively
inward from the boundary toward the axis; there is no fluid motion (v=0).

## What this test actually tests
Whether the scheme's resistive operator, combined with a Dirichlet-enforced fixed toroidal field
at a rigid, non-grid-conformal cylindrical embedded boundary, reproduces the correct inward
diffusion of an azimuthal (rather than axial) field component and its second-order spatial
accuracy (azimuthal-field-l1-convergence).

## Qualitative behaviour
Bphi rises monotonically from 0 at the axis toward Bphi(a) at the boundary, approaching the
asymptotic t->infinity linear profile Bphi(a)*r/a as the transient Fourier-Bessel correction decays.

## Validation notes
Fig. 8 (right panel) shows the L1(Bphi) error at t=0.03 s converging at the theoretical second
order against the Fourier-Bessel series solution (eq. 74): Bphi(r,t)=Bphi(a)*[r/a - sum_n
c_n*J1(k_n*r)*exp(-eta*k_n^2*t)], with k_n the non-trivial positive roots of J1(k_n*a)=0 and
c_n=2/(k_n*a*J2(k_n*a)) chosen to satisfy Bphi(r,0)=0 for r<a.

## Notes
`b_field_convention: sqrt-4pi` follows the same convention used throughout the paper. As in the
axial-field sibling test, the specific Delta x values underlying the Fig. 8 convergence sweep are
not individually enumerated in the source text; only the left-panel's 24x24 resolution is stated
directly.
