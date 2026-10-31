import os, stat, subprocess, sys
from pathlib import Path
from .scanner import scan

MARK = "# CatchBlock pre-push guard"

def _hook_path(repo: Path) -> Path:
    out = subprocess.run(["git", "-C", str(repo), "rev-parse", "--git-path", "hooks/pre-push"],
                         capture_output=True, text=True).stdout.strip()
    if not out:
        raise ValueError("Not a git repository")
    p = Path(out)
    return p if p.is_absolute() else (repo / p)

def install(repo: Path, rules=None) -> Path:
    hook = _hook_path(repo)
    if hook.exists() and MARK not in hook.read_text(encoding="utf-8", errors="ignore"):
        raise ValueError("A different pre-push hook already exists; not overwriting it")
    pkg_parent = Path(__file__).resolve().parent.parent.as_posix()
    rules_arg = f' --rules "{rules}"' if rules else ""
    hook.parent.mkdir(parents=True, exist_ok=True)
    hook.write_text(f'#!/bin/sh\n{MARK}\nPYTHONPATH="{pkg_parent}" "{Path(sys.executable).as_posix()}" -m catchblock.cli guard check .{rules_arg} \\\n'
                    f'  || {{ echo "Push blocked by CatchBlock. To push anyway: git push --no-verify"; exit 1; }}\n', encoding="utf-8", newline="\n")
    hook.chmod(hook.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return hook

def uninstall(repo: Path) -> bool:
    hook = _hook_path(repo)
    if hook.exists() and MARK in hook.read_text(encoding="utf-8", errors="ignore"):
        hook.unlink(); return True
    return False

def check(repo: Path, rules=None):
    """Blocks only on critical problems: a leaked secret or no licence."""
    r = scan(str(repo), rules)
    blockers = [f for f in r["findings"] if f["status"] == "fail" and (f["id"].startswith("secrets.") or f["id"] == "license.exists")]
    return r, blockers
