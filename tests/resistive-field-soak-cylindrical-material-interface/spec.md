---
# Authored via /add-test (NORMAL path) from Jones, McNally & Reynolds, "A constrained-transport
# embedded boundary method for compressible resistive magnetohydrodynamics", J. Comput. Phys. 550
# (2026) 114641 (citekey: jones2026), Section 7.9 "Resistive magnetic field soak across cylindrical
# material interface". Field form re-uses Section 7.3's parallel-pinch construction (eqs. 68-69,
# citekey freidberg2014 for the underlying profile form), rescaled.

slug: resistive-field-soak-cylindrical-material-interface
name: "Resistive Field Soak Across a Cylindrical Two-Material Interface"
provenance: literature
one_liner: "A parallel-pinch-derived magnetic field with a sharp discontinuity at a curved (cylindrical) two-material resistivity interface, diffusing resistively; validated by self-convergence and by a div-B-preservation check specific to a non-mesh-aligned two-sided interface."

physics:
  materials:
    - name: interior_conductor
      base: magnetic-diffusion
      terms: [resistivity]
      material_fields:
        - { name: eta, region: interior, expr: "1e4", units: "cm^2/s" }
    - name: exterior_conductor
      base: magnetic-diffusion
      terms: [resistivity]
      material_fields:
        - { name: eta, region: exterior, expr: "1e3", units: "cm^2/s" }
  coupling: electromagnetic-coupling   # field continuity across the two conducting regions (as in permeable-core-thin-shell-diffusion)

dimension:
  intrinsic: 2
  runnable_in: [2]

analysis_treatments: [axis-singularity, multi-material-interface]

capability_flags:
  time_dependent_bc: false
  has_internal_boundaries: true
geometry_stress: none

geometry:
  coord_system: cartesian   # the interface is deliberately non-mesh-aligned/non-grid-conformal, hence Cartesian rather than cylindrical framing
  domain: { x: [-450, 450], y: [-450, 450] }   # NOT stated numerically in the source beyond "square computational domain" with periodic BCs -- see Notes; sized as 3x the interface radius
  regions:
    - id: interior
      shape: cylinder
      params: { center: [0, 0], r: 150 }
    # exterior = domain minus interior

units:
  system: cgs-gaussian
  b_field_convention: sqrt-4pi

initial_conditions:
  aux:
    - { name: a,                expr: "150" }                      # pinch/interface radius, cm
    - { name: Bphi_a_unscaled,  expr: "sqrt(pi) / a" }               # unscaled Bphi(a), G (Sect. 7.3 form at this a)
    - { name: Bz_a_unscaled,    expr: "sqrt(4*pi)" }                 # unscaled Bz(a), G
    - { name: alpha,            expr: "Bphi_a_unscaled / Bz_a_unscaled" }
  equilibrium:
    - region: interior
      fields:
        # Section 7.3's A_z(r) (eq.68) and Bz(r) (eq.69), each rescaled by 1/2 inside the interface
        # radius ("we rescale the vector potential (68) and z-field (69) inside the pinch radius a
        # by 1/2"). Bx,By obtained by differentiating the (rescaled) A_z, exactly as in
        # standing-magnetosonic-wave-parallel-pinch-cylinder.
        Bx: "-(0.5 * Bphi_a_unscaled / (2*a)) * y"
        By: "(0.5 * Bphi_a_unscaled / (2*a)) * x"
        Bz: "0.5 * (Bz_a_unscaled/alpha) * sqrt(1 + (2*alpha**2/3)*(1-(r/a)**2)**2*(5-2*(r/a)**2))"
    - region: exterior
      fields:
        # "use the vacuum field for a conductor carrying the current corresponding to the unscaled
        # solution at radii greater than a" -- the source does not spell out this exterior formula;
        # the standard curl-free (current-free) vacuum extension of a pinch's edge fields is used
        # here (1/r falloff for the azimuthal component, uniform axial component), flagged as an
        # INFERRED construction, not a verbatim source formula (see Notes).
        Bx: "-Bphi_a_unscaled * a * y / (x**2 + y**2)"
        By: "Bphi_a_unscaled * a * x / (x**2 + y**2)"
        Bz: "Bz_a_unscaled"
  perturbation:
    combine_rule: additive
    fields: {}
  potentials: []

parameters:
  - { name: a,               canonical: 150,    meaning: "pinch / material-interface radius, cm" }
  - { name: eta_interior,    canonical: 1e4,    meaning: "magnetic diffusivity inside the interface, cm^2/s" }
  - { name: eta_exterior,    canonical: 1e3,    meaning: "magnetic diffusivity outside the interface, cm^2/s" }
  - { name: domain_half_extent, canonical: null, meaning: "half-extent of the square computational domain, cm", notes: "needs-source; the source states only 'square computational domain' with periodic boundaries, sufficiently larger than a=150 cm to avoid significant reconnection at the periodic boundary during the analyzed timescale, without giving a numeric extent" }

domain_bc:
  x_lo: { type: periodic }
  x_hi: { type: periodic }
  y_lo: { type: periodic }
  y_hi: { type: periodic }

