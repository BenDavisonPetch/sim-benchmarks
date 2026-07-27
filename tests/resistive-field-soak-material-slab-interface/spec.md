---
# Authored via /add-test (NORMAL path) from Jones, McNally & Reynolds, "A constrained-transport
# embedded boundary method for compressible resistive magnetohydrodynamics", J. Comput. Phys. 550
# (2026) 114641 (citekey: jones2026), Section 7.8 "Resistive magnetic field soak from one material
# slab to another".

slug: resistive-field-soak-material-slab-interface
name: "Resistive Field Soak Across a Planar Two-Material Slab Interface"
provenance: literature
one_liner: "A magnetic field diffuses resistively across a flat contact interface between two mechanically-equilibrated materials with different resistivities, producing first-order L1 convergence due to the discontinuity in resistivity."

physics:
  materials:
    - name: field_side
      base: mhd
      terms: [resistivity]
      eos:
        type: gamma-law
        params: { gamma: 1.6666666666666667 }   # not restated for this test; source-stated global default
      material_fields:
        - { name: eta, region: field_side, expr: "1e7", units: "cm^2/s" }
    - name: no_field_side
      base: mhd
      terms: [resistivity]
      eos:
        type: gamma-law
        params: { gamma: 1.6666666666666667 }
      material_fields:
        - { name: eta, region: no_field_side, expr: "4e6", units: "cm^2/s" }
  coupling: material-contact

dimension:
  intrinsic: 2     # the interface offset from the cell face is a genuinely 2D cut-cell concern, even though the field profile itself is 1D-like across y
  runnable_in: [2]

analysis_treatments: [multi-material-interface]

capability_flags:
  time_dependent_bc: false
  has_internal_boundaries: true   # physics.coupling != none
geometry_stress: none

geometry:
  coord_system: cartesian
  domain: { x: [0, 0.125], y: [0.5, 1.5] }   # source: "extents 0.125 cm by 1 cm"; y-placement (straddling the y=1 interface) inferred -- see Notes
  regions:
    - id: field_side
      shape: box
      params: { x: [0, 0.125], y: [0.5, 1] }
    - id: no_field_side
      shape: box
      params: { x: [0, 0.125], y: [1, 1.5] }

units:
  system: cgs-gaussian
  b_field_convention: sqrt-4pi   # consistent with Bx = sqrt(4*pi)*1e3 G as stated

initial_conditions:
  aux:
    - { name: rho0,   expr: "1000" }        # both materials, g/cm^3
    - { name: P0,     expr: "6e6" }         # both materials, Ba
    - { name: Bx0,    expr: "sqrt(4*pi)*1e3" }   # field-side initial field, G
    - { name: eta1,   expr: "1e7" }         # field-side resistivity, cm^2/s
    - { name: eta2,   expr: "4e6" }         # no-field-side resistivity, cm^2/s
  equilibrium:
    - region: field_side
      fields: { rho: "rho0", p: "P0", vx: "0", vy: "0", vz: "0", Bx: "Bx0", By: "0", Bz: "0" }
    - region: no_field_side
      fields: { rho: "rho0", p: "P0", vx: "0", vy: "0", vz: "0", Bx: "0", By: "0", Bz: "0" }
  perturbation:
    combine_rule: additive
    fields: {}
  potentials: []

parameters:
  - { name: rho0, canonical: 1000,                meaning: "uniform density, both materials, g/cm^3" }
  - { name: P0,   canonical: 6000000,             meaning: "uniform mechanical-equilibrium pressure, both materials, Ba" }
  - { name: Bx0,  canonical: 177.24538509055159,  meaning: "initial uniform field on the field-carrying side, G (= sqrt(4*pi)*1e3)" }
  - { name: eta1, canonical: 1e7,                 meaning: "resistivity of the field-carrying material, cm^2/s" }
  - { name: eta2, canonical: 4e6,                 meaning: "resistivity of the initially-field-free material, cm^2/s" }

domain_bc:
  x_lo: { type: neumann }
  x_hi: { type: neumann }
  y_lo: { type: neumann }
  y_hi: { type: neumann }

internal_boundaries: []   # the field_side/no_field_side coupling is the material boundary (physics.coupling)

time:
  t_final: 2e-9   # source: "Results at t=2e-9 s"
  snapshot_times: [2e-9]

