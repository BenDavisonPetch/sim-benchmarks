"""speclib — shared machinery for the Numerical Test-Case Database scripts.

Single home for the pieces validate.py / reindex.py / verify_refs.py all need
(SPEC §8; IMPLEMENTATION_PLAN Stage 3 risk note: "split the parser into a shared
module"):

  * spec.md frontmatter + body parsing
  * registry loading (ids per kind + the machine-readable frontmatter aids)
  * the IC/geometry/BC expression checker (SPEC §4, docs/ic-expression-language.md)
  * canonical INDEX.tsv row + capability-flag derivation (SPEC §8.1/§8.2/§2.3)

Pure stdlib + PyYAML. Expressions are checked with Python's `ast` module — grammar,
allow-list, call arity, aux ordering, and the t-scope rule (SPEC §4 check 6) — not by
numeric grid evaluation, so numpy is NOT a dependency (SPEC §8.5). See
docs/working/SPEC_DEVIATIONS.md D-007.
"""

from __future__ import annotations

import ast
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

# ---------------------------------------------------------------------------
# Repo layout
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent

REGISTRY_KINDS = [
    "equations",
    "terms",
    "eos",
    "tabulated-eos",
    "bc-types",
    "coord-systems",
    "internal-boundary-kinds",
    "analysis-treatments",
    "geometry-stress",
    "procedures",
]

# INDEX.tsv columns — the filterable subset only (SPEC §8.1). Order is authoritative:
# reindex.py writes and validate.py regenerates through the SAME serializer below, so
# the two can never disagree on layout.
INDEX_COLUMNS = [
    "slug",
    "physics_signature",
    "terms",
    "dims",
    "analysis_treatments",
    "bc_types_present",
    "coupling",
    "multi_material",
    "time_dependent_bc",
    "has_internal_boundaries",
    "headline_score",
    "has_exact_solution",
]

# Faces of the domain box, per SPEC §3 domain_bc (z_* only in 3D).
BC_FACES = ["x_lo", "x_hi", "y_lo", "y_hi", "z_lo", "z_hi"]


# ---------------------------------------------------------------------------
# Frontmatter / spec parsing
# ---------------------------------------------------------------------------


@dataclass
class SpecDoc:
    """A parsed spec.md: YAML frontmatter + markdown body + raw slices."""

    path: Path
    frontmatter: dict
    body: str
    raw_frontmatter: str  # verbatim text between the two --- fences (for regex write-back)


def split_frontmatter(text: str) -> tuple[str, str]:
    """Return (frontmatter_text, body_text) for a `---`-fenced document.

    Raises ValueError if the leading `---\\n ... \\n---` block is absent.
    """
    if not text.startswith("---"):
        raise ValueError("missing leading '---' frontmatter fence")
    # Drop the first fence line, then split on the next line that is exactly '---'.
    rest = text[3:]
    if rest.startswith("\n"):
        rest = rest[1:]
    end = rest.find("\n---")
    if end == -1:
        raise ValueError("missing closing '---' frontmatter fence")
    fm_text = rest[:end]
    body = rest[end + 4 :]  # skip '\n---'
    if body.startswith("\n"):
        body = body[1:]
    return fm_text, body


def load_spec(path: Path) -> SpecDoc:
    """Parse a spec.md. Raises ValueError / yaml.YAMLError on malformed input."""
    text = path.read_text(encoding="utf-8")
    fm_text, body = split_frontmatter(text)
    fm = yaml.safe_load(fm_text)
    if not isinstance(fm, dict):
        raise ValueError("frontmatter did not parse to a mapping")
    return SpecDoc(path=path, frontmatter=fm, body=body, raw_frontmatter=fm_text)


def find_specs(repo_root: Path = REPO_ROOT) -> list[Path]:
    """All tests/*/spec.md, sorted by slug."""
    return sorted((repo_root / "tests").glob("*/spec.md"))


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------


@dataclass
class Registry:
    """Loaded controlled vocabulary (SPEC §7.1). `ids[kind]` is the set of valid ids."""

    ids: dict[str, set[str]] = field(default_factory=dict)
    # equation id -> requires_eos bool (SPEC §7.1 base semantics, validate check 8)
    requires_eos: dict[str, bool] = field(default_factory=dict)

    def has(self, kind: str, id_: str) -> bool:
        return id_ in self.ids.get(kind, set())


