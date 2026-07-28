---
# Authored via /add-test (NORMAL path) from Dematté, Farmakalides, Millmore & Nikiforakis,
# "An all Mach number scheme for visco-resistive magnetically-dominated MHD flows", JCP 514
# (2024) 113229 (citekey: dematte2024), Sect. 4.1.6 "Ideal MHD blast wave problem". The test
# itself is stated to originate with Balsara & Spicer [47] (test_origin below, status: pending
# -- unresolved by this pass, per /add-test contract; a later /add-refs pass resolves the
# originating reference).

slug: ideal-mhd-blast-wave
name: "Ideal MHD Blast Wave Problem (Balsara & Spicer)"
provenance: literature
one_liner: "Over-pressurised circular region at the centre of a highly-magnetised, uniform-field domain, driving a strong MHD blast wave -- a stringent test of divergence-free preservation and shock robustness under a very strong background field."

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
  has_internal_boundaries: false   # the over-pressurised disk vs ambient split is a piecewise IC on ONE material
geometry_stress: none

geometry:
  coord_system: cartesian
  domain: { x: [-0.5, 0.5], y: [-0.5, 0.5] }
  regions:
    - id: whole
      shape: box
      params: { x: [-0.5, 0.5], y: [-0.5, 0.5] }

units:
  system: nondimensional       # bare numbers as authored, not named by the source
  b_field_convention: permeability-unity   # global (Sect. 2): "the units of B are chosen such that the vacuum magnetic permeability is unity"

initial_conditions:
  aux:
    - { name: r, expr: "sqrt(x**2 + y**2)" }
    - { name: H, expr: "step(r, 0.1, 0.1)" }   # Heaviside at r=0.1: 0 for r<=0.1 (over-pressurised disk), 1 for r>0.1 (ambient)
  equilibrium:
    - region: whole
      fields:
        rho: "1.0"
        vx: "0.0"
        vy: "0.0"
        vz: "0.0"
        Bx: "100.0/sqrt(4*pi)"
        By: "0.0"
        Bz: "0.0"
        p: "1000.0*(1-H) + 0.1*H"
  perturbation:
    combine_rule: additive
    fields: []
  potentials: []

parameters:
  - { name: gamma, canonical: 1.6666666666666667, meaning: "ratio of specific heats (= 5/3), global default" }
  - { name: blast_radius, canonical: 0.1, meaning: "radius R of the over-pressurised circular region" }
  - { name: B0x, canonical: 56.41895835477563, meaning: "uniform, very strong background Bx = 100/sqrt(4*pi)" }

domain_bc:
  # NOT stated explicitly in Sect. 4.1.6. Inferred as outflow/zero-gradient -- standard
  # practice for this benchmark (the blast is not run long enough for the shock to reach the
  # domain edge at t_final=0.01) -- and flagged needs-source in pending_extraction.md pending
  # confirmation against the retrievable Balsara & Spicer source.
  x_lo: { type: outflow }
  x_hi: { type: outflow }
  y_lo: { type: outflow }
  y_hi: { type: outflow }

internal_boundaries: []

time:
  t_final: 0.01
  snapshot_times: [0.01]

validation_modes:
  - id: density-velocity-pressure-contour-comparison
    purpose: "Characterize the density, velocity-magnitude, gas-pressure, and magnetic-pressure contour patterns at t=0.01 against the reference simulation and the wider blast-wave-benchmark literature, as no exact solution exists for this problem."
    procedure: feature-location
    inputs:
      at_time: 0.01
      variables: [rho, vmag, p, Bmag]
      reference: { kind: reference-result, key: dematte2024 }
      tolerance: "qualitative visual match to the contour patterns reported in Fig. 10; no numeric feature-location values stated in source"
    has_exact_solution: false
    score: 2
    score_justification: "No automatable numeric check stated (only 'good agreement is observed with results reported in the literature, for example Balsara and Spicer [47]'), but the solution is well-characterised by specific named fields (density, velocity magnitude, gas pressure, magnetic pressure) at the canonical evolution time, and this is a widely-reproduced, deliberately stringent canonical MHD benchmark -- rubric row 2."

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
references_unverified: []
test_origin:
  # dematte2024 states this test was "originally introduced by Balsara and Spicer [47]" -- the
  # originating reference is NOT itself in references[] above (no DOI/arXiv id was located for
  # it in this pass). Per the /add-test contract, original_intro resolution is left to a later
  # /add-refs pass; status stays `pending` rather than guessed.
  status: pending
  authored_from: dematte2024
  attribution_claims:
    - stated_by: dematte2024
      quote: "originally introduced by Balsara and Spicer [47]"
reference_results:
  - key: dematte2024
    params_used: { domain: "[-0.5,0.5]x[-0.5,0.5]", t_final: 0.01 }
    method: "proposed semi-implicit FVS scheme; staggered CT (global default, not restated per-test); 2nd-order TVD MUSCL-Hancock-type reconstruction for the explicit advective terms (stated per-test); CFL=0.8; advective-eigenvalue timestep; GMRES tol 1e-15; Picard R=Q=S=2, sigma=1e-12 (globals not restated per-test)"
    resolution: "1000x1000 uniform Cartesian cells"
    amr: "none"
    findings: >
      Fig. 10: contour lines of density, velocity magnitude, gas pressure, and magnetic pressure
      at t=0.01. "Good agreement is observed with results reported in the literature, for example
      Balsara and Spicer [47]."
related_to: []
headline_score: 2
---

## Physical problem
An over-pressurised circular region of radius R=0.1 at the centre of a square domain, embedded
in a uniform ambient fluid permeated by a very strong, uniform magnetic field aligned with the
x-axis. The large pressure jump (1000 vs 0.1) drives a strong outward-propagating MHD blast wave
that must propagate through a highly magnetised environment, straining both shock robustness and
divergence-free preservation.

## What this test actually tests
Whether the scheme produces physically admissible (non-negative density/pressure) solutions and
correctly captures the strong-shock structure of an MHD blast wave propagating through a very
strong, uniform background field, reproducing the qualitative density/velocity/pressure/
magnetic-pressure contour patterns reported in the literature at t=0.01 (feature-location mode).

## Qualitative behaviour
An outward-propagating, magnetically-shaped blast structure develops from the initially circular
over-pressurised region, elongating along the strong background field direction; the source
notes this test "can easily lead to unphysical densities or pressures if the divergence-free
condition is not adequately addressed" -- i.e. a scheme lacking robust div-B control or shock
dissipation is expected to fail outright rather than merely mismatch quantitatively. No exact
solution exists; comparison here is by qualitative pattern match against the literature.

## Validation notes
No numeric tolerance or feature-location values are stated in the source for this test -- the
paper's own validation is the qualitative statement "good agreement is observed with results
reported in the literature, for example Balsara and Spicer [47]" -- so the mode is capped at
rubric row 2. No entry-specific div-B numeric criterion (analogous to the rotor's Fig. 8) is
given for this test, so a div-b mode was NOT added here as a scored mode (it would be an
unscored provenance note only, per the universal-diagnostic rule, and is omitted rather than
padding the entry with an unscored mode).

## Notes
Domain boundary conditions are not stated explicitly for this test in Sect. 4.1.6; `outflow` is
recorded as an inferred convention and flagged needs-source in `pending_extraction.md`. The
piecewise IC (over-pressurised disk vs ambient) is encoded via a `step(r,0.1,0.1)` Heaviside
indicator rather than as separate `regions`, since it is a single-material piecewise field, not a
physical interface (`has_internal_boundaries: false`).
