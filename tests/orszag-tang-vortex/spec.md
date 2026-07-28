---
# Authored via /add-test (NORMAL path) from Dematté, Farmakalides, Millmore & Nikiforakis,
# "An all Mach number scheme for visco-resistive magnetically-dominated MHD flows", JCP 514
# (2024) 113229 (citekey: dematte2024), Sect. 4.1.5 "Ideal Orszag-Tang vortex". The test itself
# is attributed to Orszag & Tang [71] (test_origin below, status: pending -- unresolved by this
# pass, per /add-test contract; a later /add-refs pass resolves the originating reference).

slug: orszag-tang-vortex
name: "Ideal Orszag-Tang Vortex"
provenance: literature
one_liner: "Smooth, periodic 2D ideal-MHD vortex that rapidly develops multiple interacting shocks and transitions toward MHD turbulence -- a standard benchmark for shock formation and shock-shock interaction."

physics:
  materials:
    - name: plasma
      base: mhd
      terms: []
      eos:
        type: gamma-law
        params: { gamma: 1.6666666666666667 }   # gamma = 5/3, stated explicitly for this test (matches the global default)
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
  domain: { x: [0, 1], y: [0, 1] }
  regions:
    - id: whole
      shape: box
      params: { x: [0, 1], y: [0, 1] }

units:
  system: nondimensional       # bare numbers as authored, not named by the source
  b_field_convention: permeability-unity   # global (Sect. 2): "the units of B are chosen such that the vacuum magnetic permeability is unity"

initial_conditions:
  aux:
    - { name: g, expr: "1.6666666666666667" }   # gamma = 5/3
  equilibrium:
    - region: whole
      fields:
        rho: "g**2"
        vx: "-sin(2*pi*y)"
        vy: "sin(2*pi*x)"
        vz: "0.0"
        Bx: "-sin(2*pi*y)"
        By: "sin(4*pi*x)"
        Bz: "0.0"
        p: "g"
  perturbation:
    combine_rule: additive
    fields: []
  potentials: []

parameters:
  - { name: gamma, canonical: 1.6666666666666667, meaning: "ratio of specific heats (= 5/3), stated explicitly for this test" }

domain_bc:
  # NOT stated explicitly in Sect. 4.1.5 beyond "the computational domain is the square
  # [0,1]x[0,1]". Periodic BCs are the universal convention for this canonical benchmark (the
  # sinusoidal IC is doubly-periodic by construction), but that convention is NOT restated
  # verbatim in this source -- inferred and flagged needs-source in pending_extraction.md.
  x_lo: { type: periodic }
  x_hi: { type: periodic }
  y_lo: { type: periodic }
  y_hi: { type: periodic }

internal_boundaries: []

time:
  t_final: 0.7957747154594767      # 5/(2*pi), the latest of the four reported snapshot times (Fig. 9)
  snapshot_times: [0.07957747154594767, 0.3183098861837907, 0.4774648292756861, 0.7957747154594767]

validation_modes:
  - id: shock-pattern-comparison
    purpose: "Characterize the gas-pressure and magnetic-field-magnitude patterns at the four canonical evolution times (t=0.5/2pi, 2/2pi, 3/2pi, 5/2pi) as the smooth IC develops interacting shocks and transitions toward MHD turbulence, against the reference simulation and the wider Orszag-Tang literature."
    procedure: feature-location
    inputs:
      at_time: 0.7957747154594767
      variables: [p, Bmag]
      reference: { kind: reference-result, key: dematte2024 }
      tolerance: "qualitative visual match to the pressure/field-magnitude contour patterns reported at all four snapshot times (Fig. 9); no numeric feature-location values stated in source"
    has_exact_solution: false
    score: 2
    score_justification: "No automatable numeric check stated (only 'good agreement is observed with other results reported in the literature'), but the shock/turbulence-transition pattern is well-characterised by specific named snapshot times and this is a widely-reproduced canonical ideal-MHD benchmark -- rubric row 2."

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
  # dematte2024 attributes this to "the Orszag-Tang vortex test [71]" (Orszag & Tang) and
  # further points readers to Dahlburg & Picone [72,73] for the underlying physics. Neither the
  # originating Orszag & Tang [71] reference nor the Dahlburg/Picone refs are resolved to a
  # DOI/arXiv id in this pass -- left `pending` for a later /add-refs pass rather than guessed.
  status: pending
  authored_from: dematte2024
  attribution_claims:
    - stated_by: dematte2024
      quote: "the Orszag-Tang vortex test [71]"
reference_results:
  - key: dematte2024
    params_used: { domain: "[0,1]x[0,1] periodic", t_final: 0.7957747154594767 }
    method: "proposed semi-implicit scheme; unstaggered CT (Sect. 3.3.2); 2nd-order TVD MUSCL-Hancock-type reconstruction with Van Leer limiter for the advective sub-system; CFL=0.8; advective-eigenvalue timestep; GMRES tol 1e-15; Picard R=Q=S=2, sigma=1e-12 (globals not restated per-test except CT/reconstruction, which ARE stated per-test)"
    resolution: "1000x1000 uniform Cartesian cells"
    amr: "none"
    findings: >
      Fig. 9: gas-pressure and magnetic-field-magnitude fields at t=0.5/2pi, 2.0/2pi, 3/2pi, and
      5/2pi. "Good agreement is observed with other results reported in the literature, see e.g.
      Dumbser et al. [70,41], Fambri [42] and Balsara et al. [74]."
related_to: []
headline_score: 2
---

## Physical problem
A smooth, doubly-periodic 2D ideal-MHD initial condition (sinusoidal velocity and magnetic
field, uniform-times-gamma^2 density, uniform-times-gamma pressure) that is not itself an
equilibrium: it rapidly steepens into multiple interacting shock waves and shock-shock
collisions, and at later times transitions toward two-dimensional MHD turbulence.

## What this test actually tests
Whether the scheme correctly forms and propagates the multiple MHD shocks and shock-shock
interactions that develop from this smooth IC, and reproduces the qualitative pressure/
field-magnitude patterns reported in the literature at the four canonical snapshot times
(feature-location mode).

## Qualitative behaviour
Diagonal and off-diagonal shock fronts form from the smooth sinusoidal IC and collide, producing
the characteristic "cross"-like pressure/field-magnitude pattern reported at t=0.5/2pi through
2/2pi; by t=3/2pi-5/2pi the flow shows increasing small-scale structure consistent with a
transition toward MHD turbulence (Fig. 9). No exact solution exists; comparison is by qualitative
pattern match at the four canonical times.

## Validation notes
No numeric tolerance or feature-location values are stated in the source for this test -- the
paper's own validation is the qualitative statement "good agreement is observed with other
results reported in the literature" -- so the mode is capped at rubric row 2 rather than
inflated by the specificity of the four named snapshot times.

## Notes
Domain boundary conditions are not restated verbatim beyond the domain extent; `periodic` is
recorded as the (near-universal, IC-consistent) convention for this canonical benchmark and
flagged needs-source in `pending_extraction.md` pending confirmation against the source text.
