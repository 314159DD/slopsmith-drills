from drills.spec import Drill, DrillType, AudioStyle
from engine.timeline import Timeline
from engine.drum_tab import build_drum_tab

def test_no_drum_tab_for_click():
    d = Drill(id="c", title="x", type=DrillType.FINGER, tempo=60, bars=1,
              content={"string":5,"frets":[1]}, audio_style=AudioStyle.CLICK)
    assert build_drum_tab(d, Timeline(d.tempo, d.bars)) is None

def test_drum_tab_hits_match_pattern():
    d = Drill(id="r", title="x", type=DrillType.CHORD_SHAPE, tempo=60, bars=1,
              content={"chord":"Em"}, audio_style=AudioStyle.DRUM)
    tab = build_drum_tab(d, Timeline(d.tempo, d.bars))
    times = sorted({h["t"] for h in tab["hits"]})
    assert times == [0.0, 1.0, 2.0, 3.0]      # a hit on every beat (hat)
    # kick (p=0) on beats 1&3, snare (p=1) on 2&4
    kicks = sorted(h["t"] for h in tab["hits"] if h["p"] == 0)
    assert kicks == [0.0, 2.0]
