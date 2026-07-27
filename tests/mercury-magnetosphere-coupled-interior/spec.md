---
# CORRECTED against the SPEC+docs delta. Two materials by EQUATION SET (mhd vs
# magnetic-diffusion); core+mantle unified via eta(r) (minimal-material canonicalization).
# Remaining `# gap:` markers are VOCAB only (self-heal via §7.2). No schema gaps left.

slug: mercury-magnetosphere-coupled-interior
name: "Mercury Magnetosphere with Coupled Conducting Interior"
provenance: literature
one_liner: "Driven Mercury magnetosphere: ideal-MHD plasma coupled to a magnetic-diffusion interior with radially layered conductivity; core induction opposes a solar-wind pressure step."

physics:
  materials:
    - name: plasma
      base: mhd                    # ideal outside the planet (reconnection numerical)
      terms: []
      eos:
        type: gamma-law
        params: { gamma: null }    # needs-source: gamma not stated in source (Tsw=15 eV is)
    - name: interior
      base: magnetic-diffusion     # gap-A (vocab §7.2): v==0, evolves only dB/dt = -(1/mu0) curl(eta curl B)
      terms: [resistivity]         # present: eta nonzero throughout the interior
      # core+mantle = ONE material, distinguished only by eta(r) (minimal-material canonicalization).
      material_fields:
        - name: eta
          region: interior
          expr: "eta_mantle + (eta_core - eta_mantle) * (1 - r) / (1 - 0.8)"   # linear ramp in r
          units: "ohm*m"
      # no eos: magnetic-diffusion carries no fluid thermodynamics (requires_eos: false)
  coupling: electromagnetic-coupling     # gap-B (vocab §7.2): field continuity plasma <-> interior at r=1

dimension:
  intrinsic: 3                     # offset dipole + IMF Bx + Vy -> no reducing symmetry
  runnable_in: [3]

analysis_treatments: [none]        # descriptors only now; the fork is the capability flags below

capability_flags:
  time_dependent_bc: true          # x_hi inflow state references t (the pressure step)
  has_internal_boundaries: true    # plasma/interior interface at r=1
geometry_stress: none

geometry:
  coord_system: cartesian          # physical MSO frame. (Spherical GRID = Jia's method -> reference_result.)
  domain: { x: [-64, 24], y: [-32, 32], z: [-32, 32] }   # R_M, MSO
  regions:
    - id: interior
      shape: shell
      params: { center: [0,0,0], r: [0.0, 1.0] }   # whole planet r<1 is the magnetic-diffusion body
    - id: surface
      shape: sphere
      params: { center: [0,0,0], r: 1.0 }          # material boundary plasma/interior

units:
  system: si                       # nT, nPa, km/s, cm^-3, eV, S/m (stored as authored, §12)
  b_field_convention: null         # needs-source: not stated

initial_conditions:
  aux:
    - { name: R_M,        expr: "2440", units: km }
    - { name: eta_mantle, expr: "1e7"  }
    - { name: eta_core,   expr: "1e-5" }
  equilibrium:
    - region: interior
      fields:
        # Offset axial dipole is the B IC of the interior material; near-frozen in the low-eta
        # core because base=magnetic-diffusion with small eta. No prescribed-flux BC needed.
        # dipole(mx,my,mz, cx,cy,cz): point-dipole B field, moment (mx,my,mz) at center
        # (cx,cy,cz) — allow-listed builtin (docs/ic-expression-language.md §2.2). The moment
        # z-component is written INLINE from the surface equatorial field via the standard
        # relation B_eq = (mu0/4pi) m / R^3  =>  m = B_eq R^3 / (mu0/4pi), with mu0/4pi = 1e-7
        # (SI); dipole_eq_nT is in nT (x 1e-9 -> T). Center offset +dipole_offset_RM in Z (R_M).
        B: "dipole(0, 0, dipole_eq_nT * 1e-9 * R_M**3 / 1e-7, 0, 0, dipole_offset_RM)"
  perturbation:
    combine_rule: additive
    fields: []
  potentials: []