internal_boundaries: []   # the interior/exterior coupling is the material boundary (physics.coupling)

time:
  t_final: 0.05   # source: "evolved for 5e-2 s"
  snapshot_times: [0.05]

validation_modes:
  - id: azimuthal-field-self-convergence
    purpose: "Verify self-convergence of the azimuthal field toward a high-resolution reference solution, expecting a rate between the discontinuity-limited first order and the smooth-field second order at this evolution time."
    procedure: self-convergence
    inputs:
      at_time: 0.05
      variables: [Bphi]
      reference_resolution: 512
      r: 2
      reference: { kind: reference-result, key: jones2026 }
      tolerance: "measured self-convergence order lies between 1 and 2 relative to the 512^2 reference (Fig. 10b) -- the discontinuity-limited first order has not yet come to dominate the total L1 error at this evolution time"
    has_exact_solution: false
    score: 4
    score_justification: "No exact/closed-form time-dependent solution used (self-convergence against a 512^2 reference run, per Fig. 10's own description); a reliable, automatable self-convergence check — rubric row 4."

  - id: div-b-preservation-nonaligned-interface
    purpose: "Verify the magnetic divergence is maintained to machine precision specifically at a non-mesh-aligned, two-sided (two-material) cylindrical interface, a case genuinely more demanding than a single-material or grid-aligned interface for a constrained-transport scheme with per-material electric-field averaging."
    procedure: div-b
    inputs:
      at_time: 0.05
      variables: [B]
      tolerance: "div(B) at or near machine precision everywhere, including at cut cells straddling the non-mesh-aligned material interface (Fig. 10, panel d)"
    has_exact_solution: false
    score: 3
    score_justification: "Universal div-B diagnostic, scored here because the source explicitly identifies this specific case (two-sided, non-mesh-aligned interface with per-material edge-fraction-weighted electric fields, Sect. 4.2) as a genuinely discriminating stress case for the scheme's divergence-preservation claim, not a generic/automatic pass — capped at row 3 (SPEC §6.4 universal-diagnostic rule: not an exact-solution or literature comparison)."

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
    params_used: { a: 150, eta_interior: 1e4, eta_exterior: 1e3, t: 0.05 }
    method: "resistive (eta!=0) MHD induction update on a two-material master mesh (Sect. 4.2/6.2); edge-fraction-weighted combination of per-material electric fields; static level-set interface"
    resolution: "self-convergence sweep with a 512^2 reference"
    amr: "none"
    findings: "Azimuthal field self-convergence rate lies between first and second order (Fig. 10b); div(B) remains at machine precision at the non-mesh-aligned interface (Fig. 10d)."
related_to: [standing-magnetosonic-wave-parallel-pinch-cylinder, resistive-field-soak-material-slab-interface]
headline_score: 4
---

## Physical problem
A parallel-pinch-derived magnetic field configuration (as in
standing-magnetosonic-wave-parallel-pinch-cylinder, eqs. 68-69, but rescaled by 1/2 inside the
pinch/interface radius a=150 cm and replaced outside by the curl-free vacuum extension of the
unscaled edge fields) is imposed across a curved, two-material resistivity interface: magnetic
diffusivity 1e4 cm^2/s inside the interface, 1e3 cm^2/s outside. The rescaling produces a sharp
discontinuity in the field precisely at the material interface, which then diffuses resistively.

## What this test actually tests
Whether the scheme's two-material (ghost-fluid-adjacent) resistive coupling correctly handles a
genuinely curved, non-mesh-aligned material interface: self-convergence of the field
(azimuthal-field-self-convergence) and preservation of the divergence-free constraint specifically
at the non-aligned two-sided interface (div-b-preservation-nonaligned-interface).

## Qualitative behaviour
The field has a sharp kink at r=a=150 cm at t=0 that smooths as resistive diffusion proceeds; the
azimuthal-field self-convergence rate sits between the fully-smooth second order and the
discontinuity-limited first order, since (per the source) the first-order behavior has not yet come
to dominate the total L1 error at the analyzed time.

## Validation notes
Fig. 10 (top right) shows the self-convergence rate of Bphi against a 512^2 reference solution,
between first and second order. Fig. 10 (bottom right) shows div(B) at machine precision across the
domain including cut cells straddling the interface. As in the slab-interface sibling test
(Section 7.8), first-order convergence is the ultimate expectation from the resistivity
discontinuity, but is not yet dominant at this evolution time.

## Notes
The exterior (vacuum) field formula is NOT given as an explicit equation in Section 7.9 — only
described qualitatively ("use the vacuum field for a conductor carrying the current corresponding
to the unscaled solution at radii greater than a"). The expressions used here (1/r azimuthal
falloff, uniform axial field) are the standard curl-free vacuum extension of a current-carrying
pinch's edge fields, inferred by the author of this entry, not transcribed from the source. The
computational domain's numeric extent is likewise not stated (`domain_half_extent`: needs-source);
the value used here (450 cm, 3x the interface radius) is a placeholder sized only to be
"sufficiently larger" than a=150 cm as the source requires, and should be corrected if the actual
value can be recovered (e.g. from the authors' code or supplementary material).
