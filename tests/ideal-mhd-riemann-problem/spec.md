---
# Authored via /add-test (NORMAL path) from Dematté, Farmakalides, Millmore & Nikiforakis,
# "An all Mach number scheme for visco-resistive magnetically-dominated MHD flows", JCP 514
# (2024) 113229 (citekey: dematte2024). Section 4.1.1 "Riemann problem tests".
#
# INTRA-PAPER DEDUP (orchestrator, SPEC 9.1 step 2d): the source names four Riemann problems
# (RP1-RP4). All four share an IDENTICAL structural form (two constant states W_L, W_R
# separated by a single discontinuity at x=x0, on domain [0,1], ideal MHD, gamma-law EoS,
# no terms) and differ ONLY in the numeric state values, x0, and output time (dedup 2.1
# item 3: parameter values never enter identity). Per the dedup worked-case precedent ("2D
# Sod at 30 vs 45 -> existing entry; parameter; two reference_results"), RP1-RP4 fold into
# ONE canonical entry. RP1 (Brio & Wu) is authored as the canonical numeric preset; RP2-4
# are recorded as additional reference_results (params_used) on this same paper.

slug: ideal-mhd-riemann-problem
name: "1D Ideal MHD Riemann Problem (Shock-Tube Family)"
provenance: literature
one_liner: "1D ideal-MHD Riemann problem: two constant states separated by a discontinuity; canonical preset is the Brio-Wu shock tube (RP1), with RP2 (Ryu-Jones seven-wave), RP3, RP4 as parameter presets on the same entry."

physics:
  materials:
    - name: plasma
      base: mhd
      terms: []
      eos:
        type: gamma-law
        params: { gamma: 1.6666666666666667 }   # gamma = 5/3, global default ("unless otherwise stated"), stated-here
  coupling: none

dimension:
  intrinsic: 1
  runnable_in: [1]

analysis_treatments: [none]

capability_flags:
  time_dependent_bc: false
  has_internal_boundaries: false
geometry_stress: none

geometry:
  coord_system: cartesian
  domain: { x: [0, 1] }
  regions:
    - id: left
      shape: box
      params: { x: [0, x0] }
    - id: right
      shape: box
      params: { x: [x0, 1] }

units:
  system: nondimensional      # not named by the source; values given as bare numbers (standard shock-tube convention)
  b_field_convention: permeability-unity   # stated-here, global (Sect. 2): "the units of B are chosen such that the vacuum magnetic permeability is unity"

initial_conditions:
  aux:
    - { name: x0, expr: "0.5" }   # RP1 (Brio-Wu, canonical preset); RP4 uses x0=0.4 (see reference_results)
  equilibrium:
    - region: left
      fields: { rho: "1.0", vx: "0.0", vy: "0.0", vz: "0.0", Bx: "0.75", By: "1.0", Bz: "0.0", p: "1.0" }
    - region: right
      fields: { rho: "0.125", vx: "0.0", vy: "0.0", vz: "0.0", Bx: "0.75", By: "-1.0", Bz: "0.0", p: "0.1" }
  perturbation:
    combine_rule: additive
    fields: []
  potentials: []

parameters:
  - { name: gamma, canonical: 1.6666666666666667, meaning: "ratio of specific heats (= 5/3), global default 'unless otherwise stated'" }
  - { name: x0, canonical: 0.5, meaning: "initial discontinuity location (RP1-3); RP4 uses x0=0.4" }
  - { name: rho_L, canonical: 1.0, meaning: "left-state density (RP1/Brio-Wu)" }
  - { name: rho_R, canonical: 0.125, meaning: "right-state density (RP1/Brio-Wu)" }
  - { name: Bx_shared, canonical: 0.75, meaning: "normal B-field component, uniform L/R (RP1/Brio-Wu; div-B compatibility)" }
  - { name: By_L, canonical: 1.0, meaning: "left-state tangential B_y (RP1/Brio-Wu)" }
  - { name: By_R, canonical: -1.0, meaning: "right-state tangential B_y (RP1/Brio-Wu)" }
  - { name: p_L, canonical: 1.0, meaning: "left-state gas pressure (RP1/Brio-Wu)" }
  - { name: p_R, canonical: 0.1, meaning: "right-state gas pressure (RP1/Brio-Wu)" }

