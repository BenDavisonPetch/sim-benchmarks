---
# Authored via /add-test (NORMAL path) from Jones, McNally & Reynolds, "A constrained-transport
# embedded boundary method for compressible resistive magnetohydrodynamics", J. Comput. Phys. 550
# (2026) 114641 (citekey: jones2026), Section 7.3 "Standing magnetosonic wave in a cylinder -
# perturbed parallel pinch". The equilibrium field form is attributed by the source to Freidberg,
# "Ideal MHD" (Cambridge, 2014), eq. 5.33 (citekey: freidberg2014) -- a formula source, not a
# test-origin attribution claim (§5.4: not "the test introduced by").
#
# DEDUP: sibling of standing-magnetosonic-wave-theta-pinch-cylinder (same cylinder/rigid-wall
# geometry, same mhd+gamma-law physics_signature) but the equilibrium field configuration differs
# (parallel pinch Bphi(r)+Bz(r) vs pure axial theta-pinch); dedup treats a differing *value* of an
# already-present field as the SAME entry only when the structural form matches modulo numbers, but
# here Bphi(r) is a genuinely new nonzero field component (structural difference) -> NEW SIBLING.
# related_to links both ways.

slug: standing-magnetosonic-wave-parallel-pinch-cylinder
name: "Standing Fast Magnetosonic Wave in a Cylinder (Perturbed Parallel Pinch)"
provenance: literature
one_liner: "A standing fast-magnetosonic-wave test inside a rigid-walled cylindrical embedded boundary threaded by a Freidberg parallel-pinch (Bphi(r), Bz(r)) equilibrium field; validated by self-convergence against a 2048^2 reference solution."

physics:
  materials:
    - name: plasma
      base: mhd
      terms: []
      eos:
        type: gamma-law
        params: { gamma: 1.6666666666666667 }
  coupling: none

dimension:
  intrinsic: 2
  runnable_in: [2]

analysis_treatments: [axis-singularity]

capability_flags:
  time_dependent_bc: false
  has_internal_boundaries: false
geometry_stress: none

geometry:
  coord_system: cylindrical
  domain: { r: [0, 1], phi: [0, 6.283185307179586] }   # a=1 cm cylindrical embedded boundary IS the domain edge (physical); the source's "3 cm square" figure is the outer Cartesian MESH extent needed to fit cut cells around the embedded circle, a method/resolution detail, not the physical fluid domain
  regions:
    - id: interior
      shape: cylinder
      params: { center: [0, 0], r: 1 }

units:
  system: cgs-gaussian
  b_field_convention: sqrt-4pi   # consistent with Bz_a = sqrt(4*pi) G (1 in code units), as in the theta-pinch sibling

initial_conditions:
  aux:
    - { name: a,       expr: "1" }
    - { name: rho0,    expr: "1" }
    - { name: P0,      expr: "6" }
    - { name: gamma,   expr: "1.6666666666666667" }
    - { name: Bphi_a,  expr: "sqrt(pi) / a" }    # Bphi(a) = sqrt(pi)/a G
    - { name: Bz_a,    expr: "sqrt(4*pi)" }      # Bz(a) = sqrt(4*pi) G
    - { name: alpha,   expr: "Bphi_a / Bz_a" }   # alpha = Bphi(a)/Bz(a), source eq. below (68)-(69)
  equilibrium:
    - region: interior
      fields:
        rho: "rho0"
        p: "P0"
        vx: "0"
        vy: "0"
        vz: "0"
        # Bx, By obtained by direct differentiation of the source's A_z(r) potential (eq. 68) via
        # B = curl(A_z*z_hat) = (dA_z/dy, -dA_z/dx, 0); see potentials block below for A_z itself.
        Bx: "-(Bphi_a / (2*a)) * y"
        By: "(Bphi_a / (2*a)) * x"
        Bz: "(Bz_a/alpha) * sqrt(1 + (2*alpha**2/3)*(1-(r/a)**2)**2*(5-2*(r/a)**2))"   # source eq. (69)
  perturbation:
    combine_rule: additive
    fields: {}   # see parameters.perturbation_form: needs-source (not stated in Sect. 7.3, unlike the theta-pinch sibling's explicit v_r formula)
  potentials:
    - name: A_z
      expr: "Bphi_a * (a/4) * (2 - (r/a)**2)"   # source eq. (68)
      derives: "Bx = dA_z/dy, By = -dA_z/dx (B = curl(A_z*z_hat))"

parameters:
  - { name: a,      canonical: 1,     meaning: "cylinder (embedded boundary) radius, cm" }
  - { name: rho0,   canonical: 1,     meaning: "background density, g/cm^3" }
  - { name: P0,     canonical: 6,     meaning: "uniform thermal pressure, Ba" }
  - { name: gamma,  canonical: 1.6666666666666667, meaning: "ratio of specific heats (=5/3), global default" }
  - { name: Bphi_a, canonical: 1.7724538509055159, meaning: "azimuthal field at r=a, G (= sqrt(pi)/a)" }
  - { name: Bz_a,   canonical: 3.5449077018110318, meaning: "axial field at r=a, G (= sqrt(4*pi))" }
  - { name: perturbation_form, canonical: null, meaning: "functional form/magnitude of the perturbation that excites the standing magnetosonic mode for this parallel-pinch equilibrium", notes: "needs-source; Section 7.3 does not restate the velocity-kick formula given explicitly for the theta-pinch sibling test (7.2), and the parallel-pinch background is non-uniform so the eigenmode is not expected to be a simple Bessel function by direct analogy -- consult the source's supplementary material / code for the exact perturbation used" }

