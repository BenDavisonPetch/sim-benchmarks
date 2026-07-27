---
# Authored via /add-test (NORMAL path) from Jones, McNally & Reynolds, "A constrained-transport
# embedded boundary method for compressible resistive magnetohydrodynamics", J. Comput. Phys. 550
# (2026) 114641 (citekey: jones2026), Section 7.5 "Tangential field soak into conducting slab".

slug: tangential-field-soak-conducting-slab
name: "Tangential Field Soak into a Conducting Slab"
provenance: literature
one_liner: "A resistivity-only conducting square with a Dirichlet-imposed tangential field on its embedded boundary, verified near the side midpoints against a semi-analytic error-function/Fourier series solution of the pure diffusion equation."

physics:
  materials:
    - name: conductor
      base: magnetic-diffusion
      terms: [resistivity]
      material_fields:
        - { name: eta, region: interior, expr: "1000", units: "cm^2/s" }
  coupling: none

dimension:
  intrinsic: 2       # a finite square with corners; the 1D-like semi-analytic reference is only valid far from them
  runnable_in: [2]

analysis_treatments: [none]

capability_flags:
  time_dependent_bc: false
  has_internal_boundaries: false
geometry_stress: none

geometry:
  coord_system: cartesian
  domain: { x: [0, 1], y: [0, 1] }   # 1 cm conducting square IS the domain edge (physical); the source's "1.2 cm domain" is the outer MESH extent for cut cells, a method detail
  regions:
    - id: interior
      shape: box
      params: { center: [0.5, 0.5], half_extents: [0.5, 0.5] }

units:
  system: cgs-gaussian
  b_field_convention: sqrt-4pi   # consistent with B.t = sqrt(4*pi) G as stated

initial_conditions:
  aux:
    - { name: L,       expr: "1" }          # conductor side length, cm
    - { name: eta,     expr: "1000" }        # resistivity, cm^2/s
    - { name: B_bc,    expr: "sqrt(4*pi)" }  # imposed tangential field magnitude, G
  equilibrium:
    - region: interior
      fields:
        Bx: "0"
        By: "0"
        Bz: "0"
  perturbation:
    combine_rule: additive
    fields: {}
  potentials: []

parameters:
  - { name: L,    canonical: 1,    meaning: "conductor (embedded boundary) side length, cm" }
  - { name: eta,  canonical: 1000, meaning: "resistivity / magnetic diffusivity, cm^2/s" }
  - { name: B_bc, canonical: 3.5449077018110318, meaning: "imposed boundary-tangential field magnitude, G (= sqrt(4*pi))" }

domain_bc:
  # "external field along its boundary with B.t=sqrt(4*pi) G, B.n=Bz=0" -- tangential-only field on
  # each face, rotating direction with the wall (By on the vertical faces, Bx on the horizontal
  # faces) so the field is purely tangential and zero-normal everywhere on the square, consistent
  # with the stated boundary description (not spelled out per-face in the source; inferred from
  # the stated general boundary condition + square symmetry, see Notes).
  x_lo: { type: dirichlet, state: { By: "B_bc", Bx: "0", Bz: "0" } }
  x_hi: { type: dirichlet, state: { By: "B_bc", Bx: "0", Bz: "0" } }
  y_lo: { type: dirichlet, state: { Bx: "B_bc", By: "0", Bz: "0" } }
  y_hi: { type: dirichlet, state: { Bx: "B_bc", By: "0", Bz: "0" } }

internal_boundaries: []

time:
  t_final: 3e-6   # source: "L1 error in the numerical result at t=3e-6 s"
  snapshot_times: [3e-6]

validation_modes:
  - id: bx-l1-convergence
    purpose: "Verify second-order spatial L1 convergence of Bx toward the semi-analytic error-function-series diffusion solution, sampled near the side midpoints (away from corners)."
    procedure: convergence-order
    inputs:
      at_time: 3e-6
      variables: [Bx]
      sample_locus: "interface-normal direction through the side midpoints, far from the corners (source: 'far from the corners, e.g. the side midpoints')"
      resolution_sequence: [0.0343, 0.0171, 0.00857, 0.00429]   # Delta y in cm, from Fig. 6
      expected_order: 2
      reference: { kind: reference-result, key: jones2026 }
      tolerance: "measured L1(Bx) order approaches the theoretical 2nd order as Delta y -> 0 (Fig. 6, right panel)"
    has_exact_solution: true
    score: 5
    score_justification: "Accurate semi-analytic solution (error-function series, eq. 71/72, converging to machine precision) combined with a demonstrated 2nd-order L1(Bx) convergence sweep (Fig. 6) — rubric row 5."

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
    params_used: { L: 1, eta: 1000, B_bc: 3.5449077018110318, t: 3e-6 }
    method: "resistive (eta!=0) MHD induction update; single-sided static-polyline embedded boundary; Dirichlet tangential-field enforcement (Sect. 4.1)"
    resolution: "Delta y in {0.0343, 0.0171, 0.00857, 0.00429} cm"
    amr: "none"
    findings: "L1 error in Bx converges at second order in Delta y (Fig. 6, right panel), compared against the error-function-series semi-analytic solution (eq. 71)."
related_to: []
headline_score: 5
---

## Physical problem
A square conducting slab of side length L=1 cm, with uniform resistivity eta=1000 cm^2/s and zero
initial magnetic flux density, is subjected to an externally imposed field that is everywhere
tangential to its (embedded, polyline-represented) boundary, of magnitude B_bc=sqrt(4*pi) G, with
zero normal (in-plane) and zero out-of-plane (Bz) component. The field diffuses inward purely by
resistive (magnetic-diffusion) transport; there is no fluid motion (v=0).

## What this test actually tests
Whether the scheme's resistive (Ohmic) operator, combined with a Dirichlet-enforced tangential
field at a rigid, non-grid-conformal embedded boundary, reproduces the correct 1D-like diffusion
profile and its second-order spatial accuracy (bx-l1-convergence).

## Qualitative behaviour
Near the side midpoints (away from the corners, where the true 2D corner behavior deviates from
the 1D-like reference), Bx rises smoothly from 0 in the interior toward B_bc at the boundary,
following the classic error-function diffusion front shape.

## Validation notes
Fig. 6 (right panel) shows the L1(Bx) error at t=3e-6 s across four resolutions
(Delta y = 0.0343 down to 0.00429 cm), converging at the theoretical second order, compared against
the error-function series (eq. 71, N=6 terms, valid while the diffusion length (eta*t)^0.5 < L/2)
used as the reference for this short-time comparison; the source notes the alternative rapidly
converging Fourier series (eq. 72) is more accurate at longer times (not needed here).

## Notes
The exact per-face tangential-field assignment (`domain_bc`) is inferred from the source's general
description ("external field along its boundary with B.t=sqrt(4*pi) G, B.n=Bz=0") combined with
the square's four-fold symmetry — the source does not spell out Bx/By assignment per individual
face. `b_field_convention: sqrt-4pi` follows the same convention used throughout the paper's other
tests with a stated sqrt(4*pi)-scaled field magnitude.
