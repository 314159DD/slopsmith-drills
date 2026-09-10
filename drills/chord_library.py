from dataclasses import dataclass

# Open-string MIDI for standard tuning, low E (string 0) -> high e (string 5)
STANDARD_TUNING_MIDI = (40, 45, 50, 55, 59, 64)


@dataclass(frozen=True)
class ChordShape:
    name: str
    frets: tuple[int, ...]    # length 6, -1 = muted, 0 = open
    fingers: tuple[int, ...]  # length 6, -1 = none, 0 = open, 1-4 = finger

    def template(self, index: int) -> dict:
        return {
            "name": self.name,
            "displayName": self.name,
            "arp": False,
            "fingers": list(self.fingers),
            "frets": list(self.frets),
        }


def fretted_midi(shape: ChordShape, capo: int = 0) -> list[int]:
    """MIDI note for every sounding string, low-to-high."""
    notes = []
    for s, fr in enumerate(shape.frets):
        if fr < 0:
            continue
        notes.append(STANDARD_TUNING_MIDI[s] + capo + fr)
    return notes


def _c(name, frets, fingers):
    return ChordShape(name, tuple(frets), tuple(fingers))


CHORDS: dict[str, ChordShape] = {
    # open majors
    "C":  _c("C",  [-1,3,2,0,1,0], [-1,3,2,0,1,0]),
    "A":  _c("A",  [-1,0,2,2,2,0], [-1,0,1,2,3,0]),
    "G":  _c("G",  [3,2,0,0,0,3],  [2,1,0,0,0,3]),
    "E":  _c("E",  [0,2,2,1,0,0],  [0,2,3,1,0,0]),
    "D":  _c("D",  [-1,-1,0,2,3,2],[-1,-1,0,1,3,2]),
    # open minors
    "Am": _c("Am", [-1,0,2,2,1,0], [-1,0,2,3,1,0]),
    "Em": _c("Em", [0,2,2,0,0,0],  [0,2,3,0,0,0]),
    "Dm": _c("Dm", [-1,-1,0,2,3,1],[-1,-1,0,2,3,1]),
    # dominant 7
    "A7": _c("A7", [-1,0,2,0,2,0], [-1,0,2,0,3,0]),
    "B7": _c("B7", [-1,2,1,2,0,2], [-1,2,1,3,0,4]),
    "C7": _c("C7", [-1,3,2,3,1,0], [-1,3,2,4,1,0]),
    "D7": _c("D7", [-1,-1,0,2,1,2],[-1,-1,0,2,1,3]),
    "E7": _c("E7", [0,2,0,1,0,0],  [0,2,0,1,0,0]),
    "G7": _c("G7", [3,2,0,0,0,1],  [3,2,0,0,0,1]),
    # minor 7
    "Am7":_c("Am7",[-1,0,2,0,1,0], [-1,0,2,0,1,0]),
    "Dm7":_c("Dm7",[-1,-1,0,2,1,1],[-1,-1,0,3,1,2]),
    "Em7":_c("Em7",[0,2,0,0,0,0],  [0,2,0,0,0,0]),
    # major 7
    "Cmaj7":_c("Cmaj7",[-1,3,2,0,0,0],[-1,3,2,0,0,0]),
    "Fmaj7":_c("Fmaj7",[-1,-1,3,2,1,0],[-1,-1,3,2,1,0]),
    "Gmaj7":_c("Gmaj7",[3,2,0,0,0,2],[3,2,0,0,0,2]),
    "Amaj7":_c("Amaj7",[-1,0,2,1,2,0],[-1,0,2,1,3,0]),
    "Dmaj7":_c("Dmaj7",[-1,-1,0,2,2,2],[-1,-1,0,1,1,1]),
    # sus
    "Asus2":_c("Asus2",[-1,0,2,2,0,0],[-1,0,1,2,0,0]),
    "Asus4":_c("Asus4",[-1,0,2,2,3,0],[-1,0,1,2,3,0]),
    "Dsus2":_c("Dsus2",[-1,-1,0,2,3,0],[-1,-1,0,1,2,0]),
    "Dsus4":_c("Dsus4",[-1,-1,0,2,3,3],[-1,-1,0,1,2,3]),
    "Esus4":_c("Esus4",[0,2,2,2,0,0],[0,1,2,3,0,0]),
    # power chords
    "E5": _c("E5", [0,2,2,-1,-1,-1],[0,1,3,-1,-1,-1]),
    "A5": _c("A5", [-1,0,2,2,-1,-1],[-1,0,1,3,-1,-1]),
    "D5": _c("D5", [-1,-1,0,2,3,-1],[-1,-1,0,1,3,-1]),
}


