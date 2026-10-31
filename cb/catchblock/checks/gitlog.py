import re, subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from ..models import Finding

VAGUE = {"fix", "fixed", "update", "updated", "changes", "commit", "wip", "test", "final", "."}
SEP = "\x1f"

def _git(root, *args, timeout=20):
    try:
        return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True,
                              encoding="utf-8", errors="ignore", timeout=timeout).stdout
    except (OSError, subprocess.SubprocessError):
        return ""

def read_log(root: Path):
    out = _git(root, "log", f"--pretty=format:@@%an{SEP}%aI{SEP}%s", "--shortstat")
    commits = []
    for line in out.splitlines():
        if line.startswith("@@"):
            a, d, s = line[2:].split(SEP, 2)
            commits.append({"author": a, "time": datetime.fromisoformat(d), "msg": s, "ins": 0})
        elif "insertion" in line and commits:
            m = re.search(r"(\d+) insertion", line)
            commits[-1]["ins"] = int(m.group(1))
    return commits or None

def is_shallow(root: Path) -> bool:
    return _git(root, "rev-parse", "--is-shallow-repository").strip() == "true"

def timeline(commits):
    buckets = Counter(c["time"].strftime("%Y-%m-%d %H:00") for c in commits)
    return [{"hour": h, "commits": n} for h, n in sorted(buckets.items())]

def _aware(s):
    d = datetime.fromisoformat(s)
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)

def event_window(rules):
    ev = (rules or {}).get("event", {})
    if ev.get("start") and ev.get("freeze"):
        return _aware(ev["start"]), _aware(ev["freeze"])
    return None

def flag_commits(commits, rules, limit=400):
    """Oldest-first list for the heartbeat chart. Flags are review signals, not proof of anything."""
    win = event_window(rules)
    total = sum(c["ins"] for c in commits)
    out = []
    ordered = list(reversed(commits))
    for i, c in enumerate(ordered):
        flags = []
        if win and i > 0:  # the first commit (repo setup) is allowed before the start
            if c["time"] < win[0]: flags.append("pre-start")
        if win and c["time"] > win[1]: flags.append("post-freeze")
        if total > 200 and c["ins"] / total > 0.6: flags.append("dump")
        out.append({"time": c["time"].isoformat(), "author": c["author"], "msg": c["msg"][:90], "ins": c["ins"], "flags": flags})
    return out[-limit:]

def check_license_first_commit(root: Path, rules, commits, shallow):
    if not (rules or {}).get("requirements", {}).get("license_from_first_commit"):
        return None
    if shallow:
        return Finding("license.first_commit", "Licence", "warn", "medium", 5,
                       "Cannot confirm the licence came with the first commit: only recent history was fetched",
                       "The event wants a licence from the very first commit. Run `catchblock scan` on a full local clone to verify.")
    roots = set(_git(root, "rev-list", "--max-parents=0", "HEAD").split())
    added = _git(root, "log", "--diff-filter=A", "--format=%H", "--", "LICENSE*", "COPYING*").split()
    if not added:
        return None  # no licence at all: license.exists already fails
    ok = bool(roots & set(added))
    return Finding("license.first_commit", "Licence", "pass" if ok else "fail", "high", 5,
                   "Licence was in the first commit" if ok else "Licence was added after the first commit",
                   "The event rules require the licence to be present from the first commit.")

def check_git(root: Path, rules=None, commits=None, shallow=False):
    commits = commits if commits is not None else read_log(root)
    if not commits:
        return [Finding("git.repo", "Git", "warn", "medium", 5, "No git history found",
                        "Reviewers read the commit history to see how the project was built.")]
    rules = rules or {}
    req = rules.get("requirements", {})
    win = event_window(rules)
    out = []
    n = len(commits)
    note = " (most recent only)" if shallow else ""
    out.append(Finding("git.history", "Git", "pass" if n >= 8 else "warn", "medium", 5,
                       (f"{n} commits{note}" if n >= 8 else f"Only {n} commits: commit smaller and more often"),
                       "Small, frequent commits show the work was done step by step."))
    if win:
        s, f = win
        body = commits[:-1]  # the first commit (repo setup) is allowed before the start
        bad = [c for c in body if not (s <= c["time"] <= f)]
        out.append(Finding("git.window", "Git", "pass" if not bad else "fail", "high", 5,
                           "All commits are inside the event window" if not bad else f"{len(bad)} commit(s) outside the event window",
                           "Code must be written during the event and commits after the freeze do not count. This is a signal for human review, not proof of anything."))
    authors = {c["author"] for c in commits}
    need = req.get("min_authors", 1)
    out.append(Finding("git.authors", "Git", "pass" if len(authors) >= need else "warn", "medium", 5,
                       f"{len(authors)} contributors" if len(authors) >= need else f"Only {len(authors)} contributor(s)",
                       "Several contributors make a project easier to maintain and review."))
    total = sum(c["ins"] for c in commits)
    big = max(c["ins"] for c in commits)
    dump = total > 200 and big / total > 0.6
    out.append(Finding("git.dump", "Git", "warn" if dump else "pass", "medium", 5,
                       "One commit holds most of the code" if dump else "No giant dump commit",
                       "Pushing everything at once hides how the project grew."))
    vague = sum(1 for c in commits if c["msg"].strip().lower() in VAGUE)
    out.append(Finding("git.messages", "Git", "warn" if vague / n > 0.3 else "pass", "low", 5,
                       f"{vague} vague commit message(s)" if vague / n > 0.3 else "Commit messages are descriptive",
                       "Messages like 'fix' or 'update' tell reviewers nothing."))
    lf = check_license_first_commit(root, rules, commits, shallow)
    if lf: out.append(lf)
    return out
