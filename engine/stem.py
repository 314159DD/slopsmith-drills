import subprocess, tempfile, wave
from pathlib import Path
import numpy as np

from drills.spec import Drill, DrillType, AudioStyle
from drills.chord_library import CHORDS, fretted_midi
from engine.timeline import Timeline
from engine import synth
from engine.arrangement import _chord_sequence


def _mix(drill: Drill, t: Timeline) -> np.ndarray:
    dur = t.duration
    out = np.zeros(int(dur * synth.SR), dtype=np.float32)
    bar_seconds = t.beats_per_bar * t.beat_seconds

    if drill.audio_style in (AudioStyle.CLICK, AudioStyle.DRUM, AudioStyle.BACKING):
        out += synth.click_track(t.beat_times(), dur, gain=0.35)
    if drill.audio_style in (AudioStyle.DRUM, AudioStyle.BACKING):
        d = synth.drum_track(t.bar_start_times(), t.beat_seconds, t.beats_per_bar, dur)
        out[:len(d)] += d
    if drill.audio_style == AudioStyle.BACKING and drill.type != DrillType.FINGER:
        seq = _chord_sequence(drill)
        events = [(t.bar_start_times()[b], fretted_midi(CHORDS[name]))
                  for b, name in enumerate(seq)]
        bt = synth.chord_backing_track(events, dur, strum_dur=bar_seconds)
        out[:len(bt)] += bt

    peak = np.abs(out).max()
    if peak > 0:
        out = out / peak * 0.89               # normalize to ~-1 dBFS
    return out


def _write_wav(samples: np.ndarray, path: Path):
    pcm = np.clip(samples, -1, 1)
    pcm = (pcm * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(synth.SR)
        w.writeframes(pcm.tobytes())


def render_stem(drill: Drill, timeline: Timeline, out_ogg: Path):
    out_ogg = Path(out_ogg)
    out_ogg.parent.mkdir(parents=True, exist_ok=True)
    samples = _mix(drill, timeline)
    with tempfile.TemporaryDirectory() as td:
        wav = Path(td) / "stem.wav"
        _write_wav(samples, wav)
        subprocess.run(
            ["ffmpeg","-y","-loglevel","error","-i",str(wav),
             "-c:a","libvorbis","-q:a","4", str(out_ogg)],
            check=True)
    return out_ogg