# --- Movable barre shapes -------------------------------------------------
# Root pitch classes (C=0). Sharps only; we map flats to sharps for lookup.
_PC = {"C":0,"C#":1,"Db":1,"D":2,"D#":3,"Eb":3,"E":4,"F":5,"F#":6,"Gb":6,
       "G":7,"G#":8,"Ab":8,"A":9,"A#":10,"Bb":10,"B":11}

# Relative fret offsets from the barre fret, and fingers, per shape+quality.
# E-shape: root on string 0 (low E). A-shape: root on string 1 (A), string 0 muted.
_BARRE = {
    ("E","maj"): ([0,2,2,1,0,0], [1,3,4,2,1,1]),
    ("E","min"): ([0,2,2,0,0,0], [1,3,4,1,1,1]),
    ("E","7"):   ([0,2,0,1,0,0], [1,3,1,2,1,1]),
    ("E","m7"):  ([0,2,0,0,0,0], [1,3,1,1,1,1]),
    ("A","maj"): ([-99,0,2,2,2,0],[-1,1,3,3,3,1]),
    ("A","min"): ([-99,0,2,2,1,0],[-1,1,3,4,2,1]),
    ("A","7"):   ([-99,0,2,0,2,0],[-1,1,3,1,4,1]),
    ("A","m7"):  ([-99,0,2,0,1,0],[-1,1,3,1,2,1]),
}
# Barre fret that places the root note in a comfortable low position (frets 1-8).
_ROOT_STRING_OPEN = {"E": STANDARD_TUNING_MIDI[0], "A": STANDARD_TUNING_MIDI[1]}


def barre_chord(name: str, quality: str, shape: str = "E") -> ChordShape:
    # parse root from the display name (strip quality suffixes)
    root = name
    for suf in ("maj7", "m7", "maj", "min", "m", "7"):
        if root.endswith(suf):
            root = root[: -len(suf)]
            break
    root = root or name
    pc = _PC[root]
    open_pc = _ROOT_STRING_OPEN[shape] % 12
    barre_fret = (pc - open_pc) % 12
    if barre_fret == 0:
        barre_fret = 12  # avoid open; use the octave barre
    rel, fingers = _BARRE[(shape, quality)]
    frets = []
    for r in rel:
        frets.append(-1 if r == -99 else barre_fret + r)
    return ChordShape(name, tuple(frets), tuple(fingers))


def register_barre_chords() -> dict[str, ChordShape]:
    """Add a useful set of barre chords to CHORDS; return the additions."""
    wanted = [
        # majors
        ("F", "maj", "E"), ("F#", "maj", "E"), ("G#", "maj", "E"),
        ("Bb", "maj", "A"), ("B", "maj", "A"), ("C#", "maj", "A"),
        ("Eb", "maj", "A"),
        # minors
        ("Bm", "min", "A"), ("F#m", "min", "E"), ("C#m", "min", "A"),
        ("G#m", "min", "E"), ("Cm", "min", "A"), ("Gm", "min", "E"),
        ("Fm", "min", "E"), ("Bbm", "min", "A"), ("Ebm", "min", "A"),
        # dominant 7 (barre voicings for roots without open shapes)
        ("F7", "7", "E"), ("F#7", "7", "E"), ("G#7", "7", "E"),
        ("Bb7", "7", "A"), ("C#7", "7", "A"), ("Eb7", "7", "A"),
        # minor 7
        ("Bm7", "m7", "A"), ("F#m7", "m7", "E"), ("C#m7", "m7", "A"),
        ("G#m7", "m7", "E"), ("Cm7", "m7", "A"), ("Gm7", "m7", "E"),
        ("Fm7", "m7", "E"), ("Bbm7", "m7", "A"),
    ]
    added = {}
    for name, quality, shape in wanted:
        c = barre_chord(name, quality, shape=shape)
        CHORDS[name] = c
        added[name] = c
    return added


# Register on import so CHORDS is complete everywhere it is used.
register_barre_chords()
