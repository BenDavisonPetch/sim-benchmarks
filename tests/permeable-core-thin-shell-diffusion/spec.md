---
# Authored via /add-test (NORMAL path) from MIT 6.013 online course notes, ch.10.4 Example
# 10.4.1 ("Diffusion of Transverse Field into Circular Cylindrical Conducting Shell with a
# Permeable Core"). Self-contained closed-form derivation (eqs 1-20); exact analytic solution.
#
# MODEL (per user physics direction, correcting the first draft): the thin conducting wall is a
# MATERIAL obeying the magnetic-diffusion equations (finite resistivity), NOT a bespoke internal
# boundary. The insulating permeable core and the insulating free-space exterior are magnetostatic
# materials (elliptic B=mu*H). The three bodies couple by field continuity (electromagnetic-coupling,
# the existing internal-boundary-kind). One new vocab id used: equations/magnetostatics (approved).
# The closed-form A(t) solution is the thin-shell asymptotic (Delta << a): the finite-thickness
# magnetic-diffusion shell must reproduce it as Delta/a -> 0.

slug: permeable-core-thin-shell-diffusion
name: "Transverse Field Diffusion into a Permeable-Core Conducting Shell"
provenance: literature
one_liner: "Step transverse magnetic field applied to a thin resistive cylindrical shell around a linearly permeable core; the shell's eddy currents shield then release the field over a magnetic-diffusion time, with an exact thin-shell closed-form reference."

physics:
  materials:
    - name: core
      base: magnetostatics         # insulating, linearly permeable core (vocab: equations/magnetostatics, approved)
      terms: []
      material_fields:
        - name: mu
          region: core
          expr: "mu_core"
          units: "units of mu_o"
    - name: shell
      base: magnetic-diffusion     # the thin conducting wall: v==0, field diffuses (finite resistivity)
      terms: [resistivity]         # present: eta nonzero throughout the shell
      material_fields:
        - name: eta
          region: shell
          expr: "eta_shell"        # constant resistivity in the shell (= 1/sigma)
          units: "units of a^2 * mu_o / tau_diffuse"
    - name: exterior
      base: magnetostatics         # insulating free space surrounding the shell
      terms: []
      material_fields:
        - name: mu
          region: exterior
          expr: "mu_o"
          units: "units of mu_o"
  coupling: electromagnetic-coupling   # field continuity across the core/shell and shell/exterior interfaces

dimension:
  intrinsic: 2                     # fields depend only on (r, phi); z-invariant by construction
  runnable_in: [2]                 # NOT 3: a finite-z realization needs end-cap / return-current paths
                                    # ("end effect", source text) -- genuinely new analysis, not an inert
                                    # extra dimension (SPEC §2.5)

analysis_treatments: [axis-singularity]   # domain includes r=0 (the core interior)

capability_flags:
  time_dependent_bc: true          # r_hi far-field state references t via step(t,0,0)
  has_internal_boundaries: true    # physics.coupling != none (two material interfaces at the shell)
geometry_stress: none

geometry:
  coord_system: cylindrical        # physical (r,phi,z) frame the closed-form solution is posed in;
                                    # z-invariant (2D in the r-phi plane)
  domain: { r: [0, 20], phi: [0, 6.283185307179586] }   # r in units of core radius a; truncates the
                                                          # analytically unbounded exterior
  regions:
    - id: core
      shape: cylinder
      params: { center: [0, 0], r: 0.95 }        # r < a - Delta/2 (a=1, Delta=0.1): the permeable core
    - id: shell
      shape: shell
      params: { center: [0, 0], r: [0.95, 1.05] }  # the thin conducting wall, centred on r=a=1
    # exterior = domain minus (core + shell): the free-space background material

units:
  system: nondimensional            # lengths in units of a; permeability in units of mu_o; field in
                                     # units of H_m (step magnitude). Linear/scale-invariant structure
                                     # (eqs 13-20) makes this the minimal complete instance.
  b_field_convention: permeability-unity   # B = mu*H directly, no absorbed 4*pi factor (eq 6); mu_o = 1

