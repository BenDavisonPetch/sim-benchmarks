---
# Authored via /add-test (NORMAL path) from Dematté, Farmakalides, Millmore & Nikiforakis,
# "An all Mach number scheme for visco-resistive magnetically-dominated MHD flows", JCP 514
# (2024) 113229 (citekey: dematte2024). Sections 4.1.2 "Convergence study for a smooth MHD
# vortex" and 4.1.3 "Long-time simulation of a smooth stationary MHD vortex".
#
# INTRA-PAPER DEDUP (orchestrator, SPEC 9.1 step 2d): the source states, verbatim, "Here we
# repeat the smooth stationary isodensity vortex studied above in Section 4.1.2, but we now
# present results for long simulation times" — an explicit same-entry statement. Both
# sections use the identical exact-solution vortex form (same expression structure, same
# eps/mu_tilde), differing only in domain size/center (a coordinate translation: [0,10]^2
# centred at (5,5) vs [-10,10]^2 centred at (0,0) — the same vortex, translated) and in run
# duration (t=1.0 for the convergence study vs t=500/1000 for the long-time run). Folded
# into ONE canonical entry with two validation_modes.

slug: smooth-mhd-vortex
name: "Smooth Stationary Ideal MHD Vortex"
provenance: literature
one_liner: "Smooth, exact-solution-at-all-times isodensity MHD vortex on a periodic square domain; used for both a spatial-convergence study (t=1) and a long-time stationarity-preservation check (t up to 1000)."

physics:
  materials:
    - name: plasma
      base: mhd
      terms: []
      eos:
        type: gamma-law
        params: { gamma: 1.6666666666666667 }   # gamma = 5/3, global default ("unless otherwise stated"); not restated for this test
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
  domain: { x: [0, 10], y: [0, 10] }   # canonical (4.1.2, convergence study); 4.1.3's long-time run used the
                                        # translated domain [-10,10]x[-10,10] (vortex centred at origin instead
                                        # of (5,5)) — same vortex, coordinate-shifted; see reference_results.
  regions:
    - id: whole
      shape: box
      params: { x: [0, 10], y: [0, 10] }

units:
  system: nondimensional      # not named by the source; bare numbers (standard convention for this benchmark)
  b_field_convention: permeability-unity   # stated-here, global (Sect. 2): "the units of B are chosen such that the vacuum magnetic permeability is unity"

initial_conditions:
  aux:
    - { name: eps, expr: "1.0" }
    - { name: mu_tilde, expr: "sqrt(4*pi)" }
    - { name: r2, expr: "(x-5)**2 + (y-5)**2" }
  equilibrium:
    - region: whole
      fields:
        rho: "1.0"
        vx: "-(eps/(2*pi)) * exp(0.5*(1-r2)) * (y-5)"
        vy: "(eps/(2*pi)) * exp(0.5*(1-r2)) * (x-5)"
        vz: "0.0"
        Bx: "-(1/(2*pi)) * exp(0.5*(1-r2)) * (y-5)"
        By: "(1/(2*pi)) * exp(0.5*(1-r2)) * (x-5)"
        Bz: "0.0"
        p: "1 + (1/(8*pi)) * (mu_tilde/(2*pi))**2 * (1-r2) * exp(1-r2) - 0.5*(eps/(2*pi))**2 * exp(1-r2)"
  perturbation:
    combine_rule: additive
    fields: []
  potentials: []

parameters:
  - { name: gamma, canonical: 1.6666666666666667, meaning: "ratio of specific heats (= 5/3), global default" }
  - { name: eps, canonical: 1.0, meaning: "vortex velocity/field strength parameter" }
  - { name: mu_tilde, canonical: 3.5449077018110318, meaning: "vortex pressure-perturbation strength parameter (= sqrt(4*pi))" }

domain_bc:
  x_lo: { type: periodic }
  x_hi: { type: periodic }
  y_lo: { type: periodic }
  y_hi: { type: periodic }

internal_boundaries: []

time:
  t_final: 1000     # covers both modes: convergence check at t=1.0, long-time stationarity at t=500/1000
  snapshot_times: [1.0, 500, 1000]

