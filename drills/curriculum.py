from drills.spec import Drill, DrillType, AudioStyle
from drills.chord_library import CHORDS


def _finger(id, title, string, tempo=60, bars=4):
    return Drill(id=id, title=title, type=DrillType.FINGER, tempo=tempo, bars=bars,
                 content={"string": string, "frets": [1, 2, 3, 4]},
                 audio_style=AudioStyle.CLICK)


def _shape(id, title, chord, tempo=70, bars=8, style=AudioStyle.DRUM):
    return Drill(id=id, title=title, type=DrillType.CHORD_SHAPE, tempo=tempo, bars=bars,
                 content={"chord": chord}, audio_style=style)


def _change(id, title, chords, tempo=70, bars=16, style=AudioStyle.DRUM):
    return Drill(id=id, title=title, type=DrillType.CHORD_CHANGE, tempo=tempo, bars=bars,
                 content={"chords": chords}, audio_style=style)


def _song(id, title, chords, tempo=80, bars=16):
    return Drill(id=id, title=title, type=DrillType.MINI_SONG, tempo=tempo, bars=bars,
                 content={"chords": chords}, audio_style=AudioStyle.BACKING)


def chord_library_drill() -> Drill:
    names = list(CHORDS.keys())
    return Drill(id="ref-chord-library", title="Chord Library · all shapes",
                 type=DrillType.CHORD_LIBRARY, tempo=60, bars=len(names),
                 content={"library": names}, audio_style=AudioStyle.DRUM)


CURRICULUM: list[Drill] = [
    # Unit 1 — Hands
    _finger("u1-d1", "Unit 1 · String 6 (low E) 1-2-3-4", string=0),
    _finger("u1-d2", "Unit 1 · String 1 (high e) 1-2-3-4", string=5),
    _finger("u1-d3", "Unit 1 · String 4 (D) 1-2-3-4", string=2),
    # Unit 2 — First open chords
    _shape("u2-d1", "Unit 2 · Em hold @70", "Em", style=AudioStyle.CLICK),
    _shape("u2-d2", "Unit 2 · E hold @70", "E"),
    _shape("u2-d3", "Unit 2 · A hold @70", "A"),
    _change("u2-d4", "Unit 2 · Em <-> E change @70", ["Em", "E"]),
    # Unit 3 — Core changes
    _shape("u3-d1", "Unit 3 · G hold @70", "G"),
    _shape("u3-d2", "Unit 3 · C hold @70", "C"),
    _shape("u3-d3", "Unit 3 · D hold @70", "D"),
    _change("u3-d4", "Unit 3 · G <-> C change @70", ["G", "C"]),
    _change("u3-d5", "Unit 3 · C <-> D change @70", ["C", "D"]),
    _change("u3-d6", "Unit 3 · Em <-> C change @70", ["Em", "C"]),
    # Unit 4 — Rest of the open chords + 7ths
    _shape("u4-d1", "Unit 4 · Am hold @70", "Am"),
    _shape("u4-d2", "Unit 4 · Dm hold @70", "Dm"),
    _change("u4-d3", "Unit 4 · Am <-> Dm change @70", ["Am", "Dm"]),
    _change("u4-d4", "Unit 4 · E7 <-> A7 change @70", ["E7", "A7"]),
    _change("u4-d5", "Unit 4 · D7 <-> G7 change @70", ["D7", "G7"]),
    # Unit 5 — Strumming (one chord, longer hold; pattern lives in audio)
    Drill(id="u5-d1", title="Unit 5 · G strum @80", type=DrillType.STRUM_PATTERN,
          tempo=80, bars=12, content={"chord": "G"}, audio_style=AudioStyle.DRUM),
    Drill(id="u5-d2", title="Unit 5 · C strum @80", type=DrillType.STRUM_PATTERN,
          tempo=80, bars=12, content={"chord": "C"}, audio_style=AudioStyle.DRUM),
    # Unit 6 — Mini-songs
    _song("u6-d1", "Unit 6 · G-D-Em-C @80", ["G", "D", "Em", "C"]),
    _song("u6-d2", "Unit 6 · Am-F-C-G @80", ["Am", "F", "C", "G"]),
    # Unit 7 — Barre chords
    _shape("u7-d1", "Unit 7 · F barre hold @70", "F"),
    _shape("u7-d2", "Unit 7 · Bm barre hold @70", "Bm"),
    _change("u7-d3", "Unit 7 · F <-> Bm change @70", ["F", "Bm"]),
]