domain_bc:
  r_hi: { type: dirichlet, state: { Bz: "(Bz_a/alpha) * sqrt(1 + (2*alpha**2/3)*(1-(r/a)**2)**2*(5-2*(r/a)**2))", Bx: "-(Bphi_a/(2*a))*y", By: "(Bphi_a/(2*a))*x", vx: "0", vy: "0" } }   # rigid, static wall; fixed field profile (source Sect. 4.1, Eq. 42 current-free-preserving Dirichlet enforcement)

internal_boundaries: []

time:
  t_final: 0.1   # source: "Results at t=0.1s are shown in Fig. 4"
  snapshot_times: [0.1]

validation_modes:
  - id: azimuthal-field-self-convergence
    purpose: "Verify self-convergence of the azimuthal magnetic field toward a high-resolution reference solution as grid resolution is refined."
    procedure: self-convergence
    inputs:
      at_time: 0.1
      variables: [Bphi]
      resolution_sequence: [16, 32, 64, 128, 256, 512]
      reference_resolution: 2048
      r: 2
      expected_order: 2
      reference: { kind: reference-result, key: jones2026 }
      tolerance: "measured self-convergence order approaches the theoretical 2nd order relative to the 2048^2 reference solution (Fig. 4b)"
    has_exact_solution: false
    score: 4
    score_justification: "No exact solution used for this mode (source computes error against a 2048^2 high-resolution reference run, not a closed-form time-dependent solution, per Fig. 4's caption); a reliable, automatable self-convergence check demonstrating 2nd order — rubric row 4."

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
    params_used: { a: 1, rho0: 1, P0: 6, gamma: 1.6666666666666667, Bphi_a: 1.7724538509055159, Bz_a: 3.5449077018110318, t: 0.1 }
    method: "HLLD Riemann solver; single-sided static-polyline embedded boundary; staggered constrained transport; outer Cartesian mesh 3 cm square"
    resolution: "16^2 through 512^2, with a 2048^2 reference run"
    amr: "none"
    findings: "Azimuthal field self-converges toward the 2048^2 reference solution at second order (Fig. 4b)."
related_to: [standing-magnetosonic-wave-theta-pinch-cylinder, resistive-field-soak-cylindrical-material-interface]
headline_score: 4
---

## Physical problem
A standing fast-magnetosonic-wave test inside a cylindrical embedded boundary of radius a=1 cm
containing a magnetized plasma at rest (rho0=1 g/cm^3, P0=6 Ba uniform) threaded by a Freidberg
parallel-pinch equilibrium field: an azimuthal component Bphi(r) derived from a z-directed vector
potential A_z(r) (source eq. 68), and an axial component Bz(r) given directly (source eq. 69),
parameterized by alpha=Bphi(a)/Bz(a) with Bphi(a)=sqrt(pi)/a G and Bz(a)=sqrt(4*pi) G.

## What this test actually tests
Whether the scheme's MHD cut-cell embedded boundary (fixed-field Dirichlet enforcement at a rigid,
non-grid-conformal wall) correctly evolves a standing wave superposed on a non-uniform,
sheared-field (parallel-pinch) background, verified by self-convergence toward a very
high-resolution reference run (azimuthal-field-self-convergence).

## Qualitative behaviour
The azimuthal field profile is a smooth, monotonically-varying radial curve (Fig. 4a) that
converges visually toward the 2048^2 reference curve as resolution increases from 16^2 to 512^2.

## Validation notes
Fig. 4b shows the self-convergence order of the azimuthal field toward the 2048^2 reference
solution across resolutions 16^2 to 512^2, approaching the theoretical second order at the finer
levels. Unlike the theta-pinch sibling (7.2), no closed-form time-dependent analytic solution is
used for comparison here — the source uses a high-resolution numerical reference instead
(self-convergence, not exact-solution-compare), consistent with the non-uniform, non-Bessel
eigenmode structure of this sheared background.

## Notes
A direct check of eq. (69) at r=a (where the bracket reduces to 1) gives Bz(r=a) =
Bz_a/alpha = 2*sqrt(4*pi), not the separately-stated Bz(a)=sqrt(4*pi) -- an apparent internal
normalization inconsistency in the source (alpha=Bphi(a)/Bz(a)=0.5 from the stated boundary
values, but eq. 69's own r=a limit implies alpha=1). Recorded here verbatim rather than "corrected"
(no-fabrication discipline); flagged for the paper's authors/erratum or a future check against
their code before being relied on quantitatively. Likewise, differentiating eq. (68)'s A_z(r) as
printed gives Bphi(a) = Bphi(a)_input / 2 at r=a (a further apparent factor-of-2), also recorded
verbatim. The perturbation exciting the standing wave itself is a `needs-source` gap (see
`parameters.perturbation_form`). `b_field_convention: sqrt-4pi` follows the same convention as the
theta-pinch sibling test.
