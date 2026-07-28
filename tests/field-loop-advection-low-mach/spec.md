---
# Authored via /add-test (NORMAL path) from Dematté, Farmakalides, Millmore & Nikiforakis, "An
# all Mach number scheme for visco-resistive magnetically-dominated MHD flows", J. Comput. Phys.
# 514 (2024) 113229 (citekey: dematte2024), Section 4.2.1 "Field loop advection (low Mach number
# benchmark)".
#
# DEDUP: physics_signature (mhd/gamma-law), analysis_treatments ([none]) and capability_flags
# (false/false) match tests/smooth-mhd-vortex, so it entered the step-1a duplicate-candidate set;
# structural compare (step 3) fails to match — smooth-mhd-vortex's IC is a swirling Gaussian
# vortex in rho/v/B/p with no potential, while this test's B field is a potential-defined
# (A_z -> curl) compact loop advected by a UNIFORM velocity with uniform rho/p — different
# expression structure, different region topology (a single conditional radial cutoff vs a smooth
# unconditional Gaussian), no equilibrium/perturbation split here vs none there either. No
# structural match -> NEW ENTRY (dedup step 4 table, row 3); no related_to.

slug: field-loop-advection-low-mach
name: "Low Mach Number Magnetic Field Loop Advection"
provenance: literature
one_liner: "A weak, compact magnetic field loop (defined via a vector potential) passively advected once around a periodic rectangular domain by a uniform low-Mach-number (M~0.006) velocity field, testing shape-preserving advection and wall-clock efficiency of a semi-implicit scheme."

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
  domain: { x: [0, 2], y: [0, 1] }
  regions:
    - id: whole
      shape: box
      params: { x: [0, 2], y: [0, 1] }

units:
  system: nondimensional      # not named by the source; bare numbers (standard convention for this benchmark)
  b_field_convention: sqrt-4pi   # A0 = 1e-3/sqrt(4*pi); the sqrt(4*pi) factor in the stated amplitude is the CGS-Gaussian<->code-units convention marker used throughout this paper's tests

initial_conditions:
  aux:
    - { name: A0, expr: "1e-3 / sqrt(4*pi)" }
    - { name: R,  expr: "0.3" }
    - { name: r,  expr: "sqrt((x-1)**2 + (y-0.5)**2)" }
    - { name: Az, expr: "A0 * max(R - r, 0)" }   # A0*(R-r) for r<=R, 0 otherwise (max(.,0) clips the tail to zero)
  equilibrium:
    - region: whole
      fields:
        rho: "1.0"
        vx: "2.0"
        vy: "1.0"
        vz: "0.0"
        p: "1e5"
  perturbation:
    combine_rule: additive
    fields: []
  potentials:
    - { name: Az, expr: "A0 * max(R - r, 0)", derives: "B = curl(A)" }   # A = (0,0,Az); Bx=dAz/dy, By=-dAz/dx, Bz=0

parameters:
  - { name: gamma, canonical: 1.6666666666666667, meaning: "ratio of specific heats (=5/3), global default" }
  - { name: A0, canonical: 0.0002820947917738781, meaning: "vector-potential loop amplitude (= 1e-3/sqrt(4*pi), nondimensional)" }
  - { name: R, canonical: 0.3, meaning: "loop radius (nondimensional length)" }
  - { name: rho0, canonical: 1.0, meaning: "uniform background density" }
  - { name: p0, canonical: 100000.0, meaning: "uniform background pressure (sets the low Mach number M~0.006 given the advection speed)" }
  - { name: vx0, canonical: 2.0, meaning: "uniform advection velocity, x-component" }
  - { name: vy0, canonical: 1.0, meaning: "uniform advection velocity, y-component" }

domain_bc:
  x_lo: { type: periodic }
  x_hi: { type: periodic }
  y_lo: { type: periodic }
  y_hi: { type: periodic }

internal_boundaries: []

time:
  t_final: 1.0   # "by this time the magnetic field loop has travelled the entire length of the diagonal ... and has returned to the initial position"
  snapshot_times: [1.0]

