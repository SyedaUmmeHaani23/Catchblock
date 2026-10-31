import tomllib
from pathlib import Path

RULES_DIR = Path(__file__).resolve().parent.parent / "rules"

def list_rules():
    out = []
    for p in sorted(RULES_DIR.glob("*.toml")):
        try:
            data = tomllib.loads(p.read_text(encoding="utf-8"))
        except (OSError, tomllib.TOMLDecodeError):
            continue
        out.append({"id": p.stem, "name": data.get("event", {}).get("name", p.stem),
                    "start": data.get("event", {}).get("start"), "freeze": data.get("event", {}).get("freeze")})
    return out

def load_rules(spec, allow_path=True):
    """spec: None, a dict, a rulebook name from rules/, or (CLI only) a path to a .toml file."""
    if not spec:
        return {}
    if isinstance(spec, dict):
        return spec
    named = RULES_DIR / f"{Path(str(spec)).stem}.toml"
    if named.is_file():
        return tomllib.loads(named.read_text(encoding="utf-8"))
    if allow_path and Path(str(spec)).is_file():
        return tomllib.loads(Path(str(spec)).read_text(encoding="utf-8"))
    raise ValueError("Unknown rulebook")
