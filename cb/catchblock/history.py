"""Remembers past scores per repository so a report can show progress. Stored locally, never uploaded."""
import json, os, time
from pathlib import Path

MAX_RUNS, MAX_REPOS = 30, 200

def _file() -> Path:
    return Path(os.environ.get("CATCHBLOCK_HOME") or Path.home() / ".catchblock") / "history.json"

def key_for(url=None, path=None) -> str:
    if url:
        k = url.strip().lower().rstrip("/")
        return k[:-4] if k.endswith(".git") else k
    return str(Path(path or ".").resolve())

def record(key: str, score: int, now=None) -> dict:
    f = _file()
    try:
        data = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}
    except (OSError, ValueError):
        data = {}
    runs = data.get(key, [])
    prev = runs[-1]["score"] if runs else None
    runs = (runs + [{"t": int(now or time.time()), "score": int(score)}])[-MAX_RUNS:]
    data[key] = runs
    if len(data) > MAX_REPOS:  # forget the repos not scanned for longest
        for k in sorted(data, key=lambda k: data[k][-1]["t"])[: len(data) - MAX_REPOS]:
            del data[k]
    try:
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(json.dumps(data), encoding="utf-8")
    except OSError:
        pass  # history is a bonus: never fail a scan because of it
    return {"previous": prev, "delta": None if prev is None else int(score) - prev, "runs": runs[-12:]}
