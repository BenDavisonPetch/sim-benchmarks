#!/usr/bin/env python3
"""cite_chain.py — chase an attribution one hop back through a citing work (SPEC §5.4, §8.6).

When a using-ref says "the test of [X]", `/add-refs` must find X's identifier rather than
guess it. This greps the *citing* work's publisher-deposited Crossref reference list:

    python3 scripts/cite_chain.py --citing <doi> --match <substring>

Prints `DOI | first-author | year | article-title | journal` per matching reference. Rows
the publisher deposited only as free text (no structured DOI) are flagged
`(no DOI deposited)` — still useful, since the printed string is enough to verify by hand.

Exit 1 on zero matches. Not every work deposits a reference list (books typically deposit
none, e.g. 10.1007/b79761 -> 0); that is reported explicitly rather than as "no match", so
the caller knows to fall back to WebSearch instead of concluding the citation is absent.

Crossref access is imported from verify_refs.py — one HTTP path, one polite-pool UA.
No fuzzy matching: a plain case-insensitive substring test, so the output is auditable.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import verify_refs as V


def _row(ref: dict) -> tuple[str, str]:
    """Render one Crossref-deposited reference row; returns (haystack, printable)."""
    doi = ref.get("DOI")
    author = ref.get("author") or ""
    year = ref.get("year") or ""
    title = ref.get("article-title") or ref.get("volume-title") or ""
    journal = ref.get("journal-title") or ""
    unstructured = ref.get("unstructured") or ""

    if not (author or title or journal) and unstructured:
        printable = f"{doi or '(no DOI deposited)'} | {unstructured}"
    else:
        printable = " | ".join([doi or "(no DOI deposited)", str(author), str(year),
                                str(title), str(journal)])
    haystack = " ".join(str(x) for x in (doi, author, year, title, journal, unstructured) if x)
    return haystack.lower(), printable


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Grep a citing work's deposited reference list.")
    ap.add_argument("--citing", required=True, metavar="DOI",
                    help="DOI of the work that states the attribution")
    ap.add_argument("--match", required=True, metavar="SUBSTRING",
                    help="case-insensitive substring (author surname, title fragment, year)")
    args = ap.parse_args(argv)

    try:
        msg = V.crossref_work(args.citing)
    except V._Unreachable as e:
        print(f"ERROR crossref unreachable for {args.citing}: {e}")
        return 2
    if msg is None:
        print(f"ERROR {args.citing} not found on Crossref")
        return 2

    refs = msg.get("reference") or []
    if not refs:
        print(f"no reference list deposited by publisher for {args.citing} "
              f"— chase this attribution by hand (WebSearch / the paper's own bibliography)")
        return 1

    needle = args.match.lower()
    hits = [printable for haystack, printable in (_row(r) for r in refs) if needle in haystack]
    for h in hits:
        print(h)
    if not hits:
        # Some publishers (AGU/Wiley among them) deposit rows as a bare DOI with no author or
        # title, so a surname grep cannot see a citation that is genuinely there.
        bare = sum(1 for r in refs if r.get("DOI") and not (r.get("author") or r.get("article-title")
                                                            or r.get("unstructured")))
        print(f"no match for {args.match!r} among {len(refs)} deposited reference(s) of {args.citing}")
        if bare:
            print(f"note: {bare}/{len(refs)} rows are DOI-only (no author/title deposited), so a "
                  f"surname/title match cannot see them — match on a DOI fragment instead, or "
                  f"resolve a candidate with `verify_refs.py --lookup <doi>`")
        return 1
    print(f"\n{len(hits)} match(es) of {len(refs)} deposited reference(s).")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    sys.exit(main())