parameters:
  - { name: gamma,        canonical: null,   meaning: "ratio of specific heats", notes: "needs-source; not stated" }
  - { name: dipole_eq_nT, canonical: 195,    meaning: "equatorial surface dipole strength (nT)", source_ref: anderson2011 }
  - { name: dipole_offset_RM, canonical: 0.2, meaning: "northward (+Z) dipole-center offset (R_M)", source_ref: anderson2011 }
  - { name: r_surf_RM,    canonical: 1.0,    meaning: "planetary surface radius (R_M) = plasma/interior boundary" }
  - { name: eta_mantle,   canonical: 1.0e7,  meaning: "mantle resistivity (ohm*m)", source_ref: hauck2013 }
  - { name: eta_core,     canonical: 1.0e-5, meaning: "core-boundary resistivity (ohm*m)", source_ref: hauck2013 }
  - { name: sw_n_cm3,     canonical: 40,     meaning: "pre-step upstream density (cm^-3)" }
  - { name: sw_T_eV,      canonical: 15,     meaning: "upstream temperature (eV)" }
  - { name: sw_V_kms,     canonical: [-400, 50, 0], meaning: "pre-step upstream velocity MSO (km/s)" }
  - { name: imf_B_nT,     canonical: [-15.2, 8.4, -8.5], meaning: "upstream IMF MSO (nT)", source_ref: slavin2009 }
  - { name: sw_n_post_cm3, canonical: 80,    meaning: "post-step density (cm^-3)" }
  - { name: sw_speed_post_kms, canonical: 700, meaning: "post-step speed (km/s); Pdyn ~66 nPa" }
  - { name: step_start_s, canonical: 0,      meaning: "step onset time (s), measured from quasi-steady" }
  - { name: step_ramp_s,  canonical: 30,     meaning: "ramp duration (s)" }

domain_bc:
  x_hi:
    type: supersonic-inflow
    state:                         # expressions; references t -> time_dependent_bc=true
      rho: "sw_n_cm3 + (sw_n_post_cm3 - sw_n_cm3) * step(t, step_start_s, step_start_s+step_ramp_s)"
      T:   "sw_T_eV"
      vx:  "-(400 + (sw_speed_post_kms-400) * step(t, step_start_s, step_start_s+step_ramp_s))"
      vy:  "50"
      vz:  "0"
      Bx:  "imf_B_nT[0]"
      By:  "imf_B_nT[1]"
      Bz:  "imf_B_nT[2]"
  x_lo: { type: outflow }
  y_lo: { type: outflow }
  y_hi: { type: outflow }
  z_lo: { type: outflow }
  z_hi: { type: outflow }

internal_boundaries: []            # the plasma/interior coupling is the material boundary (physics.coupling)

time:
  t_final: 600                     # run to ~10 min: covers pre-step steady + step + post-step steady (~3 min after)
  snapshot_times: [ ]

validation_modes:
  - id: boundary-standoff-locations
    purpose: "Verify dayside magnetopause, bow-shock, and nightside X-line standoff distances in the pre-step quasi-steady state."
    procedure: feature-location
    inputs:
      at_time: 0                   # pre-step steady state
      variables: [J_total, p]
      cut_lines: ["subsolar x-axis (y=0,z=0)"]
      features: ["magnetopause", "bow shock", "tail X-line"]
      reference: { kind: reference, key: winslow2013 }
      tolerance: "standoff within ~0.1 R_M of the (pressure-scaled) empirical model"
    has_exact_solution: false
    score: 3
    score_justification: "Quantitative feature locations (MP ~1.5, BS ~1.9, X-line ~2 R_M) vs a MESSENGER-based empirical model; no exact solution."

  - id: induction-standoff-delta
    purpose: "Verify the induction-driven increase in compressed dayside magnetopause standoff attributable to the conducting core."
    procedure: feature-location
    baseline:
      description: "same test with the interior resistivity set uniformly high (eta = eta_mantle everywhere) so there is no inductive core response."
      config_delta: { "aux.eta_core": "eta_mantle" }
    measured: "difference in compressed magnetopause standoff, induction vs no-induction"
    inputs:
      at_time: 600                 # post-step steady state
      variables: [J_total]
      cut_lines: ["subsolar x-axis"]
      features: ["magnetopause standoff (compressed)"]
      reference: { kind: reference-result, key: jia2015 }
      tolerance: "delta ~10% (1.15 R_M with core vs 1.04 R_M without)"
    has_exact_solution: false
    score: 3
    score_justification: "Controlled quantitative A/B (the difference is the measurand); tops at 3 absent an exact solution."

