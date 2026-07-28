---
# Authored via /add-test (NORMAL path) from Dematté, Farmakalides, Millmore & Nikiforakis,
# "An all Mach number scheme for visco-resistive magnetically-dominated MHD flows", JCP 514
# (2024) 113229 (citekey: dematte2024). Section 4.3.1 "Shear layer and current sheet"
# (visco-resistive VRMHD), the resistive half of the pair.
#
# INTRA-PAPER DEDUP: paired with `mhd-shear-layer` (same section, same exact-solution family
# v(x,t) = -erf(x/(2*sqrt(mu*t))), here applied to By instead of vy). Kept as a SEPARATE entry
# (not folded) because the IC structural form differs (magnetic-field discontinuity, u=0,
# vs. `mhd-shear-layer`'s velocity discontinuity, B=0) even though both share the identical
# VRMHD term set / analysis_treatments / capability_flags -- see dedup step 3 (structural IC
# compare) and the reasoning recorded in `mhd-shear-layer`. Cross-linked via `related_to`.
#
# GENUINE SOURCE GAP (confirmed by direct re-read of page 27, NOT a transcription error on our
# part): the source's displayed IC equation for B gives only a 2-component vector,
# (0, +/-1.1e4)^T, matching the stated "exact solution for By is the same as for v in the shear
# layer test." The surrounding prose ALSO asserts "the strong, constant Bz component" but no
# numeric value for Bz is given anywhere on this page or in the equation itself. This is a gap
# in the source itself. Bz is left OUT of the equilibrium fields below (not invented, not
# borrowed from the Kelvin-Helmholtz test's B0 by analogy) and recorded as a needs-source
# parameter -- see pending_extraction.md.

slug: mhd-current-sheet
name: "Visco-Resistive MHD Current Sheet"
provenance: literature
one_liner: "1D resistive current sheet in the VRMHD system with an exact self-similar erf profile for By (Schlichting & Gersten); tests the resistive term and the low-Mach-number/strong-B capability of the scheme. The source's stated 'strong constant Bz component' has no numeric value given anywhere in the text (needs-source)."

physics:
  materials:
    - name: plasma
      base: mhd
      terms: [viscosity, resistivity, heat-conduction]
      eos:
        type: gamma-law
        params: { gamma: 1.6666666666666667 }   # gamma = 5/3, global default ("unless otherwise stated"); not restated for this test
  coupling: none

dimension:
  intrinsic: 1
  runnable_in: [1, 2]

analysis_treatments: [none]

capability_flags:
  time_dependent_bc: false
  has_internal_boundaries: false
geometry_stress: none

geometry:
  coord_system: cartesian
  domain: { x: [-1, 1], y: [-0.02, 0.02] }
  regions:
    - id: left
      shape: box
      params: { x: [-1, 0], y: [-0.02, 0.02] }
    - id: right
      shape: box
      params: { x: [0, 1], y: [-0.02, 0.02] }

units:
  system: nondimensional      # not named by the source; bare numbers (standard convention for this benchmark)
  b_field_convention: permeability-unity   # stated-here, global (Sect. 2): "the units of B are chosen such that the vacuum magnetic permeability is unity"

initial_conditions:
  aux: []
  equilibrium:
    - region: left
      # NOTE: Bz deliberately OMITTED -- source states a "strong, constant Bz component" exists
      # but gives no numeric value anywhere in the text (needs-source; see Bz0 parameter below
      # and pending_extraction.md). Do not treat the absence of a Bz key as Bz=0: the source is
      # explicit that Bz is nonzero and large.
      fields: { rho: "1.0", vx: "0.0", vy: "0.0", vz: "0.0", Bx: "0.0", By: "1.1e4", p: "1e5" }
    - region: right
      fields: { rho: "1.0", vx: "0.0", vy: "0.0", vz: "0.0", Bx: "0.0", By: "-1.1e4", p: "1e5" }
  perturbation:
    combine_rule: additive
    fields: []
  potentials: []

