import difflib, uuid
from pathlib import Path

_JOURNALS = {}  # undo_id -> (root, entries)

def _rd(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="ignore")

def _wr(p: Path, text: str):
    p.write_text(text, encoding="utf-8", newline="\n")

def _new_text(root: Path, fx: dict):
    """The text the file would have after this fix, or None if the fix would be skipped."""
    target = (root / fx["path"]).resolve()
    if root not in target.parents:
        return None, None, "outside the repository"
    old = _rd(target) if target.is_file() else ""
    if fx.get("mode", "create") == "create":
        if target.exists():
            return target, None, "file already exists"
        return target, fx["content"], None
    first = fx["content"].strip().splitlines()[0]
    if first in old:
        return target, None, "already added"
    return target, old.rstrip("\n") + ("\n\n" if old else "") + fx["content"], None

def make_diff(root: Path, fx) -> str:
    """A git-style diff for one fix (accepts a Fix or a dict). `git apply` can apply it to the repo."""
    fx = fx if isinstance(fx, dict) else fx.__dict__
    root = Path(root).resolve()
    target, new, why = _new_text(root, fx)
    if new is None:
        return ""
    old = _rd(target) if target.is_file() else ""
    if new and not new.endswith("\n"):
        new += "\n"
    if old and not old.endswith("\n"):
        old += "\n"
    rel = fx["path"].replace("\\", "/")
    body = "".join(difflib.unified_diff(old.splitlines(True), new.splitlines(True),
                                        "/dev/null" if not old else f"a/{rel}", f"b/{rel}"))
    head = f"diff --git a/{rel} b/{rel}\n" + ("new file mode 100644\n" if not old else "")
    return head + body

def _apply(root: Path, findings: list, only=None):
    root = root.resolve()
    applied, skipped, journal = [], [], []
    for f in findings:
        fx = f.get("fix")
        if not fx or f["status"] == "pass" or (only and f["id"] not in only):
            continue
        target, new, why = _new_text(root, fx)
        if new is None:
            skipped.append({"id": f["id"], "reason": why}); continue
        before = _rd(target) if target.is_file() else None
        target.parent.mkdir(parents=True, exist_ok=True)
        _wr(target, new)
        journal.append({"path": fx["path"], "kind": "created" if before is None else "appended", "before": before, "after": _rd(target)})
        applied.append({"id": f["id"], "path": fx["path"]})
    return applied, skipped, journal

def apply_fixes(root: Path, findings: list, only=None):
    """Apply suggested fixes safely: stay inside the repo, never overwrite, never delete."""
    applied, skipped, _ = _apply(Path(root), findings, only)
    return applied, skipped

def apply_with_undo(root: Path, findings: list, only=None):
    applied, skipped, journal = _apply(Path(root), findings, only)
    uid = None
    if journal:
        uid = uuid.uuid4().hex[:12]
        _JOURNALS[uid] = (Path(root).resolve(), journal)
        while len(_JOURNALS) > 50:
            _JOURNALS.pop(next(iter(_JOURNALS)))
    return applied, skipped, uid

def undo(uid: str):
    if uid not in _JOURNALS:
        raise ValueError("Nothing to undo for that id")
    root, entries = _JOURNALS.pop(uid)
    reverted, skipped = [], []
    for e in reversed(entries):
        t = (root / e["path"]).resolve()
        if root not in t.parents or not t.is_file() or _rd(t) != e["after"]:
            skipped.append({"path": e["path"], "reason": "changed since the fix was applied"}); continue
        if e["kind"] == "created":
            t.unlink()
            d = t.parent
            while d != root and not any(d.iterdir()):
                d.rmdir(); d = d.parent
        else:
            _wr(t, e["before"])
        reverted.append(e["path"])
    return reverted, skipped
