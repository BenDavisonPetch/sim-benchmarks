---
# Authored via /add-test (NORMAL path) from Toro, "Riemann Solvers and Numerical Methods for Fluid
# Dynamics", 3rd ed. (2009), Ch. 17 Sect. 17.1.1 (citekey: toro2009). Sibling of explosion-spherical-3d.

slug: explosion-cylindrical-2d
name: "Cylindrical Explosion (2D Euler)"
provenance: literature
one_liner: "Circular high-pressure/high-density region (R=0.4) in a 2x2 square at rest, ideal gas gamma=1.4; outward shock, contact and inward rarefaction compared with the equivalent 1D radial (cylindrical-symmetry) solution."

physics:
  materials:
    - name: gas
      base: hydro
      terms: []
      eos:
        type: gamma-law
        params: { gamma: 1.4 }          # source-stated (Sect. 17.1: ideal gases with gamma = 1.4)
  coupling: none

dimension:
  intrinsic: 2
  runnable_in: [2]

analysis_treatments: [none]

capability_flags:
  time_dependent_bc: false
  has_internal_boundaries: false         # single material; the initial discontinuity is an IC, not a boundary
geometry_stress: none

geometry:
  coord_system: cartesian
  domain: { x: [0, 2], y: [0, 2] }
  regions:
    - { id: whole, shape: box, params: { center: [1, 1], half_extents: [1, 1] } }   # entire domain; the IC expressions below carry the inside/outside split
    - id: blast
      shape: cylinder
      params: { center: [1, 1], r: 0.4 }

units:
  system: nondimensional                 # Sect. 17.1: no units stated (dimensionless)
  b_field_convention: null               # no magnetic field

initial_conditions:
  aux:
    - { name: r_c, expr: "sqrt((x-1)**2 + (y-1)**2)" }      # distance from the blast centre
  equilibrium:
    - region: whole
      fields:
        rho: "rho_out + (rho_ins - rho_out) * step(R - r_c, 0, 0)"
        p: "p_out + (p_ins - p_out) * step(R - r_c, 0, 0)"
        vx: "0"
        vy: "0"
  perturbation:
    combine_rule: additive
    fields: []
  potentials: []

parameters:
  - { name: R,       canonical: 0.4,   meaning: "radius of the initial high-pressure region (nondimensional)" }
  - { name: rho_ins, canonical: 1.0,   meaning: "density inside the circle (nondimensional)" }
  - { name: rho_out, canonical: 0.125, meaning: "density outside the circle (nondimensional)" }
  - { name: p_ins,   canonical: 1.0,   meaning: "pressure inside the circle (nondimensional)" }
  - { name: p_out,   canonical: 0.1,   meaning: "pressure outside the circle (nondimensional)" }

domain_bc:
  x_lo: { type: outflow }   # NOT stated by source; placeholder (see Notes)
  x_hi: { type: outflow }   # NOT stated by source; placeholder (see Notes)
  y_lo: { type: outflow }   # NOT stated by source; placeholder (see Notes)
  y_hi: { type: outflow }   # NOT stated by source; placeholder (see Notes)

internal_boundaries: []

time:
  t_final: 0.25
  snapshot_times: [0, 0.25]

validation_modes:
  - id: radial-profile-vs-1d-reference
    purpose: "Verify density, radial velocity, pressure and internal energy sampled along the x-axis (through the blast centre) at t=0.25 against the equivalent one-dimensional radial (alpha=1) geometric-source-term solution, testing that the 2D Cartesian discretisation reproduces the cylindrically-symmetric solution."
    procedure: norms
    inputs:
      at_time: 0.25
      variables: [rho, vx, p, e_int]
      sample_locus: "radial line coincident with the x-axis through the blast centre, r in [0, 1]"
      error_measure: "L1 norm of (multi-D solution minus 1D radial solution), 1D profile interpolated to sample points; no tolerance stated by source"
      reference: { kind: reference-result, key: toro2009 }
      tolerance: "not stated by source; Toro reports qualitative agreement only (Fig. 17.4) -- pick a tolerance when running"
    has_exact_solution: false
    score: 3
    score_justification: "Category (B) reference: reliable but numerical 1D radial solution, not exact/analytic and not convergence-tested here. Quantitative comparison to a reference result along one cut-line, partial coverage -> row 3 (no-exact-solution comparison caps at 3)."

  - id: wave-positions-vs-1d-reference
    purpose: "Verify the positions of the outward shock, outward contact surface and inward-travelling rarefaction along the x-axis at t=0.25 against the 1D radial reference solution."
    procedure: feature-location
    inputs:
      at_time: 0.25
      variables: [rho]
      cut_lines: ["x-axis through the blast centre"]
      features: ["shock", "contact discontinuity", "rarefaction"]
      reference: { kind: reference-result, key: toro2009 }
      tolerance: "not stated by source; Toro states shock resolved with two mesh points and contact with two to three (101x101 mesh, 2D)"
    has_exact_solution: false
    score: 3
    score_justification: "Quantitative position check against a reference numerical solution (not exact); specific named features, automatable, but reference is numerical (category B) so capped at row 3."

