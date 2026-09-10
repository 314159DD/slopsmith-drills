import argparse
import sys
from pathlib import Path

from drills.spec import Drill, DrillType, AudioStyle
from drills.curriculum import CURRICULUM, chord_library_drill
from engine.package import build_sloppak
from engine.validate import validate_sloppak

_TYPE_MAP = {
    "shape": DrillType.CHORD_SHAPE,
    "change": DrillType.CHORD_CHANGE,
    "strum": DrillType.STRUM_PATTERN,
    "song": DrillType.MINI_SONG,
}
_DEFAULT_STYLE = {
    DrillType.CHORD_SHAPE: AudioStyle.DRUM,
    DrillType.CHORD_CHANGE: AudioStyle.DRUM,
    DrillType.STRUM_PATTERN: AudioStyle.DRUM,
    DrillType.MINI_SONG: AudioStyle.BACKING,
}


def _all_drills() -> list[Drill]:
    return list(CURRICULUM) + [chord_library_drill()]


def _custom(args) -> Drill:
    dtype = _TYPE_MAP[args.type]
    chords = [c.strip() for c in args.chords.split(",") if c.strip()]
    content = {"chord": chords[0]} if dtype == DrillType.CHORD_SHAPE else {"chords": chords}
    cid = f"custom-{args.type}-{'-'.join(chords)}-{int(args.tempo)}".lower()
    return Drill(id=cid, title=f"Custom {args.type}: {'/'.join(chords)} @{int(args.tempo)}",
                 type=dtype, tempo=args.tempo, bars=args.bars, content=content,
                 audio_style=_DEFAULT_STYLE[dtype])


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Generate Slopsmith drill .sloppak files")
    p.add_argument("--all", action="store_true", help="build the whole curriculum")
    p.add_argument("--drill", help="build one curriculum drill by id")
    p.add_argument("--chords", help="ad-hoc drill: comma list, e.g. G,C,D")
    p.add_argument("--type", default="change", choices=list(_TYPE_MAP))
    p.add_argument("--tempo", type=float, default=70)
    p.add_argument("--bars", type=int, default=16)
    p.add_argument("--out", default="out", help="output directory")
    p.add_argument("--validate", action="store_true")
    args = p.parse_args(argv)

    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)

    if args.all:
        drills = _all_drills()
    elif args.drill:
        match = [d for d in _all_drills() if d.id == args.drill]
        if not match:
            print(f"unknown drill id: {args.drill}", file=sys.stderr); return 2
        drills = match
    elif args.chords:
        drills = [_custom(args)]
    else:
        p.error("specify --all, --drill <id>, or --chords <list>")

    failures = 0
    for d in drills:
        pak = build_sloppak(d, out)
        msg = f"built {pak.name}"
        if args.validate:
            warns = validate_sloppak(pak)
            if warns:
                failures += 1
                msg += "  [INVALID] " + "; ".join(warns)
        print(msg)
    if failures:
        print(f"{failures} pack(s) failed validation", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
