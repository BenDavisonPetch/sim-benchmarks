---
id: magnetostatics
human_name: "Magnetostatics (linear, non-conducting magnetic material)"
phase: solid
requires_eos: false
velocity: fixed-zero            # v ≡ 0
evolves: []                     # elliptic/instantaneous: B is not time-integrated (see Definition)
interchangeable_with: []
interchangeable_when: null
---
## Definition
Non-conducting, linearly magnetizable body carrying no free current: `∇×H = 0` (so `H = -∇Ψ`),
`∇·B = 0`, and the linear constitutive law `B = μH` (permeability `μ`; `μ = μ0` recovers free
space). Unlike `magnetic-diffusion`, `B` is **not** independently time-integrated and the material
carries no memory of its own: it satisfies the elliptic (Laplace) potential equation
instantaneously for whatever boundary / interface data holds at that instant. Any time dependence
of the field in such a region is inherited entirely from its driving boundary conditions and from
the adjoining evolved bodies (e.g. a `magnetic-diffusion` conductor) it couples to. A different
*phase of matter* from the fluid bases `hydro` / `mhd`.

## Params schema
None intrinsic. Permeability `μ` enters as this material's coefficient via a `material_fields`
entry (scalar per region, or a spatial expression, SPEC §4). No EoS (`requires_eos: false`).

## Notes
Used for insulating magnetic bodies — a permeable core, the surrounding free space — that flank a
conducting `magnetic-diffusion` region across an `electromagnetic-coupling` interface (field
continuity). Two insulating regions that differ only in `μ` and share this base remain **separate**
materials whenever a genuine physical body (e.g. a conducting shell) sits between them; where no
such body intervenes, merge them into one material with a spatial `μ(r)` (minimal-material
canonicalization, §2.4 / `triage.md` A2.5).

## Refs
(none)
