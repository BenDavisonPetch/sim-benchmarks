---
# Authored via /add-test (NORMAL path) from Dematté, Farmakalides, Millmore & Nikiforakis,
# "An all Mach number scheme for visco-resistive magnetically-dominated MHD flows", JCP 514
# (2024) 113229 (citekey: dematte2024). Section 4.4 "All Mach number lid driven MHD cavity" --
# a test explicitly introduced/proposed in THIS paper (not from a prior source).
#
# DEDUP NOTE: distinct entry from tests/lid-driven-cavity-mhd-visco-resistive (Sect 4.3.3):
# different B-field topology (Bz-only circular magnetic-pressure region here vs. uniform
# horizontal Bx there), a different terms set (viscosity+heat-conduction here, no resistivity
# stated; vs. viscosity+resistivity there, no heat-conduction stated), a time-dependent
# (ramped) lid BC here (steady lid there), and a fundamentally different validation story (no
# reference solution to compare against here, vs. a quantitative comparison to Fambri et al.
# there).

slug: all-mach-lid-driven-mhd-cavity
name: "All-Mach-Number Lid-Driven MHD Cavity (Supersonic-to-Subsonic Transition)"
provenance: literature
one_liner: "Lid-driven cavity with a Bz-only circular magnetic-pressure region and a time-ramped lid velocity driving a transition from near-zero Mach number through supersonic (M~1.8-2) and back, novel to this paper (no reference solution to compare against)."

physics:
  materials:
    - name: plasma
      base: mhd
      terms: [viscosity, heat-conduction]
      eos:
        type: gamma-law
        params: { gamma: 1.6666666666666667 }   # gamma = 5/3, global default ("unless otherwise stated"), not overridden here
  coupling: none

dimension:
  intrinsic: 2
  runnable_in: [2]

analysis_treatments: [none]

capability_flags:
  time_dependent_bc: true    # top-boundary lid velocity u_lid depends explicitly on t (Gaussian-in-time ramp)
  has_internal_boundaries: false
geometry_stress: none

geometry:
  coord_system: cartesian
  domain: { x: [-0.5, 0.5], y: [-0.5, 0.5] }
  regions:
    - id: whole
      shape: box
      params: { x: [-0.5, 0.5], y: [-0.5, 0.5] }
    - id: mag_pressure_region
      shape: cylinder
      params: { center: [0, 0], r: [0, R] }   # r = sqrt(x^2+y^2); circular region in the z=const (2D) plane

units:
  system: nondimensional     # not named by the source; values given as bare numbers
  b_field_convention: permeability-unity   # stated-here, global (Sect. 2): "the units of B are chosen such that the vacuum magnetic permeability is unity"

initial_conditions:
  aux:
    - { name: R, expr: "0.1" }
    - { name: t_peak, expr: "10.0" }
    - { name: sigma2, expr: "5.0" }
    - { name: u_max, expr: "6.0" }
    - { name: x_norm, expr: "(x + 0.5)" }   # INFERRED, not source-stated: maps domain x in [-0.5,0.5] to [0,1]
                                             # (so the parabolic bump 4*(x_norm-x_norm**2) peaks at
                                             # x=0, vanishes at x=+-0.5); x_norm's true definition is
                                             # NOT given anywhere in the source (needs-source, see
                                             # pending_extraction.md) -- this is a working convention
                                             # for validation purposes only, not a verified source value.
  equilibrium:
    - region: whole
      fields: { rho: "2.0", vx: "0.0", vy: "0.0", vz: "0.0", Bx: "0.0", By: "0.0", Bz: "0.0", p: "10.0" }
    - region: mag_pressure_region
      fields: { Bz: "0.1/sqrt(4*pi)" }
  perturbation:
    combine_rule: additive
    fields: []
  potentials: []

parameters:
  - { name: gamma, canonical: 1.6666666666666667, meaning: "ratio of specific heats (= 5/3), global default 'unless otherwise stated'" }
  - { name: R, canonical: 0.1, meaning: "radius of the initial circular Bz magnetic-pressure region" }
  - { name: Bz_region, canonical: 0.088622692545, meaning: "Bz magnitude inside r<=R, given as 0.1/sqrt(4*pi)" }
  - { name: mu, canonical: 0.02, meaning: "dynamic viscosity coefficient (stated directly for this test)" }
  - { name: lambda_heat, canonical: 1.0, meaning: "heat-capacity/conduction coefficient lambda (stated directly for this test)" }
  - { name: u_max, canonical: 6.0, meaning: "peak lid-velocity ramp amplitude parameter" }
  - { name: t_peak, canonical: 10.0, meaning: "nominal time of peak lid velocity (source names the intent, but see Notes for the as-printed exponent discrepancy)" }
  - { name: sigma2, canonical: 5.0, meaning: "ramp variance parameter sigma^2 (so sigma = sqrt(5), NOT sigma=5.0 -- stated explicitly as sigma^2=5.0)" }
  - name: x_norm
    canonical: null
    meaning: "normalisation of x used in the lid-velocity profile u_lid = 4*A*(x_norm - x_norm^2); presumably a mapping of the domain onto [0,1] but no formula is given anywhere in the visible text"
    notes: needs-source

