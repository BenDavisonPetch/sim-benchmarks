---
# Authored via /add-test (NORMAL path, partly underspecified -> triage caution applied) from
# Toro, "Riemann Solvers and Numerical Methods for Fluid Dynamics", 3rd ed. (Springer 2009), Ch. 17
# "Multidimensional Test Problems", Sect. 17.2 "Shock Wave Reflection from a Wedge" (citekey: toro2009).
# Source class: category (D) test (Ch.17 intro: experimental results available). NOT stated in the
# source: gamma, output time, domain boundary conditions, domain origin, length/time units. These are
# taken from the user-supplied settings file cut-cell-MHD validated_settings/shock_wedge_reflection (which states "Wedge test taken
# from Toro's book" and points to gokhale2018 Sect. 6.2); each such value is commented "settings file".
# Wedge placement on the y=0 floor is read from the Fig. 17.8 sketch.
# DEDUP: INDEX.tsv has no wedge / shock-reflection entry. Closest structural neighbour is
# rotated-sod-embedded-rectangle (hydro/gamma-law + rigid-wall internal boundary, oblique-to-grid) but
# its measurand (exact 1D Riemann) and geometry are different -> NEW ENTRY, not a sibling.

slug: shock-reflection-wedge-single-mach
name: "Shock Wave Reflection from a Wedge (Ms=1.7, 25 deg, Single Mach Reflection)"
provenance: literature
one_liner: "A planar Mach-1.7 shock in ambient air strikes a 25-degree reflecting wedge, producing a single Mach reflection (triple point, reflected shock, Mach stem, slip surface); validated qualitatively against Takayama's experiment as presented by Toro."

physics:
  materials:
    - name: gas
      base: hydro                      # inviscid Euler (source: Euler/ideal-gas, "Euler equations replaced with Navier-Stokes" only discussed as a caveat for high Ms)
      terms: []
      eos:
        type: gamma-law
        params: { gamma: 1.4 }         # settings file (Air.gamma = 1.4); NOT stated in Toro Sect. 17.2
  coupling: none                       # single material; wedge is a rigid-wall internal_boundary

dimension:
  intrinsic: 2
  runnable_in: [2]

analysis_treatments: [oblique-to-grid] # wedge surface at phi=25 deg and the induced reflection pattern are oblique to the Cartesian axes

capability_flags:
  time_dependent_bc: false
  has_internal_boundaries: true        # rigid-wall wedge
geometry_stress: none                  # ordinary ramp, not an adversarial geometry

geometry:
  coord_system: cartesian
  domain: { x: [0, 25.0], y: [0, 16.5] }   # size from Toro ("25.0 x 16.5"); origin [0,0] and metres from settings file (geometry.prob_lo = 0 0, "Domain size should be 25 x 16.5")
  regions:
    - id: domain
      shape: box
      params: { x: [0, 25.0], y: [0, 16.5] }
    - id: wedge
      shape: polygon
      # Apex (4.69, 0) and angle 25 deg are source-stated; resting on the y=0 wall, with the ramp surface
      # rising at phi from the x-axis, is read from the Fig. 17.8 sketch (not stated in text). Third vertex
      # is DERIVED by clipping the ramp line at the domain edge x=25: y = (25-4.69)*tan(25 deg) = 9.4707.
      params: { vertices: [[4.69, 0], [25.0, 0], [25.0, 9.4707]] }

units:
  system: si                           # ambient state given in SI by Toro; lengths (m) and times (s) per settings file
  b_field_convention: null             # no magnetic field (not applicable)

initial_conditions:
  aux:
    - { name: c_a,       expr: "sqrt(gamma*p_a/rho_a)" }                                   # ambient sound speed (derived, m/s)
    - { name: rho_post,  expr: "rho_a*((gamma+1)*M_s**2)/((gamma-1)*M_s**2+2)" }           # Rankine-Hugoniot density behind shock (source: "obtained from the Rankine-Hugoniot conditions", Toro Sect. 3.1.3)
    - { name: p_post,    expr: "p_a*(1 + (2*gamma/(gamma+1))*(M_s**2 - 1))" }              # Rankine-Hugoniot pressure behind shock
    - { name: Us,        expr: "M_s*c_a" }                                                 # shock speed (ambient at rest)
    - { name: u_post,    expr: "Us*(1 - rho_a/rho_post)" }                                 # induced post-shock velocity in +x
  equilibrium:
    - region: domain                   # fluid fills the domain outside the wedge polygon (wedge interior is solid; see internal_boundaries)
      fields:
        rho: "rho_post + (rho_a - rho_post) * step(x, x_s, x_s)"   # x<x_s: post-shock; x>=x_s: ambient
        p:   "p_post + (p_a - p_post) * step(x, x_s, x_s)"
        vx:  "u_post * (1 - step(x, x_s, x_s))"
        vy:  "0"
  perturbation:
    combine_rule: additive
    fields: []
  potentials: []

