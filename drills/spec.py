from dataclasses import dataclass
from enum import Enum


class DrillType(str, Enum):
    FINGER = "finger"
    CHORD_SHAPE = "chord-shape"
    CHORD_CHANGE = "chord-change"
    STRUM_PATTERN = "strum-pattern"
    MINI_SONG = "mini-song"
    CHORD_LIBRARY = "chord-library"


class AudioStyle(str, Enum):
    CLICK = "click"
    DRUM = "drum"
    BACKING = "backing"


@dataclass
class Drill:
    id: str
    title: str
    type: DrillType
    tempo: float
    bars: int
    content: dict           # type-specific: {"chord":...} | {"chords":[...]} | {"pattern":...}
    audio_style: AudioStyle = AudioStyle.DRUM
    repeats: int = 1
    beats_per_bar: int = 4
    artist: str = "Slopsmith Drills"
