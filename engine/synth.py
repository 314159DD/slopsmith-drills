import numpy as np

SR = 44100


def midi_to_hz(midi: int) -> float:
    return 440.0 * 2 ** ((midi - 69) / 12.0)


def adsr(dur: float, a=0.01, d=0.08, s=0.6, r=0.1) -> np.ndarray:
    n = int(dur * SR)
    env = np.zeros(n, dtype=np.float32)
    if n == 0:
        return env
    na, nd, nr = int(a*SR), int(d*SR), int(r*SR)
    na, nd, nr = min(na, n), min(nd, max(n-na, 0)), min(nr, n)
    i = 0
    if na: env[:na] = np.linspace(0, 1, na, endpoint=False); i = na
    if nd: env[i:i+nd] = np.linspace(1, s, nd, endpoint=False); i += nd
    sus_end = max(n - nr, i)
    env[i:sus_end] = s
    if nr: env[sus_end:sus_end+ (n-sus_end)] = np.linspace(env[sus_end-1] if sus_end>0 else s, 0, n-sus_end)
    return env


def pluck(midi: int, dur: float, gain: float = 0.5) -> np.ndarray:
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = midi_to_hz(midi)
    # 3 partials for a slightly richer, guitar-ish tone
    wave = (np.sin(2*np.pi*f*t)
            + 0.5*np.sin(2*np.pi*2*f*t)
            + 0.25*np.sin(2*np.pi*3*f*t))
    return (wave * adsr(dur) * gain).astype(np.float32)


def click_track(times: list[float], total_dur: float, gain: float = 0.8) -> np.ndarray:
    out = np.zeros(int(total_dur * SR), dtype=np.float32)
    click = (np.sin(2*np.pi*1000*np.arange(int(0.02*SR))/SR)
             * np.linspace(1, 0, int(0.02*SR))).astype(np.float32)
    for t in times:
        start = int(t * SR)
        end = min(start + len(click), len(out))
        out[start:end] += click[:end-start] * gain
    return out


def kick(dur: float = 0.18) -> np.ndarray:
    n = int(dur * SR); t = np.arange(n) / SR
    f = np.linspace(120, 45, n)               # pitch drop
    env = np.exp(-t * 30)
    return (np.sin(2*np.pi*f*t) * env * 0.9).astype(np.float32)


def snare(dur: float = 0.16) -> np.ndarray:
    n = int(dur * SR); t = np.arange(n) / SR
    noise = np.random.default_rng(0).standard_normal(n)
    tone = np.sin(2*np.pi*180*t)
    env = np.exp(-t * 25)
    return ((0.7*noise + 0.3*tone) * env * 0.6).astype(np.float32)


def hat(dur: float = 0.05) -> np.ndarray:
    n = int(dur * SR); t = np.arange(n) / SR
    noise = np.random.default_rng(1).standard_normal(n)
    # crude high-pass: difference of noise
    hp = np.diff(noise, prepend=0.0)
    env = np.exp(-t * 80)
    return (hp * env * 0.3).astype(np.float32)


def _place(out: np.ndarray, voice: np.ndarray, t: float):
    start = int(t * SR); end = min(start + len(voice), len(out))
    out[start:end] += voice[:end-start]


def drum_track(bar_starts, beat_seconds, beats_per_bar, total_dur) -> np.ndarray:
    out = np.zeros(int(total_dur * SR), dtype=np.float32)
    k, s, h = kick(), snare(), hat()
    for bar_t in bar_starts:
        for b in range(beats_per_bar):
            bt = bar_t + b * beat_seconds
            _place(out, h, bt)                       # hat every beat
            if b % 2 == 0:
                _place(out, k, bt)                   # kick on 1 & 3
            else:
                _place(out, s, bt)                   # snare on 2 & 4
    return out


def strum(midis: list[int], dur: float, stagger: float = 0.012, gain: float = 0.22) -> np.ndarray:
    n = int(dur * SR)
    out = np.zeros(n, dtype=np.float32)
    for i, m in enumerate(midis):
        voice = pluck(m, dur, gain=gain)
        off = int(i * stagger * SR)               # downstroke time-stagger
        end = min(off + len(voice), n)
        out[off:end] += voice[:end-off]
    # add a low root an octave down for body
    if midis:
        bass = pluck(min(midis) - 12, dur, gain=gain*0.8)
        out[:len(bass)] += bass[:n]
    return out


def chord_backing_track(events, total_dur, strum_dur) -> np.ndarray:
    """events: list of (time_seconds, [midi,...]). Each chord rings strum_dur."""
    out = np.zeros(int(total_dur * SR), dtype=np.float32)
    for t, midis in events:
        sig = strum(midis, strum_dur)
        start = int(t * SR); end = min(start + len(sig), len(out))
        out[start:end] += sig[:end-start]
    return out
