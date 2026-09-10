import subprocess, wave
from pathlib import Path
from drills.spec import Drill, DrillType, AudioStyle
from engine.timeline import Timeline
from engine.stem import render_stem

def _ogg_duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe","-v","error","-show_entries","format=duration",
         "-of","default=nk=1:nw=1", str(path)],
        capture_output=True, text=True, check=True)
    return float(out.stdout.strip())

def test_click_stem_written_and_right_duration(tmp_path):
    d = Drill(id="c", title="x", type=DrillType.FINGER, tempo=60, bars=2,
              content={"string":5,"frets":[1,2,3,4]}, audio_style=AudioStyle.CLICK)
    t = Timeline(d.tempo, d.bars)   # duration 8.0
    out = tmp_path / "full.ogg"
    render_stem(d, t, out)
    assert out.exists() and out.stat().st_size > 0
    assert abs(_ogg_duration(out) - 8.0) < 0.3

def test_backing_stem_for_mini_song(tmp_path):
    d = Drill(id="m", title="prog", type=DrillType.MINI_SONG, tempo=60, bars=4,
              content={"chords":["G","D","Em","C"]}, audio_style=AudioStyle.BACKING)
    out = tmp_path / "full.ogg"
    render_stem(d, Timeline(d.tempo, d.bars), out)
    assert out.exists() and out.stat().st_size > 0