def load_registry(repo_root: Path = REPO_ROOT) -> Registry:
    """Glob registry/<kind>/*.md; ids are filename stems. Non-.md (.gitkeep) ignored
    (SPEC_DEVIATIONS D-005). Parses equation frontmatter for requires_eos."""
    reg = Registry()
    for kind in REGISTRY_KINDS:
        d = repo_root / "registry" / kind
        found: set[str] = set()
        if d.is_dir():
            for f in sorted(d.glob("*.md")):
                found.add(f.stem)
                if kind == "equations":
                    try:
                        fm_text, _ = split_frontmatter(f.read_text(encoding="utf-8"))
                        fm = yaml.safe_load(fm_text) or {}
                        reg.requires_eos[f.stem] = bool(fm.get("requires_eos", False))
                    except (ValueError, yaml.YAMLError):
                        reg.requires_eos[f.stem] = False
        reg.ids[kind] = found
    return reg


# ---------------------------------------------------------------------------
# Expression language (SPEC §4, docs/ic-expression-language.md)
# ---------------------------------------------------------------------------

# Coordinate variables — always available; meaningfulness depends on coord_system
# and dimension (doc §1). `t` is handled separately (only in domain_bc state).
COORD_VARS = {"x", "y", "z", "r", "phi", "theta"}
CONSTANTS = {"pi"}

# Function allow-list with arity (doc §2). None arity = variadic (>=1).
FUNCTIONS: dict[str, int | None] = {
    "sin": 1, "cos": 1, "tan": 1,
    "exp": 1, "log": 1, "sqrt": 1,
    "tanh": 1, "erf": 1, "abs": 1,
    "min": None, "max": None,
    "J0": 1, "J1": 1, "Jn": 2,
    "step": 3,
}

# Binary / unary operators permitted (SPEC §4: + - * / ** and unary minus).
_ALLOWED_BINOPS = (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow)
_ALLOWED_UNARYOPS = (ast.UAdd, ast.USub)


@dataclass
class ExprResult:
    errors: list[str] = field(default_factory=list)
    free_vars: set[str] = field(default_factory=set)  # variable Names referenced
    uses_t: bool = False


class _ExprWalker(ast.NodeVisitor):
    """Walks one expression AST, collecting allow-list violations and free variables."""

    def __init__(self, allowed_names: set[str]):
        self.allowed = allowed_names
        self.errors: list[str] = []
        self.free_vars: set[str] = set()

    def visit_Call(self, node: ast.Call):
        if not isinstance(node.func, ast.Name):
            self.errors.append("call target must be a plain function name")
            return
        fname = node.func.id
        if fname not in FUNCTIONS:
            self.errors.append(f"unknown function '{fname}' (not in allow-list, SPEC §4)")
            return
        if node.keywords:
            self.errors.append(f"function '{fname}' called with keyword arguments (not allowed)")
        arity = FUNCTIONS[fname]
        n = len(node.args)
        if arity is None:
            if n < 1:
                self.errors.append(f"function '{fname}' needs >=1 argument")
        elif n != arity:
            self.errors.append(f"function '{fname}' takes {arity} arg(s), got {n}")
        for a in node.args:
            self.visit(a)

    def visit_Name(self, node: ast.Name):
        name = node.id
        if name in FUNCTIONS:
            self.errors.append(f"function '{name}' used as a value")
            return
        self.free_vars.add(name)
        if name not in self.allowed:
            self.errors.append(f"unknown identifier '{name}'")

    def visit_BinOp(self, node: ast.BinOp):
        if not isinstance(node.op, _ALLOWED_BINOPS):
            self.errors.append(f"operator {type(node.op).__name__} not allowed")
        self.visit(node.left)
        self.visit(node.right)

    def visit_UnaryOp(self, node: ast.UnaryOp):
        if not isinstance(node.op, _ALLOWED_UNARYOPS):
            self.errors.append(f"unary operator {type(node.op).__name__} not allowed")
        self.visit(node.operand)

    def visit_Subscript(self, node: ast.Subscript):
        # Only list indexing on a Name by an integer constant, e.g. imf_B_nT[0].
        if not isinstance(node.value, ast.Name):
            self.errors.append("subscript base must be a list-valued identifier")
        idx = node.slice
        if isinstance(idx, ast.Index):  # Python < 3.9
            idx = idx.value
        if not (isinstance(idx, ast.Constant) and isinstance(idx.value, int)):
            self.errors.append("subscript index must be an integer constant")
        self.visit(node.value)

    def visit_Constant(self, node: ast.Constant):
        if isinstance(node.value, bool) or not isinstance(node.value, (int, float)):
            self.errors.append(f"literal {node.value!r} not allowed (numbers only)")

    # Reject everything not explicitly whitelisted above.
    def generic_visit(self, node: ast.AST):
        allowed_nodes = (
            ast.Expression, ast.Load, ast.Add, ast.Sub, ast.Mult, ast.Div,
            ast.Pow, ast.UAdd, ast.USub,
        )
        if isinstance(node, allowed_nodes):
            super().generic_visit(node)
            return
        self.errors.append(f"syntax element {type(node).__name__} not allowed in expressions")


