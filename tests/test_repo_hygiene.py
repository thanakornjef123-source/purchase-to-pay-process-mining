"""Deployment settings and repository hygiene."""
import re
import subprocess

import tomllib

TEXT_SUFFIXES = {".py", ".ipynb", ".md", ".toml", ".txt", ".bat", ".json", ".cfg", ".ini", ".yml", ".yaml", ".html"}


def _tracked_text_files(root):
    try:
        out = subprocess.run(["git", "ls-files"], cwd=root, capture_output=True, text=True, check=True).stdout
        files = [root / f for f in out.splitlines()]
    except (subprocess.CalledProcessError, FileNotFoundError):
        files = [p for p in root.rglob("*") if p.is_file() and ".git" not in p.parts]
    return [f for f in files if f.suffix in TEXT_SUFFIXES and "tests" not in f.parts]


def test_server_never_waits_for_input(root):
    cfg = tomllib.loads((root / ".streamlit" / "config.toml").read_text(encoding="utf-8"))
    assert cfg["server"]["headless"] is True


def test_static_fonts_exist(root):
    cfg = tomllib.loads((root / ".streamlit" / "config.toml").read_text(encoding="utf-8"))
    for face in cfg["theme"]["fontFaces"]:
        assert (root / face["url"].removeprefix("app/")).exists(), face["url"]


def test_no_machine_specific_paths(root):
    pattern = re.compile(r"[A-Za-z]:\\\\Users|[A-Za-z]:\\Users|/home/[a-z]+/|/Users/[A-Za-z]+/|/mnt/user-data")
    hits = [str(f.relative_to(root)) for f in _tracked_text_files(root)
            if pattern.search(f.read_text(encoding="utf-8", errors="ignore"))]
    assert not hits, hits


def test_no_secrets(root):
    pattern = re.compile(r"(api[_-]?key|secret|password|passwd|token)\s*[:=]\s*['\"][^'\"]{8,}", re.I)
    hits = [str(f.relative_to(root)) for f in _tracked_text_files(root)
            if pattern.search(f.read_text(encoding="utf-8", errors="ignore"))]
    assert not hits, hits
    assert not (root / ".streamlit" / "secrets.toml").exists()


def test_gitignore_covers_local_files(root):
    ignore = (root / ".gitignore").read_text(encoding="utf-8").splitlines()
    for entry in ("*.db", ".venv/", "__pycache__/", ".streamlit/secrets.toml"):
        assert entry in ignore, entry


def test_requirements_pinned(root):
    for name in ("requirements.txt", "requirements-analysis.txt"):
        lines = [ln.strip() for ln in (root / name).read_text(encoding="utf-8").splitlines()
                 if ln.strip() and not ln.startswith(("#", "-r"))]
        assert lines and all("==" in ln for ln in lines), (name, lines)