parameters:
  - { name: gamma, canonical: 1.6666666666666667, meaning: "ratio of specific heats (= 5/3), global default" }
  - { name: mu, canonical: 0.1, meaning: "dynamic viscosity coefficient (VRMHD viscous term); inert here since u=0 in this test's IC, but the stated fluid-parameter set 'eta=mu=0.1... in both cases' applies to both this test and mhd-shear-layer" }
  - { name: eta, canonical: 0.1, meaning: "resistivity coefficient (VRMHD resistive term)" }
  - { name: Pr, canonical: 1.0, meaning: "Prandtl number (dimensionless), stated for both shear-layer and current-sheet tests" }
  - { name: cv, canonical: 1.0, meaning: "specific heat capacity at constant volume (code units), stated for both shear-layer and current-sheet tests" }
  - { name: kappa, canonical: 0.16666666666666666, meaning: "thermal conductivity implied by the stated Pr=1, cv=1, gamma=5/3 via the standard ideal-gas relation kappa = mu*cp/Pr with cp = gamma*cv; see mhd-shear-layer Notes for the same derivation" }
  - { name: By0, canonical: 11000.0, meaning: "left/right magnitude of the initial By discontinuity (source: '1.1e4')" }
  - name: Bz0
    canonical: null
    meaning: "the source's prose asserts a 'strong, constant Bz component' in the current-sheet IC, intended to raise the Alfven speed by orders of magnitude, but gives NO numeric value anywhere in the equation or surrounding text (Sect. 4.3.1, page 27) -- genuine source gap, confirmed by direct re-read"
    notes: needs-source

domain_bc:
  x_lo: { type: outflow }   # source: "transmissive boundary conditions ... in the x-direction"
  x_hi: { type: outflow }
  y_lo: { type: periodic }  # source: "Periodic boundary conditions are taken in the y-direction"
  y_hi: { type: periodic }

internal_boundaries: []

time:
  t_final: 0.1
  snapshot_times: [0.1]

validation_modes:
  - id: exact-solution-erf-profile
    purpose: "Verify the numerical By profile against the exact self-similar erf solution By(x,t) = -1.1e4*erf(x/(2*sqrt(eta*t))) at t=0.1 (the same erf family as the shear layer's velocity solution, here for the resistive diffusion of By)."
    procedure: exact-solution-compare
    inputs:
      at_time: 0.1
      variables: [By]
      reference: { kind: reference-result, key: dematte2024 }
      tolerance: "close visual agreement with the exact erf profile (Fig. 14, right panel); no explicit numeric L1/L2/Linf tolerance table is given in the source (only a single 200x4 grid is shown, no resolution sequence)"
    has_exact_solution: true
    score: 4
    score_justification: "A genuine closed-form exact solution exists at all times (erf profile, same family as mhd-shear-layer's velocity solution), making an automatable, resolution-independent norms check straightforward -- rubric row 4/5 territory. Capped at 4 rather than 5 because the source itself reports only a single-grid (200x4) qualitative overlay (Fig. 14) with no resolution sequence/convergence-order table demonstrating the theoretical order is achieved. The missing Bz value (needs-source) does not affect this mode, since By's exact solution is unaffected by Bz by the source's own statement ('this added component does not affect the solution for By')."

references:
  - key: dematte2024
    original_intro: false
    verification:
      status: verified
      identifier: { doi: "10.1016/j.jcp.2024.113229" }
      source: "crossref: 10.1016/j.jcp.2024.113229 -> 200"
      checked: "2026-07-28"
      meta:
        year: 2024
        first_author: Dematté
        container: Journal of Computational Physics
        title: "An all Mach number scheme for visco-resistive magnetically-dominated MHD flows"
references_unverified:
  - key: schlichting-gersten1955
    verification:
      status: unverified
      note: "Textbook: H. Schlichting, K. Gersten, 'Boundary-Layer Theory' (Springer, 'Grenzschicht-Theorie', Germany, 2005 edition cited by dematte2024 as ref [76]). No DOI located; verify_refs.py --lookup requires a doi/arxiv/url identifier, which a textbook of this vintage typically lacks. Credited (verbatim, per source) as the origin of the exact erf shear-layer/current-sheet solution. Left unverified per the no-fabrication contract -- see pending_verification.md."
test_origin:
  status: pending
  authored_from: dematte2024
  attribution_claims:
    - stated_by: dematte2024
      quote: "Here, the exact solution for By is the same as for v in the shear layer test given above."
