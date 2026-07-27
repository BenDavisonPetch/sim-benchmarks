---
# Authored via /add-test (NORMAL path) from Jones, McNally & Reynolds 2026, "A constrained-transport
# embedded boundary method for compressible resistive magnetohydrodynamics", J. Comput. Phys. 550
# (2026) 114641 (citekey: jones2026), Section 7.14 "Magnetic compression of a z-pinch with material
# interface". Unlike the eq.(68-69) parallel-pinch construction used elsewhere in this paper, the
# Bphi(r)/A_z(r) profile here is a distinct tanh/log-cosh form (source, Sect. 7.14) -- verified below
# to be self-consistent (dA_z/dr equals the stated Bphi(r) exactly, no factor-of-2-type discrepancy
# unlike the parallel-pinch siblings).
#
# DEDUP: shares the two-material mhd(resistivity)/gamma-law @material-contact physics_signature +
# analysis_treatments + capability_flags with converging-shock-parallel-pinch-material-interface and
# shocked-bubble-material-interface (all three from this paper), but the geometry/IC structural form
# (magnetically-self-driven compression of a liner, no external shock driver, distinct tanh-based
# field profile, buffer-density outer region) differs from both -- NEW ENTRY, related_to both plus
# resistive-field-soak-cylindrical-material-interface (two-material + level set + resistivity) and
# the theta/parallel-pinch compression tests (compressional dynamics).

slug: magnetic-compression-zpinch-material-interface
name: "Magnetic Compression of a Z-Pinch with Material Interface"
provenance: literature
one_liner: "A two-material (interior + liner) resistive-MHD cylindrical configuration is compressed purely by its own imposed, monotonically-increasing-outward azimuthal magnetic pressure gradient (no external driver or embedded rigid wall); validated qualitatively against the reported compression time series."

physics:
  materials:
    - name: interior_gas
      base: mhd
      terms: [resistivity]
      eos:
        type: gamma-law
        params: { gamma: 2 }
      material_fields:
        - { name: eta, region: interior, expr: "0.1", units: "cm^2/s" }
    - name: liner_gas
      base: mhd
      terms: [resistivity]
      eos:
        type: gamma-law
        params: { gamma: 1.3 }
      material_fields:
        - { name: eta, region: liner, expr: "0.05", units: "cm^2/s" }
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
  domain: { x: [-16, 16], y: [-16, 16] }   # "total simulation domain is 32 cm x 32 cm" (Fig. 15 caption); centered at origin by symmetry of the r-dependent construction
  regions:
    - id: interior
      shape: cylinder
      params: { center: [0, 0], r: 4 }
    # liner = domain minus interior; the density buffer at r>3*r1 is a piecewise IC within this
    # single liner material, not a separate material (minimal-material canonicalization, §2.4 step 5)

units:
  system: cgs-gaussian
  b_field_convention: sqrt-4pi

initial_conditions:
  aux:
    - { name: r1,        expr: "4" }                                 # liner inner radius = interior/liner interface radius, cm
    - { name: a,         expr: "5" }                                 # source-stated field-profile scale radius, cm
    - { name: rho2_base, expr: "1.4" }                                # nominal liner density, g/cm^3
    - { name: r_buffer,  expr: "12" }                                 # = 3*r1, buffer-region onset radius, cm
    - { name: Bphi,      expr: "-100 * sqrt(4*pi) * (1 + tanh((r-a)/2))" }   # source-stated Bphi(r), G
  equilibrium:
    - region: interior
      fields:
        rho: "0.5 + 0.05*sin(6*phi)*(1 - cos(pi*r/r1))"   # source-stated density perturbation
        p: "1"
        vx: "0"
        vy: "0"
        vz: "0"
        Bx: "Bphi * (y/r)"    # Bx = dA_z/dy = (dA_z/dr)*(y/r); dA_z/dr equals the stated Bphi(r) exactly for this A_z (verified, see Notes)
        By: "-Bphi * (x/r)"   # By = -dA_z/dx = -(dA_z/dr)*(x/r)
        Bz: "0"               # "Bz=0 everywhere" (source)
    - region: liner
      fields:
        rho: "rho2_base + (100*rho2_base - rho2_base) * step(r, r_buffer, r_buffer)"   # rho2 for r1<r<=3*r1; 100*rho2 for r>3*r1 (buffer region)
        p: "1"
        vx: "0"
        vy: "0"
        vz: "0"
        Bx: "Bphi * (y/r)"
        By: "-Bphi * (x/r)"
        Bz: "0"
  perturbation:
    combine_rule: additive
    fields: {}
  potentials:
    - name: A_z
      expr: "-200 * sqrt(4*pi) * (r/2 + log(cosh((a-r)/2)))"   # source-stated vector potential
      derives: "Bx = dA_z/dy, By = -dA_z/dx (B = curl(A_z*z_hat)); dA_z/dr = -100*sqrt(4*pi)*(1+tanh((r-a)/2)), which equals the stated Bphi(r) exactly"

parameters:
  - { name: r1,              canonical: 4,    meaning: "liner inner radius / initial interior-liner material interface location, cm" }
  - { name: gamma_interior,  canonical: 2,    meaning: "interior material ratio of specific heats" }
  - { name: eta_interior,    canonical: 0.1,  meaning: "interior material magnetic diffusivity, cm^2/s" }
  - { name: gamma_liner,     canonical: 1.3,  meaning: "liner material ratio of specific heats" }
  - { name: eta_liner,       canonical: 0.05, meaning: "liner material magnetic diffusivity, cm^2/s" }
  - { name: rho2_base,       canonical: 1.4,  meaning: "nominal liner density, g/cm^3 (for r1 < r <= 3*r1)" }
  - { name: r_buffer,        canonical: 12,   meaning: "= 3*r1; radius beyond which liner density is set to 100x nominal as a buffer region, cm" }
  - { name: a,               canonical: 5,    meaning: "azimuthal-field profile scale radius, cm" }

