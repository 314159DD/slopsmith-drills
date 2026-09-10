from drills.curriculum import CURRICULUM, chord_library_drill
from drills.spec import Drill, DrillType
from drills.chord_library import CHORDS

def test_curriculum_nonempty_unique_ids():
    assert len(CURRICULUM) >= 12
    ids = [d.id for d in CURRICULUM]
    assert len(ids) == len(set(ids))

def test_every_referenced_chord_exists():
    for d in CURRICULUM:
        for name in d.content.get("chords", []):
            assert name in CHORDS, f"{d.id} references missing chord {name}"
        if "chord" in d.content:
            assert d.content["chord"] in CHORDS

def test_chord_library_drill_covers_all_shapes():
    d = chord_library_drill()
    assert d.type == DrillType.CHORD_LIBRARY
    assert d.bars == len(CHORDS)
    assert set(d.content["library"]) == set(CHORDS.keys())
