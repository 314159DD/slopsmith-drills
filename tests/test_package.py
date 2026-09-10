import json, yaml
from pathlib import Path
from drills.spec import Drill, DrillType, AudioStyle
from engine.package import build_sloppak

def test_build_creates_expected_layout(tmp_path):
    d = Drill(id="u3-gc", title="G to C @70", type=DrillType.CHORD_CHANGE,
              tempo=70, bars=4, content={"chords":["G","C"]}, audio_style=AudioStyle.DRUM)
    pak = build_sloppak(d, tmp_path)
    assert pak.name == "u3-gc.sloppak"
    assert (pak / "manifest.yaml").exists()
    assert (pak / "arrangements" / "lead.json").exists()
    assert (pak / "stems" / "full.ogg").exists()
    assert (pak / "drum_tab.json").exists()

    man = yaml.safe_load((pak / "manifest.yaml").read_text())
    assert man["title"] == "G to C @70"
    assert man["arrangements"][0]["file"] == "arrangements/lead.json"
    assert man["stems"][0]["default"] is True
    assert man["drum_tab"] == "drum_tab.json"
    assert abs(man["duration"] - (4 * 4 * 60/70)) < 0.01

    arr = json.loads((pak / "arrangements" / "lead.json").read_text())
    assert len(arr["chords"]) == 4

def test_click_drill_omits_drum_tab(tmp_path):
    d = Drill(id="f1", title="finger", type=DrillType.FINGER, tempo=60, bars=1,
              content={"string":5,"frets":[1,2,3,4]}, audio_style=AudioStyle.CLICK)
    pak = build_sloppak(d, tmp_path)
    assert not (pak / "drum_tab.json").exists()
    man = yaml.safe_load((pak / "manifest.yaml").read_text())
    assert "drum_tab" not in man
