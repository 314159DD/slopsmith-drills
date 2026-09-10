import pytest
from engine.timeline import Timeline

def test_beat_seconds_at_60bpm():
    assert Timeline(tempo=60, bars=4).beat_seconds == 1.0

def test_duration_and_counts():
    t = Timeline(tempo=120, bars=8)  # 4/4 default
    assert t.total_beats == 32
    assert t.beat_seconds == 0.5
    assert t.duration == 16.0

def test_beat_times_first_and_last():
    t = Timeline(tempo=60, bars=2)
    times = t.beat_times()
    assert times[0] == 0.0
    assert times[-1] == 7.0  # 8 beats, last at index 7
    assert len(times) == 8

def test_beats_wire_measures():
    t = Timeline(tempo=60, bars=2)
    wire = t.beats_wire()
    assert wire[0] == {"time": 0.0, "measure": 1}
    assert wire[4]["measure"] == 2
    assert len(wire) == 8

def test_bar_start_times():
    t = Timeline(tempo=60, bars=3)
    assert t.bar_start_times() == [0.0, 4.0, 8.0]


# --- Input validation ---

def test_rejects_nonpositive_tempo():
    with pytest.raises(ValueError):
        Timeline(tempo=0, bars=4)
    with pytest.raises(ValueError):
        Timeline(tempo=-120, bars=4)


def test_rejects_nonpositive_bars():
    with pytest.raises(ValueError):
        Timeline(tempo=120, bars=0)


def test_rejects_nonpositive_beats_per_bar():
    with pytest.raises(ValueError):
        Timeline(tempo=120, bars=4, beats_per_bar=0)


# --- 3/4 time ---

def test_three_four_time():
    t = Timeline(tempo=60, bars=2, beats_per_bar=3)
    assert t.total_beats == 6
    assert t.bar_start_times() == [0.0, 3.0]
    assert t.beats_wire()[3]["measure"] == 2