def check_expr(expr: Any, allowed_names: set[str], allow_t: bool) -> ExprResult:
    """Validate one expression against the SPEC §4 grammar.

    `expr` may be a string (parsed) or a bare number (a constant, always valid).
    `allowed_names` = the identifiers legal here (coords, pi, in-scope aux, params).
    `allow_t` = whether `t` may appear (true only for domain_bc state, SPEC §4).
    """
    res = ExprResult()
    if isinstance(expr, bool):
        res.errors.append("boolean is not a valid expression value")
        return res
    if isinstance(expr, (int, float)):
        return res  # bare numeric constant
    if not isinstance(expr, str):
        res.errors.append(f"expression must be a string or number, got {type(expr).__name__}")
        return res
    try:
        tree = ast.parse(expr, mode="eval")
    except SyntaxError as e:
        res.errors.append(f"does not parse: {e.msg}")
        return res
    # `t` is always a recognised variable; whether it is *permitted* here is decided
    # below (doc §1), so it never surfaces as a bare "unknown identifier".
    scope = set(allowed_names) | COORD_VARS | CONSTANTS | {"t"}
    walker = _ExprWalker(scope)
    walker.visit(tree)
    res.errors = walker.errors
    res.free_vars = walker.free_vars
    res.uses_t = "t" in walker.free_vars
    # `t` outside an allowed context is a hard error (doc §1: steady fields never use t).
    if res.uses_t and not allow_t:
        res.errors.append("expression references 't' where a steady (time-independent) value is required")
    return res


# ---------------------------------------------------------------------------
# Capability derivation + INDEX serialization (SPEC §2.3, §8.1, §8.2)
# ---------------------------------------------------------------------------


def _materials(fm: dict) -> list[dict]:
    mats = (fm.get("physics") or {}).get("materials") or []
    return [m for m in mats if isinstance(m, dict)]


def compute_terms_present(fm: dict) -> set[str]:
    """Union of every material's declared terms (SPEC §2.3 term presence)."""
    terms: set[str] = set()
    for m in _materials(fm):
        for t in m.get("terms") or []:
            terms.add(t)
    return terms


def _domain_bc_uses_t(fm: dict) -> bool:
    """True iff any domain_bc face state expression references `t` (SPEC §2.3)."""
    all_names = _all_ic_names(fm)
    for face in (fm.get("domain_bc") or {}).values():
        if not isinstance(face, dict):
            continue
        state = face.get("state") or {}
        for expr in state.values():
            r = check_expr(expr, all_names, allow_t=True)
            if r.uses_t:
                return True
    return False


def compute_has_internal_boundaries(fm: dict) -> bool:
    """Structural derivation of the has_internal_boundaries capability (SPEC §2.3).

    True iff a material interface / internal boundary exists: an explicit
    physics.coupling (≠ none), any internal_boundaries entry, or >1 material (two
    materials must meet at an interface). See SPEC_DEVIATIONS D-008.
    """
    coupling = (fm.get("physics") or {}).get("coupling")
    if coupling and coupling != "none":
        return True
    if fm.get("internal_boundaries"):
        return True
    if len(_materials(fm)) > 1:
        return True
    return False


def compute_time_dependent_bc(fm: dict) -> bool:
    return _domain_bc_uses_t(fm)