domain_bc:
  # NOT explicitly stated in Sect. 4.1.1 (unlike the shear-layer/current-sheet tests, which do
  # state "transmissive... x-direction"). Inferred as outflow/zero-gradient, standard practice
  # for a shock tube whose waves do not reach the domain boundary by t_final; flagged in
  # pending_extraction.md as a convention needing confirmation against the Brio & Wu (1988) /
  # Ryu & Jones (1995) primary sources.
  x_lo: { type: outflow }
  x_hi: { type: outflow }

internal_boundaries: []

time:
  t_final: 0.1     # RP1 T_out; RP2=0.2, RP3=0.15, RP4=0.16 (see reference_results)
  snapshot_times: []

validation_modes:
  - id: rh-jump-shocks
    purpose: "Verify measured pre/post-shock jumps across the MHD shocks and discontinuities against the analytic Rankine-Hugoniot jump conditions for the ideal MHD system, for each named Riemann preset (RP1-RP4)."
    procedure: rankine-hugoniot-jump
    inputs:
      at_time: 0.1
      variables: [rho, vx, vy, Bx, By, p]
      tolerance: "measured jump within a few percent of the analytic MHD RH relations (grid-resolution dependent)"
    has_exact_solution: false
    score: 4
    score_justification: "No exact full-profile solution, but the MHD Rankine-Hugoniot jump conditions are analytic and give a reliable, automatable, resolution-independent check (rubric row 4); this is a community-canonical benchmark family (Brio & Wu; Ryu & Jones; Dumbser et al.; Fambri)."

  - id: profile-vs-high-res-reference
    purpose: "Compare density and B_y profiles at the stated output time against the paper's own high-resolution reference solution, for each Riemann preset."
    procedure: norms
    inputs:
      at_time: 0.1
      variables: [rho, By]
      reference: { kind: reference-result, key: dematte2024 }
      tolerance: "visual/qualitative agreement as reported (Fig. 2); no numeric tolerance stated in source"
    has_exact_solution: false
    score: 3
    score_justification: "Quantitative reference profile exists (paper's own high-resolution MUSCL/HLLC run) but comparison as reported is visual, not a stated numeric norm; tops at 3 (rubric)."

references:
  - key: brio1988
    original_intro: true
    verification: { status: verified, identifier: { doi: "10.1016/0021-9991(88)90120-9" }, source: "verify_refs.py live HTTP resolution (doi.org -> HTTP 200); identifier corroborated by ADS, dl.acm.org, ScienceDirect listings (WebSearch); full text paywalled, no free copy found (ScienceDirect abstract page returns HTTP 403; no arXiv preprint exists pre-dating arXiv) -- identifier is verified, no reference_result recorded (SPEC 5.2 no-fabrication: cannot report findings not read)", checked: "2026-07-24" }
  - key: ryujones1995
    original_intro: false
    verification: { status: verified, identifier: { doi: "10.1086/175437", arxiv: "astro-ph/9404074" }, source: "verify_refs.py live HTTP resolution (doi.org -> HTTP 202); full text retrieved via arXiv preprint astro-ph/9404074 (identical title/authors/journal ref to ApJ 442, 228 confirmed on the arXiv abstract page)", checked: "2026-07-24" }
  - key: dumbser2024vrmhd
    original_intro: false
    verification: { status: verified, identifier: { arxiv: "1801.06592" }, source: "verify_refs.py live HTTP resolution (arxiv.org -> HTTP 200); full text retrieved via the arXiv preprint. NOTE: published version is Dumbser, Balsara, Tavelli & Fambri, Int. J. Numer. Methods Fluids 89 (2019) 16-42, doi:10.1002/fld.4681 -- actual publication year 2019, not 2024 as the citekey suggests; DOI resolution via doi.org returned HTTP 403 (Wiley blocks scripted HEAD/GET in this environment) so the arXiv id is used as the resolvable identifier instead", checked: "2026-07-24" }
  - key: fambri2023
    original_intro: false
    verification: { status: verified, identifier: { arxiv: "2012.11218" }, source: "verify_refs.py live HTTP resolution (arxiv.org -> HTTP 200); full text retrieved via the arXiv preprint. NOTE: published version is Fambri, Int. J. Numer. Methods Fluids 93(12) (2021) 3447-3489, doi:10.1002/fld.5041 -- actual publication year 2021, not 2023 as the citekey suggests; DOI resolution via doi.org returned HTTP 403 (Wiley blocks scripted HEAD/GET in this environment) so the arXiv id is used as the resolvable identifier instead", checked: "2026-07-24" }
  - key: dematte2024
    original_intro: false
    verification: { status: verified, identifier: { doi: "10.1016/j.jcp.2024.113229" }, source: "verify_refs.py live HTTP resolution (doi.org -> HTTP 200); full text retrieved via the Cambridge institutional repository accepted manuscript (open access)", checked: "2026-07-24" }