domain_bc:
  # Physical BC (Sect 4.4): no-slip (u=0) on left/right/bottom walls; time-dependent lid velocity
  # on the top wall (see Notes for the as-printed vs. as-intended ramp-exponent discrepancy and the
  # x_norm gap -- this state expression is recorded AS PRINTED, unresolved, not guessed).
  x_lo: { type: dirichlet, state: { vx: "0.0", vy: "0.0" } }
  x_hi: { type: dirichlet, state: { vx: "0.0", vy: "0.0" } }
  y_lo: { type: dirichlet, state: { vx: "0.0", vy: "0.0" } }
  y_hi: { type: dirichlet, state: { vx: "4*(u_max*exp(-(t-t_peak)**2/(2*sigma2)))*(x_norm - x_norm**2)", vy: "0.0" } }
  # CORRECTED-FOR-VALIDATION form: source literally prints the exponent as -(1-t_peak)**2/(2*sigma2)
  # (constant "1", not "t"), which would make this expression time-INDEPENDENT and contradicts the
  # stated Gaussian-in-time ramp behaviour and capability_flags.time_dependent_bc. (t-t_peak) is used
  # here as the near-certain intended reading (see Notes / pending_extraction.md for the full
  # as-printed-vs-corrected discussion) -- NOT presented as verified source content, only as a
  # working expression. x_norm is likewise an INFERRED convention (see aux block above), not
  # source-stated. Both remain open items in pending_extraction.md.

internal_boundaries: []

time:
  t_final: 20.0   # source presents results at t=3.2, 10.0, 20.0; t=20.0 is the latest named snapshot and covers the full ramp-up/ramp-down cycle

validation_modes:
  - id: mach-number-peak-range
    purpose: "Verify the maximum Mach number of the flow reaches the stated supersonic peak (M~1.8-2) near the stated ramp-peak time, and returns to a near-zero Mach number regime after the ramp decays, as a structural check of the all-Mach transition behaviour."
    procedure: feature-location
    inputs:
      at_time: 20.0
      variables: [vx, vy, p, rho]
      features: ["max Mach number over time reaches approximately 1.8-2 near t~10 (Fig 19, Sect 4.4 text: 't=10.0 resembles a moderate (M~2) Mach number fully compressible supersonic regime')", "flow returns to a low-Mach, near-lid-driven-cavity-like regime by t=20"]
      tolerance: "physical-intuition-only check; no reference solution or numeric tolerance stated in source (source: 'there are no existing results to validate against')"
    has_exact_solution: false
    score: 2
    score_justification: "No automatable check and no reference solution exists (source explicitly states this); however the solution is well-characterised by specific, named, checkable features (peak Mach number ~1.8-2 near t=10, low-Mach regimes at t=3.2/20, a large recirculation zone forming at the bottom right at t=10) -- rubric row 2, not row 1, because the named Mach-number range is a concrete structural target even without an automatable proxy. Not inflated to 3+ absent any reference result to compare against."

references:
  - key: dematte2024
    original_intro: false   # NOT set here — only /add-refs resolves original_intro (§5.4); this paper's authorship of the test is documented in test_origin/Notes instead
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
references_unverified: []
test_origin:
  status: pending
  authored_from: dematte2024
  attribution_claims: []
  # This test is explicitly NOVEL to dematte2024 itself (not a case of resolving attribution to an
  # earlier source): "we propose another modified version of the classical lid-driven cavity test,
  # adapted here to exhibit magnetised flow which spans a wide range of Mach numbers." No
  # attribution_claims are recorded because there is no prior-source claim to capture -- dematte2024
  # IS the origin. Per the skill contract, `status` stays `pending` here regardless (only
  # /add-refs or manual review sets `resolved-*`); this note documents the origin explicitly so a
  # later resolution pass does not need to re-derive it.
reference_results:
  - key: dematte2024
    params_used: { R: 0.1, Bz_region: 0.088622692545, mu: 0.02, lambda: 1.0, u_max: 6.0, t_peak: 10.0, sigma2: 5.0, resolution_grid: "512x512", t_final: 20.0 }
    method: "proposed semi-implicit finite volume scheme; second-order-accurate MUSCL-Hancock-type TVD reconstruction for the explicit advective terms; results obtained with a velocity-dictated time step"
    resolution: "512x512 uniform Cartesian cells"
    amr: "none"
    findings: >
      At t=3.2 (very low Mach number regime): results comparable to the standard lid-driven
      cavity test. By t=10.0 (moderate, M~2, fully compressible supersonic regime): flow shape
      changes, with a large recirculation zone forming at the bottom right of the cavity. By
      t=20.0 (low Mach number again): flow becomes symmetric as it decelerates and reaches
      steady-state; magnetic pressure is advected at a slower rate as the flow decelerates. "While
      there are no existing results to validate against, the results of the simulation are
      satisfactory based on physical intuition of how the flow should behave." Fig 19 also shows
      the time evolution of the maximum Mach number, peaking at approximately 1.8 near t=10.
