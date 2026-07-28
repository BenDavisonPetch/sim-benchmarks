---
# Authored via /add-test (NORMAL path) from Dematté, Farmakalides, Millmore & Nikiforakis, "An
# all Mach number scheme for visco-resistive magnetically-dominated MHD flows", J. Comput. Phys.
# 514 (2024) 113229 (citekey: dematte2024), Sections 4.2.2 "Numerical simulation of plasma
# equilibrium (magnetic pressure dominated, STATIC)" and 4.2.3 "Numerical simulation of advected
# plasma equilibrium (magnetic pressure dominated)".
#
# INTRA-PAPER FOLD (dedup step 3/6, cf. tests/smooth-mhd-vortex's own fold note): 4.2.3 states
# verbatim "As an extension to the previous test case ... The initial conditions are the same as
# for the previous test, but the velocity is now u=(0.04,0.04,0.0)" — an explicit same-IC
# statement. Both sections share the identical theta-pinch equilibrium expression, domain
# ([-3,3]x[-3,3]), and resolution (256x256); only the (uniform) advection velocity and the run
# duration/validation story differ. A velocity value change on an EXISTING vector field (v is
# already part of the mhd state, not a new term or capability) is a parameter, not an identity
# fork (SPEC §2.2) — structurally identical to the smooth-mhd-vortex fold, which collapsed two
# sub-tests differing in domain extent and run duration into one entry. Folded into ONE canonical
# entry with two validation_modes: the STATIC case (4.2.2) is a well-balancing/force-balance check
# whose validation story is "the scheme marches to t_final in a SINGLE time step because the IC
# is already the exact equilibrium"; the ADVECTED case (4.2.3) adds a genuinely different,
# separately-scored quantitative story (wall-clock time and normalised L2(p) error vs increasing
# (Bz)0). Both are recorded as distinct reference_results rows (params_used carries the velocity
# and t_final that differ) rather than as two entries.
#
# DEDUP (cross-source): physics_signature (mhd/gamma-law) matches
# theta-pinch-compression-embedded-boundary and standing-magnetosonic-wave-theta-pinch-cylinder
# (both from jones2026), triggering the step-1a duplicate-candidate set. Structural compare
# (step 3) fails to match either: theta-pinch-compression-embedded-boundary has a moving
# perfect-conductor embedded boundary (has_internal_boundaries=true there, false here) and a
# compressing/imploding IC (radially-inward velocity v_r=-r/a); this entry has NO embedded
# boundary and a STATIC/uniformly-advected force-balance IC. standing-magnetosonic-wave-theta-
# pinch-cylinder is an eigenmode perturbation-on-equilibrium test in cylindrical coordinates with
# axis-singularity treatment and a Dirichlet rigid-wall BC (analysis_treatments differs from this
# entry's [none]). Per dedup step 1b (same physics_signature, differs in exactly one of
# analysis_treatments/capability_flags for each), both are SIBLINGS, not duplicates -> NEW
# SIBLING decision, related_to links added (this file only; the two existing entries are not
# touched, per the assignment's do-not-touch instruction).

slug: theta-pinch-equilibrium-force-balance
name: "Static and Advected Theta-Pinch Force-Balance Equilibrium"
provenance: literature
one_liner: "A magnetically-dominated theta-pinch force-balance equilibrium (grad P = J x B, adapted from Freidberg) that should show zero evolution when static, used both as a well-balancing check (scheme reaches t_final in one time step) and, with a small uniform advection velocity added, as an efficiency/accuracy comparison across magnetic field strengths."

physics:
  materials:
    - name: plasma
      base: mhd
      terms: []
      eos:
        type: gamma-law
        params: { gamma: 1.6666666666666667 }   # gamma = 5/3, global default; not restated for this test
  coupling: none

dimension:
  intrinsic: 2
  runnable_in: [2]

analysis_treatments: [none]

capability_flags:
  time_dependent_bc: false
  has_internal_boundaries: false
geometry_stress: none

geometry:
  coord_system: cartesian
  domain: { x: [-3.0, 3.0], y: [-3.0, 3.0] }
  regions:
    - id: whole
      shape: box
      params: { x: [-3.0, 3.0], y: [-3.0, 3.0] }