references_unverified: []
reference_results:
  # brio1988 intentionally has NO reference_result: its identifier is verified (DOI resolves,
  # corroborated by ADS/dl.acm.org/ScienceDirect listings) but the paper's own full text is
  # paywalled with no free copy locatable (ScienceDirect returns HTTP 403; JCP 1988 predates
  # arXiv). Per the no-fabrication contract (SPEC 5.2), findings/method/resolution are recorded
  # only when actually read from the source, never typed from secondary summaries or memory.
  - key: ryujones1995
    params_used: { preset: "RP2 origin ('test 2a', seven-wave shock tube)", x0: 0.5, rho_L: 1.08, rho_R: 1.0, vx_L: 1.2, vx_R: 0.0, vy_L: 0.01, vy_R: 0.0, vz_L: 0.5, vz_R: 0.0, Bx: 0.564190, By_L: 1.015541, By_R: 1.128379, Bz_L: 0.564190, Bz_R: 0.564190, p_L: 0.95, p_R: 1.0, t_final: 0.2 }
    method: "second-order-accurate explicit finite-difference Total Variation Diminishing (TVD) scheme (Harten 1983), a Roe-type upwind linearization with simple (non-analytic) cell-boundary averaging; compared against the authors' own nonlinear MHD Riemann solver, which treats fast/slow rarefactions exactly rather than as rarefaction shocks"
    resolution: "512 cells on x in [0,1]"
    amr: "none"
    findings: >
      Fig. 2a (this test, their "test 2a"): fast shocks, rotational discontinuities and slow shocks
      propagate from each side of the contact discontinuity. Strong fast shocks are resolved within
      2-4 cells while weak slow shocks require more cells. With the rotational-discontinuity
      steepening of Sect. 2.3, rotational discontinuities spread over only 3-5 cells (6-8 cells
      without steepening); the contact discontinuity spreads over more cells (steepening the contact
      discontinuity was found to generate numerical oscillations, so it is not applied). Courant
      constant 0.8 used. NOTE: the right state used in this ref is rho_R=1.0, By_R=4/sqrt(4*pi),
      p_R=1.0 (a clean equilibrium state); this differs from the RP2 preset canonical to this entry
      (rho_R=0.9891, By_R=1.135262, p_R=0.97159), which is inherited from dematte2024's Table 1 and
      is itself inherited from a modified right state used by dumbser2024vrmhd and fambri2023 -- both
      of whom nonetheless attribute the RP2 concept to this paper.
  - key: dumbser2024vrmhd
    params_used: { preset: "RP1 (Brio-Wu)", domain: "[-0.5,0.5]", xd: 0.0, rho_L: 1.0, rho_R: 0.125, p_L: 1.0, p_R: 0.1, t_final: 0.1, CFL: 0.9 }
    method: "semi-implicit finite volume (SIFV) scheme; convective subsystem discretized explicitly with a second-order MUSCL-type TVD reconstruction, pressure subsystem treated implicitly; compared to an exact MHD Riemann solver (courtesy S.A.E.G. Falle)"
    resolution: "1000 pressure control volumes on domain [-0.5,0.5]"
    amr: "none"
    findings: >
      All standard finite volume schemes, including this one, produce a compound wave instead of the
      wave pattern suggested by the exact Riemann solver in the density profile; only Glimm's random
      choice method reproduces the correct solution (per Falle). Numerical results are in line with
      others published in the literature despite the density-profile disagreement; the magnetic
      field component By agrees well with the exact solution.
  - key: dumbser2024vrmhd
    params_used: { preset: "RP2 (Ryu-Jones seven-wave, modified right state)", domain: "[-0.5,0.5]", xd: -0.1, rho_L: 1.08, rho_R: 0.9891, p_L: 0.95, p_R: 0.97159, t_final: 0.2, CFL: 0.9 }
    method: "same as RP1 entry above"
    resolution: "1000 pressure control volumes on domain [-0.5,0.5]"
    amr: "none"
    findings: "Wave pattern composed of discontinuities in all seven MHD waves; agreement between the numerical and exact solution is \"very good\"."
  - key: dumbser2024vrmhd
    params_used: { preset: "RP3", domain: "[-0.5,0.5]", xd: -0.1, rho_L: 1.7, rho_R: 0.2, p_L: 1.7, p_R: 0.2, t_final: 0.15, CFL: 0.9 }
    method: "same as RP1 entry above"
    resolution: "1000 pressure control volumes on domain [-0.5,0.5]"
    amr: "none"
    findings: "Also contains seven waves, but compared to RP2 the two left waves are rarefactions rather than shocks; the scheme captures the wave pattern properly apart from the weak right-moving shock."
  - key: dumbser2024vrmhd
    params_used: { preset: "RP4", domain: "[-0.5,0.5]", xd: 0.0, rho_L: 1.0, rho_R: 0.4, p_L: 1.0, p_R: 0.4, t_final: 0.16, CFL: 0.9 }
    method: "same as RP1 entry above"
    resolution: "1000 pressure control volumes on domain [-0.5,0.5]"
    amr: "none"
    findings: "The scheme has some difficulty capturing the second wave from the left at the given grid resolution (1000 cells), behaviour the authors state is similar to that observed in two other published works; the By profile is well reproduced."
  - key: fambri2023
    params_used: { preset: "RP1 (Brio-Wu)", domain: "[-0.5,0.5]", xd: 0.0, rho_L: 1.0, rho_R: 0.125, p_L: 1.0, p_R: 0.1, t_final: 0.1, CFL: 0.9, theta_p: 1.0, theta_B: 0.55 }
    method: "structure-preserving semi-implicit finite volume method for viscous/resistive MHD; convective subsystem explicit (second-order MUSCL-type), pressure/magnetic subsystem implicit with stiffening parameters theta_p, theta_B; mesh resolution dx=1e-3; compared to an exact MHD Riemann solver (courtesy S.A.E.G. Falle)"
    resolution: "mesh resolution dx = 1e-3 on domain [-0.5,0.5] (~1000 cells)"
    amr: "none"
    findings: >
      Computed solution shown to be in good agreement with other published works. When a
      convective-and-Alfvenic Courant number dt=dt(lambda_vB) is used, results fit very well those
      of a compared reference; using a purely convective Courant number dt=dt(lambda_v) instead
      yields a gain of 2-5x in Courant number, at the cost of numerical diffusion from lower
      time-accuracy and slightly more oscillatory behaviour from unresolved time-scales.
  - key: fambri2023
    params_used: { preset: "RP2 (Ryu-Jones seven-wave, modified right state)", domain: "[-0.5,0.5]", xd: -0.1, rho_L: 1.08, rho_R: 0.9891, p_L: 0.95, p_R: 0.97159, t_final: 0.2, CFL: 0.9, theta_p: 1.0, theta_B: 0.55 }
    method: "same as RP1 entry above"
    resolution: "mesh resolution dx = 1e-3 on domain [-0.5,0.5] (~1000 cells)"
    amr: "none"
    findings: "Same Courant-number-choice trade-off reported jointly for RP1-RP4 (see RP1 entry above): 2-5x gain in Courant number at the cost of accuracy when using a purely convective time step."
  - key: fambri2023
    params_used: { preset: "RP3", domain: "[-0.5,0.5]", xd: -0.1, rho_L: 1.7, rho_R: 0.2, p_L: 1.7, p_R: 0.2, t_final: 0.15, CFL: 0.9, theta_p: 1.0, theta_B: 0.55 }
    method: "same as RP1 entry above"
    resolution: "mesh resolution dx = 1e-3 on domain [-0.5,0.5] (~1000 cells)"
    amr: "none"
    findings: "Same Courant-number-choice trade-off reported jointly for RP1-RP4 (see RP1 entry above): 2-5x gain in Courant number at the cost of accuracy when using a purely convective time step."
  - key: fambri2023
    params_used: { preset: "RP4", domain: "[-0.5,0.5]", xd: 0.0, rho_L: 1.0, rho_R: 0.4, p_L: 1.0, p_R: 0.4, t_final: 0.16, CFL: 0.9, theta_p: 1.0, theta_B: 0.65 }
    method: "same as RP1 entry above"
    resolution: "mesh resolution dx = 1e-3 on domain [-0.5,0.5] (~1000 cells)"
    amr: "none"
    findings: "Same Courant-number-choice trade-off reported jointly for RP1-RP4 (see RP1 entry above): 2-5x gain in Courant number at the cost of accuracy when using a purely convective time step. Stiffening parameter theta_B raised to 0.65 for this preset (vs. 0.55 for RP1-RP3)."
  - key: dematte2024
    params_used: { preset: "RP1 (Brio-Wu)", x0: 0.5, rho_L: 1.0, rho_R: 0.125, Bx: 0.75, By_L: 1.0, By_R: -1.0, p_L: 1.0, p_R: 0.1, t_final: 0.1, CFL: 0.8 }
    method: "proposed semi-implicit FVS scheme (Rusanov advective flux, nested-Picard implicit pressure sub-system); staggered CT for div-B; second-order-accurate MUSCL-Hancock-type TVD reconstruction for the advective sub-system"
    resolution: "1000 cells on [0,1]"
    amr: "none"
    findings: >
      "An artificial compound wave in the density profile" is present, "a common feature of standard
      finite volume schemes for ideal MHD"; results are "in line with others published in the
      literature" (citing Brio & Wu, Dumbser & Toro, Falle & Komissarov, Dumbser et al., and Fambri).
      Good agreement with a high-resolution reference solution (their own explicit density-based
      second-order MUSCL-type TVD scheme with an HLLC Riemann solver) is shown for both a purely
      advective time step and an Alfvenic time step.
  - key: dematte2024
    params_used: { preset: "RP2 (Ryu-Jones seven-wave)", x0: 0.5, rho_L: 1.08, rho_R: 0.9891, vx_L: 1.2, vx_R: -0.0131, vy_L: 0.01, vy_R: 0.0269, vz_L: 0.5, vz_R: 0.010037, Bx: 0.564190, By_L: 1.015541, By_R: 1.135262, Bz_L: 0.564190, Bz_R: 0.564923, p_L: 0.95, p_R: 0.97159, t_final: 0.2, CFL: 0.8 }
    method: "same as RP1 entry above"
    resolution: "1000 cells on [0,1]"
    amr: "none"
    findings: "Scheme reproduces the wave pattern properly; good agreement with the high-resolution reference solution described in the RP1 entry above."
  - key: dematte2024
    params_used: { preset: "RP3", x0: 0.5, rho_L: 1.7, rho_R: 0.2, vz_R: -1.496891, Bx: 1.1, By_L: 1.0, By_R: 0.785887, Bz_R: 0.618370, p_L: 1.7, p_R: 0.2, t_final: 0.15, CFL: 0.8 }
    method: "same as RP1 entry above"
    resolution: "1000 cells on [0,1]"
    amr: "none"
    findings: >
      Choice of a purely-advective dt-a produces less accurate results than the Alfvenic dt-alv, "due
      to the lower resolution in time which leads to unresolved time-scales of the flow." Re-run with
      a purely-advective dt-a at different CFL numbers (Fig. 3): "reducing the CFL number ... there is
      a slight increase in the accuracy of the numerical solution, attributed to the improved
      resolution of the flow's time-scales."
  - key: dematte2024
    params_used: { preset: "RP4", x0: 0.4, rho_L: 1.0, rho_R: 0.4, Bx: 1.3, By_L: 1.0, By_R: -1.0, p_L: 1.0, p_R: 0.4, t_final: 0.16, CFL: 0.8 }
    method: "same as RP1 entry above"
    resolution: "1000 cells on [0,1]"
    amr: "none"
    findings: "Same purely-advective-vs-Alfvenic dt accuracy trade-off as RP3 (see RP3 entry above); re-run at multiple CFL numbers (Fig. 3) with the same qualitative trend."
