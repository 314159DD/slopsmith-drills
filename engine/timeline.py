from dataclasses import dataclass


@dataclass(frozen=True)
class Timeline:
    """The single source of truth for a drill's beat grid.

    Both the arrangement (note/chord/beat times) and the audio stem derive
    their event times from this object so they can never drift apart.
    """
    tempo: float            # beats per minute
    bars: int
    beats_per_bar: int = 4

    def __post_init__(self) -> None:
        if self.tempo <= 0:
            raise ValueError(f"tempo must be > 0, got {self.tempo}")
        if self.bars <= 0:
            raise ValueError(f"bars must be > 0, got {self.bars}")
        if self.beats_per_bar <= 0:
            raise ValueError(f"beats_per_bar must be > 0, got {self.beats_per_bar}")

    @property
    def beat_seconds(self) -> float:
        return 60.0 / self.tempo

    @property
    def total_beats(self) -> int:
        return self.bars * self.beats_per_bar

    @property
    def duration(self) -> float:
        return self.total_beats * self.beat_seconds

    def beat_times(self) -> list[float]:
        return [round(i * self.beat_seconds, 6) for i in range(self.total_beats)]

    def bar_start_times(self) -> list[float]:
        step = self.beats_per_bar * self.beat_seconds
        return [round(b * step, 6) for b in range(self.bars)]

    def beats_wire(self) -> list[dict]:
        out = []
        for i in range(self.total_beats):
            out.append({
                "time": round(i * self.beat_seconds, 6),
                "measure": i // self.beats_per_bar + 1,
            })
        return out
