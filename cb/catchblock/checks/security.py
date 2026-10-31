import re
from pathlib import Path
from ..models import Finding

SKIP = {".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build", ".next"}
PATTERNS = {
    "AWS access key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "GitHub token": re.compile(r"gh[pousr]_[A-Za-z0-9]{36,}"),
    "Private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "API key assignment": re.compile(r"""(?i)(?:api[_-]?key|secret|token)\s*[:=]\s*['"][A-Za-z0-9_\-]{20,}['"]"""),
}

SKIP_SUFFIX = (".lock", ".min.js", ".min.css", ".map", "package-lock.json")

def _files(root: Path, limit=2000):
    n = 0
    for p in root.rglob("*"):
        if any(part in SKIP for part in p.relative_to(root).parts):
            continue
        if p.is_file() and not p.is_symlink() and not p.name.endswith(SKIP_SUFFIX) and p.stat().st_size < 200_000:
            n += 1
            if n > limit:
                return
            yield p

def scan_secrets(root: Path):
    hits = []
    for p in _files(root):
        rel = p.relative_to(root)
        if p.name == ".env":
            hits.append((str(rel), 0, ".env file committed"))
            continue
        try:
            data = p.read_bytes()
        except OSError:
            continue
        if b"\0" in data[:1024]:
            continue
        for i, line in enumerate(data.decode(errors="ignore").splitlines(), 1):
            for label, rx in PATTERNS.items():
                if rx.search(line):
                    hits.append((str(rel), i, label))
    return hits

def check_secrets(root: Path, rules=None):
    hits = scan_secrets(root)
    if not hits:
        return Finding("secrets.scan", "Security", "pass", "critical", 20,
                       "No leaked secrets found", "Leaked keys can be used by anyone who sees the repo.")
    where = "; ".join(f"{f}:{l} ({k})" for f, l, k in hits[:3])
    return Finding("secrets.scan", "Security", "fail", "critical", 20,
                   f"{len(hits)} possible secret(s): {where}",
                   "Anyone who can see the repo can use these keys. Rotate them and remove them from history.")


# ---------------------------------------------------------------------------------------------
# Secrets that were committed once and later deleted. They are gone from the files but still in
# git history, so anyone who clones the repo can read them. Values are never stored or shown.
# ---------------------------------------------------------------------------------------------
import subprocess

HISTORY_COMMITS = 300
HISTORY_TIMEOUT = 40
HISTORY_MAX_BYTES = 30_000_000
EXCLUDE = [":!*.lock", ":!*package-lock.json", ":!*.min.js", ":!*.min.css", ":!*.map", ":!*.svg"]

def _still_in_tree(root: Path, rel: str, rx) -> bool:
    p = root / rel
    try:
        return p.is_file() and not p.is_symlink() and p.stat().st_size < 200_000 and bool(rx.search(p.read_text(encoding="utf-8", errors="ignore")))
    except OSError:
        return False

def scan_history(root: Path, max_commits=HISTORY_COMMITS):
    """[(short_hash, path, label)] for secrets added in recent commits that are no longer in the files."""
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), "log", "-p", "-U0", "--no-color", "--no-ext-diff", "--diff-filter=AM",
             f"--max-count={max_commits}", "--pretty=format:@@@%h", "--", ".", *EXCLUDE],
            capture_output=True, timeout=HISTORY_TIMEOUT)
    except (OSError, subprocess.SubprocessError):
        return []
    text = proc.stdout[:HISTORY_MAX_BYTES].decode("utf-8", errors="ignore")
    commit, path, seen, hits = "", "", set(), []
    for line in text.splitlines():
        if line.startswith("@@@"):
            commit = line[3:]
        elif line.startswith("+++ b/"):
            path = line[6:]
            if any(part in SKIP for part in Path(path).parts):
                path = ""
        elif path and line.startswith("+") and not line.startswith("+++"):
            body = line[1:]
            for label, rx in PATTERNS.items():
                if rx.search(body) and (path, label) not in seen:
                    seen.add((path, label))
                    if not _still_in_tree(root, path, rx):
                        hits.append((commit, path, label))
    return hits

def check_history_secrets(root: Path, rules=None, has_history=True):
    if not has_history:
        return None
    hits = scan_history(root)
    if not hits:
        return Finding("secrets.history", "Security", "pass", "high", 10,
                       "No deleted secrets found in recent history",
                       "A key you delete is still readable in old commits. CatchBlock checked the most recent commits.")
    where = "; ".join(f"{h} {f} ({k})" for h, f, k in hits[:3])
    return Finding("secrets.history", "Security", "fail", "critical", 10,
                   f"{len(hits)} secret(s) were committed and deleted but are still in git history: {where}",
                   "Deleting a file does not delete it from history. Rotate the key first, then remove it from history "
                   "(for example with git filter-repo). Values are never shown here.")