units:
  system: nondimensional      # not named by the source; bare numbers (standard convention for this benchmark)
  b_field_convention: permeability-unity   # global default (Sect. 2): "the units of B are chosen such that the vacuum magnetic permeability is unity" — not overridden here (B0=8.0 given directly, no sqrt(4*pi) factor, unlike Sect 4.1.6/4.2.1)

initial_conditions:
  aux:
    - { name: B0,   expr: "8.0" }
    - { name: R,    expr: "0.9" }
    - { name: p_bg, expr: "0.1" }
    - { name: u0x,  expr: "0.0" }   # static case (4.2.2); advected case (4.2.3) sets u0x=u0y=0.04 (see reference_results row 2)
    - { name: u0y,  expr: "0.0" }
    - { name: r,    expr: "sqrt(x**2 + y**2)" }
    - { name: Bz,   expr: "B0 * min((r/R)**2, 1)" }   # B0*r^2/R^2 for r<=R, B0 otherwise (min(.,1) caps the ratio at 1 beyond R)
  equilibrium:
    - region: whole
      fields:
        rho: "1.0"
        vx: "u0x"
        vy: "u0y"
        vz: "0.0"
        Bx: "0.0"
        By: "0.0"
        Bz: "Bz"
        p: "p_bg + 0.5 * (B0**2 - Bz**2)"   # = 0.5*(B0^2-Bz^2)+0.1 for r<=R, and = p_bg (=0.1) for r>R since Bz=B0 there — one formula covers both stated regions
  perturbation:
    combine_rule: additive
    fields: []
  potentials: []

parameters:
  - { name: gamma, canonical: 1.6666666666666667, meaning: "ratio of specific heats (=5/3), global default" }
  - { name: B0, canonical: 8.0, meaning: "peak axial magnetic field strength (nondimensional)" }
  - { name: R, canonical: 0.9, meaning: "theta-pinch core radius (nondimensional length)" }
  - { name: rho0, canonical: 1.0, meaning: "uniform density (nondimensional)" }
  - { name: p_bg, canonical: 0.1, meaning: "background/exterior pressure offset (nondimensional)" }
  - { name: u0x, canonical: 0.0, meaning: "uniform advection velocity, x-component (0 for the static case 4.2.2; the advected case 4.2.3 uses 0.04, recorded in reference_results)" }
  - { name: u0y, canonical: 0.0, meaning: "uniform advection velocity, y-component (0 for the static case 4.2.2; the advected case 4.2.3 uses 0.04, recorded in reference_results)" }

domain_bc:
  x_lo: { type: outflow }
  x_hi: { type: outflow }
  y_lo: { type: outflow }
  y_hi: { type: outflow }

internal_boundaries: []

time:
  t_final: 400   # covers both modes: static well-balancing check at t=2.0 (4.2.2, "arbitrary time"), advected run to t=400 (4.2.3, one full advection of the equilibrium around the domain)
  snapshot_times: [2.0, 400]

