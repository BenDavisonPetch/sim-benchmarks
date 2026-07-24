# refs-enrichment worksheet (SPEC §5.3–§5.5) — one pass PER ref; a FILL-AID, not a scaffold

Run once per reference being enriched. Transcribe answers into `reference_results[]` /
`references[]` / `references_unverified[]` and the `original_intro` flags inside the single `spec.md`
(§11.9). Discard after. Authorities: SPEC §5, docs/spec-schema.md.

NEVER fabricate a citation. A DOI read off a PDF is a CLAIM, not a verification (§5.2). Verification is
verify_refs.py's job (online), or a pending_verification.md hand-off (offline).

---

## Per-ref fill

- [ ] `key` (citekey) → ____   (must be a references[] key; offline may resolve to
      references_unverified[] — §5.3 / check 7 / D-016. Never invent a key.)
- [ ] verified? → yes (references[]) / no (references_unverified[], offline)
- [ ] `params_used` — structural params, values AS THE REF USED THEM → { }
- [ ] `method` — numerical method, PROVENANCE ONLY (never in the problem block, §1.6) → "____"
- [ ] `resolution` → "____"
- [ ] `amr` → "____" or "none"
- [ ] `findings` — SPECIFIC, quantitative where reported; numbers VERBATIM WITH UNITS (§11.10)
      (orders, jump sizes, growth rates, resolution thresholds, timings). Do not round or paraphrase.
      → >
- [ ] `figure_asset` (O) — assets/<file>; cite + describe reproduction → ____

## original_intro (§5.4 — by RULE, never guessed)

- [ ] Among VERIFIED refs using this test, earliest publication → `original_intro: true`
      UNLESS this ref states it took the test from elsewhere → follow that attribution.
- [ ] Every other using ref → `original_intro: false`.
- [ ] Cannot order by date (e.g. all unverified offline) → leave `unknown` + note. NEVER guess.
      → this ref: true / false / unknown

## Verification path (§5.2)

- [ ] ONLINE → run `.venv/bin/python scripts/verify_refs.py`; on success move
      references_unverified[] -> references[], stamp verification {status: verified, source, checked}.
      A verified ref with no resolvable identifier HARD-FAILS — fix, never fake.
- [ ] OFFLINE → keep as `status: unverified` with the identifier extracted VERBATIM (a claim); add a
      row to pending_verification.md (top-level template). Emit ZERO `verified` entries.

## pending_extraction.md rows (§5.5) — only if the file exists

- [ ] For each needs-source row whose defining ref you can ACTUALLY retrieve: read the value, write it
      into the named spec.md field, set `source_ref: <citekey>`, remove the row.
- [ ] Unretrievable ⇒ stays `needs-source`. NEVER type from memory. Leave its row.
- [ ] Convention checks (b-field convention, unit system) answered only from a retrieved source.
- [ ] Delete pending_extraction.md only when EVERY row is resolved.

---

## Prose (§11.6 spirit)
- [ ] `## Validation notes` ties ref findings to the entry's modes with SPECIFIC numbers + units.
- [ ] NEVER "compares with literature" (or any vague equivalent).

## Pre-transcribe checklist
- [ ] Zero fabricated citations / identifiers (§5.2, §11.5).
- [ ] Every number verbatim with units (§11.10).
- [ ] original_intro set by the §5.4 rule or left unknown-with-note.
- [ ] method/resolution/amr only in reference_results, never the problem block (§1.6 / check 7).
- [ ] Then: `reindex.py` + `validate.py` (`--offline` if offline).
