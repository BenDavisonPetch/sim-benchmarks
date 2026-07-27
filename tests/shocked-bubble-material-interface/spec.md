---
# Authored via /add-test (NORMAL path) from Jones, McNally & Reynolds 2026, "A constrained-transport
# embedded boundary method for compressible resistive magnetohydrodynamics", J. Comput. Phys. 550
# (2026) 114641 (citekey: jones2026), Section 7.13 "Shocked bubble with material interface". The
# magnetic-field construction re-uses Section 7.12's parallel-pinch form (eqs. 68-69, ultimately
# citekey freidberg2014), rescaled to a=r2=0.25 cm. Source attributes the PROBLEM CLASS (not the
# specific numeric parameters, which are explicitly "unconstrained by physical experiment") to Quirk
# & Karni 1996 -- recorded verbatim in test_origin.attribution_claims[] below, NOT resolved/verified
# as a references[] entry in this pass (deferred to /add-refs).
#
# DEDUP: no existing entry shares this physics_signature (two-material mhd(resistivity)/gamma-law
# @material-contact, shock-driven) + analysis_treatments + capability_flags -- NEW ENTRY. Related to
# the parallel-pinch field-construction siblings and the other two-material/material-contact entries.

slug: shocked-bubble-material-interface
name: "Shocked Bubble with Material Interface"
provenance: literature
one_liner: "A Mach 1.5 planar shock impacts a cylindrical low-density, high-gamma bubble across a two-material (ghost-fluid) interface, with optional embedded parallel-pinch magnetic field and resistive coupling; validated qualitatively by comparing bubble deformation across unmagnetized / magnetized-ideal / magnetized-resistive configurations (config_delta differential modes)."

physics:
  materials:
    - name: background_gas
      base: mhd
      terms: [resistivity]
      eos:
        type: gamma-law
        params: { gamma: 1.6666666666666667 }
      material_fields:
        - { name: eta, region: exterior, expr: "1", units: "cm^2/s" }
    - name: bubble_gas
      base: mhd
      terms: [resistivity]
      eos:
        type: gamma-law
        params: { gamma: 5 }
      material_fields:
        - { name: eta, region: bubble, expr: "0.1", units: "cm^2/s" }
  coupling: material-contact

dimension:
  intrinsic: 2
  runnable_in: [2]

analysis_treatments: [multi-material-interface]

capability_flags:
  time_dependent_bc: false
  has_internal_boundaries: true
geometry_stress: none

geometry:
  coord_system: cartesian
  domain: { x: [0, 1.5], y: [0, 1.5] }   # "Domain is 1.5 cm x 1.5 cm" (Fig. 14 caption)
  regions:
    - id: bubble
      shape: cylinder
      params: { center: [0.75, 0.75], r: 0.25 }
    # exterior = domain minus bubble; further split spatially by the shock position x=0.4 (see aux)

units:
  system: cgs-gaussian
  b_field_convention: sqrt-4pi

