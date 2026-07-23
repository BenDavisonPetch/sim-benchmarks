# procedures.md — norm / convergence / seed-procedure formula definitions

The norms, convergence-order formulae, and every seed validation procedure, **defined once**
(SPEC §6.2). `registry/procedures/<id>.md` files and `validation_modes` reference these definitions
by name and never re-derive them. Each seed procedure named in SPEC §6.1 has its formula stub here.

Notation: discrete fields live on cells `i` with cell volume `V_i`. On embedded / cut-cell
geometry each cell carries an **active volume fraction** `f_i ∈ [0,1]` (`f_i = 1` for a full
interior cell, `0` for a fully excluded cell). Define the cell weight `w_i = f_i · V_i`. An error
field is `e_i = u_i − u*_i` (numeric minus reference) for the variable under test.

---

## 1. Norms (procedure `norms`)

**Volume-weighted** discrete norms over active cells (`w_i > 0`):

```
L1   = ( Σ_i w_i |e_i| )      / ( Σ_i w_i )
L2   = sqrt( ( Σ_i w_i e_i^2 ) / ( Σ_i w_i ) )
Linf = max_i |e_i|                          (over active cells, f_i > 0)
```

On uniform Cartesian grids `w_i = V_i` is constant and these reduce to the usual normalized
discrete norms. On embedded/cut-cell geometry the active volume fraction `f_i` is the weight
(SPEC §6.1). Norms are computed **per variable** unless a mode states a combined norm.

- **applies_to:** any mode measuring an error field against a reference.
- **inputs (slots):** variables, reference (exact or reference-result), norm choice(s).
- **output form:** one scalar per (variable, norm).
- **pass-criterion:** value below the mode's stated tolerance.

---

## 2. Convergence order (procedure `convergence-order`)

Given errors `E(h)` at grid spacings `h` with refinement ratio `r = h_coarse / h_fine`:

**Pairwise order**

```
p = log( E_coarse / E_fine ) / log( r )
```

**Least-squares order** — fit a line to `(log h, log E)`; the slope is the observed order `p`.

- **applies_to:** methods with a known theoretical order and a refinable error measure.
- **inputs (slots):** error measure (usually a `norms` output), resolution sequence, `r`,
  expected order.
- **output form:** `p` (pairwise per pair, and/or LSQ slope) with the resolution sequence.
- **pass-criterion:** `p` within tolerance of the theoretical order.

---

## 3. Exact-solution compare (procedure `exact-solution-compare`)

Sample the exact/analytic solution at cell **centroids**; form `e_i = u_i − u*_i` and reduce with
the `norms` definitions (§1) per variable.

- **applies_to:** problems with an exact or analytic solution.
- **inputs (slots):** exact solution reference, sample time(s), variables, norm choice(s),
  tolerance.
- **output form:** `norm(numeric − exact)` per variable.
- **pass-criterion:** norms below tolerance; combined with `convergence-order` this is the route to
  a score of 5 (`scoring-rubric.md`).

---

## 4. Self-convergence (procedure `self-convergence`)

No exact solution: use a high-resolution run as the reference and measure Richardson-style
convergence of successively refined runs toward it. The refinement ratio `r` between levels is
**stated explicitly**; the order estimate uses the `convergence-order` formulae (§2) with the
high-resolution run in place of the exact solution.

- **applies_to:** canonical problems with no closed form.
- **inputs (slots):** resolution sequence, high-resolution reference level, `r`, variables,
  tolerance/expected order.
- **output form:** self-convergence order per variable.
- **pass-criterion:** order within tolerance of the expected value.

---

## 5. Rankine–Hugoniot jump (procedure `rankine-hugoniot-jump`)

Measure pre- and post-shock states and compare against the analytic jump conditions (mass,
momentum, energy — and, for MHD, the magnetic jump relations) for the measured shock speed, within
tolerance.

- **applies_to:** problems with well-defined shocks whose jump conditions are analytic.
- **inputs (slots):** shock identity, pre/post sampling locations or method, variables, tolerance.
- **output form:** measured jumps vs analytic jumps per conserved quantity.
- **pass-criterion:** each jump within tolerance.

---

## 6. Feature location (procedure `feature-location`)

Locate named features (shocks, contacts, rarefaction heads, standoff surfaces, X-lines) along
stated cut-lines at stated times, and compare positions against a reference (exact, canonical, or a
`reference_result`) within a positional tolerance (e.g. "positions within 2 cells").

- **applies_to:** problems with named, locatable features.
- **inputs (slots):** sample time(s) (≤ `t_final`), variables, cut_lines, features, reference,
  tolerance.
- **output form:** measured position per named feature.
- **pass-criterion:** each position within tolerance of the reference.

---

## 7. Well-balancing (procedure `well-balancing`)

Initialize the `equilibrium` state, evolve, and require the deviation norm from the initial
equilibrium to stay below tolerance (the scheme must preserve the equilibrium). Optionally add the
`perturbation` and check **perturbation preservation** — that a small perturbation on the
equilibrium is transported/maintained correctly rather than swamped by discrete equilibrium error.

- **applies_to:** problems with a nontrivial `equilibrium` (SPEC §4 split).
- **inputs (slots):** equilibrium reference (the IC), evolve time, variables, deviation tolerance;
  optional perturbation-preservation check.
- **output form:** deviation norm(s) vs time (§1 norms of `u(t) − u_equilibrium`).
- **pass-criterion:** deviation below tolerance (well-balanced); perturbation preserved within
  tolerance.

---

## 8. Conservation drift (procedure `conservation-drift`) — universal diagnostic (SPEC §6.4)

Track a globally conserved quantity `Q` (total mass, momentum, energy, or a stated flux balance)
versus time; the drift is

```
drift(t) = | Q(t) − Q(0) |        (absolute)
         = | Q(t) − Q(0) | / |Q(0)|   (relative, when Q(0) ≠ 0)
```

- **applies_to:** any conservative system; **scored** only when genuinely discriminating for the
  problem (SPEC §6.4), else recorded unscored.
- **inputs (slots):** conserved quantity, evolve time, drift form, tolerance/criterion.
- **output form:** drift vs time.
- **pass-criterion:** drift below the stated criterion.

---

## 9. Div-B (procedure `div-b`) — universal diagnostic (SPEC §6.4)

Compute a norm of `∇·B` (per §1, over the domain) and compare against a criterion. As a universal
diagnostic it is **scored** only when the entry asserts why controlling `∇·B` is specifically
challenging for that problem; otherwise it is an unscored provenance metric.

- **applies_to:** MHD problems.
- **inputs (slots):** norm choice, sample time(s), criterion.
- **output form:** `norm(∇·B)` (per §1).
- **pass-criterion:** below the stated criterion.