reference_results:
  - key: dematte2024
    params_used: { domain: "[-1,1]x[-0.02,0.02], periodic-y/transmissive-x, 200x4 cells", eta: 0.1, mu: 0.1, Pr: 1.0, cv: 1.0, "dt (fixed override)": 0.0045, t_final: 0.1 }
    method: "proposed semi-implicit FVS scheme; VRMHD viscous/resistive terms treated implicitly (GMRES tol 1e-15, Picard sigma=1e-12, R=Q=S=2); staggered CT for div-B"
    resolution: "200x4 cells (2D strip, y-direction inert)"
    amr: "none"
    findings: >
      Fig. 14 (right panel): numerical By profile at t=0.1 matches the exact erf solution
      closely. Because the IC velocity is zero, a fixed timestep dt=0.0045 is imposed "to mimic
      the Delta t of the shear-layer test with ||u||=1" (an explicit override of the paper's
      default advective-eigenvalue dt rule, needed here only because zero initial velocity would
      otherwise force reliance on the magneto-sonic speed for the first step). Both tests
      "ran in 23 time steps."
related_to: [mhd-shear-layer]
headline_score: 4
---

## Physical problem
A 1D resistive current sheet: two half-spaces of quiescent, uniform-density, uniform-pressure
fluid at rest, with a discontinuous jump in By at x=0 (+1.1e4 for x<=0, -1.1e4 for x>0),
evolved under the VRMHD equations. Resistive diffusion smooths the By discontinuity into the same
self-similar erf profile family as the shear layer's velocity solution. The source states the IC
also carries a "strong, constant Bz component" specifically to push the Alfven speed far above the
fluid speed (stressing the scheme's low-Mach-number capability in a magnetically-dominated
regime) -- but gives no numeric value for it anywhere in the text (see needs-source flag above).

## What this test actually tests
Diffusive accuracy of the scheme's resistive term against a genuine closed-form exact solution
(the erf self-similar profile for By), in a magnetically-dominated (strong-B), low-Mach-number
regime intended to stress the semi-implicit scheme's suitability for that regime specifically
(the paper's stated purpose of the missing Bz component).

## Qualitative behaviour
The By jump at x=0 smooths monotonically over time following By(x,t) = -1.1e4*erf(x/(2*sqrt(eta*t)));
with eta=0.1 and t=0.1 the diffusion length scale is the same ~0.2 in x as the shear-layer test
(same erf argument form, different diffusivity coefficient playing the same role as mu there).
The IC's zero velocity means the run uses an explicitly overridden fixed dt=0.0045 rather than the
paper's default advective-eigenvalue time-step rule (see Notes).

## Validation notes
The exact solution is closed-form at all t>0 for By specifically (unaffected by the unresolved Bz
value, per the source's own statement), making this an automatable, resolution-independent check
in principle (rubric row 4/5). As with `mhd-shear-layer`, the source's own reported comparison
(Fig. 14) is a single 200x4-cell run with no stated numeric error/resolution sequence -- scored 4,
not 5.

## Notes
Bz's numeric value is a genuine, unresolved gap in the source itself (confirmed by direct re-read
of page 27): the displayed IC equation gives only a 2-component (0,+/-By0) vector, and while the
prose separately asserts a "strong, constant Bz component" meant to raise the Alfven speed "by
orders of magnitude," no number for it appears anywhere in the equation or surrounding text. Do
NOT borrow the Kelvin-Helmholtz test's B0=0.07/sqrt(4*pi) or any other value by analogy -- this is
recorded `needs-source` (canonical: null) per the no-fabrication contract (SPEC §5.2); Bz is
correspondingly omitted from the IC `fields` above rather than set to a guessed number or to zero
(the source is explicit Bz is nonzero and large). See `pending_extraction.md`.

`kappa` derivation and the shared eta=mu=0.1/Pr=1/cv=1 fluid-parameter statement mirror
`mhd-shear-layer`'s Notes (same joint "In both cases..." sentence). This test's dt=0.0045 is an
explicit per-test OVERRIDE of the global-defaults advective-eigenvalue dt rule (stated reason:
zero IC velocity would otherwise force the first step onto the magneto-sonic speed, as the
paper's own global-defaults section separately warns against for any zero/small-velocity test).
