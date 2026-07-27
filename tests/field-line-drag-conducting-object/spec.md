---
# Authored via /add-test (NORMAL path) from Jones, McNally & Reynolds 2026, "A constrained-transport
# embedded boundary method for compressible resistive magnetohydrodynamics", J. Comput. Phys. 550
# (2026) 114641 (citekey: jones2026), Section 7.4 "Field line drag around perfectly conducting
# object". No analytic solution stated (source: "in this qualitative problem there is no analytic
# solution available") -- qualitative validation only.
#
# DEDUP: no existing entry shares this physics_signature (mhd/gamma-law, single material, no
# coupling) + analysis_treatments + capability_flags combination against a static, tangential-field
# perfect-conductor boundary; closest siblings by internal-boundary kind are the embedded-boundary
# compression tests (theta/parallel-pinch-compression-embedded-boundary), linked via related_to.
# NEW ENTRY.
#
# SCHEMA GAP (flagged, not resolved here): the source's two rotated-rounded-square boundary variants
# have corners rounded to a radius of 0.15 cm; none of the fixed geometry primitives (box, cylinder,
# sphere, shell, halfspace, polygon) or their rotate/translate transforms support a corner-fillet
# radius. Represented below as a plain rotated box (side 0.5 cm) with the corner rounding *omitted*
# -- see Notes. This is a structural-primitive gap (no place to put a fillet radius), not a missing
# registry id, so it is not routed through vocab-extension.

slug: field-line-drag-conducting-object
name: "Field Line Drag Around a Perfectly Conducting Object"
provenance: literature
one_liner: "A tangential magnetic-field band advected by a uniform cross-flow wraps around a static, perfectly-conducting embedded-boundary object (circle, and a rotated rounded-square approximated as a rotated box); validated qualitatively by field-line no-penetration/topology and quantitatively by div-B preservation in the active mesh."

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
geometry_stress: none   # see Notes: the rotated rounded-square variant is arguably purpose-built to
                        # stress non-grid-aligned boundary handling, but no registry/geometry-stress
                        # id exists yet for this -- deferred to a batched vocab proposal, not set here

geometry:
  coord_system: cartesian
  domain: { x: [0, 1], y: [0, 2] }   # source body text, Sect. 7.4; Fig. 5 caption says "domain shown is 32x32 cells" -- see Notes (unresolved discrepancy, recorded verbatim, not resolved)
  regions:
    - id: obstacle
      shape: cylinder
      params: { center: [0.5, 1.0], r: 0.25 }   # canonical (circular) variant

units:
  system: cgs-gaussian
  b_field_convention: sqrt-4pi

initial_conditions:
  aux:
    - { name: rho0, expr: "1" }
    - { name: P0,   expr: "50" }
    - { name: vy0,  expr: "0.75" }
    - { name: Bx0,  expr: "(sqrt(4*pi)/8) * cos(pi/8) * (1/(1+exp(-75*(y-0.2)))) * (1 - 1/(1+exp(-75*(y-0.6))))" }   # source eq. (70)
  equilibrium:
    - region: obstacle
      fields:
        rho: "rho0"
        p: "P0"
        vx: "0"
        vy: "vy0"
        Bx: "Bx0"
        By: "0"
        Bz: "0"
  perturbation:
    combine_rule: additive
    fields: {}
  potentials: []

parameters:
  - { name: rho0, canonical: 1,    meaning: "uniform initial density, g/cm^3" }
  - { name: P0,   canonical: 50,   meaning: "uniform initial gas pressure, Ba" }
  - { name: vy0,  canonical: 0.75, meaning: "uniform initial y-velocity, cm/s" }
  - { name: obstacle_radius, canonical: 0.25, meaning: "circular embedded-boundary radius, cm (canonical shape variant)" }
  - { name: square_side, canonical: 0.5, meaning: "rounded-square variant: side length before rounding, cm" }
  - { name: square_corner_radius, canonical: 0.15, meaning: "rounded-square variant: corner fillet radius, cm -- NOT representable by any current geometry primitive (schema gap), omitted from the region encoding below" }
  - { name: square_rotation_1, canonical: 1.5707963267948966, meaning: "rounded-square variant 1 rotation angle, rad (= pi/2)" }
  - { name: square_rotation_2, canonical: 0.19634954084936207, meaning: "rounded-square variant 2 rotation angle, rad (= pi/16)" }

domain_bc:
  x_lo: { type: periodic }
  x_hi: { type: periodic }
  y_lo: { type: periodic }
  y_hi: { type: periodic }

internal_boundaries:
  - kind: perfect-conductor-wall
    geometry: { region: obstacle, surface: boundary }
    motion: none

time:
  t_final: 0.8   # "Results at time t=0.8 s are shown in Fig. 5" (Sect. 7.4)
  snapshot_times: [0.8]

