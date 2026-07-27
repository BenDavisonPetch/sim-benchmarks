---
# Authored via /add-test (NORMAL path) from Jones, McNally & Reynolds 2026, "A constrained-transport
# embedded boundary method for compressible resistive magnetohydrodynamics", J. Comput. Phys. 550
# (2026) 114641 (citekey: jones2026), Section 7.12 "Hydrodynamic shock compression of a parallel
# pinch with material interface". Field form re-uses Section 7.3's parallel-pinch construction (eqs.
# 68-69, citekey freidberg2014 for the underlying profile form), rescaled to a=r2.
#
# DEDUP: shares the parallel-pinch field construction with parallel-pinch-compression-embedded-
# boundary / standing-magnetosonic-wave-parallel-pinch-cylinder (related_to), and the two-material
# ghost-fluid MHD coupling with resistive-field-soak-material-slab-interface, but no existing entry
# matches this physics_signature (mhd(resistivity)/gamma-law x2 @material-contact) +
# analysis_treatments + capability_flags combination -- NEW ENTRY.

slug: converging-shock-parallel-pinch-material-interface
name: "Converging Shock Compressing a Parallel Pinch with Material Interface"
provenance: literature
one_liner: "A hydrodynamically-driven converging shock compresses a density-perturbed inner cylinder threaded by a parallel-pinch magnetic field, across a two-material (ghost-fluid) resistive interface; validated qualitatively by comparing Richtmyer-Meshkov instability growth with vs without the magnetic field (config_delta differential mode)."

physics:
  materials:
    - name: outer_gas
      base: mhd
      terms: [resistivity]
      eos:
        type: gamma-law
        params: { gamma: 1.6666666666666667 }
      material_fields:
        - { name: eta, region: exterior, expr: "1", units: "cm^2/s" }
    - name: inner_gas
      base: mhd
      terms: [resistivity]
      eos:
        type: gamma-law
        params: { gamma: 4 }
      material_fields:
        - { name: eta, region: interior, expr: "0.1", units: "cm^2/s" }
  coupling: material-contact

dimension:
  intrinsic: 2
  runnable_in: [2]

analysis_treatments: [multi-material-interface]

capability_flags:
  time_dependent_bc: false
  has_internal_boundaries: true
geometry_stress: none

geometry:
  coord_system: cartesian
  domain: { x: [-0.5, 0.5], y: [-0.5, 0.5] }   # "domain is 1 cm x 1 cm square" (Fig. 13 caption); centering at origin inferred by symmetry (not explicitly restated), as in the parallel-pinch-compression sibling
  regions:
    - id: interior
      shape: cylinder
      params: { center: [0, 0], r: 0.3 }
    # exterior = domain minus interior

units:
  system: cgs-gaussian
  b_field_convention: sqrt-4pi

initial_conditions:
  aux:
    - { name: a,               expr: "0.3" }                       # = r2, pinch/interface radius, cm
    - { name: rho1,            expr: "1.4" }
    - { name: rho2_base,       expr: "0.5" }
    - { name: P_eq,            expr: "1" }
    - { name: P_driver,        expr: "50" }
    - { name: r_driver,        expr: "0.45" }
    - { name: Bphi_a,          expr: "5 * sqrt(pi) / a" }           # source-stated Bphi(a), G
    - { name: Bz_a,            expr: "0.1 * sqrt(4*pi)" }           # source-stated Bz(a), G
    - { name: alpha,           expr: "Bphi_a / Bz_a" }
  equilibrium:
    - region: interior
      fields:
        rho: "rho2_base + 0.1*sin(6*phi + 3*pi/2)*(1 - cos(pi*r/a))"   # source-stated density perturbation
        p: "P_eq"
        vx: "0"
        vy: "0"
        vz: "0"
        # Bx,By from A_z(r) (source eq. 68, as in standing-magnetosonic-wave-parallel-pinch-cylinder)
        Bx: "-(Bphi_a / (2*a)) * y"
        By: "(Bphi_a / (2*a)) * x"
        Bz: "(Bz_a/alpha) * sqrt(1 + (2*alpha**2/3)*(1-(r/a)**2)**2*(5-2*(r/a)**2))"   # source eq. 69
    - region: exterior
      fields:
        rho: "rho1"
        p: "P_eq + (P_driver - P_eq) * step(r, r_driver, r_driver)"   # equilibrium P_gas=1 at the interface, driven region r>0.45 at P=50 (Heaviside at r_driver)
        vx: "0"
        vy: "0"
        vz: "0"
        # No exterior magnetic field is stated in the source for this test (unlike the vacuum-field
        # extension explicitly described for resistive-field-soak-cylindrical-material-interface);
        # taken here as B=0 outside the pinch radius a, an INFERRED simplification -- see Notes.
        Bx: "0"
        By: "0"
        Bz: "0"
  perturbation:
    combine_rule: additive
    fields: {}
  potentials:
    - name: A_z
      expr: "Bphi_a * (a/4) * (2 - (r/a)**2)"
      derives: "Bx = dA_z/dy, By = -dA_z/dx (B = curl(A_z*z_hat)), interior region only"

