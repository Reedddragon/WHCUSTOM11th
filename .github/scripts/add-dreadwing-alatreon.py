#!/usr/bin/env python3
"""One-time, narrow Dreadwing restoration using the historical Dark Angels catalogue."""
import copy
import html
import json
import subprocess
from pathlib import Path

SPACE = "Imperium - Space Marines.json"
DARK = "Imperium - Dark Angels.json"
NATIVE = "WHCUSTOM11th Native Stratagems.json"
NAME = "Dreadwing: Alatreon Protocol"
UNITS = ["Dreadwing Naufragia", "Dreadwing Interptors", "Dreadwing Fellglaive", "Marduk Sedras"]
PREFIX = "drwp-1108-2026-"
ident = lambda i: PREFIX + str(i).zfill(4)

def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))

def old_dark():
    data = subprocess.check_output([
        "git", "show",
        "origin/backup-before-bsdata-sync-2026-10-25:" + DARK
    ])
    return json.loads(data.decode("utf-8-sig"))

def write(path, doc, pretty=False):
    if pretty:
        data = json.dumps(doc, ensure_ascii=False, indent=2) + "\n"
    else:
        data = json.dumps(doc, ensure_ascii=False, separators=(",", ":")) + "\n"
    Path(path).write_text(data, encoding="utf-8")

STRATS = [
    ("Unto the Death of the World", 1, "Shooting phase", "Your turn",
     "Your Shooting phase, when a friendly DREADWING unit that has not shot this phase is selected to shoot.",
     "That DREADWING unit.",
     "Until the end of the phase, add 3 to the Strength, improve AP by 1, and add 1 to the Damage characteristic of its HAZARDOUS ranged weapons. MELTA and TORRENT weapons equipped by that unit gain HAZARDOUS. Subtract 3 from Hazardous test rolls made for that unit."),
    ("Eskaton Imperative", 1, "Shooting phase", "Opponent's turn",
     "Your opponent's Shooting phase, just after an enemy unit has shot and destroyed one or more models in a friendly DREADWING unit.",
     "That DREADWING unit.",
     "Your unit can shoot as if it were your Shooting phase, but it must target that enemy unit, and only if it is an eligible target."),
    ("Extinction of Life", 1, "Shooting phase", "Your turn",
     "Your Shooting phase, just after a friendly DREADWING unit shoots an enemy unit within range of an objective marker.",
     "That DREADWING unit.",
     "For each enemy unit within range of that objective marker, roll one D6: on a 4+, that enemy unit suffers 3 mortal wounds and must take a Battle-shock test. An affected unit must also take a Battle-shock test in each subsequent battle round while it remains within range of that objective marker."),
    ("This World Shall Fall First Before Us", 1, "Shooting phase", "Your turn",
     "Your Shooting phase, when a friendly DREADWING unit that has not shot this phase is selected to shoot.",
     "That DREADWING unit.",
     "MELTA and TORRENT weapons equipped by models in your unit gain HAZARDOUS until the end of the phase. If a model in that unit is destroyed by a failed Hazardous test this phase, do not remove it immediately. After the current attacking unit finishes making its attacks, that model can shoot once, automatically passing Hazardous tests for those attacks; then remove it. This can allow a model to shoot again after its earlier attacks."),
    ("No Point Hiding", 2, "Shooting phase", "Your turn",
     "Your Shooting phase, when a friendly DREADWING unit that has not shot this phase is selected to shoot.",
     "That DREADWING unit.",
     "Until the end of the phase, its HAZARDOUS ranged weapons gain +6\" Range and [INDIRECT FIRE]. MELTA weapons gain HAZARDOUS. Subtract 4 from Hazardous test rolls and add 1 to Hazardous damage rolls for that unit."),
    ("Malevolence of the Legion", 1, "Shooting phase", "Your turn",
     "Your Shooting phase, when a friendly DREADWING unit that has not shot this phase is selected to shoot.",
     "That DREADWING unit.",
     "Until the end of the phase, re-roll Wound rolls of 1 for attacks made by that unit. Against your Oath of Moment target, re-roll Wound rolls instead for attacks made with HAZARDOUS weapons. MELTA and TORRENT weapons equipped by that unit gain HAZARDOUS."),
]
assert len(STRATS) == 6

sdoc, ddoc, ndoc, pdoc = read(SPACE), read(DARK), read(NATIVE), old_dark()
s, d, n, pre = sdoc["catalogue"], ddoc["catalogue"], ndoc["data"], pdoc["catalogue"]

