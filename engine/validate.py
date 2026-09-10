import json
from pathlib import Path
import yaml


def _schema_warnings(pak: Path) -> list[str]:
    w = []
    man_path = pak / "manifest.yaml"
    if not man_path.exists():
        return [f"missing manifest.yaml in {pak.name}"]
    man = yaml.safe_load(man_path.read_text())
    if not isinstance(man, dict):
        return ["manifest.yaml must be a mapping at the top level"]
    for key in ("title", "duration", "arrangements", "stems"):
        if key not in man:
            w.append(f"manifest missing required key: {key}")
    for arr in man.get("arrangements", []):
        f = pak / arr.get("file", "")
        if not f.exists():
            w.append(f"arrangement file missing: {arr.get('file')}")
        else:
            data = json.loads(f.read_text())
            ids = {i for i, _ in enumerate(data.get("templates", []))}
            for c in data.get("chords", []):
                if c.get("id") not in ids:
                    w.append(f"chord at t={c.get('t')} references unknown template id {c.get('id')}")
    for st in man.get("stems", []):
        s = pak / st.get("file", "")
        if not s.exists() or s.stat().st_size == 0:
            w.append(f"stem missing or empty: {st.get('file')}")
    if "drum_tab" in man and not (pak / man["drum_tab"]).exists():
        w.append(f"drum_tab missing: {man['drum_tab']}")
    return w


def _loader_warnings(pak: Path) -> list[str]:
    """Best-effort load via vendored lib.sloppak; silent if unavailable."""
    import sys
    vendor = Path(__file__).resolve().parents[1] / "vendor" / "slopsmith"
    lib_dir = vendor / "lib"
    if not (lib_dir / "sloppak.py").exists():
        return []
    # the vendored repo uses flat imports from lib/ (`from song import ...`,
    # `from safepath import ...`), so lib/ itself must be importable
    if str(lib_dir) not in sys.path:
        sys.path.insert(0, str(lib_dir))
    try:
        import sloppak  # type: ignore
        sloppak.load_manifest(pak)   # raises on a malformed mapping
    except Exception as e:           # pragma: no cover - environment dependent
        return [f"lib.sloppak load error: {e}"]
    return []


def validate_sloppak(pak: Path) -> list[str]:
    pak = Path(pak)
    return _schema_warnings(pak) + _loader_warnings(pak)