validation_modes:
  - id: loop-shape-preservation
    purpose: "Verify the passively-advected weak magnetic field loop preserves its compact, circularly-symmetric shape (no excess numerical diffusion) after travelling the full diagonal of the periodic domain and returning to its initial position."
    procedure: feature-location
    inputs:
      at_time: 1.0
      variables: [B]
      features: ["|B| contour shape/extent of the advected loop, compared at 20 equidistant contour levels in [1e-5,1e-3]/sqrt(4*pi) (Fig. 11)"]
      reference: { kind: reference-result, key: dematte2024 }
      tolerance: "qualitative shape preservation (loop remains compact and circular, matching the less-diffuse of the two schemes' contour plots); no numeric tolerance stated"
    has_exact_solution: false
    score: 2
    score_justification: "No exact/analytic or community-canonical solution is cited for this variant; the paper's own check is a qualitative contour-shape comparison against a second (explicit) scheme, with named, specific, checkable features (loop compactness/circularity at stated contour levels) — rubric row 2."

  - id: semi-implicit-vs-explicit-efficiency
    purpose: "Verify the reported wall-clock time and time-step-count efficiency of the proposed semi-implicit scheme relative to an explicit MUSCL/HLLEM+CT reference scheme for this low Mach number advection problem."
    procedure: norms
    inputs:
      at_time: 1.0
      variables: [wall_clock_time, n_timesteps]
      reference: { kind: reference-result, key: dematte2024 }
      tolerance: "reproduces the reported order-of-magnitude efficiency gap: ~960 time steps / 2930s (proposed) vs ~240427 time steps / 85340s (explicit reference scheme)"
    has_exact_solution: false
    score: 3
    score_justification: "A specific, quantitative reference-result comparison (reported wall-clock seconds and time-step counts for both schemes) — rubric row 3 (quantitative comparison to a reference result; no exact solution, so capped at 3 per the validation-authoring rule that an observation/model comparison tops at 3)."

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
  - key: gardinerstone2008
    original_intro: false   # only one ref may carry original_intro:true (SPEC §5.4 rule 6); this
    # test AS RUN is the low-Mach VARIANT (dumbser2019vrmhd), so that ref carries the flag instead.
    # Gardiner & Stone's origination of the BASE (non-low-Mach) loop test is still fully recorded,
    # verbatim, in test_origin.attribution_claims above — not lost, just not double-flagged here.
    verification:
      status: verified
      identifier: { doi: "10.1016/j.jcp.2007.12.017", arxiv: "0712.2634" }
      source: "crossref: 10.1016/j.jcp.2007.12.017 -> 200; arxiv api: 0712.2634 -> 1 entry"
      checked: "2026-07-28"
      meta:
        year: 2007                  # crossref priority date; print issue is 2008 (citekey year)
        first_author: Gardiner
        container: Journal of Computational Physics
        title: "An unsplit Godunov method for ideal MHD via constrained transport in three dimensions"
  - key: dumbser2019vrmhd
    original_intro: true   # "a low Mach number variation proposed by Dumbser et al. [41]" — the low-Mach variant specifically
    verification:
      status: verified
      identifier: { doi: "10.1002/fld.4681", arxiv: "1801.06592" }
      source: "crossref: 10.1002/fld.4681 -> 200; arxiv api: 1801.06592 -> 1 entry"
      checked: "2026-07-28"
      meta:
        year: 2018
        first_author: Dumbser
        container: International Journal for Numerical Methods in Fluids
        title: "A divergence-free semi-implicit finite volume scheme for ideal, viscous, and resistive magnetohydrodynamics"
references_unverified: []
test_origin:
  # Two separate stated attributions in the same sentence (§5.4): the ORIGINAL loop test is
  # Gardiner & Stone [48]; the LOW-MACH VARIANT of it (used here) is stated as "proposed by
  # Dumbser et al. [41]". Both are recorded as pending attribution_claims; /add-refs resolves
  # status/ref.
  status: pending
  authored_from: dematte2024
  attribution_claims:
    - stated_by: dematte2024
      quote: "This test represents a low Mach number variation of the benchmark magnetic field loop originally designed by Gardiner and Stone [48], to assess the ability of a numerical scheme to preserve the shape of a passively advected weak magnetic field loop that is produced by a low Mach number variation proposed by Dumbser et al. [41]"
