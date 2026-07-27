---
# Authored via /add-test (NORMAL path) from Jones, McNally & Reynolds, "A constrained-transport
# embedded boundary method for compressible resistive magnetohydrodynamics", J. Comput. Phys. 550
# (2026) 114641 (citekey: jones2026), Section 7.10 "Compression of a theta-pinch".

slug: theta-pinch-compression-embedded-boundary
name: "Sub-Alfvenic Compression of a Theta-Pinch by a Moving Embedded Boundary"
provenance: literature
one_liner: "A uniform-Bz theta-pinch plasma is adiabatically compressed by a moving, reflecting perfect-conductor embedded boundary converging radially inward, validated against the adiabatic P-rho relation and mass/flux conservation drift."

physics:
  materials:
    - name: plasma
      base: mhd
      terms: []
      eos:
        type: gamma-law
        params: { gamma: 1.6666666666666667 }
  coupling: none   # single material; the moving wall is an internal_boundaries entry, not a material interface

dimension:
  intrinsic: 2
  runnable_in: [2]

analysis_treatments: [none]

capability_flags:
  time_dependent_bc: false   # the moving wall's motion is carried in internal_boundaries.motion, not a domain_bc state referencing t
  has_internal_boundaries: true
geometry_stress: none

geometry:
  coord_system: cartesian
  domain: { x: [-0.5, 0.5], y: [-0.5, 0.5] }   # "square domain of side length unity" (source), centered on the cylinder
  regions:
    - id: interior
      shape: cylinder
      params: { center: [0, 0], r: 0.4 }   # initial radius a=0.4 cm; shrinks per the moving boundary

units:
  system: cgs-gaussian
  b_field_convention: sqrt-4pi   # consistent with Bz = sqrt(4*pi) G as stated

initial_conditions:
  aux:
    - { name: a,     expr: "0.4" }
    - { name: rho0,  expr: "1" }
    - { name: P0,    expr: "10" }
    - { name: gamma, expr: "1.6666666666666667" }
    - { name: Bz0,   expr: "sqrt(4*pi)" }
  equilibrium:
    - region: interior
      fields:
        rho: "rho0"
        p: "P0"
        vx: "-(x/a)"    # v_r = -r/a, i.e. v = -(r/a)*r_hat
        vy: "-(y/a)"
        vz: "0"
        Bx: "0"
        By: "0"
        Bz: "Bz0"
  perturbation:
    combine_rule: additive
    fields: {}
  potentials: []

parameters:
  - { name: a,     canonical: 0.4,  meaning: "initial cylinder (embedded boundary) radius, cm" }
  - { name: rho0,  canonical: 1,    meaning: "initial density, g/cm^3" }
  - { name: P0,    canonical: 10,   meaning: "initial thermal pressure, Ba" }
  - { name: gamma, canonical: 1.6666666666666667, meaning: "ratio of specific heats (=5/3), global default" }
  - { name: Bz0,   canonical: 3.5449077018110318, meaning: "initial uniform axial field, G (= sqrt(4*pi))" }

domain_bc:
  x_lo: { type: outflow }   # outer square domain edge; never reached by the shrinking, fluid-filled interior before t_final
  x_hi: { type: outflow }
  y_lo: { type: outflow }
  y_hi: { type: outflow }

internal_boundaries:
  - kind: perfect-conductor-wall
    geometry: { region: interior, surface: boundary }
    motion: { type: prescribed-velocity, expr: "v_r = -r/a" }   # source: "moving polyline with specified motion following v_r=-r/a"; reflecting perfect conductor

time:
  t_final: 0.3   # snapshot times in Fig. 11 run 0.000 to 0.300 s
  snapshot_times: [0, 0.025, 0.05, 0.075, 0.1, 0.125, 0.15, 0.175, 0.2, 0.225, 0.25, 0.275, 0.3]