parameters:
  - { name: M_s,      canonical: 1.7,      meaning: "incident shock Mach number (dimensionless)" }
  - { name: phi_deg,  canonical: 25,       meaning: "wedge angle to the shock propagation (x) direction, degrees" }
  - { name: x_s,      canonical: 4.0,      meaning: "initial planar shock position, m" }
  - { name: x_apex,   canonical: 4.69,     meaning: "x-position of the wedge apex, m" }
  - { name: rho_a,    canonical: 1.225,    meaning: "ambient density ahead of shock, kg/m^3" }
  - { name: p_a,      canonical: 101325,   meaning: "ambient pressure ahead of shock, Pa (source: 1.01325 x 10^5 Pa)" }
  - { name: gamma,    canonical: 1.4,      meaning: "ratio of specific heats", notes: "settings file (Air.gamma = 1.4); not stated in Toro Sect. 17.2" }
  - { name: t_output, canonical: 0.025,    meaning: "output time, s", notes: "settings file (stop_time = 0.025); Toro never states a value. After the shock passes the apex the reflection is self-similar, so the measured pattern is independent of t_output provided waves have not reached the domain boundary (shock at x ~ 18.5 m at t=0.025)" }

domain_bc:
  # Not stated in Toro Sect. 17.2; from settings file (Air.loBCs = transmissive reflective,
  # Air.hiBCs = transmissive transmissive).
  x_lo: { type: outflow }
  x_hi: { type: outflow }
  y_lo: { type: reflecting }           # floor ahead of the apex; wedge rests on it (Fig. 17.8 sketch)
  y_hi: { type: outflow }

internal_boundaries:
  - kind: rigid-wall
    geometry: { region: wedge, surface: boundary }   # reflecting wedge surface; no-penetration (inviscid)
    motion: none

time:
  t_final: 0.025                       # settings file stop_time; self-similar pattern, value is a convention (see t_output)
  snapshot_times: [0.025]

validation_modes:
  - id: single-mach-reflection-structure
    purpose: "Verify the computed density field reproduces the single-Mach-reflection pattern of the experiment: three shocks (incident, reflected, Mach stem) meeting at a triple point, with the Mach stem joining the triple point to the wedge surface, and a slip surface emerging from the triple point."
    procedure: feature-location
    inputs:
      at_time: t_final
      variables: [rho]
      cut_lines: ["visual comparison of density contours against the experimental interferogram/photograph (Fig. 17.9 top frame)"]
      features: ["triple point", "incident shock (part of)", "reflected shock", "Mach stem joining triple point to wedge surface", "slip surface from triple point meeting wedge at a sharp angle"]
      reference: { kind: reference-result, key: toro2009 }
      tolerance: "qualitative visual agreement only -- source states 'qualitative agreement ... is excellent' and gives no numeric position criterion"
    has_exact_solution: false
    score: 2
    score_justification: "Observation (experiment) comparison, qualitative only, no automatable check and no exact solution (tops at 3). The pattern is specific and named (five identified features, standard single-Mach-reflection structure) and reproduced by two independent computations in the source, so row 2, not 1. Not row 3: no quantitative position/angle data are stated."

  - id: slip-surface-resolution
    purpose: "Verify the slip surface (density and tangential-velocity discontinuity) from the triple point is represented as a sharp feature and not smeared, the delicate feature the source identifies as solver-sensitive."
    procedure: feature-location
    inputs:
      at_time: t_final
      variables: [rho]
      cut_lines: ["visual inspection of the slip surface in the density contours (Fig. 17.9 bottom, Fig. 17.10 bottom)"]
      features: ["slip surface from triple point to wedge surface"]
      reference: { kind: reference-result, key: toro2009 }
      tolerance: "qualitative only: slip surface not smeared 'to unacceptable levels'; no numeric width criterion stated"
    has_exact_solution: false
    score: 1
    score_justification: "Single qualitative feature, no stated checkable width/position, no exact solution -- row 1."

