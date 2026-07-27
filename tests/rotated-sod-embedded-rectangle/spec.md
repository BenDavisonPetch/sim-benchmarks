---
# Synthesized via /create-test from the free-text description "rotated Sod in an embedded
# rectangle". No source document — physics authored directly (SPEC §9.3). De-dup ran first
# against INDEX.tsv (only prior entry: mercury-magnetosphere-coupled-interior, a distinct
# mhd+magnetic-diffusion signature) — no structural match on any pass, so this is a NEW ENTRY,
# not a sibling (no plain "1D Sod" entry exists yet to link via related_to).

slug: rotated-sod-embedded-rectangle
name: "Rotated Sod Shock Tube in an Embedded Rectangle"
provenance: synthesized
one_liner: "Classic Sod shock tube posed inside a rigid-walled rectangular channel rotated 30 deg to the grid, embedded in a larger Cartesian domain."

physics:
  materials:
    - name: gas
      base: hydro                # inviscid Euler (no terms)
      terms: []
      eos:
        type: gamma-law
        params: { gamma: 1.4 }
  coupling: none                  # single material; the channel wall is a rigid-wall internal_boundary, not a material interface

dimension:
  intrinsic: 2                    # rotation relative to the grid is undefined in 1D
  runnable_in: [2]

analysis_treatments: [oblique-to-grid]   # the tube axis + diaphragm + channel walls are rotated off the Cartesian axes

capability_flags:
  time_dependent_bc: false        # no domain_bc state references t
  has_internal_boundaries: true   # internal_boundaries (rigid-wall channel) is non-empty
geometry_stress: none              # plain embedded rectangle, not an adversarial geometry (dedup §2.5 worked case)

geometry:
  coord_system: cartesian
  domain: { x: [-1.5, 1.5], y: [-1.5, 1.5] }
  regions:
    - id: channel                 # the fluid-filled tube: a box in its own (unrotated) local
                                   # frame, rotated about the domain center. Only this region
                                   # carries fluid state; outside it is solid (rigid-wall exterior).
      shape: box
      params:
        center: [0, 0]
        half_extents: [1.0, 0.2]  # [along-axis half-length, transverse half-width], pre-rotation
        rotate: { deg: 30, about: [0, 0] }

units:
  system: nondimensional          # classic Sod nondimensional units (rho, p, gamma only)
  b_field_convention: null        # no magnetic field in this problem (not applicable, not needs-source)

initial_conditions:
  aux:
    - { name: theta, expr: "rotation_deg * pi / 180" }   # tube-axis angle, radians
    - { name: xi,    expr: "x * cos(theta) + y * sin(theta)" }   # coordinate along the tube axis (center at origin)
  equilibrium:
    - region: channel
      fields:
        rho: "rho_L + (rho_R - rho_L) * step(xi, x0, x0)"   # step(a,a) = Heaviside at xi = x0 (diaphragm)
        p:   "p_L + (p_R - p_L) * step(xi, x0, x0)"
        vx:  "0"
        vy:  "0"
  perturbation:
    combine_rule: additive
    fields: []
  potentials: []

parameters:
  - { name: rotation_deg, canonical: 30,    meaning: "angle of the tube axis from the x-axis (degrees)" }
  - { name: x0,           canonical: 0,     meaning: "diaphragm position along the tube axis xi (channel is centered at xi=0)" }
  - { name: rho_L,        canonical: 1.0,   meaning: "left-state density (nondimensional)" }
  - { name: p_L,          canonical: 1.0,   meaning: "left-state pressure (nondimensional)" }
  - { name: rho_R,        canonical: 0.125, meaning: "right-state density (nondimensional)" }
  - { name: p_R,          canonical: 0.1,   meaning: "right-state pressure (nondimensional)" }

domain_bc:
  x_lo: { type: outflow }         # far exterior of the embedded channel; never reached by fluid before t_final
  x_hi: { type: outflow }
  y_lo: { type: outflow }
  y_hi: { type: outflow }

internal_boundaries:
  - kind: rigid-wall
    geometry: { region: channel, surface: boundary }   # no-penetration on all four sides of the rotated channel box
    motion: none

time:
  t_final: 0.2                    # classic Sod evaluation time; max feature excursion (~0.35 from diaphragm)
                                   # stays well inside the channel half-length (1.0), so no wall/end-cap
                                   # reflection contaminates the comparison
  snapshot_times: [0, 0.2]