validation_modes:
  - id: exact-solution-l2-convergence
    purpose: "Verify second-order spatial L2 convergence against the exact stationary-vortex solution for density, x-velocity, Bx, and total energy at t=1."
    procedure: convergence-order
    inputs:
      at_time: 1.0
      variables: [rho, vx, Bx, E]
      resolution_sequence: [16, 32, 64, 128, 256, 512]
      r: 2
      expected_order: 2
      reference: { kind: reference-result, key: dematte2024 }
      tolerance: "measured order within ~0.1-0.2 of the theoretical 2nd order at the finer grid levels"
    has_exact_solution: true
    score: 5
    score_justification: "Exact analytic solution at all times (the IC is the exact solution) combined with a demonstrated ~2nd-order L2 convergence (Table 2: rho, vx, Bx, E) at t=1 — rubric row 5."

  - id: long-time-stationarity-preservation
    purpose: "Verify the scheme preserves the exact stationary equilibrium (normalised ||b|| profile) over a long integration time (t up to 1000), for both the staggered and unstaggered CT adaptations."
    procedure: well-balancing
    inputs:
      at_time: 1000
      variables: [B]
      reference: { kind: reference-result, key: dematte2024 }
      tolerance: "qualitative preservation of the normalised ||b|| profile vs the initial (exact) solution, per Figs. 4-5; no numeric tolerance stated in source"
    has_exact_solution: true
    score: 3
    score_justification: "The equilibrium is exactly known at all times (well-balancing is in principle automatable), but the paper's own reported check (Figs. 4-5) is a qualitative visual overlay with no stated numeric deviation tolerance — rubric row 3 (quantitative-capable reference, partial/qualitative reporting as given)."

references: []
references_unverified:
  - key: dematte2024
    verification: { status: unverified, identifier: { doi: "10.1016/j.jcp.2024.113229" }, source: "", checked: null }
  - key: dumbser2024vrmhd
    verification: { status: unverified, identifier: { arxiv: "1801.06592" }, source: "", checked: null }
  - key: fambri2023
    verification: { status: unverified, identifier: { arxiv: "2012.11218" }, source: "", checked: null }
reference_results:
  - key: dematte2024
    params_used: { mode: "convergence study (4.1.2)", domain: "[0,10]x[0,10] periodic, centred at (5,5)", t_final: 1.0 }
    method: "proposed semi-implicit FVS scheme; fixed dt=0.01; 2nd-order MUSCL-Hancock reconstruction WITHOUT limiter (unlimited, to isolate spatial order)"
    resolution: "Nx=Ny in {16,32,64,128,256,512}"
    amr: "none"
    findings: >
      Table 2: L2(rho,1)=2.436E-02 (Nx=16) down to 3.647E-05 (Nx=512), with observed order
      converging to ~2.0 for rho, vx, Bx, and E as resolution increases (e.g. at Nx=512: order(rho)
      =1.998, order(vx)=2.001, order(Bx)=1.987, order(E)=2.000).
  - key: dematte2024
    params_used: { mode: "long-time run (4.1.3)", domain: "[-10,10]x[-10,10] periodic, centred at (0,0)", t_final: 1000, CFL: 0.45 }
    method: "proposed semi-implicit scheme; both staggered (Sect 3.3.1) and unstaggered (Sect 3.3.2) CT adaptations compared; CFL-type step based on fluid velocity only"
    resolution: "200x200 cells"
    amr: "none"
    findings: >
      Normalised ||b|| = B/max||B0|| at t=500 and t=1000 (Fig. 4) and a 1D line-out along the
      x-axis at t=1000 (Fig. 5) show the vortex stationarity is satisfactorily preserved by both
      CT adaptations, in good qualitative agreement with Fambri (2023).
related_to: []
headline_score: 5
---

## Physical problem
A smooth, doubly-periodic 2D ideal-MHD vortex whose initial condition is, by construction, the
exact solution of the ideal MHD equations at all later times (a stationary/self-similar
structure): constant density, a swirling velocity and magnetic field pair sharing the same
Gaussian-like radial profile, and a pressure profile chosen to balance the magnetic and kinetic
contributions exactly.

## What this test actually tests
(1) Spatial order of accuracy of the scheme against a known exact solution (convergence-order
mode). (2) Long-time preservation of an exact stationary MHD equilibrium under both the
staggered and unstaggered constrained-transport adaptations (well-balancing mode) — i.e. whether
the scheme's divergence-cleaning choice introduces spurious drift away from the exact state.

## Qualitative behaviour
The vortex remains visually stationary (isodensity, exact self-similar profile) through t=1000
in both CT adaptations; no significant diffusion or asymmetry is reported at either t=500 or
t=1000 (Fig. 4/5).

## Validation notes
Table 2's empirical order climbs from ~1.57-1.85 at the coarsest grids (Nx=16-64) to ~1.95-2.01
by Nx=256-512, consistent with the theoretical 2nd order of the MUSCL-Hancock (unlimited)
advective reconstruction combined with the implicit pressure sub-system. The long-time mode has
no stated numeric tolerance in the source — recorded as qualitative (score 3) rather than
inflating to 4/5 on reproduction breadth alone (rubric: "do not let prose richness inflate a
score").

## Notes
The two runs use different domain extents/centres (a coordinate translation of the same vortex);
the canonical `geometry.domain` above is the convergence-study version (4.1.2); the long-time
run's alternate domain is recorded in its own `reference_results` row rather than forking the
entry, per the dedup fold noted above. `runnable_in` is kept at `[2]` only — the paper's methods
section states 3D is a straightforward generalisation of the algorithm, but this specific vortex
test was not run in 3D.
