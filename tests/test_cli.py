import sys, subprocess
from pathlib import Path

def _run(args, cwd):
    return subprocess.run([sys.executable, "build_drills.py", *args],
                          cwd=cwd, capture_output=True, text=True)

ROOT = Path(__file__).resolve().parents[1]

def test_cli_custom_change(tmp_path):
    r = _run(["--chords","G,C,D","--tempo","70","--type","change",
              "--bars","8","--out",str(tmp_path)], ROOT)
    assert r.returncode == 0, r.stderr
    paks = list(tmp_path.glob("*.sloppak"))
    assert len(paks) == 1
    assert (paks[0] / "manifest.yaml").exists()

def test_cli_single_curriculum_drill(tmp_path):
    r = _run(["--drill","u3-d4","--out",str(tmp_path),"--validate"], ROOT)
    assert r.returncode == 0, r.stderr
    assert (tmp_path / "u3-d4.sloppak").exists()

def test_cli_all_builds_curriculum(tmp_path):
    r = _run(["--all","--out",str(tmp_path)], ROOT)
    assert r.returncode == 0, r.stderr
    from drills.curriculum import CURRICULUM
    # curriculum + chord-library reference drill
    assert len(list(tmp_path.glob("*.sloppak"))) == len(CURRICULUM) + 1
