#!/usr/bin/env python3
"""new_test.py — scaffold a new test entry (SPEC §8.5).

Creates tests/<slug>/ from templates/spec.template.md plus an empty assets/ dir. Refuses
to overwrite an existing entry. Substitutes the slug into the template's `slug:` line so
the copy already satisfies the slug == directory-name rule (spec-schema §1.1).

    python3 scripts/new_test.py <slug>
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import speclib as S

_SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Scaffold tests/<slug>/ (SPEC §8.5).")
    ap.add_argument("slug", help="kebab-case slug (conventions.md §3)")
    args = ap.parse_args(argv)

    slug = args.slug
    if not _SLUG_RE.match(slug):
        print(f"ERROR: '{slug}' is not a valid kebab-case slug (conventions.md §3)", file=sys.stderr)
        return 1

    template = S.REPO_ROOT / "templates" / "spec.template.md"
    if not template.exists():
        print(f"ERROR: missing {template.relative_to(S.REPO_ROOT)}", file=sys.stderr)
        return 1

    test_dir = S.REPO_ROOT / "tests" / slug
    if test_dir.exists():
        print(f"ERROR: {test_dir.relative_to(S.REPO_ROOT)} already exists", file=sys.stderr)
        return 1

    text = template.read_text(encoding="utf-8")
    # Fill the slug so the scaffold matches its directory (spec-schema §1.1).
    text = re.sub(r"^slug:.*$", f"slug: {slug}", text, count=1, flags=re.MULTILINE)

    (test_dir / "assets").mkdir(parents=True)
    (test_dir / "assets" / ".gitkeep").write_text("", encoding="utf-8")
    (test_dir / "spec.md").write_text(text, encoding="utf-8")

    print(f"scaffolded {test_dir.relative_to(S.REPO_ROOT)}/ (spec.md + assets/)")
    print("next: fill spec.md from the template, then run reindex.py + validate.py")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    sys.exit(main())
