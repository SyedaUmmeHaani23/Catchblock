import json, re, tomllib
from pathlib import Path
from ..models import Finding

def _py_name(line: str):
    line = line.split("#")[0].strip()
    if not line or line.startswith(("-", "git+", "http")):
        return None
    m = re.match(r"^[A-Za-z0-9][A-Za-z0-9._-]*", line)
    return m.group(0).lower() if m else None

def collect_deps(root: Path) -> dict:
    """name -> ecosystem. Reads manifests only; nothing is installed or executed."""
    deps = {}
    pj = root / "package.json"
    if pj.is_file():
        try:
            d = json.loads(pj.read_text(encoding="utf-8", errors="ignore"))
            for k in ("dependencies", "devDependencies"):
                for n in (d.get(k) or {}):
                    deps[n.lower()] = "npm"
        except (ValueError, AttributeError):
            pass
    for rq in root.glob("requirements*.txt"):
        for line in rq.read_text(encoding="utf-8", errors="ignore").splitlines():
            n = _py_name(line)
            if n: deps[n] = "pip"
    pp = root / "pyproject.toml"
    if pp.is_file():
        try:
            d = tomllib.loads(pp.read_text(encoding="utf-8", errors="ignore"))
            for line in d.get("project", {}).get("dependencies", []):
                n = _py_name(line)
                if n: deps[n] = "pip"
        except tomllib.TOMLDecodeError:
            pass
    return deps

def check_deps(root: Path, rules=None):
    issues, manifests = [], 0
    pj = root / "package.json"
    if pj.is_file():
        manifests += 1
        try:
            d = json.loads(pj.read_text(encoding="utf-8", errors="ignore"))
            allv = {**(d.get("dependencies") or {}), **(d.get("devDependencies") or {})}
            loose = [n for n, v in allv.items() if str(v).strip() in ("*", "latest", "")]
            if loose:
                issues.append(f"{len(loose)} npm package(s) use '*' or 'latest' ({', '.join(loose[:3])})")
            if allv and not any((root / f).exists() for f in ("package-lock.json", "yarn.lock", "pnpm-lock.yaml", "bun.lockb")):
                issues.append("no npm lockfile committed")
        except (ValueError, AttributeError):
            issues.append("package.json is not valid JSON")
    for rq in root.glob("requirements*.txt"):
        manifests += 1
        lines = [l.split("#")[0].strip() for l in rq.read_text(encoding="utf-8", errors="ignore").splitlines()]
        pkgs = [l for l in lines if l and not l.startswith(("-", "git+", "http"))]
        unpinned = [l for l in pkgs if "==" not in l]
        if pkgs and len(unpinned) / len(pkgs) > 0.5:
            issues.append(f"{len(unpinned)} of {len(pkgs)} Python packages in {rq.name} are not pinned with ==")
    if not manifests:
        return None
    return Finding("deps.hygiene", "Dependencies", "warn" if issues else "pass", "low", 5,
                   "Dependency hygiene: " + "; ".join(issues) if issues else "Dependencies are declared and pinned sensibly",
                   "Unpinned or lockfile-less dependencies make builds unreproducible. CatchBlock checks pinning and lockfiles; "
                   "a live 'is it outdated' check needs registry access and is not run.")
