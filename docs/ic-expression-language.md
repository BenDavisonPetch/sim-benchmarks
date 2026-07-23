# ic-expression-language.md — IC / geometry / BC expression grammar

The expression language used in `initial_conditions` (aux, equilibrium, perturbation, potentials),
`material_fields`, term coefficients, and `domain_bc[*].state` (SPEC §4). Documented once here;
parsed, aux-resolved, and allow-list-checked by `scripts/validate.py` (check 6). **Every expression
must be numpy-evaluable on a coordinate grid.**

---

## 1. Variables

Coordinate variables are **coordinate-system aware** (the entry's `geometry.coord_system`):

- `x, y, z` — Cartesian coordinates.
- `r, phi, theta` — radial / azimuthal / polar coordinates.
- `t` — time.

`t` appears **only** in `domain_bc[*].state` expressions and any explicitly time-dependent field.
A steady problem never references `t`. Any `domain_bc` face-state that references `t` forces
`capability_flags.time_dependent_bc = true` (SPEC §2.3; `validate.py` check 6 enforces the
biconditional). Referencing `t` anywhere a steady field is expected is a validation error.

All coordinate variables listed are always available; which are *meaningful* depends on
`coord_system` and problem `dimension`. Evaluation broadcasts over the grid.

---

## 2. Function allow-list

The **only** callable names (SPEC §4). `validate.py` rejects any other identifier used as a call.

| Name | Meaning |
|---|---|
| `sin, cos, tan` | trigonometric |
| `exp, log` | exponential / natural log |
| `sqrt` | square root |
| `tanh` | hyperbolic tangent |
| `erf` | error function |
| `abs` | absolute value |
| `min, max` | element-wise/reducing min, max |
| `J0, J1` | Bessel functions of the first kind, order 0 and 1 |
| `Jn(n, ·)` | Bessel function of the first kind, order `n` |
| `step(t, a, b)` | transition helper (§2.1) |
| `dipole(mx,my,mz, cx,cy,cz)` | point-dipole **B** field builtin (§2.2) |

Plus the constant `pi` and standard arithmetic operators `+ - * / **`, parentheses, unary minus,
and numeric literals (including scientific notation, e.g. `1e-5`). List indexing on a
list-valued aux/parameter (e.g. `imf_B_nT[0]`) is permitted.

### 2.1 `step(t, a, b)` — definition

`step` is a clamped linear ramp from `0` to `1` as `t` goes from `a` to `b`:

```
step(t, a, b) = clip( (t - a) / (b - a), 0, 1 )
              = 0            for t <= a
                (t-a)/(b-a)  for a < t < b
                1            for t >= b
```

Degenerate `a == b` gives a Heaviside step at `t = a` (`0` for `t < a`, `1` for `t >= a`).
`step` is the canonical way to author a driven BC: a jump is `step` with `a == b`, a ramp is
`a < b`, and any smooth `f(t)` composes from `step` and the allowed functions. This is why
step-vs-ramp-vs-sinusoid do **not** fork identity — the BC-state expression is a value, not a
capability (SPEC §2.3).

### 2.2 `dipole(mx, my, mz, cx, cy, cz)` — field builtin

A **vector-valued** field builtin: the magnetostatic field of a point dipole with moment vector
`(mx, my, mz)` located at center `(cx, cy, cz)`, evaluated at the coordinate point. Its result is a
vector, so it is assigned to the **vector** field name `B` (not to scalar components `Bx/By/Bz`):

```yaml
equilibrium:
  - region: interior
    fields:
      B: "dipole(0, 0, m_z, 0, 0, 0.2)"     # axial dipole, moment +z, center offset +0.2 north
```

All six arguments are **positional scalar expressions** — no keyword arguments, no list literals
(both outside this grammar). The dipole *strength* is authored **inline** from whatever the source
states (e.g. a surface equatorial field via `m = B_eq R^3 / (mu0/4pi)`); it is **not** a
precomputed number and **not** a problem-specific helper builtin. The field convention (the `mu0`
factor / Gaussian vs SI) follows the entry's `units` (SPEC §12, units-as-authored); `validate.py`
checks the expression structurally (AST), not its numeric value (SPEC_DEVIATIONS D-007).

---

## 3. Aux bindings

`initial_conditions.aux` is an **ordered** list of `{name, expr, units?}`, evaluated **top-down**.
A later expression may reference any earlier aux name; forward references are a validation error.

```yaml
aux:
  - { name: K,   expr: "<complex>" }
  - { name: rho, expr: "exp(-K)" }     # may use K, defined above
  - { name: p,   expr: "K" }
```

Aux names are then usable in equilibrium, perturbation, potential, material-coefficient, and BC
expressions. `validate.py` resolves the whole aux chain and every downstream expression against it.

---

## 4. Material coefficients

Term parameters and `material_fields` entries accept **expressions** in position + aux variables,
exactly like ICs — not only scalars. This enables e.g. a spatially-varying resistivity field
`eta(r)`:

```yaml
material_fields:
  - name: eta
    region: interior
    expr: "eta_mantle + (eta_core - eta_mantle) * (1 - r) / (1 - 0.8)"
    units: "ohm*m"
```

Note (SPEC §2.3): a coefficient that is nonzero *anywhere* in the domain counts the term as
**present**, even if it is zero in part of the domain. A spatial coefficient does not change that
binary.

---

## 5. Equilibrium + perturbation split

ICs split into `equilibrium` (the base state, possibly trivial) and `perturbation` (added on top),
combined by `combine_rule` ∈ `additive | replace`. The split enables the `well-balancing`
validation procedure (init equilibrium → evolve → deviation norm) and perturbation-on-equilibrium
tests. Structurally, the split is part of entry identity (SPEC §2.1 item 3), compared modulo
numeric values.

---

## 6. Potentials

An author may define a potential (e.g. `A_z`) with a stated `derives` rule:

```yaml
potentials:
  - { name: A_z, expr: "...", derives: "B = curl(A)" }
```

The derivation rule is a **physical** statement (how the field is obtained from the potential), not
a numerical method. `validate.py` parses the potential's `expr`; the `derives` rule is recorded
verbatim.

---

## 7. Evaluation contract (what `validate.py` guarantees)

1. Every expression parses under this grammar.
2. Only allow-listed function names and permitted variables appear.
3. The aux chain resolves top-down with no forward references.
4. Every expression is numpy-evaluable on a coordinate grid of the entry's dimension.
5. The `t` ⇔ `time_dependent_bc` biconditional holds.

---

## 8. Allow-list extension protocol

The function allow-list is **extensible, but only by a logged change** (SPEC §4). To add a
function or builtin (e.g. a `dipole` field builtin):

1. Add the name + its definition/signature to §2 of **this file**.
2. Add it to the allow-list in `scripts/validate.py` with its numpy implementation.
3. Log the change in `docs/working/SPEC_DEVIATIONS.md` (it is a filled gap / elaboration).

Both edits land in the **same commit**. Never extend the allow-list in `validate.py` without the
matching entry here, and never reference a name in a spec before it is allow-listed. (The worked
example's `dipole` builtin was exactly such an extension, landed in Stage 4 — see §2.2 above and
SPEC_DEVIATIONS D-015.)
