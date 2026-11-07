# WHCUSTOM11th — native Stratagems viewer rollout

## Core stratagem visibility and refresh (2026-11-06)

Book 105 has been regenerated at **revision 3** with all 11 core entries as `type: "Core – Stratagem"`, `faction_id: ""`, and `detachment: ""`. The 240 custom detachment records are preserved. New Recruit 37.14 uses `type.startsWith("Core –")` to select global core cards. Its extracted native matching method returned **14 Grav-Assault Force cards: 3 custom + 11 core**.

New Recruit also caches the loaded stratagem book by game system short name (`wh40k-11e`). Keeping both main and one or more separate experimental copies imported can retain stale Book 105 contents within an application session.

**If custom cards appear but core is missing:** update the imported experiment in My Systems, fully close and reopen New Recruit, and choose the **All phases** filter/chip in the roster Stratagems panel. Verify both **Coordinated Dive** (custom) and **Command Re-roll** / **Counteroffensive** (core). On the dedicated system-wide Stratagems reference page, choose **Core Stratagems** in the faction dropdown.

The format and native matching path are validated. Rendering of the regenerated Book 105 revision 3 still needs a logged-in interactive test.
## Current verified result (2026-11-06)

The Custodes Book 105 experiment was reported working in New Recruit's native Stratagems viewer. Using the same schema, this **test branch** now generates a single `WHCUSTOM11th Native Stratagems.json` book (id `105`) for the structured stratagems currently in the repository.

The generator's validation passed on GitHub Actions. **Core stratagems are now included: 11 globally available records** (Command Re-roll, Fire Overwatch, Crushing Impact, Epic Challenge, Rapid Ingress, Heroic Intervention, Insane Bravery, Smokescreen, Explosives, Counteroffensive, New Orders).

They are sourced from the [Game Datacards 11th Edition core data](https://github.com/game-datacards/datasources/blob/6f98bb1ce06e4dc2bed2c1c2cf27388cf7dbfa6a/11th/gdc/core.json) pinned at the October 2026 version. The workflow converts the source's timing, CP, target, effect, restrictions and alternate modes into native New Recruit cards. Core cards have no faction or detachment restriction, and source-index timing conflicts are resolved in favour of WHEN.

The generator's custom-profile validation covers:
- Adeptus Custodes: **42** entries, 13 detachments
- Space Marines: **148** entries, 36 detachments (including the custom Deathwing Protocol)
- Orks: **47** entries, 14 detachments
- Necrons: **3** entries, 1 detachment

Total: **251** records (11 core and 240 custom) spanning **64** customized source detachments. Eleven Space Marine chapter catalogues also receive alias mappings for inherited Space Marine detachments (e.g. Dark Angels and Blood Angels). The source records are read from the existing catalogue profiles; no unit, points, enhancement or detachment rules were changed.

## How to try the new Book 105

1. In New Recruit, add the repository from GitHub: `Reedddragon/WHCUSTOM11th`.
2. Select **Custom ref** and enter `experiment/all-native-stratagems-20261106`.
3. Choose **Keep separate** (do not overwrite your established imported main system).
4. Create a test roster for Orks, Space Marines (including Dark Angels / Deathwing Protocol), Necrons, or Custodes.
5. Choose a detachment that has a custom stratagem profile and open the **native Stratagems panel**.
6. Verify names, CP, timing, and effects; switch detachments and reload. The generated book includes base CP plus an explicit COST line for conditional 1/2 CP stratagems.

This has passed automatic structural checks. Live New Recruit tests for the other factions are still required.

## Important limitation — do not merge to main yet

The New Recruit adapter fetches **one global Book 105**, using `data.stratagems` and `data.custom`. The test Book 105 contains **all 11 core stratagems plus the 240 custom records**. Replacing the production book wholesale would still lose the official stratagems for unchanged detachments/factions. The core records have been structurally validated; live New Recruit UI testing of the combined set is still pending.

The script intentionally refuses to generate a production book without an explicit, appropriately sourced original Book 105 file passed using `--baseline /path/to/book.json`. It also requires `--core-source /path/to/core.json`. The `--experimental-incomplete-base` option is allowed only for isolated branch testing. The experiment workflow retrieves a pinned core JSON and supplies it automatically.

When a legal/current complete source is supplied, the script merges into `data.custom` only for matching modified detachment names, retaining unaffected official catalogue mappings and global fields. It also appends custom records to `data.stratagems`; live validation should verify no duplicate cards or unintended matches.

## Ongoing maintenance

The generator lives in `.github/scripts/build_native_stratagems.py` and the experiment-only GitHub workflow is `.github/workflows/build-all-native-stratagems.yml`. Changes to faction JSONs on this test branch regenerate the output automatically, except for output-file-only commits (avoids loops).

When the preservation/merge behavior has been verified in a live app with core and unmodified factions, adapt the workflow for `main`, supply the baseline via a maintained approved data source, and remove the experimental-incomplete option. Do not silently replace official base records or assume the remote data will remain stable.

## Deathwing Protocol naming (November 6, 2026)

The actual detachment in `Imperium - Space Marines.json` is named **Deathwing Protocol** on both `main` and the native-viewer test branch. Book 105 uses the exact same name, with six existing custom stratagems mapped to that detachment. The temporary comma-name alias was removed. Source rules and conditional 1/2 CP costs are preserved.

## Ravenwing Protocol (November 8, 2026)

Added a separate **Ravenwing Protocol** detachment to the Space Marines catalogue, using the original *Ravenwing, Nephilim Protocols* design. The 3DP detachment retains Hunters in Black, advancing/falling back and shooting, extra Mounted charge eligibility, Outrider Battleline, and six 1CP stratagems. Book 105 revision 6 maps the six native cards to the same detachment name for Dark Angels and inherited Space Marine chapter catalogues. Existing Darkflight Pursuit and Wrath of the Rock remain unchanged. This is still an experimental incomplete-baseline Book 105 pending live New Recruit validation.