references:
  - key: toro2009
    original_intro: false
    verification:
      status: verified
      identifier: { doi: "10.1007/b79761" }
      source: "crossref: 10.1007/b79761 -> 200"
      checked: "2026-11-06"
      meta:
        year: 2009
        first_author: Toro
        container: Springer Berlin Heidelberg
        title: "Riemann Solvers and Numerical Methods for Fluid Dynamics"
  - key: glaz1985
    verification:
      status: verified
      identifier: { doi: "10.1098/rspa.1985.0028" }
      source: "crossref: 10.1098/rspa.1985.0028 -> 200"
      checked: "2026-11-06"
      meta:
        container: Proceedings of the Royal Society of London. A. Mathematical and Physical Sciences
        first_author: Glaz
        title: A numerical study of oblique shock-wave reflections with experimental comparisons
        year: 1985
  - key: gokhale2018
    original_intro: false
    verification:
      status: verified
      identifier: { doi: "10.1016/j.jcp.2018.03.005" }
      source: "crossref: 10.1016/j.jcp.2018.03.005 -> 200"
      checked: "2026-11-06"
      meta:
        container: Journal of Computational Physics
        first_author: Gokhale
        title: "A dimensionally split Cartesian cut cell method for hyperbolic conservation laws"
        year: 2018
references_unverified:
  - key: glaz1985report
    verification:
      status: unverified
      note: "Toro ref [210]: H. M. Glaz, P. Colella, I. I. Glass, and R. L. Deschambault. A Detailed Numerical, Graphical and Experimental Study of Oblique Shock Wave Reflections. Technical Report 285, Institute for Aerospace Science, University of Toronto (UTIAS), 1985. (Text from Toro bibliography, inputs/toro_references.pdf.) Candidate DOI 10.2172/889235 resolves (crossref 200) to an OSTI/LBNL report with the same title, authors and year, but it is not confirmed to be the UTIAS 285 edition Toro cites. See pending_verification.md."
  - key: takayama-experiment
    verification:
      status: unverified
      note: "Experimental result 'Courtesy of Professor K. Takayama, Shock Wave Research Center, Sendai, Japan' (Fig. 17.9 top). A private-communication image, not a bibliographic entry. Toro's Takayama refs [477] (Optical Flow Visualization of Shock Wave Phenomena, Shock Waves @ Marseille Vol. 4, 1995) and [478] (Shock Waves, Proc. 18th Int. Symp. on Shock Waves, Sendai 1991, Springer 1992) are generic shock-wave literature, not asserted as this image's source. Needs source."
test_origin:
  status: pending
  authored_from: toro2009
  attribution_claims:
    - stated_by: toro2009
      quote: "Two very useful reference are the UTIAS report by Glaz, Colella, Glass and Deschambault [210] and the paper by the same authors [211]. Many experimental and numerical results for this type of problems are presented and discussed in these works."
    - stated_by: toro2009
      quote: "The top frame shows the experimental result (Courtesy of Professor K. Takayama, Shock Wave Research Center, Sendai, Japan) and the bottom frame shows the computed result for density."
reference_results:
  - key: toro2009
    params_used: { M_s: 1.7, phi_deg: 25, x_s: 4.0, x_apex: 4.69, domain: "25.0 x 16.5", rho_a: 1.225, p_a: 101325, u_a: 0, v_a: 0, t_output: "not stated" }
    method: "Run 1 (Fig. 17.9 bottom): WAF with dimensional splitting (Toro Sects. 16.2-16.3), HLLC Riemann solver (Sect. 10.4), vanleer limiter (Sects. 13.7-13.8), CFL 0.9, max wave speed per Sect. 16.3.2. Start-up reset: the 2D code first propagates the shock through 90% of the distance between its initial position and the wedge apex, then the state behind the shock is reset so the initial states are connected through the numerical shock rather than the Rankine-Hugoniot jump (practice of Glaz et al. 1985, Proc. R. Soc. Lond. A 398:117-140 [Toro ref 211], and Hillier 1995, 'Numerical Modelling of Shock Wave Diffraction', Shock Waves @ Marseille IV, pp. 17-26, doi:10.1007/978-3-642-79532-9_3 [Toro ref 250]). Run 2 (Fig. 17.10): WAF + HLLC with a combined CHIMERA + Adaptive Mesh Refinement + Cartesian-mesh scheme (Boden 1997, PhD thesis, Cranfield University [Toro ref 66]; Boden and Toro 1997, 'A Combined Chimera-AMR Technique for Hyperbolic PDEs', Proc. Fifth Annual Conf. CFD Society of Canada, pp. 5.13-5.18 [Toro ref 67])."
    resolution: "Run 1: regular curvilinear mesh 800 x 528. Run 2: base grid 50 x 33 with two further refinement levels, each with refinement factor 4"
    amr: "Run 1: none. Run 2: CHIMERA-AMR-Cartesian, 2 levels x4"
    findings: >
      Wave pattern corresponds to single Mach reflection: three shocks meet at the triple point (part of the
      incident shock, the reflected shock, the Mach stem, which joins the triple point with the wedge surface);
      a slip surface emerges from the triple point and joins the wedge surface at a sharp angle. "The
      qualitative agreement between the experimental result and the computations is excellent." Both the
      800 x 528 WAF-HLLC solution and the AMR-CHIMERA solution are compared against Takayama's experiment
      (Fig. 17.9/17.10); no numeric quantities (angles, positions) are reported. Source also warns that for high
      shock Mach numbers (real-gas and dissipative effects) agreement deteriorates unless Navier-Stokes plus a
      real-gas EoS is used.
  - key: gokhale2018
    params_used: { M_s: 1.7, gamma: 1.4, rho_a: 1.225, p_a: 101325, x_s: 3.0, wedge_vertices: "(2,-1), (27,-1+25*sin(30 deg)), (27,-1)", domain: "26 x 16.8", t_output: 0.025 }
    method: "From cut-cell-MHD validated_settings/shock_wedge_reflection (settings file says 'Described in Gokhale and Nikiforakis ... Section 6.2'; the paper itself has NOT been read). Cut-cell method LPFS, Strang splitting, MUSCL-Hancock with exact Riemann solver, van-Leer limiter, CFL 0.9 (0.18 for first 5 steps), area-weighted shock initialisation (5 divisions)."
    resolution: "520 x 336 base (domain rounded up from 25 x 16.5 / 500 x 330 for blocking_factor 8)"
    amr: "max_level 2, density-gradient tagging threshold 0.1"
    findings: "Not yet extracted; run /add-refs on gokhale2018 Sect. 6.2. NOTE: settings-file wedge differs from Toro: ramp slope 12.5/25 => 26.57 deg (not 25), ramp meets y=0 at x=4.0 (Toro 4.69), shock at x=3.0 (Toro 4.0)."
