---
# Copy-and-fill scaffold for a NEW registry vocabulary id (SPEC §7.1/§7.2).
# One markdown file per id at registry/<kind>/<id>.md. id MUST equal the filename (conventions §4).
# Added ONLY via the hard-stop-and-propose flow (§7.2) — never invented silently inside an entry.
# Delete every comment line before committing the filled file.
id: <kebab-case-id>                 # == filename, kebab-case, physical descriptor only (never a method)
human_name: "<Human Readable Name>"
kind: <equation|term|eos|bc-type|coord-system|internal-boundary|analysis-treatment|geometry-stress
#      |wall-pressure-treatment>
# --- kind-specific frontmatter (keep only what applies; mirror a sibling file in the same dir) ---
# equations:            phase: <fluid|solid>, requires_eos: <true|false>, velocity: <evolved|fixed-zero>,
#                       evolves: [<...>], interchangeable_with: [<ids>], interchangeable_when: "<predicate|null>"
# terms:                param_bearing: <true|false>, coefficient: <name>, applies_to: [<equation ids>]
# eos:                  params: [<param names>]
# bc-types:             requires_state: <true|false|optional>, physical: true,
#                       state_keys: [<allowed state keys>]   # composite bc-types only; check 2
# wall-pressure-treatment: (no extra keys)   # what a REFERENCE did at a conducting wall (§5.3)
# coord-systems:        variables: [<...>], axis_singularity: <true|false>
# internal-boundary:    physical: true            # PHYSICAL couplings ONLY, never a numerical method
# analysis-treatment:   (no extra keys)
# geometry-stress:      (searchable tag; §2.3 exception)
---
## Definition
<What this id means physically. For internal-boundary/bc-types: state it as a PHYSICAL condition,
never a numerical treatment (no ghost-fluid / cut-cell / grid). Cite the SPEC section it encodes.>

## Params schema
<Parameters this id carries (name, meaning, units-as-authored). "None." if none. Note where values
may be expressions (§4) vs scalars, and any needs-source discipline (§5.2).>

## Notes
<Identity implications (does it fork? §2.1/§2.3), distinctions from sibling ids, interchangeability
predicates, gotchas.>

## Refs
(none)