initial_conditions:
  aux:
    - { name: a,             expr: "0.25" }                        # = r2, bubble radius (= pinch radius in magnetized variants), cm
    - { name: rho1,          expr: "2" }                            # background pre-shock density, g/cm^3
    - { name: P1,            expr: "1" }                            # background/bubble pressure-equilibrium value, Ba
    - { name: gamma1,        expr: "1.6666666666666667" }
    - { name: M,             expr: "1.5" }                          # shock Mach number
    - { name: x_shock,       expr: "0.4" }                          # planar shock initial x-position, cm
    - { name: c1,            expr: "sqrt(gamma1*P1/rho1)" }         # pre-shock sound speed
    - { name: rho_post,      expr: "rho1*((gamma1+1)*M**2)/((gamma1-1)*M**2+2)" }   # standard Rankine-Hugoniot density ratio
    - { name: P_post,        expr: "P1*(1 + (2*gamma1/(gamma1+1))*(M**2 - 1))" }     # standard R-H pressure ratio
    - { name: Us,            expr: "M*c1" }                         # shock speed (lab frame, pre-shock ambient at rest)
    - { name: u_post_lab,    expr: "Us*(1 - rho1/rho_post)" }       # induced post-shock velocity, lab frame
    - { name: vx_pre,        expr: "-u_post_lab" }                  # pre-shock ambient/bubble velocity in the paper's frame (post-shock velocity shifted to zero)
    - { name: Bphi_a,        expr: "sqrt(pi) / a" }                 # source-stated Bphi(a), G (magnetized variants only)
    - { name: Bz_a,          expr: "0.1 * sqrt(4*pi)" }              # source-stated Bz(a), G (magnetized variants only)
    - { name: alpha,         expr: "Bphi_a / Bz_a" }
  equilibrium:
    - region: exterior
      fields:
        rho: "rho_post + (rho1 - rho_post) * step(x, x_shock, x_shock)"     # x<0.4: post-shock; x>=0.4: pre-shock ambient
        p:   "P_post + (P1 - P_post) * step(x, x_shock, x_shock)"
        vx:  "vx_pre * step(x, x_shock, x_shock)"                            # post-shock (x<0.4) velocity is zero by construction; pre-shock ambient (x>=0.4) carries vx_pre
        vy:  "0"
        vz:  "0"
        Bx: "0"    # no exterior magnetic field is stated in the source for this test; inferred B=0 outside the bubble (see Notes, as in the converging-shock sibling)
        By: "0"
        Bz: "0"
    - region: bubble
      fields:
        rho: "0.5"
        p:   "P1"                     # pressure equilibrium with the (pre-shock) ambient
        vx:  "vx_pre"                 # co-moving with the pre-shock ambient it sits within, before the shock arrives (see Notes)
        vy:  "0"
        vz:  "0"
        # Bx,By from A_z(r) (source eq. 68, as in the converging-shock sibling); magnetized variants only
        Bx: "-(Bphi_a / (2*a)) * (y - 0.75)"
        By: "(Bphi_a / (2*a)) * (x - 0.75)"
        Bz: "(Bz_a/alpha) * sqrt(1 + (2*alpha**2/3)*(1-(r/a)**2)**2*(5-2*(r/a)**2))"
  perturbation:
    combine_rule: additive
    fields: {}
  potentials:
    - name: A_z
      expr: "Bphi_a * (a/4) * (2 - (r/a)**2)"
      derives: "Bx = dA_z/dy, By = -dA_z/dx (B = curl(A_z*z_hat), centered on the bubble at (0.75,0.75)); bubble region only"

parameters:
  - { name: a,        canonical: 0.25, meaning: "bubble radius / magnetized-variant pinch radius, cm" }
  - { name: rho1,     canonical: 2,    meaning: "background pre-shock density, g/cm^3" }
  - { name: gamma1,   canonical: 1.6666666666666667, meaning: "background ratio of specific heats (=5/3), global default" }
  - { name: rho_bubble, canonical: 0.5, meaning: "bubble initial density, g/cm^3" }
  - { name: gamma_bubble, canonical: 5, meaning: "bubble ratio of specific heats" }
  - { name: P1,       canonical: 1,    meaning: "background/bubble pressure-equilibrium value, Ba" }
  - { name: M,        canonical: 1.5,  meaning: "shock Mach number" }
  - { name: x_shock,  canonical: 0.4,  meaning: "initial planar shock x-position, cm" }
  - { name: eta_background, canonical: 1,   meaning: "background magnetic diffusivity, cm^2/s (magnetized-resistive canonical case)" }
  - { name: eta_bubble,     canonical: 0.1, meaning: "bubble magnetic diffusivity, cm^2/s (magnetized-resistive canonical case)" }
  - { name: Bphi_a,   canonical: 1.7724538509055159, meaning: "azimuthal field at r=a, G (= sqrt(pi)/a, a=0.25), magnetized variants" }
  - { name: Bz_a,     canonical: 0.35449077018110318, meaning: "axial field at r=a, G (= 0.1*sqrt(4*pi)), magnetized variants" }

domain_bc:
  x_lo: { type: outflow }   # not explicitly stated in the source; outflow inferred as the conventional choice for an open shock-tube-like domain -- see Notes
  x_hi: { type: outflow }
  y_lo: { type: outflow }
  y_hi: { type: outflow }

internal_boundaries: []   # material interface is physics.coupling (material-contact)

time:
  t_final: 1.4   # source (Fig. 14 panel labels): snapshots at t=0, 7.0e-1, 1.4e0 -- units plausibly inconsistent with a fast M=1.5 shock crossing a 1.5cm domain (see Notes); recorded verbatim, not corrected
  snapshot_times: [0, 0.7, 1.4]

