#!/usr/bin/env python3
"""Build New Recruit Book 105 from WHCUSTOM11th's existing Detachment Stratagems profiles.

This deliberately requires an opt-in to build an incomplete base. A live New Recruit
installation uses one global Book 105; replacing it without a complete baseline
removes official faction stratagem data; core records can be supplied separately.
"""
import argparse
import collections
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "WHCUSTOM11th Native Stratagems.json"
SYS_ID = "sys-352e-adc2-7639-d610"
REQUIRED = frozenset({"CP", "When", "Target", "Effect"})
IGNORE_NAMES = {"Detachment", "Detachment Stratagems", "Shield Host Detachments (Max 1)", "Legacy Stratagem Options (hidden; now attached automatically)"}
FALLBACK_FIDS = {
    "Imperium - Adeptus Custodes": "AC",
    "Imperium - Adeptus Astartes - Space Marines": "SM",
    "Xenos - Orks": "OR",
    "Xenos - Necrons": "NE",
}

def html_rules(value):
    escaped = html.escape(str(value), quote=True)
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", escaped, flags=re.S)
    escaped = re.sub(r"\*(.+?)\*", r"<i>\1</i>", escaped, flags=re.S)
    return escaped.replace("\r\n", "\n").replace("\n", "<br>")

def phase_from_when(when):
    phases = [p for p in ("Command", "Movement", "Shooting", "Charge", "Fight") if re.search(r"\b" + p + r" phase\b", when, re.I)]
    return phases[0] + " phase" if len(phases) == 1 else "Any phase"

def turn_from_when(when):
    low = when.casefold()
    # A single timing can be relevant in either player's turn; preserve the full WHEN in its card.
    opponent = any(k in low for k in ("opponent's", "opponent’s", "opposing player's"))
    your = any(k in low for k in ("your command phase", "your movement phase", "your shooting phase", "your charge phase", "your fight phase"))
    return "Either turn" if (opponent and your) or (not opponent and not your) else "Opponent's turn" if opponent else "Your turn"


def core_records_from_source(path):
    """Convert pinned 11e core cards to the same New Recruit Book 105 record shape.

    Core records are global, with no faction_id and no detachment assignment.
    """
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data.get("stratagems")
    if not isinstance(rows, list) or len(rows) != 11:
        raise ValueError(f"{path}: expected exactly 11 11th-edition core stratagems")
    turn_map = {"your": "Your turn", "opponents": "Opponent's turn", "either": "Either turn"}
    phase_map = {"any": "Any phase", "command": "Command phase", "movement": "Movement phase",
                 "shooting": "Shooting phase", "charge": "Charge phase", "fight": "Fight phase"}
    converted = []
    for row in rows:
        name = (row.get("name") or {}).get("en")
        when = (row.get("when") or {}).get("en")
        target = (row.get("target") or {}).get("en")
        effect = (row.get("effect") or {}).get("en")
        phases = row.get("phase", [])
        cost = row.get("cost")
        if not (row.get("id") and name and when and target and effect and
                isinstance(cost, int) and cost > 0 and isinstance(phases, list) and phases and
                row.get("turn") in turn_map and all(p in phase_map for p in phases)):
            raise ValueError(f"Malformed core stratagem: {name!r}")
        # Preserve upstream HTML formatting, but convert nonstandard tag styling to bold.
        def body(value):
            return str(value).replace("<k>", "<b>").replace("</k>", "</b>").replace("<appref>", "").replace("</appref>", "")
        desc = "<b>WHEN:</b> " + body(when) + "<br><b>TARGET:</b> " + body(target) + "<br><b>EFFECT:</b> " + body(effect)
        if row.get("secondary_effect"):
            alt = (row["secondary_effect"] or {}).get("en", "")
            extra = row.get("secondary_effect_cost")
            desc += "<br><b>ALTERNATIVE (" + ("+" + str(extra) + " CP" if extra else "no additional CP") + "):</b> " + body(alt)
        if row.get("restrictions"):
            restrict = (row["restrictions"] or {}).get("en", "")
            if restrict:
                desc += "<br><b>RESTRICTIONS:</b> " + body(restrict)
        # Use the actual WHEN timing if the source index disagrees (e.g. Insane Bravery).
        timing_phase = phase_from_when(str(when))
        displayed_phase = timing_phase if timing_phase != "Any phase" else ", ".join(phase_map[x] for x in phases)
        converted.append(dict(
            id=row["id"], name=name, detachment="", faction_id=None,
            type="Core – Stratagem", cp_cost=cost,
            phase=displayed_phase,
            turn=turn_map[row["turn"]], description=desc
        ))
    names = [x["name"].casefold() for x in converted]
    if len(set(names)) != 11:
        raise ValueError("Duplicate core stratagem names")
    return converted