domain_bc:
  x_lo: { type: neumann }
  x_hi: { type: neumann }
  y_lo: { type: neumann }
  y_hi: { type: neumann }

internal_boundaries: []   # material interface is physics.coupling (material-contact); no separate embedded rigid wall -- compression is driven entirely by the imposed Bphi(r) pressure gradient

time:
  t_final: 0.1   # source (Fig. 15 panel labels): snapshots at t=0, 3.00e-2, 4.60e-2, 1.00e-1
  snapshot_times: [0, 0.03, 0.046, 0.1]

validation_modes:
  - id: magnetically-driven-compression-time-series
    purpose: "Verify that the imposed azimuthal magnetic field's monotonically-increasing-outward magnetic pressure (implying an inward-pointing net force) drives a qualitatively correct time-dependent compression of the interior/liner material interface, with no external driver or embedded rigid wall -- the interface's own MHD dynamics under the ambient field is the only compressing agent."
    procedure: feature-location
    inputs:
      at_time: [0, 0.03, 0.046, 0.1]
      variables: [rho]
      cut_lines: ["visual inspection of the interior/liner material-interface contour, per Fig. 15 (central 12 cm section shown)"]
      features: ["progressive inward compression of the interior/liner interface over the four snapshot times"]
      reference: { kind: reference-result, key: jones2026 }
      tolerance: "qualitative visual match only -- no numeric compression-ratio or interface-position criterion is stated for this test (no analytic solution)"
    has_exact_solution: false
    score: 2
    score_justification: "No automatable check and no exact solution, but the expected behavior is a specific, named, checkable qualitative feature (progressive inward compression driven purely by the imposed field, not an external wall or shock) -- rubric row 2."

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
references_unverified: []
test_origin:
  status: pending
  authored_from: jones2026
  attribution_claims: []
reference_results:
  - key: jones2026
    params_used: { r1: 4, gamma_interior: 2, eta_interior: 0.1, gamma_liner: 1.3, eta_liner: 0.05, rho2_base: 1.4, r_buffer: 12, a: 5, t_final: 0.1 }
    method: "resistive MHD; two-material ghost-fluid coupling (Sect. 3.2/4.2) with per-material edge-fraction-weighted electric field; level-set-tracked interior/liner interface; HLLD Riemann solver; 512x512 Cartesian mesh over the full 32cm x 32cm domain, central 12 cm section shown in figures"
    resolution: "512^2 Cartesian mesh (Fig. 15 caption)"
    amr: "none"
    findings: "The interior/liner interface progressively compresses inward under the imposed magnetic pressure gradient over the four reported snapshot times (Fig. 15, t=0, 3.00e-2, 4.60e-2, 1.00e-1)."
related_to: [converging-shock-parallel-pinch-material-interface, shocked-bubble-material-interface, resistive-field-soak-cylindrical-material-interface, theta-pinch-compression-embedded-boundary, parallel-pinch-compression-embedded-boundary]
headline_score: 2
---

## Physical problem
A cylindrical interior material (r<r1=4 cm, gamma=2, eta=0.1 cm^2/s) with a sin(6*phi)-seeded
density perturbation is surrounded by a liner material (gamma=1.3, eta=0.05 cm^2/s, nominal density
1.4 g/cm^3, with a 100x-density buffer region for r>3*r1=12 cm to isolate the domain-edge boundary
condition from the pinch dynamics). Both materials start at P_gas=1 Ba with Bz=0 everywhere and a
purely azimuthal field Bphi(r) (source-stated tanh profile, scale radius a=5 cm) whose magnitude
increases monotonically with r, producing an outward-pointing magnetic-pressure gradient and hence a
net inward force that compresses the interior/liner interface -- with no external shock driver and
no embedded rigid wall; the material interface itself, tracked with a level set, is the only moving
boundary.

## What this test actually tests
Whether the scheme's two-material resistive-MHD coupling correctly evolves a purely
magnetically-self-driven compression of a material interface (no rigid-wall or shock driver
involved), reproducing the qualitative inward-compression time series shown in Fig. 15
(magnetically-driven-compression-time-series).

## Qualitative behaviour
The interior/liner material interface, initially at r=4 cm, compresses progressively inward over
the four snapshot times (t=0, 0.03, 0.046, 0.1 s) under the imposed Bphi(r) magnetic pressure
gradient; the density perturbation seeded in the interior material evolves along with the
compression. No analytic solution exists for this test.

## Validation notes
Fig. 15 shows the compression time series over a central 12 cm section of the full 32 cm x 32 cm
domain at t=0, 3.00e-2, 4.60e-2, 1.00e-1 s. No quantitative conservation-drift or div-B diagnostic is
stated or plotted for this test in the source; none is fabricated here.

## Notes
A genuine internal inconsistency in the source is recorded verbatim, not resolved: Section 7.14
states the liner density buffer region exists "to provide a buffer region between the
computationally expedient **periodic** boundary condition applied to the square edges of the
domain and the inner section", but the same paragraph later states "The interface is tracked with a
level set, and **all domain boundaries are zero-gradient**." These two statements (periodic vs
zero-gradient/Neumann) directly conflict. `domain_bc` here uses the later, more specific
zero-gradient/Neumann statement as authoritative; the earlier "periodic" mention is recorded here for
completeness and left unresolved. The dA_z/dr derivation was checked explicitly against the stated
Bphi(r) and found self-consistent (no factor-of-2-type discrepancy as seen in the parallel-pinch
eq.(68-69) siblings). Domain centering at the origin is inferred by symmetry of the r-dependent
construction, not explicitly restated in the source.
