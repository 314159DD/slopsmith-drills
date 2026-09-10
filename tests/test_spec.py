from drills.spec import Drill, DrillType, AudioStyle

def test_drill_defaults():
    d = Drill(id="u2-d1", title="Em hold", type=DrillType.CHORD_SHAPE,
              tempo=70, bars=8, content={"chord": "Em"})
    assert d.audio_style == AudioStyle.DRUM
    assert d.repeats == 1

def test_drill_change_content():
    d = Drill(id="u3-gc", title="G to C", type=DrillType.CHORD_CHANGE,
              tempo=70, bars=16, content={"chords": ["G", "C"]},
              audio_style=AudioStyle.DRUM)
    assert d.content["chords"] == ["G", "C"]
