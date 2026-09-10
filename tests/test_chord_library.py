from drills.chord_library import ChordShape, CHORDS, fretted_midi, STANDARD_TUNING_MIDI

def test_every_shape_well_formed():
    for name, shape in CHORDS.items():
        assert shape.name == name
        assert len(shape.frets) == 6
        assert len(shape.fingers) == 6
        for fr in shape.frets:
            assert -1 <= fr <= 15
        for fg in shape.fingers:
            assert -1 <= fg <= 4

def test_open_chords_present():
    for n in ["C", "A", "G", "E", "D", "Am", "Em", "Dm", "E7", "G7", "D7"]:
        assert n in CHORDS

def test_template_shape():
    tpl = CHORDS["E"].template(0)
    assert tpl["name"] == "E"
    assert tpl["frets"] == [0, 2, 2, 1, 0, 0]
    assert tpl["arp"] is False

def test_fretted_midi_e_major():
    # E major open: E2 B2 E3 G#3 B3 E4 -> midi 40,47,52,56,59,64
    assert fretted_midi(CHORDS["E"]) == [40, 47, 52, 56, 59, 64]

def test_fretted_midi_skips_muted():
    # C: x32010 -> strings 1..5 sound
    midis = fretted_midi(CHORDS["C"])
    assert len(midis) == 5
    assert midis[0] == 48  # C3 on A string fret 3


from drills.chord_library import barre_chord, register_barre_chords

def test_barre_f_major_is_e_shape_at_fret_1():
    f = barre_chord("F", "maj")
    assert f.frets == (1, 3, 3, 2, 1, 1)
    assert f.name == "F"

def test_barre_b_major_is_a_shape_at_fret_2():
    b = barre_chord("B", "maj", shape="A")
    assert b.frets == (-1, 2, 4, 4, 4, 2)

def test_barre_bm_is_a_shape_minor():
    bm = barre_chord("Bm", "min", shape="A")
    assert bm.frets == (-1, 2, 4, 4, 3, 2)

def test_register_adds_expected_names():
    reg = register_barre_chords()
    for n in ["F", "B", "Bm", "F#m", "C#m", "Bb"]:
        assert n in reg
    # combined with open chords we exceed 56 shapes
    from drills.chord_library import CHORDS
    assert len(CHORDS) >= 56
