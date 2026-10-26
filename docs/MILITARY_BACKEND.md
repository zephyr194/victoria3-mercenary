# Military adapter: release blocker

## Required capabilities

The shipping backend-ready trigger returns **no**. Do not flip it to yes to make the button clickable: the live button intentionally has no purchase effect, and the accounting branches alone do not deliver troops.

A future backend must implement a single atomic contract operation covering:

1. Validate eligibility, origin supply, manpower, legal equipment, affordability and the national cap.
2. Reserve the finite offer and allocate a persistent identity to its units.
3. Create a deployable formation with exactly the advertised military backing; debit only after successful delivery, or roll back both sides.
4. Distinguish contract troops from ordinary troops even after formation merges, splitting, upgrades, state conquest, revolutions and save/load.
5. Replenish from a defined manpower pool; do not advertise foreign manpower while recruiting employer pops.
6. Prevent replacements after withdrawal starts. Determine whether release is safe during battles, movement and naval invasion.
7. Remove only contract-owned units/backing, retain casualties/debt and return surviving manpower to an exhausted/resting market offer exactly once.
8. Separate demo and live financial records. Demo funds must never settle real debt; demo credit must not affect live credit.
9. Freeze a live base-cost quote excluding the surcharge; avoid paying for vanilla payroll twice. Current fixed £400 reference is for the demo only.
10. Pass the full matrix separately for the actual installed builds of 1.13 and 1.14.

## Evidence and limitations

Generated 1.13.11 and 1.14.5-openbeta effects document `create_military_formation` with `combat_unit`, `service_type`, `state_region`, `count`. This proves a creation syntax exists, not which backing building is allocated or that it can be reversed safely.

`transfer_to_formation` supports **character**, not combat-unit scope. It is not an API for lending an army.

`add_modifier` does not list military-formation or combat-unit scopes in these snapshots. Never apply a country-wide offense modifier and describe it as an individual mercenary bonus.

`remove_building` removes the specified building type in a state. It cannot by itself identify contract-owned levels of a vanilla barracks. `destroy_container` only destroys script containers, not formations.

No dedicated unit/formation destruction effect was identified in the checked snapshots. This does not prove that no safe workaround exists. A custom military building, custom recruitment backend or provider-country model needs proof from game files and a running game first.

## Next investigation using an installed game

- Inspect `common/buildings`, `common/building_groups`, `common/combat_unit_types`, relevant production methods and army recruitment GUI.
- Generate `script_docs` in debug mode for the precise installed build; rerun the interface audit.
- In a disposable save create a one-unit contract beside ordinary units, then split/merge and release it. Compare regular army, population and payroll before/after.
- Test backing-building removal during combat before implementing any automatic cleanup.

No destructive probe is shipped in the default mod. No vanilla files are copied into this repository.