references:
  - key: toro2009
    verification:
      status: verified
      identifier: { doi: "10.1007/b79761" }
      source: "crossref: 10.1007/b79761 -> 200"
      checked: "2026-11-06"
      meta:
        year: 2009
        first_author: Toro
        container: Springer Berlin Heidelberg
        title: "Riemann Solvers and Numerical Methods for Fluid Dynamics"
references_unverified: []
test_origin:
  status: pending
  authored_from: toro2009
  attribution_claims: []                 # no sentence in the source says where this test originated
reference_results:
  - key: toro2009
    params_used: { gamma: 1.4, R: 0.4, rho_ins: 1.0, rho_out: 0.125, p_ins: 1.0, p_out: 0.1, t: 0.25 }
    method: "2D Euler: WAF (Ch.14) with space splitting (Sect.16.2), HLLC Riemann solver, vanleer limiter, CFL 0.9, area-weighted initial data on cells cut by the discontinuity. 1D radial reference: Random Choice Method (Ch.7) + splitting for geometric source term (Ch.15), CFL 0.4."
    resolution: "2D: 101x101 cells; 1D radial RCM: M=1000 cells on r in [0,1]"
    amr: "none"
    findings: >
      Fig. 17.4: 2D WAF solution (symbols) vs 1D radial RCM solution (line) along the x-axis at t=0.25, profiles of density, velocity, pressure, internal energy. Shock wave resolved with two mesh points and contact surface with two to three mesh points. Comparisons along other radial directions give virtually identical results; solution very symmetric (Figs. 17.2, 17.3). Toro regards the RCM solution as the exact solution (RCM resolves discontinuities as true discontinuities).
related_to: [explosion-spherical-3d]
headline_score: 3
---

## Physical problem
Two-dimensional Euler equations (ideal gas, gamma=1.4) on a 2.0 x 2.0 square in the x-y plane. Inside a circle of radius R=0.4 centred at (1,1) the gas is at rest with rho=1.0, p=1.0; outside, at rest with rho=0.125, p=0.1. The circular discontinuity at t=0 is the 2D analogue of a shock tube. Run to t=0.25.

## What this test actually tests
Whether a 2D Cartesian Euler scheme preserves cylindrical symmetry and resolves a circular shock, contact and inward rarefaction as sharply as in 1D, judged against the equivalent 1D radial solution (radial-profile-vs-1d-reference, wave-positions-vs-1d-reference).

## Qualitative behaviour
At t=0.25 the solution has an outward cylindrical shock, a cylindrical contact surface travelling the same direction, and a cylindrical rarefaction travelling toward the centre; pressure is continuous across the contact. Comparisons along other radial directions give virtually identical results (Toro). At later times (not scored) a complex wave pattern emerges: the shock weakens as it expands, the contact weakens and comes to rest then moves inward, the rarefaction reflects as a rarefaction and over-expands to form an inward shock that implodes into the origin and reflects outward, colliding with the contact.

## Validation notes
Reference is category (B) in Toro's classification: a reliable numerical solution of the equivalent 1D inhomogeneous equations U_t + F(U)_r = S(U), alpha=1, not an exact solution; Toro computes it on r in [0,1]. Toro's profile comparison (Fig. 17.4: density, velocity, pressure, internal energy vs position) is graphical; no numeric values or tolerances are stated, so none are recorded. Symmetry across radial directions is stated qualitatively and is not scored (no registry procedure; symmetry is not a reliable proxy under non-uniform gridding).

## Notes
Units dimensionless. Boundary conditions are NOT stated by the source. domain_bc `outflow` is a placeholder inference, not sourced: the equivalent 1D radial problem is solved on r in [0,1] (the inscribed circle/sphere of the domain) and compared at t=0.25, which implies waves do not reach r=1; the Fig. 17.4/17.7 profiles are not read here, so this is unconfirmed. Flagged unresolved. Initial data on cells cutting the discontinuity are area-weighted in Toro's runs (method, recorded in reference_results only). The source remarks the data can be reversed to give an implosion problem; not authored here.
