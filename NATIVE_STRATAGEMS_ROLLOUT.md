# WHCUSTOM11th — native Stratagems viewer rollout

## Current verified result (2026-11-06)

The Custodes Book 105 experiment was reported working in New Recruit's native Stratagems viewer. Using the same schema, this **test branch** now generates a single `WHCUSTOM11th Native Stratagems.json` book (id `105`) for the structured stratagems currently in the repository.

The generator's validation passed on GitHub Actions:
- Adeptus Custodes: **42** entries, 13 detachments
- Space Marines: **148** entries, 36 detachments (including the custom Deathwing Protocol, Xanax System)
- Orks: **47** entries, 14 detachments
- Necrons: **3** entries, 1 detachment

Total: **240** stratagem records across **64** source detachments. Eleven Space Marine chapter catalogues also receive alias mappings for inherited Space Marine detachments (e.g. Dark Angels and Blood Angels). The source records are read from the existing catalogue profiles; no unit, points, enhancement or detachment rules were changed.

## How to try the new Book 105

1. In New Recruit, add the repository from GitHub: `Reedddragon/WHCUSTOM11th`.
2. Select **Custom ref** and enter `experiment/all-native-stratagems-20261106`.
3. Choose **Keep separate** (do not overwrite your established imported main system).
4. Create a test roster for Orks, Space Marines (including Dark Angels / Deathwing Protocol), Necrons, or Custodes.
5. Choose a detachment that has a custom stratagem profile and open the **native Stratagems panel**.
6. Verify names, CP, timing, and effects; switch detachments and reload. The generated book includes base CP plus an explicit COST line for conditional 1/2 CP stratagems.

This has passed automatic structural checks. Live New Recruit tests for the other factions are still required.

## Important limitation — do not merge to main yet

The New Recruit adapter fetches **one global Book 105**, using `data.stratagems` and `data.custom`. The test Book 105 contains the custom 240 records only. Replacing the production book wholesale currently loses the original core stratagems and the official stratagems for unchanged detachments/factions.

The script intentionally refuses to generate a production book without an explicit, appropriately sourced original Book 105 file passed using `--baseline /path/to/book.json`. The `--experimental-incomplete-base` option is allowed only for isolated branch testing.

When a legal/current complete source is supplied, the script merges into `data.custom` only for matching modified detachment names, retaining unaffected official catalogue mappings and global fields. It also appends custom records to `data.stratagems`; live validation should verify no duplicate cards or unintended matches.

## Ongoing maintenance

The generator lives in `.github/scripts/build_native_stratagems.py` and the experiment-only GitHub workflow is `.github/workflows/build-all-native-stratagems.yml`. Changes to faction JSONs on this test branch regenerate the output automatically, except for output-file-only commits (avoids loops).

When the preservation/merge behavior has been verified in a live app with core and unmodified factions, adapt the workflow for `main`, supply the baseline via a maintained approved data source, and remove the experimental-incomplete option. Do not silently replace official base records or assume the remote data will remain stable.