initial_conditions:
  aux:
    - { name: a,         expr: "1"   }   # core/shell radius -- adopted length unit
    - { name: delta,     expr: "0.1" }   # shell thickness (thin: delta/a = 0.1); exact soln is the delta->0 limit
    - { name: mu_o,      expr: "1"   }   # free-space permeability -- adopted permeability unit
    - { name: mu_core,   expr: "200" }   # core permeability = 200*mu_o (Fig. 10.4.3 worked example)
    - { name: H_m,       expr: "1"   }   # step-field magnitude -- adopted field unit (solution linear in H_m, eq 16)
    - { name: sigma,     expr: "10"  }   # shell conductivity (sets the diffusion time; see tau_m note)
    - { name: eta_shell, expr: "1/sigma" }  # shell resistivity = 1/sigma
  equilibrium:
    - region: core
      fields: { H: "0" }               # "no field inside or outside... before t=0" (source text)
    - region: shell
      fields: { B: "0" }               # magnetic-diffusion body: field IC is zero before the step
  perturbation:
    combine_rule: additive
    fields: []                         # all time dependence carried by the driven far-field BC + shell diffusion
  potentials:
    - name: Psi
      expr: "0"
      derives: "H = -grad(Psi)"        # eq (7): scalar potential in the insulating (magnetostatic) regions

parameters:
  - { name: a,        canonical: 1,    meaning: "shell/core radius (length unit)" }
  - { name: delta,    canonical: 0.1,  meaning: "shell thickness in units of a (thin-shell: exact solution is the delta/a -> 0 limit)" }
  - { name: mu_o,     canonical: 1,    meaning: "free-space permeability (permeability unit)" }
  - { name: mu_core,  canonical: 200,  meaning: "core permeability, in units of mu_o (Fig. 10.4.3: mu = 200*mu_o)" }
  - { name: H_m,      canonical: 1,    meaning: "magnitude of the applied step field H_o(t) (field unit)" }
  - { name: sigma,    canonical: 10,   meaning: "shell conductivity; with delta it fixes the thin-shell decay time tau_m = mu_o*sigma*delta*a*(mu/(mu+mu_o)), eq 14 (the validation target, not an input)" }
  - { name: eta_shell, canonical: 0.1, meaning: "shell resistivity = 1/sigma (magnetic-diffusion coefficient)" }

domain_bc:
  r_hi:
    type: dirichlet
    state:
      # far field: Psi -> -H_o(t)*r*cos(phi) = -H_o(t)*x (eq 8); truncated at r=20a, the O(A/r^2)
      # dipole correction is negligible there. step(t,0,0) is a Heaviside step at t=0 (source: "H_o
      # is a step function of magnitude H_m turned on when t=0").
      Psi: "-H_m*step(t,0,0)*r*cos(phi)"
  phi_lo: { type: periodic }
  phi_hi: { type: periodic }
  # r_lo (r=0, the axis) is a coordinate singularity, not a physical face -- no state (handled by
  # the axis-singularity analysis_treatment, per registry/coord-systems/cylindrical.md).

internal_boundaries: []            # the core/shell/exterior coupling is the material boundary (physics.coupling)

time:
  t_final: 3                       # in units of tau_m; covers all sampled times up to t/tau_m = 2
  snapshot_times: [0, 0.25, 0.5, 1, 2]   # matches Fig. 10.4.3's t/tau = 0, 0.25, 0.5, 2

validation_modes:
  - id: dipole-coefficient-exact-compare
    purpose: "Verify the induced fields (B_r, B_phi) on both sides of the conducting shell against the closed-form thin-shell transient dipole-coefficient solution A(t) (eq 16) at stated times."
    procedure: exact-solution-compare
    inputs:
      at_time: [0.25, 0.5, 1.0, 2.0]
      variables: [B_r, B_phi]
      cut_lines: ["r = 0.5*a (inside core)", "r = 1.5*a (just outside shell)"]
      reference: { kind: reference, key: mit6013-ch10-4 }
      tolerance: "L2(B_r,B_phi) error < a few % of mu_o*H_m at each sampled t/tau_m, in the thin-shell (delta/a << 1) limit"
    has_exact_solution: true
    score: 5
    score_justification: "Exact closed-form analytic solution (eqs 15-20, thin-shell limit) fully self-contained in the source, paired with the convergence-order mode below for quantitative convergence to the theoretical order (scoring-rubric.md row 5). The measured field must approach the thin-shell A(t) as delta/a -> 0."

  - id: dipole-coefficient-convergence-order
    purpose: "Verify the numerical scheme's spatial convergence toward the exact A(t)-derived field solution as grid resolution is refined (at fixed thin-shell thickness)."
    procedure: convergence-order
    inputs:
      at_time: [1.0]
      variables: [B_r, B_phi]
      error_measure: "L2(B_r,B_phi) vs the exact-solution-compare mode above"
      resolution_sequence: "at least 3 successive uniform refinements; refinement ratio r stated by the run"
      expected_order: "scheme's theoretical spatial order (interior); reduced near the shell interface"
      tolerance: "measured order within 0.2 of the theoretical order away from the shell interface"
    has_exact_solution: true
    score: 5
    score_justification: "Exact solution + demonstrated convergence to the theoretical order is the compound criterion for score 5 (scoring-rubric.md row 5)."

