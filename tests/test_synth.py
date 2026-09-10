import numpy as np
from engine.synth import SR, adsr, pluck, click_track

def test_sr_is_44100():
    assert SR == 44100

def test_adsr_length_and_bounds():
    env = adsr(1.0)
    assert len(env) == SR
    assert env.max() <= 1.0 + 1e-6
    assert env[0] <= env[int(SR*0.05)]  # attack rises

def test_pluck_is_nonsilent_correct_length():
    sig = pluck(midi=64, dur=0.5)
    assert len(sig) == int(0.5 * SR)
    assert np.abs(sig).max() > 0.01

def test_click_track_has_transients_at_beats():
    times = [0.0, 1.0, 2.0]
    track = click_track(times, total_dur=3.0)
    assert len(track) == int(3.0 * SR)
    # energy near each beat is much higher than mid-beat silence
    at_beat = np.abs(track[int(1.0*SR):int(1.0*SR)+200]).max()
    mid = np.abs(track[int(1.5*SR):int(1.5*SR)+200]).max()
    assert at_beat > mid * 5


from engine.synth import kick, snare, hat, drum_track

def test_drum_voices_nonsilent():
    for v in (kick(), snare(), hat()):
        assert np.abs(v).max() > 0.01

def test_drum_track_basic_rock_pattern():
    # 1 bar at 60bpm 4/4 = 4s; kick on 1&3, snare on 2&4, hat on every beat
    track = drum_track(bar_starts=[0.0], beat_seconds=1.0, beats_per_bar=4, total_dur=4.0)
    assert len(track) == int(4.0 * SR)
    assert np.abs(track).max() > 0.01


from engine.synth import strum, chord_backing_track

def test_strum_nonsilent():
    sig = strum([40, 47, 52, 56, 59, 64], dur=2.0)
    assert len(sig) == int(2.0 * SR)
    assert np.abs(sig).max() > 0.01

def test_chord_backing_track_length():
    track = chord_backing_track(
        events=[(0.0, [40,47,52,56,59,64]), (4.0, [48,52,55,60,64])],
        total_dur=8.0, strum_dur=4.0)
    assert len(track) == int(8.0 * SR)
    assert np.abs(track).max() > 0.01