validation_modes:
  - id: bx-l1-first-order-convergence
    purpose: "Verify first-order L1 convergence of the cell-averaged Bx across the resistivity-discontinuous material interface, against an analytic diffusion solution."
    procedure: convergence-order
    inputs:
      at_time: 2e-9
      variables: [Bx]
      resolution_sequence: [0.0625, 0.03125, 0.015625, 0.0078125]   # Delta y in cm, from Fig. 9
      expected_order: 1
      reference: { kind: reference-result, key: jones2026 }
      tolerance: "measured L1(Bx) order approaches the theoretical 1st order (not 2nd) as Delta y -> 0, due to the discontinuity in resistivity at the interface (Fig. 9)"
    has_exact_solution: true
    score: 5
    score_justification: "Analytic diffusion solution across the discontinuous-resistivity interface (labeled 'exact' in Fig. 9) combined with a demonstrated 1st-order L1(Bx) convergence sweep matching the theoretically-expected reduced order at a resistivity discontinuity — rubric row 5 (the theoretical order here is 1, not 2, and the scheme matches it)."

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
    params_used: { rho0: 1000, P0: 6e6, Bx0: 177.24538509055159, eta1: 1e7, eta2: 4e6, t: 2e-9 }
    method: "resistive MHD induction update; ghost-fluid two-material coupling (Sect. 3.2/4.2); static level-set interface; interface deliberately offset by sin(1)*Delta y from the cell face at each resolution to stress-test the cut-cell method (results shifted back to y=1 for display)"
    resolution: "Delta y in {0.0625, 0.03125, 0.015625, 0.0078125} cm"
    amr: "none"
    findings: "L1 error of the cell-averaged Bx converges at first order in Delta y (Fig. 9), matching the theoretical reduction from 2nd to 1st order caused by the resistivity discontinuity at the interface."
related_to: [resistive-field-soak-cylindrical-material-interface]
headline_score: 5
---

## Physical problem
Two adjacent materials of equal density (rho0=1000 g/cm^3) and pressure (P0=6e6 Ba, in mechanical
equilibrium) but different magnetic diffusivities (eta1=1e7 cm^2/s, eta2=4e6 cm^2/s) meet at a flat
contact interface. One material carries a uniform initial field Bx0=sqrt(4*pi)*1e3 G; the other
starts with zero field. The field diffuses resistively across the interface into the
initially-field-free material.

## What this test actually tests
Whether the scheme's two-material ghost-fluid resistive coupling correctly reproduces the expected
*reduced* (first-order, not second-order) convergence rate that a genuine discontinuity in
resistivity imposes on the resistive operator (bx-l1-first-order-convergence) — i.e. that the
scheme is not spuriously over- or under-converging at a genuine material discontinuity.

## Qualitative behaviour
Bx falls smoothly from its initial value on the field-carrying side, through the interface, to zero
on the field-free side, with a kink in slope at the interface reflecting the discontinuous
resistivity (Fig. 9, left panel).

## Validation notes
Fig. 9 (right panel) shows the L1(Bx) error at t=2e-9 s converging at first order (not the usual
second order) across four resolutions (Delta y = 0.0625 down to 0.0078125 cm) — this reduced rate
is the theoretically expected consequence of the discontinuity in resistivity at the material
interface, and the source explicitly states this expectation is "reflected in the numerical
results."

## Notes
The exact y-domain placement (`geometry.domain.y`, chosen here as `[0.5, 1.5]` so the stated
interface location y=1 sits at the domain midpoint) is inferred: the source states only the domain
*extents* (0.125 cm by 1 cm) and the interface location (y=1, after re-centering for display), not
the absolute domain placement. At each resolution the source actually offsets the interface by
`sin(1)*Delta y` from the nearest cell face (a per-run, mesh-dependent stress-test of the cut-cell
method) and shifts the plotted results back to y=1 for interpretability; this resolution-dependent
offset is a method/reference_result detail, not part of the canonical physical geometry, so the
canonical interface here is placed at the clean y=1 plane. Which named material (`field_side` vs
`no_field_side`) sits on which side of y=1 is not stated in the source and is an arbitrary
assignment here. `intrinsic: 2` because the resolution study's sub-cell interface offset (see above) is inherently a
2D cut-cell concern, even though the source describes the field profile itself as "locally
essentially one-dimensional behavior."
