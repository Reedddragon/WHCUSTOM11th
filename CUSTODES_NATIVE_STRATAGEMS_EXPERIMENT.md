# Custodes native stratagem experiment

Status: imports into the live New Recruit web app; native card rendering is NOT yet verified because the test browser is unsigned-in and displays the supporter gate.

This branch adds `Custodes Native Stratagems.json` only; existing catalogue rules and points are unchanged. The supplementary file is a library catalogue with string ID `105` and a sibling `data` object. New Recruit's native adapter requests book 105, then reads `data.stratagems` and `data.custom`.

## Scope

Aquilan Shield: Manoeuvre and Fire, Tip of the Talon, Rapid Reactions. Each is 1 CP. WHEN, TARGET and EFFECT are copied from the existing Custodes Detachment Stratagems profiles. Records are keyed to the original catalogue name `Imperium - Adeptus Custodes` and detachment name `Aquilan Shield`.

This is deliberately a limited experiment: the replacement book contains only these three stratagems, no core stratagems or other factions/detachments. Unit eligibility remains in the displayed TARGET text; structured unit-target filtering has not been implemented. Do not merge into main as a complete replacement.

## Validation completed

- Parsed the new JSON and ran the live application's extracted loadExtraBooks and detachment matching methods against it.
- Verified book 105 is requested and all three Aquilan Shield records are returned.
- Verified Tip of the Talon's +2 Strength effect is preserved and Dread Host does not match these records.
- Imported branch `experiment/custodes-native-stratagems` through New Recruit's GitHub importer, choosing Custom ref and Keep separate.
- Created a Custodes test roster, selected Aquilan Shield, and opened the native Stratagems section (separate from Profiles).
- The section shows Support New Recruit. This does not prove the custom book reached the renderer; a supporter-enabled UI test is still required.

## Reproduce in a supporter-enabled session

1. Add from GitHub: Reedddragon/WHCUSTOM11th.
2. Select Custom ref: experiment/custodes-native-stratagems.
3. Choose Keep separate for the experiment.
4. Create a Custodes roster. The guided detachment step does not currently expose the nested Shield Hosts; after creation, open Detachment and select Aquilan Shield in Shield Host Detachments.
5. Open the native Stratagems section and check for all three names, 1 CP each, the Movement/Shooting phase labels, opponent-turn Rapid Reactions, and Tip of the Talon granting +2 Strength within Half Range.
6. Reload and repeat to check persistence. Switch away from Aquilan Shield to check matching.

Pending: supporter-enabled card rendering; reload persistence; unit eligibility filters; preserving the official core and other faction stratagems before any wider rollout.