def compute_capability_set(fm: dict) -> dict:
    """The identity-bearing capability set computed from the CANONICAL entry
    (SPEC §2.3, §6.3A guard). Used for the baseline-invariance check (validate 9)."""
    return {
        "terms_per_material": tuple(
            (m.get("name"), tuple(sorted(m.get("terms") or []))) for m in _materials(fm)
        ),
        "time_dependent_bc": compute_time_dependent_bc(fm),
        "has_internal_boundaries": compute_has_internal_boundaries(fm),
        "coupling": (fm.get("physics") or {}).get("coupling"),
        "n_materials": len(_materials(fm)),
    }


def headline_score(fm: dict) -> int:
    scores = [m.get("score") for m in (fm.get("validation_modes") or []) if isinstance(m, dict)]
    scores = [s for s in scores if isinstance(s, int)]
    return max(scores) if scores else 0


def physics_signature(fm: dict) -> str:
    """Canonical, deterministic physics signature for INDEX (SPEC §2.1 item 1).

    Per material: `base(term1|term2)` (terms sorted) with `/eostype` appended when an
    eos is present; materials sorted; joined by `+`; coupling appended as `@coupling`.
    Interchangeable-base collapsing (SPEC §2.4) is a dedup convention, not applied here
    (SPEC_DEVIATIONS D-009)."""
    parts = []
    for m in _materials(fm):
        base = m.get("base", "?")
        terms = sorted(m.get("terms") or [])
        s = base
        if terms:
            s += "(" + "|".join(terms) + ")"
        eos = m.get("eos")
        if isinstance(eos, dict) and eos.get("type"):
            s += "/" + str(eos["type"])
        parts.append(s)
    parts.sort()
    sig = "+".join(parts)
    coupling = (fm.get("physics") or {}).get("coupling")
    if coupling and coupling != "none":
        sig += "@" + str(coupling)
    return sig


def bc_types_present(fm: dict) -> set[str]:
    out: set[str] = set()
    for face in (fm.get("domain_bc") or {}).values():
        if isinstance(face, dict) and face.get("type"):
            out.add(face["type"])
    return out


def has_exact_solution(fm: dict) -> bool:
    """Entry-level flag for INDEX: true iff any mode has an exact solution
    (SPEC §3.1 is per-mode; INDEX carries one column — SPEC_DEVIATIONS D-010)."""
    return any(
        bool(m.get("has_exact_solution"))
        for m in (fm.get("validation_modes") or [])
        if isinstance(m, dict)
    )


def _join_set(s: set[str]) -> str:
    return "|".join(sorted(s))


def index_row(fm: dict) -> list[str]:
    """The INDEX.tsv cells for one entry, in INDEX_COLUMNS order."""
    dims = fm.get("dimension") or {}
    runnable = dims.get("runnable_in") or []
    return [
        str(fm.get("slug", "")),
        physics_signature(fm),
        _join_set(compute_terms_present(fm)),
        "|".join(str(d) for d in runnable),
        _join_set(set(fm.get("analysis_treatments") or [])),
        _join_set(bc_types_present(fm)),
        str((fm.get("physics") or {}).get("coupling") or "none"),
        _bool(len(_materials(fm)) > 1),
        _bool(compute_time_dependent_bc(fm)),
        _bool(compute_has_internal_boundaries(fm)),
        str(headline_score(fm)),
        _bool(has_exact_solution(fm)),
    ]


def _bool(b: bool) -> str:
    return "true" if b else "false"


def render_index(specs: list[SpecDoc]) -> str:
    """The full INDEX.tsv text (header + one sorted row per entry). Single serializer
    shared by reindex.py (write) and validate.py (regenerate-and-diff)."""
    lines = ["\t".join(INDEX_COLUMNS)]
    rows = [index_row(s.frontmatter) for s in specs]
    rows.sort(key=lambda r: r[0])  # by slug
    for r in rows:
        lines.append("\t".join(r))
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Expression scope helpers
# ---------------------------------------------------------------------------


def _param_names(fm: dict) -> set[str]:
    return {p.get("name") for p in (fm.get("parameters") or []) if isinstance(p, dict) and p.get("name")}


def _aux_names(fm: dict) -> list[str]:
    ic = fm.get("initial_conditions") or {}
    return [a.get("name") for a in (ic.get("aux") or []) if isinstance(a, dict) and a.get("name")]


def _all_ic_names(fm: dict) -> set[str]:
    """Names available to non-aux expressions: params + all aux (+ coords/pi added by
    the checker). Used for equilibrium / perturbation / material_fields / BC state."""
    return _param_names(fm) | set(_aux_names(fm))