reference_results:
  - key: dematte2024
    params_used: { domain: "[0,2]x[0,1] periodic", A0: 0.0002820947917738781, R: 0.3, rho0: 1.0, p0: 100000.0, vx0: 2.0, vy0: 1.0, t_final: 1.0 }
    method: "proposed semi-implicit FVS scheme, staggered CT; compared against a second-order explicit MUSCL-type scheme with HLLEM Riemann solver for the pressure sub-system, using the original Gardiner & Stone CT algorithm"
    resolution: "512x256 cells"
    amr: "none"
    findings: >
      Both schemes' magnetic-field-norm contours (Fig. 11, 20 equidistant levels in
      [1e-5,1e-3]/sqrt(4*pi)) are in good qualitative agreement with the literature at t=1, with
      the explicit scheme visibly more diffuse. The explicit scheme required 240427 time steps and
      85340s wall-clock time; the proposed semi-implicit scheme required only 960 time steps and
      2930s wall-clock time (two orders of magnitude fewer time steps).
related_to: []
headline_score: 3
---

## Physical problem
A weak, compact circular loop of in-plane magnetic field (defined via a z-directed vector
potential A_z that ramps linearly from A0 at the loop center to 0 at radius R=0.3, and is exactly
zero beyond R) sits inside a periodic rectangular domain [0,2]x[0,1]. Density and pressure are
uniform (rho=1, p=1e5, giving a very low plasma Mach number M~0.006 given the uniform advection
speed), and the entire domain is advected by a uniform velocity u=(2,1,0). Because the velocity
is spatially uniform, the exact solution is a rigid translation of the initial loop; by t=1 the
loop has traversed the full diagonal of the domain (periodic wrap-around) and returned to its
starting position.

## What this test actually tests
(1) Whether the scheme's constrained-transport treatment of the induction equation preserves the
compact, circular shape of a passively advected weak field loop without excessive numerical
diffusion over many periodic wraps (loop-shape-preservation). (2) Whether the proposed
semi-implicit scheme's efficiency advantage (far fewer, larger time steps at higher per-step cost)
over an explicit CT-based scheme is reproduced for this low Mach number advection problem
(semi-implicit-vs-explicit-efficiency).

## Qualitative behaviour
The loop's |B| contour remains compact and circularly symmetric under the semi-implicit scheme's
960-time-step integration; the explicit reference scheme's 240427-time-step integration produces a
visibly more diffuse (smeared) loop by t=1, per Fig. 11. There is no analytic solution to compare
against pointwise beyond the trivial "rigid translation" statement (the exact loop shape at t=1 is
identical to the IC, but the source reports only qualitative contour-plot agreement, not a
pointwise error norm).

## Validation notes
The source gives explicit efficiency numbers: 85340s / 240427 time steps (explicit MUSCL+HLLEM+CT
scheme) vs 2930s / 960 time steps (proposed semi-implicit scheme) — a ~2 order-of-magnitude
reduction in time-step count and a ~29x wall-clock speed-up, "although the computational cost per
element and time step of the proposed semi-implicit scheme is relatively high." No numeric error
norm or tolerance is stated for the shape-preservation comparison itself (Fig. 11 contour levels
only), hence the shape-preservation mode is capped at rubric row 2 rather than being elevated by
the efficiency numbers, which are scored as their own separate mode.

## Notes
`b_field_convention: sqrt-4pi` is inferred from the stated amplitude A0 = 1e-3/sqrt(4*pi), which
follows the same sqrt(4*pi) convention marker used in this paper's other MHD tests (Sect. 4.1.4,
4.1.6) rather than being restated as a units statement in Sect. 4.2.1 itself. Although the
underlying loop test (Gardiner & Stone) is 3D in general, this variant's stated domain and
velocity are purely 2D (vz=0, uniform in z); `runnable_in` is kept at `[2]` since a 3D run was not
reported for this specific variant.
