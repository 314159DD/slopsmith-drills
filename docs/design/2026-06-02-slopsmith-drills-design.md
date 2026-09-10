# Slopsmith Drills - Design Spec

**Date:** 2026-06-02
**Status:** Approved design, pre-implementation

## 1. Purpose

A beginner guitar–learning resource for **Slopsmith Desktop**, delivered as custom
`.sloppak` "songs" that act as practice drills. A single **generator engine** emits
the drills; the focused chord trainer, the full beginner curriculum, the all-shapes
chord library, and unlimited custom variations are all *content produced by that one
engine*.

Target user: a brand-new guitarist (the author). Drills appear in Slopsmith's library
and play on the note highway like any song, with backing audio appropriate to each
drill type.

## 2. Goals / Non-goals

**Goals**
- One engine, declarative drill specs → valid `.sloppak` files with generated audio.
- A curated, sequenced beginner curriculum (open chords → changes → strumming → mini-songs → barre).
- A canonical, editable chord library (~56 shapes) used both as drill content and as an at-a-glance reference drill.
- CLI: build the whole curriculum, a single drill, or an ad-hoc custom drill.
- Output validates against Slopsmith's own `lib.sloppak` loader.

**Non-goals (YAGNI for v1)**
- No in-app Slopsmith plugin / UI (Approach B) - possible later front-end once the engine is proven.
- No Guitar Pro / MIDI authoring path (Approach C).
- No soundfont/fluidsynth rendering - numpy synthesis is sufficient for v1; soundfont is a later quality upgrade.
- No automatic scoring tuning - drills render the same whether or not the user has audio input wired.

## 3. Architecture

New standalone Python project, separate from the three JobFlowAI repos:

```
slopsmith-drills/
├─ vendor/slopsmith/          # the slopsmith repo, cloned, for lib.sloppak (validation) + format reference
├─ drills/
│  ├─ chord_library.py        # canonical shapes: name -> frets[6] + fingers[6]  (the "56")
│  ├─ curriculum.py           # ordered list of Drill specs (the course)
│  └─ spec.py                 # Drill dataclass: id, title, type, tempo, bars, repeats, audio_style, content
├─ engine/
│  ├─ timeline.py             # Timeline(tempo, bars) -> beat grid (single source of truth)
│  ├─ arrangement.py          # Drill spec + Timeline -> arrangement JSON (notes/chords/templates/beats/sections)
│  ├─ stem.py                 # Drill spec + Timeline -> stems/full.ogg (numpy synth -> WAV -> ffmpeg)
│  ├─ drum_tab.py             # Drill spec + Timeline -> drum_tab.json (for drum/backing styles)
│  └─ package.py              # assemble manifest.yaml + arrangement(s) + stem -> .sloppak dir; validate via lib.sloppak
├─ build_drills.py            # CLI entrypoint
├─ tests/
└─ out/                       # built .sloppak files (then copied to the library folder)
```

**Correctness rule - one timeline, two consumers.** `engine/timeline.py` computes the
beat grid from `(tempo, bars)`. Both `arrangement.py` (note/chord/`beats` times) and
`stem.py` (audio event times) derive from that same grid, so the highway and the audio
cannot drift.

**Reuse vs. build.** `lib.sloppak` is read-only (no writer), so we serialize `.sloppak`
ourselves (PyYAML + `json`). We import `lib.sloppak.load_song` / `load_manifest` only to
**validate** generated output. `lib.drums` is drum *notation* logic we mirror for
`drum_tab.json`. `lib.audio` confirms the encode path (ffmpeg → OGG Vorbis); we do not
use it directly.

## 4. The `.sloppak` output format (as authored)

Directory form (zipped only for sharing):

```
<drill-id>.sloppak/
├─ manifest.yaml
├─ arrangements/
│  └─ lead.json
├─ drum_tab.json            # only for drum/backing audio styles
└─ stems/
   └─ full.ogg
```

**manifest.yaml** (required: title, artist, duration, arrangements, stems):
```yaml
title: "Unit 2 · Drill 3 - Em ↔ E change @70"
artist: "Slopsmith Drills"
duration: 48.0
arrangements:
  - id: lead
    name: Lead
    file: arrangements/lead.json
    tuning: [0, 0, 0, 0, 0, 0]
    capo: 0
drum_tab: drum_tab.json        # omitted for click-only drills
stems:
  - id: full
    file: stems/full.ogg
    default: true
```

**arrangements/lead.json** uses the wire format (short keys). Top-level objects:
`name, tuning, capo, notes[], chords[], anchors[], handshapes[], templates[], beats[], sections[]`.

- **note**: `{t, s, f, sus, sl, slu, bn, ho, po, hm, hp, pm, mt, vb, tr, ac, tp, rh, pkd, ig}`
  (time, string 0=lowest, fret 0=open, sustain, slides, bend, technique flags…)
- **chord**: `{t, id, hd, notes:[{s,f,…}]}` - `id` indexes `templates`; member notes omit `t`.
- **template**: `{name, displayName, arp, fingers:[6], frets:[6]}` - the chord shape.
- **anchor**: `{time, fret, width}` (fretting-hand position).
- **handshape**: `{chord_id, start_time, end_time, arp}`.
- **beats**: `[{time, measure}]` (song-level; stored on first arrangement).
- **sections**: `[{name, number, time}]` (drill labels, e.g. "Em", "now: E").

## 5. Drill taxonomy