validation_modes:
  - id: bubble-deformation-unmagnetized-vs-magnetized
    purpose: "Verify that the hydrodynamic shock deforms the bubble in the classic shocked-bubble manner when unmagnetized, and that an embedded parallel-pinch magnetic field within the bubble qualitatively suppresses/resists that deformation relative to the unmagnetized case -- a controlled A/B comparison, not either run in isolation."
    procedure: feature-location
    inputs:
      at_time: [0, 0.7, 1.4]
      variables: [rho]
      cut_lines: ["visual inspection of the bubble interface contour, per Fig. 14"]
      features: ["classic shocked-bubble deformation (unmagnetized)", "pinch-equilibrium resistance to deformation (magnetized)"]
      reference: { kind: reference-result, key: jones2026 }
      tolerance: "qualitative visual match only -- no numeric deformation-amplitude criterion is stated for this test"
    has_exact_solution: false
    score: 2
    score_justification: "No automatable check and no exact solution; but the measurand is a specific, named, checkable qualitative difference (bubble deformation vs pinch-resisted deformation), reproducing a widely-known phenomenology (Quirk & Karni-type shocked-bubble deformation) -- rubric row 2, not inflated to the row-3 differential ceiling absent any quantitative amplitude/growth-rate metric."
    baseline:
      description: "unmagnetized variant: no magnetic field, no resistive term in either material (Bphi_a=Bz_a=0, eta_background=eta_bubble=0)"
      config_delta: { "physics.materials[0].terms": "[]", "physics.materials[1].terms": "[]", "initial_conditions.aux.Bphi_a": "0", "initial_conditions.aux.Bz_a": "0" }
    measured: "difference in bubble-interface deformation at t=0, 0.7, 1.4 between the magnetized+resistive canonical run and the unmagnetized baseline (source: 'In the unmagnetized version, the hydrodynamic shock deforms the bubble in the same qualitative manner as has been found in both experiment and simulation... In the magnetized case, the pinch equilibrium pushes back and prevents the bubble from deforming as readily')"

  - id: ideal-vs-resistive-interplay
    purpose: "Verify the scheme captures the complex interplay between ideal-MHD pinch-equilibrium stabilization and finite-resistivity diffusion of that same stabilizing field during the shock-bubble interaction, by comparing the magnetized-ideal and magnetized-resistive configurations."
    procedure: feature-location
    inputs:
      at_time: [0, 0.7, 1.4]
      variables: [rho, Bz]
      cut_lines: ["visual inspection of the bubble interface and field structure, per Fig. 14"]
      features: ["magnetized-ideal pinch stabilization retained through the shock interaction", "magnetized-resistive variant showing additional field diffusion/interplay effects"]
      reference: { kind: reference-result, key: jones2026 }
      tolerance: "qualitative visual match only -- no numeric criterion is stated for this test"
    has_exact_solution: false
    score: 2
    score_justification: "No automatable check and no exact solution; a specific, named qualitative comparison (ideal vs resistive field behavior during the interaction) rather than a vague impression, but not a quantitative differential measurement -- rubric row 2."
    baseline:
      description: "magnetized-ideal variant: same B-field as canonical, but no resistive term in either material (eta_background=eta_bubble=0)"
      config_delta: { "physics.materials[0].terms": "[]", "physics.materials[1].terms": "[]" }
    measured: "difference between the magnetized-ideal and magnetized-resistive (canonical) configurations in how the pinch field and bubble interface evolve through the shock interaction (source: 'The variations with ideal and resistive MHD demonstrate the ability of the scheme to capture the complex interplay between the multiple physical effects.')"

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
  attribution_claims:
    - stated_by: quirk_karni1996
      quote: "This setup is based on the classic shocked helium bubble problem (e.g. Quirk and Karni [38])."
