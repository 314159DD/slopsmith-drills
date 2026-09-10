import json
from pathlib import Path
import yaml

from drills.spec import Drill
from engine.timeline import Timeline
from engine.arrangement import build_arrangement
from engine.drum_tab import build_drum_tab
from engine.stem import render_stem


def build_sloppak(drill: Drill, out_dir: Path) -> Path:
    out_dir = Path(out_dir)
    pak = out_dir / f"{drill.id}.sloppak"
    (pak / "arrangements").mkdir(parents=True, exist_ok=True)
    (pak / "stems").mkdir(parents=True, exist_ok=True)

    t = Timeline(drill.tempo, drill.bars, drill.beats_per_bar)

    arrangement = build_arrangement(drill, t)
    (pak / "arrangements" / "lead.json").write_text(json.dumps(arrangement))

    render_stem(drill, t, pak / "stems" / "full.ogg")

    manifest = {
        "title": drill.title,
        "artist": drill.artist,
        "duration": round(t.duration, 3),
        "arrangements": [{
            "id": "lead", "name": "Lead", "file": "arrangements/lead.json",
            "tuning": [0, 0, 0, 0, 0, 0], "capo": 0,
        }],
        "stems": [{"id": "full", "file": "stems/full.ogg", "default": True}],
    }

    tab = build_drum_tab(drill, t)
    if tab is not None:
        (pak / "drum_tab.json").write_text(json.dumps(tab))
        manifest["drum_tab"] = "drum_tab.json"

    (pak / "manifest.yaml").write_text(yaml.safe_dump(manifest, sort_keys=False))
    return pak
