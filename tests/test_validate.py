from pathlib import Path
from drills.spec import Drill, DrillType, AudioStyle
from engine.package import build_sloppak
from engine.validate import validate_sloppak

def test_valid_pack_has_no_warnings(tmp_path):
    d = Drill(id="ok", title="Em", type=DrillType.CHORD_SHAPE, tempo=60, bars=2,
              content={"chord":"Em"}, audio_style=AudioStyle.DRUM)
    pak = build_sloppak(d, tmp_path)
    assert validate_sloppak(pak) == []

def test_missing_stem_is_flagged(tmp_path):
    d = Drill(id="bad", title="Em", type=DrillType.CHORD_SHAPE, tempo=60, bars=1,
              content={"chord":"Em"}, audio_style=AudioStyle.DRUM)
    pak = build_sloppak(d, tmp_path)
    (pak / "stems" / "full.ogg").unlink()
    warnings = validate_sloppak(pak)
    assert any("stem" in w.lower() for w in warnings)