parameters:
  - { name: a,          canonical: 0.3,   meaning: "inner cylinder / material-interface radius (=r2), cm" }
  - { name: rho1,       canonical: 1.4,   meaning: "outer material initial density, g/cm^3" }
  - { name: gamma1,     canonical: 1.6666666666666667, meaning: "outer material ratio of specific heats (=5/3), global default" }
  - { name: rho2_base,  canonical: 0.5,   meaning: "inner material base density (before perturbation), g/cm^3" }
  - { name: gamma2,     canonical: 4,     meaning: "inner material ratio of specific heats" }
  - { name: P_eq,       canonical: 1,     meaning: "mechanical-equilibrium gas pressure at the material interface, Ba" }
  - { name: P_driver,   canonical: 50,    meaning: "driver-region gas pressure (r>0.45 cm) initiating the converging shock, Ba" }
  - { name: r_driver,   canonical: 0.45,  meaning: "radius beyond which the driver pressure is set, cm" }
  - { name: eta1,       canonical: 1,     meaning: "outer material magnetic diffusivity, cm^2/s (magnetized/resistive canonical case)" }
  - { name: eta2,       canonical: 0.1,   meaning: "inner material magnetic diffusivity, cm^2/s (magnetized/resistive canonical case)" }
  - { name: Bphi_a,     canonical: 15.336006479985266, meaning: "azimuthal field at r=a, G (= 5*sqrt(pi)/a, a=0.3)" }
  - { name: Bz_a,       canonical: 0.35449077018110318, meaning: "axial field at r=a, G (= 0.1*sqrt(4*pi))" }

domain_bc:
  x_lo: { type: neumann }
  x_hi: { type: neumann }
  y_lo: { type: neumann }
  y_hi: { type: neumann }

internal_boundaries: []   # material interface is physics.coupling (material-contact); no separate rigid/embedded boundary

time:
  t_final: 0.1   # source (Fig. 13 panel labels): snapshots at t=0, 5e-2, 1e-1 s
  snapshot_times: [0, 0.05, 0.1]

validation_modes:
  - id: rm-instability-suppression-with-vs-without-field
    purpose: "Verify that a converging hydrodynamic shock compressing a density-perturbed material interface grows a Richtmyer-Meshkov instability from the seeded density perturbation in the absence of a magnetic field, and that the instability is qualitatively suppressed when the parallel-pinch magnetic field and resistive coupling are present -- a controlled A/B comparison, not either run in isolation."
    procedure: feature-location
    inputs:
      at_time: [0, 0.05, 0.1]
      variables: [rho]
      cut_lines: ["visual inspection of the material-interface contour, per Fig. 13"]
      features: ["density-perturbation-seeded interface instability growth (unmagnetized)", "reverse shock striking the interface a second time (both cases)", "interface instability suppression (magnetized+resistive)"]
      reference: { kind: reference-result, key: jones2026 }
      tolerance: "qualitative visual match only -- no numeric growth-rate or amplitude criterion is stated for this test (no analytic solution)"
    has_exact_solution: false
    score: 2
    score_justification: "No automatable check and no exact solution, but the measurand is a specific, named, checkable qualitative difference (instability growth vs suppression) between two controlled configurations, not a vague single-run impression -- rubric row 2 (a differential A/B comparison would ordinarily allow up to row 3, but no quantitative amplitude/growth-rate metric is reported for this test, so it is scored conservatively at row 2, not inflated to 3)."
    baseline:
      description: "unmagnetized variant: no magnetic field, no resistive term (Bphi_a=Bz_a=0, eta1=eta2=0)"
      config_delta: { "physics.materials[0].terms": "[]", "physics.materials[1].terms": "[]", "initial_conditions.aux.Bphi_a": "0", "initial_conditions.aux.Bz_a": "0" }
    measured: "difference in interface/instability morphology at t=0, 0.05, 0.1 s between the magnetized+resistive canonical run and the unmagnetized baseline (source: 'In the case without magnetic fields, the instability grows from the density perturbation seeds. In the case with magnetic fields, the instability is suppressed.')"

