---
# Authored via /add-test (NORMAL path) from Dematté, Farmakalides, Millmore & Nikiforakis,
# "An all Mach number scheme for visco-resistive magnetically-dominated MHD flows", JCP 514
# (2024) 113229 (citekey: dematte2024). Section 4.3.1 "Shear layer and current sheet"
# (visco-resistive VRMHD), the viscous half of the pair.
#
# INTRA-PAPER DEDUP: paired with `mhd-current-sheet` (same section, same exact-solution
# family v(x,t) = -erf(x/(2*sqrt(mu*t))) attributed to Schlichting & Gersten). The two tests
# have DIFFERENT IC structural form (velocity discontinuity here vs magnetic-field
# discontinuity there) even though physics_signature/analysis_treatments/capability_flags are
# identical (both run the full VRMHD term set: eta=mu=0.1 nonzero "in both cases" per the
# source, even though the shear layer's B=0 IC and the current sheet's u=0 IC each make one
# term physically inert for that run). Per dedup step 3 (structural compare of IC form), the
# velocity-jump vs field-jump ICs do not match structurally, so these are kept as separate
# entries (not folded, not a capability-flag sibling pair) and cross-linked via `related_to`.

slug: mhd-shear-layer
name: "Visco-Resistive MHD Shear Layer"
provenance: literature
one_liner: "1D viscous shear layer in the VRMHD system with an exact self-similar erf velocity profile (Schlichting & Gersten); tests the viscous term and CT robustness under a nominally 1D setup run on a thin 2D strip."

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
      fields: { rho: "1.0", vx: "0.0", vy: "1.0", vz: "0.0", Bx: "0.0", By: "0.0", Bz: "0.0", p: "1e5" }
    - region: right
      fields: { rho: "1.0", vx: "0.0", vy: "-1.0", vz: "0.0", Bx: "0.0", By: "0.0", Bz: "0.0", p: "1e5" }
  perturbation:
    combine_rule: additive
    fields: []
  potentials: []

parameters:
  - { name: gamma, canonical: 1.6666666666666667, meaning: "ratio of specific heats (= 5/3), global default" }
  - { name: mu, canonical: 0.1, meaning: "dynamic viscosity coefficient (VRMHD viscous term)" }
  - { name: eta, canonical: 0.1, meaning: "resistivity coefficient (VRMHD resistive term); inert here since B=0 in this test's IC, but the stated fluid-parameter set 'eta=mu=0.1... in both cases' applies to both this test and mhd-current-sheet" }
  - { name: Pr, canonical: 1.0, meaning: "Prandtl number (dimensionless), stated for both shear-layer and current-sheet tests" }
  - { name: cv, canonical: 1.0, meaning: "specific heat capacity at constant volume (code units), stated for both shear-layer and current-sheet tests" }
  - { name: kappa, canonical: 0.16666666666666666, meaning: "thermal conductivity implied by the stated Pr=1, cv=1, gamma=5/3 via the standard ideal-gas relation kappa = mu*cp/Pr with cp = gamma*cv; NOT stated as a bare number in the source itself, but mechanically computed from quantities the source DOES state (mu, Pr, cv, gamma) via a standard, non-source-specific thermodynamic identity, not fabricated -- flagged in Notes" }

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
    purpose: "Verify the numerical y-velocity (shear) profile against the exact self-similar erf solution v(x,t) = -erf(x/(2*sqrt(mu*t))) at t=0.1."
    procedure: exact-solution-compare
    inputs:
      at_time: 0.1
      variables: [vy]
      reference: { kind: reference-result, key: dematte2024 }
      tolerance: "close visual agreement with the exact erf profile (Fig. 14, left panel); no explicit numeric L1/L2/Linf tolerance table is given in the source (only a single 200x4 grid is shown, no resolution sequence)"
    has_exact_solution: true
    score: 4
    score_justification: "A genuine closed-form exact solution exists at all times (erf profile), making an automatable, resolution-independent norms check straightforward -- rubric row 4/5 territory. Capped at 4 rather than 5 because the source itself reports only a single-grid (200x4) qualitative overlay (Fig. 14) with no resolution sequence/convergence-order table demonstrating the theoretical order is achieved."