| Type | Content | Highway | Audio style |
|------|---------|---------|-------------|
| `finger` | one string, walk frets 1-2-3-4 (dexterity) | single notes | click |
| `chord-shape` | form one chord, strum each beat, hold | chord + template | click → drum |
| `chord-change` | alternate two chords per bar (e.g. G↔C) | chords + sections | drum groove |
| `strum-pattern` | one chord, a strumming rhythm (D-DU-UDU) | chords w/ pick dir | drum groove |
| `mini-song` | a 4-chord progression as a 30–60s song | chords + sections | full backing |
| `chord-library` | cycle through all shapes, one named per bar | chords + sections | drum |

Each drill = a `Drill` dataclass instance: `id, title, type, tempo, bars, repeats, audio_style, content` (content = chord names / fret pattern / progression depending on type).

## 6. Curriculum

`curriculum.py` orders drills into beginner units. `build_drills.py --all` builds every
unit plus the chord-library reference drill.

- **Unit 1 - Hands:** `finger` dexterity drills (each string, 1-2-3-4), picking timing. *click.*
- **Unit 2 - First open chords:** Em, E, A - `chord-shape` then `chord-change` pairs. *click→drum.*
- **Unit 3 - Core changes:** G, C, D added; the classic change pairs (G↔C, C↔D, Em↔C…). *drum.*
- **Unit 4 - The rest of the open chords:** Am, Dm, A7, D7, E7, etc. *drum.*
- **Unit 5 - Strumming:** one chord + common patterns. *drum.*
- **Unit 6 - Mini-songs:** 4-chord progressions (e.g. G-D-Em-C). *full backing.*
- **Unit 7 - Barre chords:** E-shape & A-shape, moving up the neck. *drum.*

## 7. Chord library (the "56")

`chord_library.py` - data-driven, editable. Seed set (≈50–60 shapes):
- Open **majors**: C A G E D F B · open **minors**: Am Em Dm Bm F#m
- **Dom7**: A7 B7 C7 D7 E7 G7 · **min7**: Am7 Bm7 Dm7 Em7 · **maj7**: Amaj7 Cmaj7 Dmaj7 Fmaj7 Gmaj7
- **sus**: Asus2 Asus4 Dsus2 Dsus4 Esus4 · **power**: E5 A5 D5
- **Barre system**: E-shape & A-shape (maj/min/7) generating remaining roots.

Each entry: `name`, `frets[6]` (−1 = muted, 0 = open), `fingers[6]`. Used directly as
arrangement chord `templates` (§4).

## 8. Audio pipeline (`engine/stem.py`)

numpy synthesis → 16-bit mono WAV (stdlib `wave`) → `ffmpeg -c:a libvorbis` → `stems/full.ogg`.

- **click**: sine/noise tick at each beat time from the Timeline.
- **drum kit**: synthesized `kick` (decaying sine ~60–120 Hz), `snare` (noise burst + 180 Hz tone), `hat` (high-passed noise); a small pattern library places hits per tempo. Drum/backing styles also emit `drum_tab.json` (§4) so Slopsmith shows the drum lane.
- **chord backing**: each chord's template → fretted pitches (standard tuning + capo) → summed harmonic partials with an ADSR pluck envelope, strings staggered ~15 ms for a strum, plus a root bass note. Strum times come from the Timeline.
- **mix**: sum tracks, peak-normalize to −1 dBFS, dither to int16.

`duration` in the manifest = Timeline total seconds (kept exact so scrubbing lines up).

## 9. Build / integration

- **Library target:** `C:\Slopsmith\Library` (writable, outside Program Files). The app's
  `dlc_dir` (in `…\slopsmith-config\config.json`, currently `C:\Program Files\Slopsmith\plugins`)
  is repointed here via Settings → DLC folder. The generator writes `.sloppak` dirs here;
  the app rescans and lists them.
- **CLI** (`build_drills.py`):
  - `--all` - build the full curriculum + chord-library drill into `--out` (default `out/`, or the library folder).
  - `--drill <id>` - rebuild one curriculum drill.
  - `--chords G,C,D --tempo 70 --type change [--bars 16]` - ad-hoc custom drill.
  - `--out <dir>` - write target (e.g. the library folder directly).
  - `--validate` - load each built pack with `lib.sloppak.load_song` and fail on warnings.

## 10. Dependencies

All present on the dev machine (verified 2026-06-02): Python 3.13, numpy 2.2.4,
PyYAML 6.0.2, ffmpeg 7.1.1 with libvorbis. The `slopsmith` repo is vendored under
`vendor/slopsmith` for `lib.sloppak` validation and format reference. No new system installs.

## 11. Testing

- **Unit:** `timeline.py` (beat grid math), `chord_library.py` (every shape has 6 frets +
  6 fingers, valid ranges), `arrangement.py` (chord references a real template; times within duration).
- **Integration:** build a sample drill of each type; load it with `lib.sloppak.load_song`
  and assert no warnings, expected arrangement counts, stem present and non-empty.
- **Audio sanity:** generated WAV/OGG is non-silent, correct duration (±1 frame), peak ≤ 0 dBFS.
- **End-to-end (manual):** build `--all` into the library; confirm drills appear and play in Slopsmith.

## 12. Risks / open items

- **stem required but no metronome mode** - mitigated: we always generate a stem.
- **Audio/highway alignment** - mitigated by the single-Timeline rule (§3).
- **Barre-system pitch/fret correctness** - covered by chord_library unit tests.
- **Format drift** if Slopsmith changes the wire format - vendored repo pins a known-good reference; `--validate` catches breakage.
- **Chord-backing realism** - synth is "good enough" for v1; soundfont rendering is a noted future upgrade.
