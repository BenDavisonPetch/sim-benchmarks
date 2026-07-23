#!/usr/bin/env python3
"""reindex.py — regenerate INDEX.tsv from all spec.md (SPEC §8.2).

INDEX.tsv is a pure derived artifact and is never hand-edited (SPEC §11.4). This
recomputes every row — physics_signature, capability flags, and headline_score — from
the canonical set of each entry (SPEC §2.3) and writes INDEX.tsv.

It also writes the recomputed `headline_score` back into each spec.md via a single-line,
comment-preserving edit of the frontmatter (SPEC §8.2: headline_score "set by
reindex.py"). It does NOT rewrite the rest of the frontmatter — a full YAML round-trip
would destroy authored inline comments (SPEC_DEVIATIONS D-011).

    python3 scripts/reindex.py [--check]

`--check` prints what would change and exits non-zero if anything is stale, without
writing (useful in CI alongside validate.py).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import speclib as S

_HEADLINE_RE = re.compile(r"^(headline_score:)([^\n#]*)(.*)$", re.MULTILINE)


def _rewrite_headline(doc: S.SpecDoc, new_value: int) -> bool:
    """Replace the `headline_score:` value in the frontmatter in place, preserving any
    trailing comment. Returns True if the file changed."""
    text = doc.path.read_text(encoding="utf-8")
    fm_text, _ = S.split_frontmatter(text)

    def repl(m: re.Match) -> str:
        return f"{m.group(1)} {new_value}{m.group(3)}"

    new_fm, n = _HEADLINE_RE.subn(repl, fm_text, count=1)
    if n == 0:
        return False  # missing field — validate.py check 1 will flag it
    if new_fm == fm_text:
        return False
    new_text = text.replace(fm_text, new_fm, 1)
    doc.path.write_text(new_text, encoding="utf-8")
    return True


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Regenerate INDEX.tsv (SPEC §8.2).")
    ap.add_argument("--check", action="store_true",
                    help="report staleness and exit non-zero without writing")
    args = ap.parse_args(argv)

    specs: list[S.SpecDoc] = []
    for path in S.find_specs():
        try:
            specs.append(S.load_spec(path))
        except Exception as e:
            print(f"ERROR {path.relative_to(S.REPO_ROOT)}: failed to parse: {e}", file=sys.stderr)
            return 1

    expected = S.render_index(specs)
    index_path = S.REPO_ROOT / "INDEX.tsv"

    stale: list[str] = []
    if not index_path.exists() or index_path.read_text(encoding="utf-8") != expected:
        stale.append("INDEX.tsv")

    # headline_score write-back (or check)
    for doc in specs:
        computed = S.headline_score(doc.frontmatter)
        declared = doc.frontmatter.get("headline_score")
        rel = str(doc.path.relative_to(S.REPO_ROOT))
        if declared != computed:
            if args.check:
                stale.append(f"{rel} (headline_score {declared} -> {computed})")
            else:
                if _rewrite_headline(doc, computed):
                    print(f"updated headline_score in {rel}: {declared} -> {computed}")

    if args.check:
        if stale:
            print("STALE:")
            for s in stale:
                print(f"  {s}")
            print("run scripts/reindex.py to regenerate")
            return 1
        print("INDEX.tsv and headline scores are up to date.")
        return 0

    index_path.write_text(expected, encoding="utf-8")
    print(f"wrote {index_path.relative_to(S.REPO_ROOT)} ({len(specs)} entr{'y' if len(specs)==1 else 'ies'}).")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    sys.exit(main())