related_to: []
headline_score: 2
---

## Physical problem
A modified lid-driven-cavity test in visco-resistive MHD, purpose-built to exercise a wide
range of Mach numbers within a single simulation. The domain [-0.5,0.5]x[-0.5,0.5] starts
at rest with uniform density rho=2, pressure p=10, and a Bz-only magnetic field of magnitude
0.1/sqrt(4*pi) confined to a circular region of radius R=0.1 at the domain center (Bz=0
outside); MHD effects enter solely through this passively-advected Bz component so as not to
strongly influence the dynamics. The top boundary carries a time-dependent lid velocity that
ramps the flow from near-zero Mach number up through a supersonic regime (M~2) and back down,
via a Gaussian-in-time amplitude envelope peaking near t=10.

## What this test actually tests
The scheme's ability to handle a single simulation spanning near-zero, supersonic (M>1), and
transitional Mach-number regimes, including the transition to/from each extreme, alongside
correct passive advection of a magnetic-pressure region that only weakly back-reacts on the
flow.

## Qualitative behaviour
t=3.2: standard, very-low-Mach lid-driven-cavity-like flow. t=10.0: flow has accelerated
into the supersonic regime (M~2), with a large recirculation zone forming at the bottom
right of the cavity. t=20.0: flow has decelerated back to a very-low-Mach regime and become
symmetric, approaching steady-state; magnetic pressure advects more slowly as the flow
decelerates. There is no exact or community-reference solution for this test (source: "there
are no existing results to validate against, the results of the simulation are satisfactory
based on physical intuition").

## Validation notes
This entry's only validation anchor is the named, source-stated Mach-number behaviour: a
peak maximum Mach number of approximately 1.8-2 occurring near t=10, together with the
qualitative low-Mach / supersonic / low-Mach regime sequence at t=3.2/10.0/20.0 and the
stated recirculation-zone feature at t=10.0. There is no automatable proxy and no reference
solution (source states this explicitly), so the mode is scored 2 (specific, named,
checkable features; not inflated for prose richness per the rubric's rule against letting
qualitative description alone raise the score above what the checkable content supports).

## Notes
- FLAG (source oddity, confirmed by direct re-read of page 30 of the PDF, twice): the
  lid-velocity ramp amplitude is given in the source as
  `A = u_max * exp( -(1 - t_peak)^2 / (2*sigma^2) )`, i.e. literally using the constant `1`,
  not the time variable `t`, in the exponent. Taken completely literally this makes A a
  time-independent constant, which contradicts the described Gaussian-in-time ramp behaviour
  (Fig 19 bottom-right shows the maximum Mach number peaking in a bump shape near t=10, and
  the surrounding prose describes the lid velocity being "ramped up" then "ramped down").
  This is almost certainly a typesetting error in the published paper for `(t - t_peak)^2`,
  but per instruction this has been recorded AS PRINTED in `domain_bc.y_hi.state` above (see
  the comment there) rather than silently substituting the corrected form. This discrepancy
  is unresolved; do not treat either reading as verified source content without further
  confirmation.
- FLAG (source gap, confirmed by direct re-read of page 30): `x_norm`, used in
  `u_lid = 4*A*(x_norm - x_norm^2)`, is never defined anywhere in the visible text. It is
  presumably a normalisation of `x` onto `[0,1]` (consistent with `4*(x_norm - x_norm^2)`
  peaking at 1 when `x_norm=0.5`, i.e. a parabolic bump vanishing at the cavity's side
  walls), but no formula is stated. Recorded as `needs-source`/unresolved (see
  `pending_extraction.md`); NOT guessed. Because `x_norm` is undefined, the `domain_bc.y_hi`
  lid-velocity `state` expression above cannot currently be evaluated as written and is
  recorded for documentation of the as-printed source form pending resolution.
- terms: only viscosity (mu=0.02) and heat conduction (lambda=1.0) are stated for this test;
  resistivity is not mentioned anywhere in Sect 4.4, unlike the visco-resistive lid-cavity
  test (Sect 4.3.3) or the shear-layer/current-sheet/KH tests. This is treated as a genuine
  physics difference (resistivity absent/zero), not an omission on our part, and is the
  primary reason this is a NEW ENTRY rather than folded into
  `tests/lid-driven-cavity-mhd-visco-resistive` (which has resistivity present).
- Units are stored as authored (bare, nondimensional numbers); b_field_convention
  (permeability-unity) is a global, paper-wide statement (Sect. 2), not a needs-source item.
- Schema note: as in the visco-resistive lid-cavity sibling test, `domain_bc` here records
  only the velocity Dirichlet condition per face; the source gives no explicit B-field or
  density/pressure boundary statement for this specific test (Sect 4.4 does not restate the
  perfectly-conducting-wall / homogeneous-Neumann convention used in Sect 4.3.3), so none is
  inferred here by analogy.