related_to: [rotated-sod-embedded-rectangle]
headline_score: 2
---

## Physical problem
A planar shock of shock Mach number M_s = 1.7, initially perpendicular to the x-direction at x = 4.0,
travels in +x through quiescent ambient gas (rho_a = 1.225 kg/m^3, p_a = 1.01325e5 Pa, u = v = 0). The
state behind the shock follows from the Rankine-Hugoniot conditions given the ambient state and M_s. The
shock meets a rigid reflecting wedge of half-angle phi = 25 degrees to the propagation direction, with
apex at x = 4.69, in a rectangular domain of size 25.0 x 16.5. Inviscid ideal-gas dynamics (Euler).

## What this test actually tests
Whether a multidimensional Euler scheme with a solid oblique wall reproduces the experimentally observed
single Mach reflection topology (single-mach-reflection-structure) and keeps the slip surface sharp
(slip-surface-resolution), the latter being solver-sensitive (HLL smears it; complete Riemann solvers do not).

## Qualitative behaviour
Single Mach reflection (one of four regimes: regular, single Mach, complex Mach, double Mach, selected by M_s
and phi): three shocks meet at the triple point, namely part of the incident shock, the reflected shock and
the Mach stem, which joins the triple point with the wedge surface. A slip surface emerges from the triple point
and joins the wedge surface at a sharp angle; across it density and velocity are discontinuous.

## Validation notes
Qualitative only: no numeric position, angle or error measure is given in the source. Reference comparison is
Toro's Fig. 17.9 (experiment, Takayama, top; WAF-HLLC density contours on 800 x 528, bottom) and Fig. 17.10
(CHIMERA-AMR). Source: "qualitative agreement ... is excellent". Score capped by observation comparison (<=3)
and further limited to 2/1 by absence of any stated quantitative criterion. The experimental image is
unverified/needs-source (see references_unverified). Class (D) per Toro Ch. 17 intro: "Care is required in
class (D) when experimental results are used."

## Notes
Toro Sect. 17.2 does not state gamma, the output time, domain BCs, domain origin or length/time units. These
come from the settings file cut-cell-MHD validated_settings/shock_wedge_reflection: gamma = 1.4; t_final = 0.025 s; x_lo/x_hi/y_hi
transmissive (outflow), y_lo reflective; origin [0,0]; lengths in m. The reflection is self-similar once the
shock has passed the apex, so t_final only needs to keep waves inside the domain. Wedge placement on the y=0
floor is read from the Fig. 17.8 sketch; third polygon vertex derived as (25-4.69)*tan(25 deg) = 9.4707. The
settings-file wedge geometry differs from Toro (26.57 deg ramp, foot at x=4.0, shock at x=3.0); the canonical
problem here keeps Toro's values. The "reset through the numerical shock at 90% of the distance
to the apex" start-up practice is classed as METHOD (reference_results): it mitigates start-up error of the
numerical scheme and does not change the physical problem, which is the ideal Rankine-Hugoniot step.
