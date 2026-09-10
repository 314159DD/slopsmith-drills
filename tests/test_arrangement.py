from drills.spec import Drill, DrillType, AudioStyle
from engine.timeline import Timeline
from engine.arrangement import build_arrangement

def test_chord_change_alternates_per_bar():
    d = Drill(id="x", title="G-C", type=DrillType.CHORD_CHANGE, tempo=60, bars=4,
              content={"chords": ["G", "C"]})
    t = Timeline(d.tempo, d.bars)
    arr = build_arrangement(d, t)
    # 4 bars -> 4 chord strikes, alternating G,C,G,C at bar starts 0,4,8,12
    assert [c["t"] for c in arr["chords"]] == [0.0, 4.0, 8.0, 12.0]
    # templates deduped to 2 (G, C); chord.id indexes into templates
    names = [tpl["name"] for tpl in arr["templates"]]
    assert set(names) == {"G", "C"}
    first = arr["chords"][0]
    assert arr["templates"][first["id"]]["name"] == "G"

def test_sections_label_each_change():
    d = Drill(id="x", title="G-C", type=DrillType.CHORD_CHANGE, tempo=60, bars=2,
              content={"chords": ["G", "C"]})
    arr = build_arrangement(d, Timeline(d.tempo, d.bars))
    assert arr["sections"][0]["name"] == "G"
    assert arr["sections"][1]["name"] == "C"

def test_beats_present_and_match_timeline():
    d = Drill(id="x", title="Em", type=DrillType.CHORD_SHAPE, tempo=60, bars=2,
              content={"chord": "Em"})
    t = Timeline(d.tempo, d.bars)
    arr = build_arrangement(d, t)
    assert arr["beats"] == t.beats_wire()

def test_chord_member_notes_from_template():
    d = Drill(id="x", title="Em", type=DrillType.CHORD_SHAPE, tempo=60, bars=1,
              content={"chord": "Em"})
    arr = build_arrangement(d, Timeline(d.tempo, d.bars))
    # Em sounds strings 0,1,2,3,4,5 except none muted -> 6 notes, frets 0,2,2,0,0,0
    notes = arr["chords"][0]["notes"]
    assert {n["s"]: n["f"] for n in notes} == {0:0,1:2,2:2,3:0,4:0,5:0}

def test_finger_drill_walks_frets():
    d = Drill(id="f", title="String 5 1-2-3-4", type=DrillType.FINGER, tempo=60, bars=1,
              content={"string": 5, "frets": [1, 2, 3, 4]})
    arr = build_arrangement(d, Timeline(d.tempo, d.bars))
    assert [n["t"] for n in arr["notes"]] == [0.0, 1.0, 2.0, 3.0]
    assert [n["f"] for n in arr["notes"]] == [1, 2, 3, 4]
    assert all(n["s"] == 5 for n in arr["notes"])
    assert arr["chords"] == []