validation_modes:
  - id: div-b-preservation-active-mesh
    purpose: "Verify the magnetic divergence remains at roundoff throughout the active (non-cut) mesh as the tangential field wraps around a static perfect-conductor embedded boundary, specifically testing whether the boundary's cut-cell truncation error stays confined to the boundary layer rather than polluting the bulk active mesh."
    procedure: div-b
    inputs:
      at_time: 0.8
      variables: [B]
      tolerance: "div(B) at roundoff everywhere in the active mesh (source: 'no divergence appears in the magnetic field in the active mesh'); cut cells may show a finite, boundary-confined effective resistivity"
    has_exact_solution: false
    score: 3
    score_justification: "Universal div-B diagnostic, scored here because the source explicitly asserts this as the discriminating claim for this test (cut-cell truncation error acts like a finite numerical resistivity localized to the boundary, while the active mesh stays divergence-free) -- capped at rubric row 3 (SPEC §6.4), no exact solution or literature quantitative anchor available."

  - id: field-wrap-topology-qualitative
    purpose: "Verify the tangential field band wraps around the embedded-boundary object without net penetration -- every flux line entering the boundary re-emerges elsewhere -- matching the qualitative field-and-flow topology shown in Fig. 5 at t=0.8 s for the circular obstacle."
    procedure: feature-location
    inputs:
      at_time: 0.8
      variables: [Bx, By]
      cut_lines: ["visual inspection of field-line topology around the obstacle, per Fig. 5"]
      features: ["field lines wrap around the object with no net penetration", "flow wraps around the object consistently with the field"]
      reference: { kind: reference-result, key: jones2026 }
      tolerance: "qualitative visual match only -- no numeric position criterion is stated for this test (no analytic solution, source: 'in this qualitative problem there is no analytic solution available')"
    has_exact_solution: false
    score: 2
    score_justification: "No automatable check and no exact solution; but the expected topology is a specific, named, checkable feature (no-net-penetration field wrapping) rather than a vague visual impression -- rubric row 2."
    baseline:
      description: "rounded-square obstacle (approximated here as a rotated box, corner rounding omitted -- see Notes) rotated pi/2 rad instead of the canonical circular obstacle"
      config_delta: { "geometry.regions[0].shape": "box", "geometry.regions[0].params": "{center:[0.5,1.0], half_extents:[0.25,0.25], rotate:{deg:90, about:[0.5,1.0]}}" }
    measured: "whether the same qualitative field-wrap/no-penetration topology is reproduced across obstacle shape/rotation (circle vs rotated rounded-square at pi/2 and pi/16 rad), per source: 'the same qualitative behavior is observed for a range of numerical resolutions' across the three shape variants shown in Fig. 5"

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
    params_used: { rho0: 1, P0: 50, vy0: 0.75, obstacle_radius: 0.25, t_final: 0.8 }
    method: "ideal MHD; static-polyline embedded perfect-conductor boundary, tangential-E=0 enforcement (Sect. 4.1); staggered constrained transport; HLLD Riemann solver; 32x64 Cartesian mesh (body text) or possibly a cropped 32x32 view (Fig. 5 caption, see Notes); three boundary shapes (circle; rounded square rotated pi/2 and pi/16 rad) at a range of resolutions"
    resolution: "32x64 cells (body text); Fig. 5 caption states '32x32 cells' for the domain shown -- discrepancy recorded verbatim, not resolved"
    amr: "none"
    findings: "Field wraps around all three obstacle shapes without net penetration in the active mesh; same qualitative behavior across a range of resolutions (Fig. 5, t=0.8 s)."
related_to: [theta-pinch-compression-embedded-boundary, parallel-pinch-compression-embedded-boundary]
headline_score: 3
---

## Physical problem
A uniform-density (rho0=1 g/cm^3), uniform-pressure (P0=50 Ba) fluid carrying a smooth horizontal
band of tangential magnetic field Bx(y) (source eq. 70) is advected by a uniform y-velocity
(vy0=0.75 cm/s) across a static, perfectly-conducting embedded-boundary object centered at
(0.5, 1.0) cm. Three obstacle-shape variants are considered: a circle of radius 0.25 cm (canonical
here), and a rounded square of side 0.5 cm with 0.15 cm corner fillets rotated pi/2 and pi/16 rad
relative to the mesh (both approximated, with the fillet omitted, as a rotated box -- see Notes).
Domain is periodic in both directions.

## What this test actually tests
Whether the scheme's embedded-boundary treatment of a perfectly-conducting object correctly drags
and wraps a tangential magnetic field around a static, non-grid-conformal (and, for the square
variants, non-mesh-aligned) obstacle without spurious field penetration or divergence buildup in the
active mesh (field-wrap-topology-qualitative, div-b-preservation-active-mesh), and whether this
qualitative behavior is shape/rotation-invariant (the config_delta baseline).

## Qualitative behaviour
By t=0.8 s the initially-horizontal field band has wrapped around the obstacle in both flow and
field, with no field lines crossing the active-mesh boundary of the object; any flux crossing occurs
only through evolved cut-cell faces, behaving like a finite, boundary-localized numerical
resistivity (source, Sect. 7.4). No analytic solution exists for this test (source states this
explicitly) -- validation here is qualitative topology matching plus the automatable div-B check.

## Validation notes
Fig. 5 (Sect. 7.4) shows the wrapped field/flow pattern for all three obstacle shapes at t=0.8 s. The
source reports the same qualitative behavior "for a range of numerical resolutions", supporting the
resolution-independence implicit in the div-b-preservation-active-mesh mode's tolerance. No
convergence-order or exact-solution mode is possible here (source: "no analytic solution available").

## Notes
Two discrepancies from the source are recorded verbatim, not resolved:
1. Domain/mesh: body text states the domain is [0,1]x[0,2] cm with 32x64 cells; the Fig. 5 caption
   states "the domain shown is 32x32 cells". These are likely reconciled by Fig. 5 showing a
   cropped/rendered view of the full 32x64 domain, but this is speculation -- not adopted here.
2. Geometry primitive gap: the rounded-square variants' 0.15 cm corner fillet is not representable by
   any of the fixed geometry primitives (box/cylinder/sphere/shell/halfspace/polygon + rotate/
   translate) -- there is no field for a corner radius on a box or polygon. The `config_delta` above
   uses a plain rotated box with the fillet omitted as the closest available approximation; this is a
   genuine schema gap (a structural primitive is missing, not a registry id), flagged for
   re-grilling, not resolved by vocab-extension.
`geometry_stress` is left `none` because no `registry/geometry-stress` id yet exists to describe a
"rotated non-grid-aligned boundary" case (a vocab proposal, not authored here).