def records_from_catalogue(path):
    document = json.loads(path.read_text(encoding="utf-8"))
    cat = document.get("catalogue")
    if not isinstance(cat, dict) or not cat.get("name"):
        return None, [], []
    name = cat["name"]
    records = []
    def walk(node, ancestors=()):
        if isinstance(node, list):
            for v in node:
                walk(v, ancestors)
        elif isinstance(node, dict):
            title = node.get("name", "")
            if node.get("typeName") == "Detachment Stratagems":
                parents = [x for x in ancestors if x not in IGNORE_NAMES]
                if not parents or parents[-1] == name:
                    raise ValueError(f"{path}: unable to identify detachment for {title!r}, parents={parents}")
                detachment = parents[-1]
                ch = {x.get("name"): x.get("$text", "") for x in node.get("characteristics", []) if isinstance(x, dict)}
                if not REQUIRED.issubset(ch):
                    raise ValueError(f"{path}: {detachment}/{title} missing: {REQUIRED - set(ch)}")
                m = re.search(r"(\d+)\s*CP\b", str(ch["CP"]), flags=re.I)
                if not m:
                    raise ValueError(f"{path}: invalid CP cost on {detachment}/{title}: {ch['CP']!r}")
                when = str(ch["When"])
                records.append(dict(
                    id=node["id"], name=title, detachment=detachment,
                    faction_id=FALLBACK_FIDS.get(name, name),
                    type="WHCUSTOM11th – Detachment Stratagem",
                    cp_cost=int(m.group(1)), phase=phase_from_when(when), turn=turn_from_when(when),
                    description=("<b>COST:</b> " + html_rules(ch["CP"]) + "<br>" if str(ch["CP"]).strip().casefold() != f"{m.group(1)} cp" else "") + "<b>WHEN:</b> " + html_rules(when) +
                                "<br><b>TARGET:</b> " + html_rules(ch["Target"]) +
                                "<br><b>EFFECT:</b> " + html_rules(ch["Effect"])
                ))
            new_parents = ancestors + ((title,) if isinstance(title, str) and title else ())
            for v in node.values():
                if isinstance(v, (dict, list)):
                    walk(v, new_parents)
    walk(cat)
    return name, records, [x.get("name", "") for x in cat.get("catalogueLinks", [])]

def build(baseline_path, permit_incomplete, core_source):
    native = collections.defaultdict(list)
    marine_inheritors = []
    for path in sorted(ROOT.glob("*.json")):
        if path.name == OUTPUT.name:
            continue
        cat_name, records, links = records_from_catalogue(path)
        if cat_name and cat_name != "Imperium - Adeptus Astartes - Space Marines" and "Imperium - Space Marines" in links:
            marine_inheritors.append(cat_name)
        if records:
            native[cat_name].extend(records)
    all_records = [r for cat in sorted(native) for r in native[cat]]
    core_records = core_records_from_source(core_source)
    # Imported Space Marine detachments appear in multiple chapter catalogues.
    # The native viewer matches custom rows by the roster's original catalogue name.
    view_custom = {cat: list(rows) for cat, rows in native.items()}
    marine = native.get("Imperium - Adeptus Astartes - Space Marines", [])
    for chapter in sorted(set(marine_inheritors)):
        view_custom[chapter] = list(marine) + list(native.get(chapter, []))
    known = set()
    for cat, records in native.items():
        for row in records:
            k = (cat.casefold(), row["detachment"].casefold(), row["name"].casefold())
            if k in known:
                raise ValueError(f"Duplicate stratagem: {k}")
            known.add(k)
    if len(all_records) < 240:
        raise ValueError(f"Expected at least 240 structured custom stratagems, found {len(all_records)}")

    if baseline_path:
        supplied = json.loads(baseline_path.read_text(encoding="utf-8"))
        base = supplied.get("data", supplied)
        if not isinstance(base, dict) or "stratagems" not in base or "custom" not in base:
            raise ValueError("Supplied official Book 105 must contain data.stratagems and data.custom")
        result = {k: v for k, v in base.items()}
        custom = {k: list(v) for k, v in base.get("custom", {}).items()}
        # Keep official/default records for all unaffected detachments and catalogues.
        for cat, rows in view_custom.items():
            overridden = {r["detachment"].casefold() for r in rows}
            keep = [s for s in custom.get(cat, []) if str(s.get("detachment", "")).casefold() not in overridden]
            custom[cat] = keep + rows
        result["custom"] = custom
        # Retain original global core/unmodified stratagems; add custom rows for native searching.
        original = list(base["stratagems"])
        official_core_names = {x["name"].casefold() for x in core_records}
        existing_names = {
            str(x.get("name", "")).casefold()
            for x in original if x.get("detachment", "") in ("", None)
        }
        missing_cores = [x for x in core_records if x["name"].casefold() not in existing_names]
        result["stratagems"] = original + missing_cores + all_records
    elif permit_incomplete:
        result = {
            "stratagems": core_records + all_records, "custom": view_custom, "units": [],
            "keywords": {}, "alias": {}, "conditional": {},
        }
    else:
        raise SystemExit("Refusing to replace global Book 105 without baseline; pass --experimental-incomplete-base for isolated testing")

    game = {
        "catalogue": {
            "id": "105", "name": "WHCUSTOM11th Native Stratagems",
            "gameSystemId": SYS_ID, "gameSystemRevision": 19,
            "revision": 1, "battleScribeVersion": "2.03", "library": True,
        },
        "data": result,
    }
    OUTPUT.write_text(json.dumps(game, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    dets = {cat: len({r["detachment"] for r in rows}) for cat, rows in native.items()}
    summary = {cat: {"stratagems": len(rows), "detachments": dets[cat]} for cat, rows in native.items()}
    print("GENERATED:", len(all_records), "custom stratagems across", len(native), "catalogues")
    print("CORE:", len(core_records), "globally scoped stratagems:", [x["name"] for x in core_records])
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    print("CHAPTER ALIASES:", len(marine_inheritors), sorted(set(marine_inheritors)))
    print("BASE:", "preserved" if baseline_path else "INCOMPLETE; test branch only")
    return len(all_records)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", type=Path, help="Complete original native Book 105 JSON, supplied with permission")
    parser.add_argument("--core-source", type=Path, required=True, help="Pinned 11th-edition core JSON")
    parser.add_argument("--experimental-incomplete-base", action="store_true")
    args = parser.parse_args()
    build(args.baseline, args.experimental_incomplete_base, args.core_source)
