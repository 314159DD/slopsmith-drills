from drills.spec import Drill, AudioStyle
from engine.timeline import Timeline

# piece ids: 0 = kick, 1 = snare, 2 = closed hat (mirrors lib/drums vocabulary)
KICK, SNARE, HAT = 0, 1, 2


def build_drum_tab(drill: Drill, timeline: Timeline) -> dict | None:
    if drill.audio_style not in (AudioStyle.DRUM, AudioStyle.BACKING):
        return None
    hits = []
    for bar_t in timeline.bar_start_times():
        for b in range(timeline.beats_per_bar):
            t = round(bar_t + b * timeline.beat_seconds, 4)
            hits.append({"t": t, "p": HAT})
            hits.append({"t": t, "p": KICK if b % 2 == 0 else SNARE})
    return {"hits": hits}