validation_modes:
  - id: force-balance-well-balancing
    purpose: "Verify the scheme preserves the exact theta-pinch force-balance equilibrium (zero flow) with no evolution of density or pressure, reaching the final time in a single implicit time step as a direct consequence of the IC already satisfying grad P = J x B."
    procedure: well-balancing
    inputs:
      at_time: 2.0
      variables: [rho, p]
      reference: { kind: reference-result, key: dematte2024 }
      tolerance: "no evolution of the fluid variables away from the IC (source: 'there should be no evolution of the fluid variables in time'); the scheme reaches t_final=2.0 in exactly ONE time step, versus 8833 time steps (with visible diffusion of the solution) for a divergence-free explicit reference scheme over the same interval"
    has_exact_solution: true
    score: 4
    score_justification: "The IC is the exact force-balance equilibrium at all times (well-balancing with a KNOWN exact answer), and the paper reports a specific, reproducible, automatable diagnostic distinguishing exact preservation from numerical drift: the scheme takes exactly ONE time step to reach t_final, vs 8833 steps (with visible diffusion) for the explicit comparison scheme — rubric row 4 (reliable automatable quantitative check, analogous to a feature-location/self-convergence check). Not row 5: no convergence-order sweep to a theoretical order is reported for this test (unlike the standing-wave theta-pinch sibling)."

  - id: advected-equilibrium-efficiency-scaling
    purpose: "Verify the reported normalised L2(pressure) error and total wall-clock time for the advected theta-pinch equilibrium remain approximately constant across increasing magnetic field magnitudes (Bz)0, in contrast to the exponential wall-clock/error growth of a divergence-free explicit reference scheme."
    procedure: norms
    inputs:
      at_time: 400
      variables: [p]
      reference: { kind: reference-result, key: dematte2024 }
      tolerance: "normalised L2(p) error (relative to the exact/IC equilibrium) and total wall-clock time remain approximately constant across (Bz)0 in {1,2,4,8,16,32} for the proposed scheme (time step unchanged in all six runs); the explicit reference scheme shows exponential growth in both wall-clock time and L2(p) error with (Bz)0, reaching L2~1 (fully diffused profile) and ~250x longer wall-clock time at (Bz)0=32"
    has_exact_solution: true
    score: 3
    score_justification: "Quantitative comparison to a specific reference result (reported wall-clock times and normalised L2(p) error across six (Bz)0 values, plus the single-case numbers: 1150 vs 117546 time steps, 104s vs 4240s) — rubric row 3. Although the IC remains the exact equilibrium, no convergence-order sweep vs the theoretical order is reported for the advected case, and prose richness (the six-point (Bz)0 sweep) is not allowed to inflate the score past 3 per the validation-authoring rule that an observation/efficiency comparison without an exact-solution convergence check tops at 3."

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
  - key: freidberg2008
    original_intro: true   # "a simple theta-pinch solution adapted from Freidberg [75]"
    verification:
      status: verified
      identifier: { doi: "10.1017/CBO9780511755705" }
      source: "crossref: 10.1017/CBO9780511755705 -> 200"
      checked: "2026-07-28"
      meta:
        year: 2007
        first_author: Freidberg
        container: Cambridge University Press
        title: "Plasma Physics and Fusion Energy"
references_unverified: []
test_origin:
  status: pending
  authored_from: dematte2024
  attribution_claims:
    - stated_by: dematte2024
      quote: "we restrict ourselves to a simple theta-pinch solution adapted from Freidberg [75]"
reference_results:
  - key: dematte2024
    params_used: { mode: "static (4.2.2)", B0: 8.0, R: 0.9, u0x: 0.0, u0y: 0.0, t_final: 2.0 }
    method: "proposed semi-implicit FVS scheme, staggered CT; compared against a divergence-free second-order explicit MUSCL-type scheme with HLLEM Riemann solver for the pressure sub-system, using the original Gardiner & Stone CT algorithm"
    resolution: "256x256 cells"
    amr: "none"
    findings: >
      The proposed semi-implicit scheme reaches t_final=2.0 in a single time step (Fig. 12
      caption: "the proposed semi-implicit scheme is able to march to the final time of the
      simulation in a single iteration"). The explicit comparison scheme requires 8833 time
      steps to reach the same final time, over which the density/pressure solution visibly
      diffuses (Fig. 12, right panel).
  - key: dematte2024
    params_used: { mode: "advected (4.2.3)", B0: 8.0, R: 0.9, u0x: 0.04, u0y: 0.04, t_final: 400, Bz0_sweep: [1, 2, 4, 8, 16, 32] }
    method: "same proposed semi-implicit scheme and explicit comparison scheme as the static case, at a fixed resolution of 256x256 for the (Bz)0 efficiency sweep"
    resolution: "256x256 cells"
    amr: "none"
    findings: >
      Base case ((Bz)0 as stated, B0=8.0): proposed scheme requires 1150 time steps / 104s
      wall-clock to reach t=400, vs 117546 time steps / 4240s for the explicit scheme (a ~40x
      wall-clock speed-up); the proposed scheme's solution is visibly less diffuse (Fig. 13, 1D
      pressure cross-section). Sweep over (Bz)0 in {1,2,4,8,16,32}: the proposed scheme's total
      wall-clock time and normalised L2(p) error remain essentially constant across all six
      values (time step unchanged); the explicit scheme shows exponential growth in both
      wall-clock time and L2(p) error with (Bz)0, reaching a fully diffused profile (normalised
      L2=1) and ~250x longer wall-clock time at (Bz)0=32 (Fig. 13, efficiency plot).