reference_results:
  - key: jones2026
    params_used: { a: 0.25, rho1: 2, gamma1: 1.6666666666666667, rho_bubble: 0.5, gamma_bubble: 5, P1: 1, M: 1.5, x_shock: 0.4, eta_background: 1, eta_bubble: 0.1, Bphi_a: 1.7724538509055159, Bz_a: 0.35449077018110318, t_final: 1.4 }
    method: "resistive MHD; two-material ghost-fluid coupling (Sect. 3.2/4.2) with per-material edge-fraction-weighted electric field; level-set-tracked bubble interface; HLLD Riemann solver; 200x200 Cartesian mesh; three configurations run (unmagnetized, magnetized-ideal, magnetized-resistive)"
    resolution: "200^2 Cartesian mesh (Fig. 14 caption)"
    amr: "none"
    findings: "Unmagnetized: bubble deforms in the classic shocked-bubble manner, consistent with prior experiment/simulation. Magnetized: the pinch equilibrium resists deformation. Ideal vs resistive variants show the interplay between MHD stabilization and resistive diffusion (Fig. 14, t=0, 7.0e-1, 1.4e0)."
related_to: [converging-shock-parallel-pinch-material-interface, resistive-field-soak-material-slab-interface, standing-magnetosonic-wave-parallel-pinch-cylinder]
headline_score: 2
---

## Physical problem
A planar Mach-1.5 shock (Rankine-Hugoniot jump conditions, background rho1=2 g/cm^3, gamma1=5/3,
P1=1 Ba), initialized at x=0.4 cm in a frame chosen so the post-shock flow velocity is zero, sweeps
rightward through a background material toward a cylindrical bubble of radius 0.25 cm centered at
(0.75, 0.75) cm (rho=0.5 g/cm^3, gamma=5), initially in pressure equilibrium with the (pre-shock)
background. Three configurations are considered: unmagnetized; magnetized-ideal, with a parallel-
pinch field (source eqs. 68-69, a=0.25 cm, Bphi(a)=sqrt(pi) G, Bz(a)=0.1*sqrt(4*pi) G) confined to the
bubble; and magnetized-resistive, adding finite magnetic diffusivity (eta_background=1,
eta_bubble=0.1 cm^2/s) to both materials. The material interface is tracked with a level set.

## What this test actually tests
Whether the scheme's two-material shock-capturing + resistive-MHD coupling reproduces the classic
shocked-bubble deformation phenomenology when unmagnetized, and whether an embedded pinch-equilibrium
magnetic field qualitatively resists that deformation, plus whether ideal vs resistive MHD produce a
qualitatively distinct interplay of effects during the interaction
(bubble-deformation-unmagnetized-vs-magnetized, ideal-vs-resistive-interplay).

## Qualitative behaviour
In the unmagnetized configuration, the shock deforms the bubble in the same qualitative manner
documented in prior shocked-bubble experiment/simulation literature (mushroom-cap-like deformation
typical of a low-density bubble in a higher-density ambient). In the magnetized configuration, the
pinch equilibrium's magnetic pressure resists this deformation. No analytic solution exists for any
of the three configurations.

## Validation notes
Fig. 14 shows three snapshots (t=0, 7.0e-1, 1.4e0) for each of unmagnetized / magnetized-ideal /
magnetized-resistive, on a 1.5 cm x 1.5 cm domain. No quantitative conservation-drift or div-B
diagnostic is stated or plotted for this test in the source; none is fabricated here.

## Notes
Two source ambiguities are recorded verbatim, not resolved:
1. Snapshot timing: the stated snapshot times (t=0, 7.0e-1, 1.4e0) appear slow for a Mach-1.5 shock
   crossing a 1.5 cm domain (a naive crossing-time estimate would be well under 1 s at these
   densities/pressures). This may indicate the times are in different units, a different
   normalization, or a typo in the source; recorded verbatim per the no-fabrication discipline, not
   "corrected".
2. The pre-shock/bubble initial velocity (`vx_pre`, derived from the standard Rankine-Hugoniot
   relations for a frame where the *post*-shock velocity is zero) is nonzero, which is in some
   tension with the source's looser description "accelerating it to the right from rest" (which
   could be read as the bubble having zero initial velocity). The literal, quantitative statement
   ("the flow is initially set in a frame where the post-shock flow velocity is zero") is treated
   here as controlling; "from rest" is read as descriptive prose about the bubble's undisturbed state
   prior to the shock's arrival, not as an independent zero-velocity IC requirement. Flagged for
   reconsideration if the authors' code/supplementary material is consulted.
The exterior (background) magnetic field is taken as identically zero outside the bubble, an
INFERRED simplification (not explicitly stated), matching the same inference made in
converging-shock-parallel-pinch-material-interface. `domain_bc` (outflow, all faces) is likewise
inferred, not explicitly stated in Section 7.13.