references:
  - key: jones2026
    original_intro: false
    verification:
      status: verified
      identifier: { doi: "10.1016/j.jcp.2025.114641" }
      source: "crossref: 10.1016/j.jcp.2025.114641 -> 200"
      checked: "2026-07-27"
      meta:
        year: 2026
        first_author: Jones
        container: Journal of Computational Physics
        title: "A constrained-transport embedded boundary method for compressible resistive magnetohydrodynamics"
  - key: freidberg2014
    verification:
      status: verified
      identifier: { doi: "10.1017/CBO9780511795046" }
      source: "crossref: 10.1017/CBO9780511795046 -> 200"
      checked: "2026-07-27"
      meta:
        year: 2014
        first_author: Freidberg
        container: Cambridge University Press
        title: "Ideal MHD"
references_unverified: []
test_origin:
  status: pending
  authored_from: jones2026
  attribution_claims: []
reference_results:
  - key: jones2026
    params_used: { a: 0.3, rho1: 1.4, rho2_base: 0.5, gamma1: 1.6666666666666667, gamma2: 4, P_eq: 1, P_driver: 50, r_driver: 0.45, eta1: 1, eta2: 0.1, Bphi_a: 15.336006479985266, Bz_a: 0.35449077018110318, t_final: 0.1 }
    method: "resistive MHD; two-material ghost-fluid coupling (Sect. 3.2/4.2) with per-material edge-fraction-weighted electric field; level-set-tracked material interface; HLLD Riemann solver; two runs (unmagnetized hydro-only, and magnetized+resistive)"
    resolution: "not restated for this test beyond the two-run comparison"
    amr: "none"
    findings: "Both cases show the converging shock compressing the inner material with a reverse shock striking the interface a second time; the unmagnetized case grows a Richtmyer-Meshkov-type instability from the seeded density perturbation, while the magnetized+resistive case suppresses it (Fig. 13, t=0, 5e-2, 1e-1 s)."
related_to: [parallel-pinch-compression-embedded-boundary, standing-magnetosonic-wave-parallel-pinch-cylinder, resistive-field-soak-material-slab-interface]
headline_score: 2
---

## Physical problem
An infinite outer cylinder of material 1 (gamma1=5/3, rho1=1.4 g/cm^3) surrounds an inner cylinder
of material 2 (gamma2=4, rho2 base 0.5 g/cm^3 with a sin(6*phi)-seeded density perturbation decaying
to r=0) of radius r2=a=0.3 cm. Both materials start in mechanical equilibrium at P_gas=1 Ba at the
interface; a converging shock is driven inward by setting P=50 Ba in material 1 for r>0.45 cm. In the
magnetized (canonical) case, a parallel-pinch magnetic field (source eqs. 68-69, a=r2,
Bphi(a)=5*sqrt(pi)/a G, Bz(a)=0.1*sqrt(4*pi) G) threads the inner material, and both materials carry
finite magnetic diffusivity (eta1=1, eta2=0.1 cm^2/s). The material interface is tracked with a level
set; the domain boundary is zero-gradient (Neumann).

## What this test actually tests
Whether the scheme's two-material resistive-MHD coupling correctly captures a converging-shock-
driven Richtmyer-Meshkov-type interface instability, and specifically whether an embedded parallel-
pinch magnetic field suppresses the instability growth relative to the unmagnetized case
(rm-instability-suppression-with-vs-without-field, a config_delta differential mode).

## Qualitative behaviour
In both cases the hydrodynamic shock compresses the inner material and a reverse shock strikes the
interface a second time. In the unmagnetized baseline, the seeded sin(6*phi) density perturbation
grows into a visible interface instability. In the magnetized+resistive canonical case, the same
perturbation is qualitatively suppressed by the pinch field (Fig. 13, t=0, 5e-2, 1e-1 s). No analytic
solution exists for either case.

## Validation notes
Fig. 13 shows three snapshots (t=0, 5e-2, 1e-1 s) side by side for the unmagnetized and magnetized
cases. Unlike Sections 7.10/7.11 (which report an adiabat-tracking and a mass/flux conservation-drift
diagnostic), Section 7.12 does not state or plot any quantitative conservation-drift or div-B
diagnostic for this specific test -- none is fabricated here; the entry is scored conservatively on
the single qualitative differential mode above.

## Notes
The exterior (material 1) magnetic field is taken as identically zero outside the pinch radius a=0.3
cm. This is an INFERRED simplification, not an explicit source statement -- Section 7.12 states only
the interior pinch field (eqs. 68-69 at a=r2) and does not describe an exterior vacuum extension the
way Section 7.9 (resistive-field-soak-cylindrical-material-interface) does. If a nonzero exterior
field is confirmed from the authors' code/supplementary material, this entry should be revised.
Domain centering at the origin and its 1 cm x 1 cm square extent are read from the Fig. 13 caption;
the body text does not restate the domain size. `related_to` links the parallel-pinch field
construction and material-interface coupling siblings; no sibling shares the specific converging-
shock-driven RM-instability setup, so this is a NEW ENTRY, not a fork of any of them.
