"""Safe, read-only access to public GitHub repositories.

Rules this module enforces: only github.com repo URLs, a throw-away directory, no repo code is ever
executed (no hooks, no installs), symlinks are not materialised, size and time are capped, and the
checkout is always deleted. Error messages never contain local paths.
"""
import os, re, shutil, subprocess, tempfile, time
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import urlparse

MAX_MB = 200
TIMEOUT_S = 90
DEPTH = 500

OWNER_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})$")
REPO_RE = re.compile(r"^[A-Za-z0-9._-]{1,100}$")
BRANCH_RE = re.compile(r"^[A-Za-z0-9._/-]{1,100}$")

class SourceError(Exception):
    """A problem the user can act on. str(e) is safe to show."""
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code

def parse_github_url(raw: str):
    raw = (raw or "").strip()
    if not raw or len(raw) > 300:
        raise SourceError("bad_url", "Paste a GitHub repository link, like https://github.com/owner/repo")
    if "://" not in raw:
        raw = "https://" + raw
    u = urlparse(raw)
    if u.scheme not in ("http", "https") or (u.hostname or "").lower() not in ("github.com", "www.github.com") \
            or u.username or u.password or u.port or u.query or u.fragment:
        raise SourceError("bad_url", "Only public github.com repository links are supported.")
    parts = [p for p in u.path.split("/") if p]
    if len(parts) < 2:
        raise SourceError("bad_url", "That link needs an owner and a repository: github.com/owner/repo")
    owner, repo = parts[0], parts[1]
    repo = repo[:-4] if repo.endswith(".git") else repo
    branch = None
    if len(parts) > 2:
        if parts[2] != "tree" or len(parts) < 4:
            raise SourceError("bad_url", "Use the repository's main link, or a /tree/<branch> link.")
        branch = "/".join(parts[3:])
        if ".." in branch or not BRANCH_RE.match(branch):
            raise SourceError("bad_url", "That branch name is not valid.")
    if not OWNER_RE.match(owner) or not REPO_RE.match(repo) or repo in (".", "..") or ".." in repo:
        raise SourceError("bad_url", "That does not look like a valid GitHub repository.")
    return owner, repo, branch

def _dir_mb(path: Path) -> float:
    total = 0
    for dp, _dn, fn in os.walk(path):
        for f in fn:
            try:
                total += os.lstat(os.path.join(dp, f)).st_size
            except OSError:
                pass
    return total / 1_048_576

def _clone(remote, dest: Path, branch, allow_file=False, timeout=TIMEOUT_S, max_mb=MAX_MB, depth=DEPTH):
    env = {**os.environ, "GIT_TERMINAL_PROMPT": "0", "GIT_ASKPASS": "echo", "GIT_LFS_SKIP_SMUDGE": "1",
           "GIT_CONFIG_NOSYSTEM": "1"}
    protos = ["-c", "protocol.allow=never", "-c", "protocol.https.allow=always"]
    if allow_file:  # tests only
        protos += ["-c", "protocol.file.allow=always"]
    cmd = ["git", *protos, "-c", "core.symlinks=false", "-c", "core.hooksPath=" + os.devnull,
           "clone", "--quiet", "--no-tags", "--single-branch", "--depth", str(depth)]
    if branch:
        cmd += ["--branch", branch]
    cmd += [remote, str(dest)]
    try:
        errf = tempfile.TemporaryFile("w+", encoding="utf-8", errors="ignore")
        proc = subprocess.Popen(cmd, env=env, stdout=subprocess.DEVNULL, stderr=errf, text=True)
    except OSError:
        raise SourceError("git_missing", "Git is not available on the server.")
    start = time.time()
    while proc.poll() is None:
        if time.time() - start > timeout:
            proc.kill(); proc.wait(); errf.close()
            raise SourceError("timeout", "Cloning took too long, so the scan was stopped. Try a smaller repository.")
        if dest.exists() and _dir_mb(dest) > max_mb:
            proc.kill(); proc.wait(); errf.close()
            raise SourceError("too_large", f"This repository is larger than the {max_mb} MB scan limit.")
        time.sleep(0.4)
    errf.seek(0); err = errf.read().lower(); errf.close()
    if proc.returncode != 0:
        if "not found" in err or "could not read username" in err or "authentication" in err or "403" in err:
            raise SourceError("not_found", "Repository not found, or it is private. CatchBlock only scans public repositories.")
        if "remote branch" in err:
            raise SourceError("no_branch", "That branch does not exist in the repository.")
        if "could not resolve" in err or "unable to access" in err or "timed out" in err:
            raise SourceError("network", "Could not reach GitHub. Check the connection and try again.")
        raise SourceError("clone_failed", "Could not clone that repository.")
    if _dir_mb(dest) > max_mb:
        raise SourceError("too_large", f"This repository is larger than the {max_mb} MB scan limit.")

@contextmanager
def checkout(url: str, _remote=None):
    """Yield (path, source_info) for a temporary read-only checkout; always cleaned up."""
    owner, repo, branch = parse_github_url(url)
    tmp = Path(tempfile.mkdtemp(prefix="catchblock-"))
    try:
        dest = tmp / "repo"
        remote = _remote or f"https://github.com/{owner}/{repo}.git"
        _clone(remote, dest, branch, allow_file=_remote is not None)
        info = {"type": "github", "owner": owner, "repo": repo, "name": f"{owner}/{repo}",
                "branch": branch, "url": f"https://github.com/{owner}/{repo}"}
        yield dest, info
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