references:
  - key: dematte2024
    original_intro: false           # the entry was authored FROM this paper, which is not where the test came from
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
      quote: "The exact solution to this test problem is given by Schlichting and Gersten [76] as v(x,t) = -erf( (1/2) * x / sqrt(mu*t) )."
reference_results:
  - key: dematte2024
    params_used: { domain: "[-1,1]x[-0.02,0.02], periodic-y/transmissive-x, 200x4 cells", eta: 0.1, mu: 0.1, Pr: 1.0, cv: 1.0, t_final: 0.1 }
    method: "proposed semi-implicit FVS scheme; VRMHD viscous/resistive terms treated implicitly (GMRES tol 1e-15, Picard sigma=1e-12, R=Q=S=2); staggered CT for div-B"
    resolution: "200x4 cells (2D strip, y-direction inert)"
    amr: "none"
    findings: >
      Fig. 14 (left panel): numerical v-velocity profile at t=0.1 matches the exact erf solution
      closely (black line vs. numerical points); the test "ran in 23 time steps, only possible
      due to the implicit treatment of not only the chosen pressure sub-system but also the
      visco-resistive terms."
related_to: [mhd-current-sheet]
headline_score: 4
---

## Physical problem
A 1D viscous shear layer: two half-spaces of quiescent, uniform-density, uniform-pressure fluid
with a discontinuous jump in the tangential (y) velocity component at x=0 (+1 for x<=0, -1 for
x>0), evolved under the visco-resistive MHD (VRMHD) equations with B=0. Viscous diffusion smooths
the velocity discontinuity into the classical self-similar Schlichting-Gersten erf profile. Run
on a thin 2D strip (rather than truly 1D) specifically to confirm that the constrained-transport
divergence-cleaning machinery does not introduce spurious y-dependence into an otherwise
1D-translation-invariant problem.

## What this test actually tests
Diffusive accuracy of the scheme's viscous term against a genuine closed-form exact solution
(the erf self-similar profile), and (secondarily, qualitatively) that constrained transport does
not break the 1D symmetry of the problem when run on a multi-cell-thick 2D strip.

## Qualitative behaviour
The velocity jump at x=0 smooths monotonically over time following v(x,t) = -erf(x/(2*sqrt(mu*t)));
by t=0.1 with mu=0.1 the profile has a diffusion length scale ~2*sqrt(mu*t) = 2*sqrt(0.01) = 0.2 in
x. No y-dependence should appear in a correctly-behaving scheme (the CT-symmetry-breaking trap the
source explicitly designed this 2D-strip geometry to catch).

## Validation notes
The exact solution is closed-form at all t>0, making this an automatable, resolution-independent
check in principle (rubric row 4/5). The source's own reported comparison (Fig. 14) is a single
200x4-cell run against the exact profile with no stated numeric L1/L2/Linf error or a resolution
sequence demonstrating convergence order -- so this entry is scored 4, not 5 (no demonstrated
order-of-accuracy data in-source; see docs/scoring-rubric.md row 5 vs row 4).

## Notes
`kappa` (heat-conduction coefficient) is not stated as a bare number in the source; it is computed
here from the source's own stated Pr=1, cv=1, gamma=5/3 via the standard ideal-gas relation
kappa = mu*cp/Pr with cp = gamma*cv (so kappa = 0.1*(5/3*1)/1 = 1/6). This is a mechanical
application of a universal thermodynamic identity to explicitly-stated source quantities, not an
invented value -- distinguished from a genuine `needs-source` gap (contrast `mhd-current-sheet`'s
Bz, which has no source-derivable value at all).

`domain_bc` (transmissive-x / periodic-y) and the eta=mu=0.1/Pr=1/cv=1 fluid-parameter set are
stated jointly for both this test and `mhd-current-sheet` ("In both cases, the fluid parameters
are chosen as..."); both entries carry the identical VRMHD term set (viscosity + resistivity +
heat-conduction) even though each test's own IC leaves one diffusive term (resistivity here,
viscosity there) physically inert for that particular run -- term presence is determined by
coefficient value, not by whether the field it acts on is nonzero in that IC (registry
`terms/resistivity.md`, `terms/viscosity.md`).