validation_modes:
  - id: centerline-riemann-convergence
    purpose: "Verify convergence of density, velocity, and pressure sampled along the tube centerline to the exact self-similar Riemann solution as resolution refines, confirming the rotated/embedded rigid-wall representation does not degrade the scheme's formal accuracy."
    procedure: convergence-order
    inputs:
      at_time: 0.2
      variables: [rho, vx, p]
      sample_locus: "tube centerline (xi-axis through channel center), away from wall-adjacent cut cells"
      error_measure: "L1 norm (norms procedure) of numeric minus the exact Riemann solution, mapped to the rotated xi coordinate"
      resolution_sequence: "a refinement sequence at fixed ratio r (concrete levels recorded by whichever reference_result executes this)"
      reference: { kind: reference, key: toro2009 }
      tolerance: "measured order p within 0.2 of the theoretical first-order rate expected at the shock/contact discontinuities"
    has_exact_solution: true
    score: 5
    score_justification: "Exact closed-form self-similar Riemann solution (Toro) plus a measured convergence order along the unobstructed centerline — row 5, provided the oblique rigid-wall treatment does not corrupt the formal order away from the wall boundary layer."

  - id: shock-contact-rarefaction-locations
    purpose: "Verify the positions of the rarefaction head, rarefaction tail, contact discontinuity, and shock along the tube axis at a fixed time against the exact Riemann solution, testing correct feature propagation when the tube is oblique to the grid."
    procedure: feature-location
    inputs:
      at_time: 0.2
      variables: [rho]
      cut_lines: ["tube centerline (xi-axis)"]
      features: ["rarefaction head", "rarefaction tail", "contact discontinuity", "shock"]
      reference: { kind: reference, key: toro2009 }
      tolerance: "positions within 2 cells (measured along xi) of the exact self-similar locations"
    has_exact_solution: true
    score: 4
    score_justification: "Single-snapshot quantitative feature check against the exact solution (no convergence sweep in this mode, unlike centerline-riemann-convergence) — reliable automatable check, row 4."

  - id: channel-mass-conservation
    purpose: "Verify total fluid mass within the embedded rectangular channel is conserved over the run despite the oblique, small/partial cut cells along the rotated rigid-wall boundary — the small-cell problem is a known failure mode specifically for non-grid-aligned embedded/cut-cell walls, unlike an axis-aligned box."
    procedure: conservation-drift
    inputs:
      conserved_quantity: "total mass within the channel region (active-volume-fraction weighted)"
      evolve_time: [0, 0.2]
      drift_form: relative
      tolerance: "relative drift < 1e-3"
    has_exact_solution: false
    score: 3
    score_justification: "Quantitative, automatable drift-vs-tolerance check; genuinely discriminating here because the rotated channel walls force small/partial cut cells (unlike an axis-aligned box), a known conservation risk — not a literature or exact-solution comparison, so capped at row 3 (SPEC §6.4 universal-diagnostic rule)."

references: []
references_unverified:
  # Offline authoring (SPEC §5.2B): unverified until /add-refs (Stage 6, online) resolves it.
  - key: toro2009
    verification: { status: unverified, identifier: { doi: "10.1007/b79761" }, source: "", checked: null }
reference_results: []
related_to: []
headline_score: 5
---

## Physical problem
The classic Sod shock-tube discontinuity — a diaphragm separating a high-density/high-pressure
left state (rho=1, p=1) from a low-density/low-pressure right state (rho=0.125, p=0.1), gamma=1.4,
both initially at rest — posed inside a rigid-walled rectangular channel whose long axis is
rotated 30 degrees from the x-axis. The channel is embedded in a larger Cartesian computational
domain; outside the channel there is no fluid (solid, bounded by the channel's rigid walls on all
four sides).

## What this test actually tests
Whether a scheme reproduces the exact 1D Sod Riemann solution when the tube axis, diaphragm, and
confining rigid walls are all oblique to the underlying grid, and whether its embedded/cut-cell
treatment of the non-grid-aligned channel walls preserves both formal convergence order and total
mass conservation (centerline-riemann-convergence, shock-contact-rarefaction-locations,
channel-mass-conservation).

## Qualitative behaviour
Along the tube axis (xi), the exact solution is the standard Sod wave fan: a left-running
rarefaction (head near xi=-0.26, tail near xi=-0.07 at t=0.2), a contact discontinuity near
xi=0.19, and a right-running shock near xi=0.35 (rho_L=1,p_L=1,rho_R=0.125,p_R=0.1,gamma=1.4).
Transverse velocity (perpendicular to the tube axis) should remain exactly zero everywhere; a
scheme with a poor embedded/oblique-wall treatment may generate spurious transverse velocity near
the rotated walls — this is a specific, checkable trap, not a symmetry proxy that gridding could
silently break.

## Validation notes
centerline-riemann-convergence expects only first-order convergence (p~1) near the shock/contact
even for high-order schemes — this is the correct theoretical target, not row-5 inflation. The
resolution sequence and concrete grid levels are left to the reference_result that executes this
mode (method/resolution never belongs in the problem block, SPEC §1.6). toro2009 (Toro, "Riemann
Solvers and Numerical Methods for Fluid Dynamics") is the standard source for the exact self-similar
solution formulae used by all three modes; it is unverified pending /add-refs (offline authoring).

## Notes
Units are nondimensional (classic Sod convention); b_field_convention is null because this is a
pure-hydro problem with no magnetic field (not a needs-source gap). tube_half_length=1.0 and
t_final=0.2 are chosen so the maximum wave excursion (~0.35 from the diaphragm) stays well inside
the channel, away from the end-cap rigid walls — no wave/end-wall reflection occurs before
t_final. rotation_deg=30 mirrors the canonical example in registry/analysis-treatments/oblique-to-grid.md.
