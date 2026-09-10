# Slopsmith Drills

A generator for guitar practice drills in the Slopsmith `.sloppak` format. One engine produces a seven-unit beginner curriculum, a full chord-shape reference, and unlimited ad-hoc drills, each with a note-highway arrangement, a drum tab where it helps, and synthesized backing audio locked to the same beat grid.

[![Tests](https://github.com/314159DD/slopsmith-drills/actions/workflows/test.yml/badge.svg)](https://github.com/314159DD/slopsmith-drills/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)

## What it generates

| Set | Contents |
|---|---|
| Curriculum | 7 units: finger dexterity, open chords, chord changes, strumming, mini-songs, barre chords |
| Chord library | Every open and barre shape as a reference drill |
| Ad-hoc | Any chord set, tempo, drill type, and bar count from the command line |

Drill types: `shape` (hold one chord), `change` (alternate chords per bar), `strum` (one chord over a drum groove), `song` (progression with full backing).

## How it works

```
Drill spec (chords, tempo, bars, type)
   |
   +--> timeline.py     beat grid: bar / beat / sample positions from the tempo
   +--> arrangement.py  note-highway events on that grid (frets, strings, durations)
   +--> drum_tab.py     kick / snare / hat pattern on the same grid
   +--> synth.py        backing audio rendered sample-locked to the grid
   +--> stem.py         encode to Ogg Vorbis via ffmpeg
   +--> package.py      write the .sloppak (manifest, arrangement, tab, audio)
   +--> validate.py     optional: load the pack through Slopsmith's own loader
```

The point of the shared timeline is that the highway, the drum tab, and the audio never drift: every event is placed at a sample index derived from one tempo map, so a chord change on beat 1 of bar 9 lands on the same sample in all three.

## Build

```
pip install -r requirements.txt
git clone --depth 1 https://github.com/slopsmith/slopsmith.git vendor/slopsmith   # optional, enables --validate
python build_drills.py --all --out "<your Slopsmith library>" --validate
```

Point Slopsmith (Settings > DLC folder) at the output folder or any parent of it and rescan.

Requires Python 3.11+, numpy, PyYAML, and ffmpeg with libvorbis on PATH.

## Ad-hoc drills

```
python build_drills.py --chords G,C,D --tempo 70 --type change --bars 16 --out "<library>"
python build_drills.py --drill u3-d4 --out "<library>" --validate      # one curriculum drill
```

## Tests

```
pytest
```

47 tests over the timeline math, arrangement placement, drum patterns, synthesis, packaging, validation, and the curriculum definitions. The packaging and stem tests call ffmpeg, so it must be on PATH.

## Project structure

```
build_drills.py      CLI
drills/              Drill spec model, curriculum, chord library
engine/              timeline, arrangement, drum_tab, synth, stem, package, validate
tests/               47 tests
docs/design/         Design spec
```

## License

MIT. See [LICENSE](LICENSE).
