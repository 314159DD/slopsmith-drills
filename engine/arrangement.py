from drills.spec import Drill, DrillType
from drills.chord_library import CHORDS
from engine.timeline import Timeline

EMPTY_ARRANGEMENT = {
    "name": "Lead", "tuning": [0, 0, 0, 0, 0, 0], "capo": 0,
    "notes": [], "chords": [], "anchors": [], "handshapes": [],
    "templates": [], "beats": [], "sections": [],
}


def _chord_sequence(drill: Drill) -> list[str]:
    c = drill.content
    if "chords" in c:                       # change / mini-song
        seq = c["chords"]
        return [seq[b % len(seq)] for b in range(drill.bars)]
    if "chord" in c:                        # single chord held every bar
        return [c["chord"]] * drill.bars
    if "library" in c:                      # chord-library: one per bar in order
        names = c["library"]
        return [names[b % len(names)] for b in range(drill.bars)]
    raise ValueError(f"drill {drill.id} has no chord content")


def _template_index(templates: list[dict], shape) -> int:
    for i, tpl in enumerate(templates):
        if tpl["name"] == shape.name:
            return i
    templates.append(shape.template(len(templates)))
    return len(templates) - 1


def build_arrangement(drill: Drill, timeline: Timeline) -> dict:
    arr = {k: (v.copy() if isinstance(v, list) else v) for k, v in EMPTY_ARRANGEMENT.items()}
    arr["beats"] = timeline.beats_wire()

    if drill.type == DrillType.FINGER:
        string = drill.content["string"]
        frets = drill.content["frets"]
        beat_times = timeline.beat_times()
        for i, t in enumerate(beat_times):
            fr = frets[i % len(frets)]
            arr["notes"].append({"s": string, "f": fr, "t": round(t, 4),
                                 "sus": round(timeline.beat_seconds * 0.9, 4)})
        return arr

    seq = _chord_sequence(drill)
    bar_starts = timeline.bar_start_times()
    last_name = None
    for bar, name in enumerate(seq):
        shape = CHORDS[name]
        t = bar_starts[bar]
        tid = _template_index(arr["templates"], shape)
        member_notes = [
            {"s": s, "f": fr, "sus": round(timeline.beats_per_bar * timeline.beat_seconds, 4)}
            for s, fr in enumerate(shape.frets) if fr >= 0
        ]
        arr["chords"].append({"t": round(t, 4), "id": tid, "hd": False, "notes": member_notes})
        arr["handshapes"].append({
            "chord_id": tid, "start_time": round(t, 4),
            "end_time": round(t + timeline.beats_per_bar * timeline.beat_seconds, 4),
            "arp": False,
        })
        if name != last_name:
            arr["sections"].append({"name": name, "number": bar + 1, "time": round(t, 4)})
            last_name = name
    return arr
