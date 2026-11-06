# Custodes native stratagem integration — 13 detachment coverage

## Expansion completed on test branch (2026-11-06)

The file `Custodes Native Stratagems.json` now contains **42 catalogue-derived stratagems across all 13 Custodes detachments**, including six Shield Hosts and seven Unit Detachments. A GitHub Actions job generated and validated all 42 directly from the current `Imperium - Adeptus Custodes.json`, without editing Custodes unit profiles, detachment rules, points, or enhancements.

Counts: Aquilan Shield 3; Dread Host 3; Emissaries Imperatus 3; Emperor's Chosen 3; Shadow Keepers 3; Solar Watch 3; Null Maiden Vigil 3; Auric Champions 3; Lions of the Emperor 3; Might of the Moritoi 3; Guardians of the Throne 6; Honoured Companions 3; Grav-Assault Force 3.

The generated file is a valid JSON catalogue-wrapped Book 105 with `data.stratagems`, `data.custom["Imperium - Adeptus Custodes"]`, and optional adapter fields. The same three Aquilan Shield records from the earlier visual test are present. Generation verified all expected CP/WHEN/TARGET/EFFECT fields, stable source ids, unique name-detachment pairs, and two specifically modified stratagems (Tip of the Talon and Golden Light of the Moiraides).

**Validation scope:** Generation and structural checks succeeded. Previous live New Recruit 37.14 verification established native-card behavior for Aquilan Shield's three stratagems, but the full set of 42 has not yet been visually tested in the live app.

**Important production safeguard:** This branch's Book 105 currently replaces the standard stratagem book with Custodes-only entries. It does **not** preserve core stratagems or unrelated factions' native stratagems. Therefore do not merge this file into `main` until the existing base Book 105 data can be retained and the combined book retested.

## How to test

Import `Reedddragon/WHCUSTOM11th` from GitHub using Custom ref `experiment/custodes-native-stratagems`, select **Keep separate**, then make a Custodes roster and select each detachment. Use the native Stratagems panel, not the catalogue Profiles panel.

---

## Scope

Aquilan Shield: Manoeuvre and Fire, Tip of the Talon, Rapid Reactions. Each is 1 CP. WHEN, TARGET and EFFECT are copied from the existing Custodes Detachment Stratagems profiles. Records are keyed to the original catalogue name `Imperium - Adeptus Custodes` and detachment name `Aquilan Shield`.

This is deliberately a limited experiment: the replacement book contains only these three stratagems, no core stratagems or other factions/detachments. Unit eligibility remains in the displayed TARGET text; structured unit-target filtering has not been implemented. Do not merge into main as a complete replacement.

## Validation completed

- Parsed the new JSON and ran the live application's extracted loadExtraBooks and detachment matching methods against it.
- Verified book 105 is requested and all three Aquilan Shield records are returned.
- Verified Tip of the Talon's +2 Strength effect is preserved and Dread Host does not match these records.
- Imported branch `experiment/custodes-native-stratagems` through New Recruit's GitHub importer, choosing Custom ref and Keep separate.
- Created a Custodes test roster, selected Aquilan Shield, and opened the native Stratagems section (separate from Profiles).
- With supporter access, the native section lists Manoeuvre and Fire, Tip of the Talon and Rapid Reactions at 1 CP each.
- Opened Tip of the Talon: native card displays WHCUSTOM11th, Your turn, Shooting phase, and the exact +2 Strength within Half Range effect.
- Reloaded the page, reopened Stratagems, and verified all three records and the Tip of the Talon card again.

## Reproduce in a supporter-enabled session

1. Add from GitHub: Reedddragon/WHCUSTOM11th.
2. Select Custom ref: experiment/custodes-native-stratagems.
3. Choose Keep separate for the experiment.
4. Create a Custodes roster. The guided detachment step does not currently expose the nested Shield Hosts; after creation, open Detachment and select Aquilan Shield in Shield Host Detachments.
5. Open the native Stratagems section and check for all three names, 1 CP each, the Movement/Shooting phase labels, opponent-turn Rapid Reactions, and Tip of the Talon granting +2 Strength within Half Range.
6. Reload and repeat to check persistence. Switch away from Aquilan Shield to check matching.

Pending: in-app detachment-switch and phase-filter tests; unit eligibility filters; preserving the official core and other faction stratagems before any wider rollout. No production merge has been made.
