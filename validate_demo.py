"""Validate the published TERRA VIVA *snapshot*, not the private simulation engine."""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
REQUIRED = {"world", "census", "residents", "events", "evolution", "research", "engineering"}

def validate():
    for filename in ("README.md", "LICENSE.txt", "index.html", "earth.jpg", "snapshot.json"):
        if not (ROOT / filename).is_file():
            raise ValueError("missing public demo asset: " + filename)
    if (ROOT / "snapshot.json").stat().st_size > 16_000_000:
        raise ValueError("snapshot exceeds public demo size policy")
    with (ROOT / "snapshot.json").open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not REQUIRED.issubset(data):
        raise ValueError("snapshot schema missing keys")
    world = data["world"]
    census = data["census"]
    if not isinstance(data["residents"], list) or not isinstance(data["events"], list):
        raise ValueError("expected lists of sample residents and events")
    if not isinstance(census["total"], int) or census["total"] < len(data["residents"]):
        raise ValueError("census total inconsistent with resident sample")
    if not isinstance(world.get("cities"), list) or not world["cities"]:
        raise ValueError("missing city data")
    if not isinstance(data["evolution"].get("projects"), list):
        raise ValueError("missing evolution projects")
    if not isinstance(data["engineering"], (dict, list)):
        raise ValueError("invalid engineering section")
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    if "snapshot.json" not in html or "TERRA VIVA" not in html:
        raise ValueError("viewer not connected to snapshot")
    return {
        "census_total": census["total"],
        "detailed_residents": len(data["residents"]),
        "events_sample": len(data["events"]),
        "evolution_projects": len(data["evolution"]["projects"]),
        "scope": "static snapshot only",
    }

def main():
    try:
        result = validate()
    except (ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print("Public demo validation failed:", exc, file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    sys.exit(main())