references: []
references_unverified:
  # Offline authoring (§5.2B): source is a specific web page (URL read directly from the saved
  # HTML's `saved from url=` comment); no DOI. Author/year/publisher NOT asserted here -- that would
  # be a memory-fabricated bibliographic claim, not something read from the supplied file.
  - key: mit6013-ch10-4
    verification: { status: unverified, identifier: { url: "https://web.mit.edu/6.013_book/www/chapter10/10.4.html" }, source: "saved-page comment in permeable_shell_ref.html", checked: null }
reference_results: []
related_to: []
headline_score: 5
---

## Physical problem
An infinitely long circular cylindrical shell (radius `a`, thickness `Delta << a`, conductivity
`sigma`) is filled by a linearly permeable, non-conducting core (permeability `mu = 200*mu_o`) and
surrounded by free space (permeability `mu_o`). A magnetic field `H_o(t)`, uniform far from the
cylinder and transverse to its axis, is imposed everywhere at once (no z dependence). Before `t=0`
there is no field anywhere; at `t=0`, `H_o(t)` steps to magnitude `H_m`. The core and the exterior
are insulating and respond only through the linear constitutive law `B = mu*H` (magnetostatic); the
thin shell is the sole conductor, a magnetic-diffusion body whose eddy currents shield the interior
immediately after the step and then diffuse away over the shell diffusion time.

## What this test actually tests
Whether a method reproduces the exact time-dependent magnetoquasistatic response of a resistive
conducting shell separating two insulating, differently-permeable magnetic materials: the induced
dipole coefficient `A(t)` (eq 16) governing the exterior/core field pattern, from initial perfect
shielding (`t=0+`, matching the perfect-conductor limit) to the final magnetization-only state
(`t -> infinity`, set purely by `(mu-mu_o)/(mu+mu_o)`). It exercises a coupled magnetostatic /
magnetic-diffusion multi-material system with a driven, time-dependent far-field boundary.

## Qualitative behaviour
At `t/tau_m = 0` (an instant after the step): shell currents completely shield the core from the
field (perfect-conductor-like response, `A(0) = -H_m*a^2`). At `t/tau_m = 0.25, 0.5`: the shielding
progressively decays as currents diffuse (Fig. 10.4.3). At `t/tau_m = 2`: the field pattern has
essentially reached its final form, drawn preferentially into the permeable core (`mu=200*mu_o`),
the shell's transient response negligible. The sign of the equivalent dipole moment `A` reverses
during the transient whenever `mu > mu_o` (source: "This sign reversal occurs only if `mu > mu_o`..
due to the magnetization of the core"). No AMR/gridding symmetry-breaking trap applies (the
cylindrical `axis-singularity` treatment is the only special handling needed).

## Validation notes
The reference solution is the closed-form thin-shell asymptote (eqs 15-20 of the source):
`A(t) = H_m*a^2*[ (mu-mu_o)/(mu+mu_o)*(1 - exp(-t/tau_m)) - exp(-t/tau_m) ]`, with
`tau_m = mu_o*sigma*Delta*a*(mu/(mu+mu_o))` (eq 14); the shell surface current
`K_z = -2*H_m*exp(-t/tau_m)*sin(phi)` (eq 20) follows. Because the finite-thickness shell here is a
`magnetic-diffusion` material, `tau_m` is a *derived* quantity (a validation target), not an input:
the numeric result must converge to the thin-shell `A(t)` as `Delta/a -> 0`. `mu_core = 200`
reproduces the source's worked illustration (Fig. 10.4.3). The only unverified reference is the
source page itself.

## Notes
`Delta` (shell thickness) and `sigma` (conductivity) are given explicit small/finite values so the
shell can be a genuine `magnetic-diffusion` material; the source's closed form is their thin-shell
limit, where only the product `sigma*Delta` (via `tau_m`) matters. The outer domain radius `r=20*a`
truncates the analytically unbounded exterior (same convention as the Mercury magnetosphere entry's
finite box); the far-field Dirichlet state on `r_hi` drops the O(1/r^2) dipole correction, valid at
this truncation radius. `runnable_in` excludes 3D: a finite-length realization requires end-cap
return-current paths ("end effect", source text) that are genuinely different physics. One new
registry id was used for this entry: `equations/magnetostatics` (insulating linear magnetic
material, approved); the shell reuses the existing `magnetic-diffusion` base and the interfaces the
existing `electromagnetic-coupling` kind.