related_to: []
headline_score: 4
---

## Physical problem
A 1D ideal-MHD Riemann problem: two uniform constant states (density, velocity, magnetic field,
gas pressure) separated by a single discontinuity at x=x0 on the domain [0,1], evolved under the
ideal MHD equations with an ideal-gas EoS. The canonical numeric preset (RP1) is the classical
Brio-Wu shock tube; RP2-RP4 are alternate presets of the same structural problem.

## What this test actually tests
Shock-capturing and wave-pattern fidelity of a numerical MHD scheme across the seven ideal-MHD
wave families (fast/slow shocks, rotational discontinuities, contact, entropy wave), including
correct reproduction of the artificial compound wave known to appear in RP1's density profile.

## Qualitative behaviour
RP1 (Brio-Wu): fast rarefaction, compound wave, contact discontinuity, slow shock, fast
rarefaction (left to right); a numerically-generated compound wave is a known, expected feature
in the density profile of standard finite-volume MHD schemes. RP2-RP4: analogous multi-wave
structures at their respective states (see reference_results for each preset's findings).

## Validation notes
RH-jump conditions provide a resolution-independent, analytic check across all four presets.
`dematte2024`'s own comparison (Fig. 2/3, 1000 cells on [0,1]) is against a high-resolution
reference solution (their own explicit density-based 2nd-order MUSCL-type TVD/HLLC run), not an
exact solution — this caps the `profile-vs-high-res-reference` mode at score 3, while the
`rh-jump-shocks` mode (analytic conditions) reaches score 4.

RP1 (Brio-Wu) is originally due to `brio1988` (identifier verified; full text inaccessible, so no
`reference_result` is recorded for it — see Notes). `ryujones1995` originated RP2 as their "test 2a"
(seven-wave shock tube, 512 cells on [0,1], Courant constant 0.8): they report strong fast shocks
resolved within 2-4 cells, rotational discontinuities within 3-5 cells with steepening (6-8 cells
without), and the contact discontinuity spread over more cells than that. `dumbser2024vrmhd`
(1000 control volumes on [-0.5,0.5], CFL 0.9) and `fambri2023` (dx=1e-3 on [-0.5,0.5], CFL 0.9,
theta_B=0.55 for RP1-3 / 0.65 for RP4) both run all four RP1-4 presets with their own
semi-implicit schemes: for RP1 they report the same artificial compound wave as `dematte2024` and
attribute the correct (non-compound) solution only to Glimm's random choice method; for RP3
`dumbser2024vrmhd` reports the wave pattern is captured "properly apart from the weak
right-moving shock"; for RP4 they report difficulty "capturing the second wave from the left at
the given grid resolution"; `fambri2023` reports a purely-convective time step yields a 2-5x gain
in Courant number at the cost of numerical diffusion and mild time-scale-related oscillation,
mirroring `dematte2024`'s own purely-advective-vs-Alfvenic dt finding for RP3/RP4.

## Notes
domain_bc type (outflow) remains an inferred convention: it is not stated in `dematte2024` Sect.
4.1.1, and the retrievable primary source (`ryujones1995`, full text checked via its arXiv
preprint) states no boundary-condition convention anywhere for its 1D shock-tube tests either
(only "boundary" usage found concerns the internal Riemann discontinuity, not the domain edges).
`brio1988` could not be checked (its JCP 1988 paper is paywalled with no free copy locatable); see
`pending_extraction.md`, left open pending that check. Bx is uniform across the discontinuity in
every preset (required for div-B compatibility of a 1D normal field). Units are stored as
authored (bare, nondimensional numbers); b_field_convention (permeability-unity) IS stated in the
source (Sect. 2), so is not a needs-source item.

`brio1988` (DOI 10.1016/0021-9991(88)90120-9) is `verified` (identifier live-resolved via
verify_refs.py) but carries no `reference_result`: ScienceDirect returns HTTP 403 to automated
fetches and no free copy of the 1988 paper (pre-arXiv) could be located, so no findings/method/
resolution could be read from the primary source itself (SPEC 5.2 no-fabrication contract).

`dumbser2024vrmhd` and `fambri2023` are citekeys carried over unmodified from the offline-authored
`pending_verification.md`; their actual publication years are 2019 (Int. J. Numer. Methods Fluids
89, 16-42, doi:10.1002/fld.4681) and 2021 (Int. J. Numer. Methods Fluids 93(12), 3447-3489,
doi:10.1002/fld.5041) respectively, not 2024/2023 as the keys suggest. Both DOIs are correct and
match the titles given in `pending_verification.md`, but `doi.org` returns HTTP 403 to this
script's automated HEAD/GET in this environment (Wiley appears to block non-browser requests); the
arXiv preprint identifiers (1801.06592, 2012.11218) were used instead as the `verified` identifier
since they resolve live over HTTP 200. Both papers' RP1-RP4 initial states are expressed in
un-normalized Gaussian-type units (a factor of sqrt(4*pi) larger in B) and on domain [-0.5,0.5]
(vs. this entry's [0,1], permeability-unity convention) — same physical states, different
convention, consistent with the b_field_convention note above.