related_to: [theta-pinch-compression-embedded-boundary, standing-magnetosonic-wave-theta-pinch-cylinder]
headline_score: 4
---

## Physical problem
A cylindrically-symmetric (in the x-y plane) theta-pinch magnetic-pressure equilibrium, adapted
from Freidberg's textbook treatment of force-balance plasma confinement: a uniform-density plasma
with an axial field Bz that rises quadratically from 0 at the center to B0=8.0 at radius R=0.9 and
is uniform (=B0) beyond R, with the pressure profile p = 0.5*(B0^2 - Bz^2) + 0.1 chosen so that
grad P = J x B holds exactly everywhere (zero net force). In the STATIC case (4.2.2) the velocity
is identically zero, so the configuration is a true equilibrium with no flow. In the ADVECTED
case (4.2.3), the identical equilibrium profile is given a small uniform translation velocity
u=(0.04,0.04,0), so the exact solution becomes a rigid advection of the same force-balance
profile once around the domain by t=400.

## What this test actually tests
(1) Whether the scheme exactly (to machine/implicit-solver precision) preserves a magnetically-
dominated, low-Mach-number force-balance equilibrium with zero flow, without the numerical
diffusion an explicit scheme exhibits over many time steps (force-balance-well-balancing) — the
paper's own reported diagnostic is that the scheme reaches the final time in a single time step.
(2) Whether the scheme's reported efficiency advantage (near-constant wall-clock time and L2
pressure error as the magnetic field strength (Bz)0 increases, vs the exponential blow-up of an
explicit scheme's cost/error) is reproduced when the same equilibrium is advected
(advected-equilibrium-efficiency-scaling).

## Qualitative behaviour
Static case: density and pressure remain visually identical to the IC at t=2.0 under the proposed
scheme (Fig. 12, left), while the explicit comparison scheme's solution has visibly diffused by
the same time (Fig. 12, right). Advected case: the 1D pressure cross-section at t=400 (Fig. 13,
left) shows the proposed scheme's profile close to the exact (IC) solution, while the explicit
scheme's profile is markedly more diffuse; the efficiency plot (Fig. 13, right) shows the two
schemes' wall-clock-time-vs-L2-error trade-off diverging sharply as (Bz)0 increases.

## Validation notes
Static case: reaching t_final in a single time step (vs 8833 for the explicit scheme) is reported
as a direct, specific, reproducible number, not merely a qualitative visual match — the basis for
scoring this mode at rubric row 4 rather than the row-3 qualitative treatment given to the
smooth-mhd-vortex long-time-stationarity mode (which had no comparably specific automatable
number). Advected case: base numbers are 1150 vs 117546 time steps and 104s vs 4240s wall-clock
(a ~40x speed-up); the (Bz)0 sweep over {1,2,4,8,16,32} shows the proposed scheme's wall-clock
time and normalised L2(p) error essentially flat, while the explicit scheme's cost/error grows
exponentially, reaching a fully diffused profile (normalised L2=1) and ~250x longer wall-clock
time at (Bz)0=32. No numeric tolerance for the L2(p) error or wall-clock ratios is stated beyond
these reported figures (Fig. 13), consistent with capping this mode at rubric row 3.

## Notes
Domain boundary conditions are NOT explicitly restated in Sect. 4.2.2/4.2.3 of the source (checked
against the full normalized extract; no statement found). `domain_bc: outflow` is an INFERRED
convention (the compact equilibrium structure, R=0.9, sits well inside the [-3,3]x[-3,3] domain
and is never expected to reach the boundary before t_final in the static case; the advected
case's velocity is tiny, 0.04, so the profile also stays well clear of the boundary by t=400).
Recorded per the same "standard practice, unconfirmed" convention used in
tests/ideal-mhd-riemann-problem — see `pending_extraction.md`. The two runs (static vs advected)
share one canonical geometry/IC form and are folded per the header note above; `u0x`/`u0y` are
authored as `parameters` with `canonical: 0.0` (the static case) rather than as two separate
entries, mirroring how `tests/smooth-mhd-vortex` records its two domain variants as two
`reference_results` rows on one entry.