validation_modes:
  - id: central-adiabat-tracking
    purpose: "Verify the central (geometric-center) pressure and density trace the expected adiabatic relation P/P0=(rho/rho0)^gamma throughout the sub-Alfvenic compression."
    procedure: exact-solution-compare
    inputs:
      at_time: [0, 0.025, 0.05, 0.075, 0.1, 0.125, 0.15, 0.175, 0.2, 0.225, 0.25, 0.275, 0.3]
      variables: [rho, p]
      cut_lines: ["geometric center of the mesh cell containing the domain center"]
      reference: { kind: reference-result, key: jones2026 }
      tolerance: "central (rho,P) trace lies on the adiabat P/P0=(rho/rho0)^gamma to within plotting precision (Fig. 11, panel c)"
    has_exact_solution: false
    score: 3
    score_justification: "Quantitative comparison to a well-motivated reference relation (the adiabatic invariant, valid in the stated strongly sub-Alfvenic limit) rather than an exact solution of the full compressible MHD equations at finite radius — rubric row 3."

  - id: mass-flux-conservation-drift
    purpose: "Verify the total mass and total z-direction magnetic flux enclosed within the moving, embedded compressing boundary are conserved over the run, despite the moving cut-cell wall representation."
    procedure: conservation-drift
    inputs:
      conserved_quantity: "total mass and total Bz flux within the compressing interior region (active-volume/area-fraction weighted)"
      evolve_time: [0, 0.3]
      drift_form: relative
      tolerance: "source reports a small but nonzero, near-equal relative drift in both mass and Bz flux (Fig. 11, panel d) -- not exactly conserved, but the two errors track each other closely"
    has_exact_solution: false
    score: 3
    score_justification: "Automatable, quantitative drift-vs-time diagnostic, genuinely discriminating here because the compressing wall is a moving, non-grid-conformal embedded (cut-cell) boundary — a known conservation-error source the source itself explicitly discusses — rubric row 3 (SPEC §6.4 universal-diagnostic rule)."

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
    params_used: { a: 0.4, rho0: 1, P0: 10, gamma: 1.6666666666666667, Bz0: 3.5449077018110318, t_final: 0.3 }
    method: "ideal MHD; moving-polyline embedded boundary (Sect. 3.1/4.1), reflecting perfect-conductor wall, velocity = v_r=-r/a"
    resolution: "128^2 Cartesian mesh (initial resolution ~51.2 cells across the cylinder radius)"
    amr: "none"
    findings: "Central density/pressure trace the adiabat closely (Fig. 11c); total mass and Bz flux inside the compressing boundary show small, closely-tracking relative conservation errors (Fig. 11d)."
related_to: [parallel-pinch-compression-embedded-boundary]
headline_score: 3
---

## Physical problem
A cylindrical plasma of initial radius a=0.4 cm, uniform density rho0=1 g/cm^3, thermal pressure
P0=10 Ba, and a uniform axial field Bz0=sqrt(4*pi) G, is adiabatically compressed by a moving,
reflecting perfect-conductor embedded boundary contracting with radial velocity v_r=-r/a. The wall
motion is strongly sub-Alfvenic (the magnetic pressure is subdominant), so the compression is
smooth and quasi-uniform in density; MHD equations are solved only inside the (shrinking) boundary.

## What this test actually tests
Whether the scheme's moving-embedded-boundary MHD treatment (a moving polyline, reflecting
perfect-conductor wall) correctly captures adiabatic compressional heating (central-adiabat-tracking)
and whether the moving cut-cell representation introduces significant non-conservation of mass or
magnetic flux (mass-flux-conservation-drift).

## Qualitative behaviour
Density and axial field rise smoothly and nearly uniformly across the shrinking interior as the
wall contracts (Fig. 11a-b); the central pressure-density trace lies tightly on the adiabat
(Fig. 11c). The mass and Bz-flux conservation errors are small early (especially at higher
resolution) but diverge and become non-monotonic at later times/lower resolutions (Fig. 11d).

## Validation notes
No grid-convergence sweep is reported specifically for this test (Fig. 11 shows time snapshots at a
single 128^2 resolution, not multiple resolutions), so neither mode can reach rubric row 4/5;
both are capped at row 3. The companion parallel-pinch compression test
(parallel-pinch-compression-embedded-boundary) is explicitly noted by the source to behave
differently because it has a nonzero in-plane (Bphi) field component.

## Notes
`internal_boundaries[0].motion` records the source's stated boundary velocity profile
(v_r=-r/a) as free text; the repository schema does not yet define a strict structured form for
prescribed boundary motion beyond "geometry + optional motion" (SPEC §1.10) — this is recorded
in the clearest available form rather than left blank. The outer square domain edges
(`domain_bc`) are physically inert (never reached by the shrinking fluid region before t_final) and
set to `outflow` by the same convention used in `rotated-sod-embedded-rectangle`.