references:
  # All 5 DOIs resolve on the Crossref metadata API (§8.4). `meta` is resolver output, never typed.
  - key: jia2015
    original_intro: true            # sole using-ref; SPEC §5.4 rule 3 (see test_origin below)
    verification:
      status: verified
      identifier: { doi: "10.1002/2015JA021143" }
      source: "crossref: 10.1002/2015JA021143 -> 200"
      checked: "2026-07-27"
      meta:
        year: 2015
        first_author: Jia
        container: "Journal of Geophysical Research: Space Physics"
        title: "Global MHD simulations of Mercury's magnetosphere with coupled planetary interior: Induction effect of the planetary conducting core on the global interaction"
  - key: winslow2013      # empirical magnetopause/bow-shock model (mode reference, NOT a using-ref)
    verification:
      status: verified
      identifier: { doi: "10.1002/jgra.50237" }
      source: "crossref: 10.1002/jgra.50237 -> 200"
      checked: "2026-07-27"
      meta:
        year: 2013
        first_author: Winslow
        container: "Journal of Geophysical Research: Space Physics"
        title: "Mercury's magnetopause and bow shock from MESSENGER Magnetometer observations"
  - key: anderson2011     # MESSENGER offset-dipole strength/offset (source_ref)
    verification:
      status: verified
      identifier: { doi: "10.1126/science.1211001" }
      source: "crossref: 10.1126/science.1211001 -> 200"
      checked: "2026-07-27"
      meta:
        year: 2011
        first_author: Anderson
        container: Science
        title: "The Global Magnetic Field of Mercury from MESSENGER Orbital Observations"
  - key: hauck2013        # Mercury interior resistivity/structure (source_ref)
    verification:
      status: verified
      identifier: { doi: "10.1002/jgre.20091" }
      source: "crossref: 10.1002/jgre.20091 -> 200"
      checked: "2026-07-27"
      meta:
        year: 2013
        first_author: Hauck
        container: "Journal of Geophysical Research: Planets"
        title: "The curious case of Mercury's internal structure"
  - key: slavin2009       # MESSENGER upstream IMF (source_ref)
    verification:
      status: verified
      identifier: { doi: "10.1029/2008GL036158" }
      source: "crossref: 10.1029/2008GL036158 -> 200"
      checked: "2026-07-27"
      meta:
        year: 2009
        first_author: Slavin
        container: Geophysical Research Letters
        title: "MESSENGER observations of Mercury's magnetosphere during northward IMF"
references_unverified: []
test_origin:
  status: resolved-in-list
  ref: jia2015                      # the only ref with a reference_results[] row = the only using-ref
  authored_from: jia2015
reference_results:
  - key: jia2015
    params_used: { sw_n_cm3: 40, sw_speed_post_kms: 700, sw_n_post_cm3: 80 }
    method: "resistive/diffusive MHD (BATSRUS/SWMF); nonuniform SPHERICAL grid; inner boundary truncated at r0=0.8 R_M with dipole flux prescribed there; semi-implicit time integration"
    resolution: "~0.008 R_M (~20 km) near planet, ~0.02 R_M near 2 R_M"
    amr: "adaptive (block-adaptive)"
    findings: >
      Pre-step: magnetopause ~1.5 R_M, bow shock ~1.9 R_M, tail X-line ~2 R_M, cross-polar-cap
      potential ~25 kV (obs ~30 kV), cusps ~70 deg N / ~65 deg S. Surface |Bz| perturbation
      ~80 nT dayside / ~40 nT nightside pre-step, rising to ~235 nT / ~120 nT post-step (~66 nPa).
      Induction: compressed magnetopause standoff ~1.15 R_M with conducting core vs ~1.04 R_M
      without (~10% increase from induction alone). Diffusion times: mantle ~0.02 s, core outer
      layer ~2.7 h.
    figure_asset: null
related_to: []
headline_score: 3
---

## Physical problem
Mercury's magnetosphere, driven by the solar wind, with the planetary interior included as a
conducting body. An offset dipole is the interior's field; the interior conducts (low resistivity
in the core, high in the mantle) and responds inductively to external field changes. Upstream
solar wind and IMF are held at M2-flyby values, then a dynamic-pressure step compresses the
system and the core opposes the compression.

## What this test actually tests
Whether a resistive/diffusive-MHD method reproduces (a) the standoff geometry of a small,
strongly interior-coupled magnetosphere against a data-based empirical model, and (b) the core
induction response to time-dependent forcing — the ~10% standoff increase attributable to the
conducting interior alone (differential mode).

## Qualitative behaviour
Strong N-S asymmetry from the offset dipole. Pre/post-step feature values as recorded in the
jia2015 reference_result. Induction opposes penetration of external perturbations into the core.

## Validation notes
The 30 s step penetrates the mantle (diffusion ~0.02 s) but not the core (~2.7 h), giving a
near-100%-efficiency inductive response. Standoff comparison uses the pressure-scaled Winslow
(2013) empirical model. The induction mode is a differential A/B against a no-induction baseline
(uniform high resistivity); the difference is the measurand.

## Notes
Units stored as authored (SI-ish); B-field convention unconfirmed and gamma not stated (see
pending_extraction). Jia's spherical grid and the r0=0.8 truncation with prescribed dipole flux
are method choices, recorded in the reference_result, not in the problem block.

---

## GAP LEDGER (pressure-test output)
Schema gaps from the prior draft are all dissolved by the SPEC delta + coupled-material framing.
Vocab/expression gaps are all resolved (Stage 4):
- gap-A: equations/magnetic-diffusion (v==0, induction-only) — registry id exists (Stage 2).
- gap-B: internal-boundary-kinds/electromagnetic-coupling (field continuity, distinct from
  material-contact) — registry id exists (seed).
- gap-C: `step(t,a,b)` and the `dipole` field builtin are allow-listed
  (docs/ic-expression-language.md §2). The dipole moment is
  written inline (no problem-specific builtin, no precomputed value).

Needs-source (-> pending_extraction.md): gamma, b_field_convention, and every source_ref value.