group = next(x for x in s["sharedSelectionEntryGroups"] if x["name"] == "Detachment")
assert not any(x["name"] == NAME for x in group["selectionEntries"]), "Detachment already present"
rav = next(x for x in group["selectionEntries"] if x["name"] == "Ravenwing Protocol")
rule = (
    "All DREADWING units from your army have Feel No Pain 6+ against ranged attacks "
    "and Feel No Pain 5+ against mortal wounds.\n\n"
    "For the purposes of this detachment's rules and Stratagems, INFERNUS SQUAD, "
    "HELLBLASTER SQUAD, DESOLATION SQUAD, DEVASTATOR SQUAD and ADEPTUS ASTARTES "
    "GRAVIS units from your army gain the DREADWING keyword.\n\n"
    "Restrictions: Your army can include DARK ANGELS units, but cannot include "
    "ADEPTUS ASTARTES units drawn from another Chapter."
)
entry = {
    "name": NAME, "id": ident(1), "hidden": False, "import": True, "type": "upgrade",
    "categoryLinks": [dict(copy.deepcopy(x), id=ident(i + 2)) for i, x in enumerate(rav["categoryLinks"])],
    "constraints": [dict(copy.deepcopy(x), id=ident(i + 5)) for i, x in enumerate(rav["constraints"])],
    "costs": copy.deepcopy(rav["costs"]),
    "modifiers": copy.deepcopy(rav["modifiers"]),
    "rules": [{"name": "World Ending Dread", "id": ident(6), "hidden": False, "description": rule}],
    "profiles": [
        {"name": name, "id": ident(i + 7), "typeId": "7e2f-1026-f100-0001",
         "typeName": "Detachment Stratagems", "hidden": False,
         "comment": "Adapted from the original Dreadwing: Alatreon Protocol document.",
         "characteristics": [
             {"name": "CP", "$text": str(cp) + " CP"},
             {"name": "When", "$text": when}, {"name": "Target", "$text": target},
             {"name": "Effect", "$text": effect}
         ]} for i, (name, cp, phase, turn, when, target, effect) in enumerate(STRATS)
    ]
}
assert next(x["value"] for x in entry["costs"] if x["name"] == "Detachment Points") == 3
idx = next(i for i, x in enumerate(group["selectionEntries"]) if x["name"] == "Ravenwing Protocol")
group["selectionEntries"].insert(idx + 1, entry)
s["revision"] = int(s.get("revision", 0)) + 1

# Historical Dreadwing units: retain original profiles and point costs.
units = [copy.deepcopy(next(x for x in pre["sharedSelectionEntries"] if x["name"] == name)) for name in UNITS]
assert not any(x["name"] in UNITS for x in d["sharedSelectionEntries"])
cats = [copy.deepcopy(x) for x in pre["categoryEntries"] if "Dreadwing" in x["name"]]
groups = [copy.deepcopy(x) for x in pre.get("sharedSelectionEntryGroups", []) if x["name"] == "Dreadwing Weapons"]
links = [copy.deepcopy(x) for x in pre["entryLinks"] if x["name"] in UNITS]
assert len(units) == len(cats) == len(links) == 4 and len(groups) == 1

def repair(obj):
    if isinstance(obj, list):
        for child in obj: repair(child)
    elif isinstance(obj, dict):
        # Replace obsolete pre-sync references with the current shared equivalents.
        if obj.get("targetId") == "b095-d588-7f75-2f48":
            obj["targetId"] = "6c7d-af5b-482-6fbe"  # A3 WS3+ S4 close combat weapon
        if obj.get("targetId") == "4362-2036-1522-de2e":
            obj["targetId"] = "241f-f84f-4d2f-95a7"  # Damaged: 1-8
        if obj.get("name") == "Oath of Moment" and obj.get("targetId") == "3b76-4053-ece9-6e7d":
            obj["name"] = "Combat Doctrines"  # Current shared rule at this ID
        for value in obj.values(): repair(value)

for unit in units: repair(unit)
d["sharedSelectionEntries"].extend(units)
d["categoryEntries"].extend(cats)
d.setdefault("sharedSelectionEntryGroups", []).extend(groups)
d["entryLinks"].extend(links)
d["revision"] = int(d.get("revision", 0)) + 1

# Use the same IDs and exact detachment name in the native viewer's Book 105.
newcards = []
for i, (name, cp, phase, turn, when, target, effect) in enumerate(STRATS):
    newcards.append({
        "id": ident(i + 7), "name": name, "detachment": NAME, "faction_id": "SM",
        "type": "WHCUSTOM11th – Detachment Stratagem",
        "cp_cost": cp, "phase": phase, "turn": turn,
        "description": "<b>WHEN:</b> " + html.escape(when, quote=True) +
                       "<br><b>TARGET:</b> " + html.escape(target, quote=True) +
                       "<br><b>EFFECT:</b> " + html.escape(effect, quote=True),
    })
assert not any(x["detachment"] == NAME for x in n["stratagems"])
n["stratagems"].extend(newcards)
count = 0
for key, val in n["custom"].items():
    if key.startswith("Imperium - Adeptus Astartes - "):
        val.extend(copy.deepcopy(newcards))
        count += 1
assert count == 12, f"Expected 12 Space Marine chapter catalogues, got {count}"
ndoc["catalogue"]["revision"] = int(ndoc["catalogue"].get("revision", 0)) + 1

assert len([x for x in group["selectionEntries"] if x["name"] == NAME]) == 1
assert len([x for x in d["sharedSelectionEntries"] if x["name"] in UNITS]) == 4
assert len([x for x in d["entryLinks"] if x["name"] in UNITS]) == 4
assert len([x for x in n["custom"]["Imperium - Adeptus Astartes - Dark Angels"] if x["detachment"] == NAME]) == 6
assert len([x for x in n["stratagems"] if x["detachment"] == NAME]) == 6

write(SPACE, sdoc)
write(DARK, ddoc, pretty=True)
write(NATIVE, ndoc)
for path in (SPACE, DARK, NATIVE):
    read(path)  # validates serialized JSON
print("Dreadwing migration ready:", NAME, "3DP, 6 native stratagems, 4 restored units")
