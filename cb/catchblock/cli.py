import argparse, json, sys
from pathlib import Path

def _is_url(s):
    return s.startswith(("http://", "https://")) or s.lower().startswith(("github.com/", "www.github.com/"))

def main():
    ap = argparse.ArgumentParser(prog="catchblock", description="Catch issues before they catch you.")
    ap.add_argument("command", choices=["scan", "serve", "guard"])
    ap.add_argument("args", nargs="*", help="scan <path|github-url> | guard install|check|uninstall [path]")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--min-score", type=int, help="exit with code 1 if the score is lower (use as a CI gate)")
    ap.add_argument("--badge", metavar="FILE", help="write a health badge SVG to FILE")
    ap.add_argument("--markdown", action="store_true", help="print the report as a Markdown checklist")
    ap.add_argument("--rules", help="rulebook name (e.g. hacktoberfest) or path to a .toml file")
    a = ap.parse_args()
    if a.command == "serve":
        from .server import serve
        return serve()
    if a.command == "guard":
        from . import guard
        action = a.args[0] if a.args else "check"
        repo = Path(a.args[1] if len(a.args) > 1 else ".").resolve()
        try:
            if action == "install":
                print("Installed:", guard.install(repo, a.rules)); return
            if action == "uninstall":
                print("Removed" if guard.uninstall(repo) else "No CatchBlock hook found"); return
            report, blockers = guard.check(repo, a.rules)
        except ValueError as e:
            print(e); sys.exit(2)
        for b in blockers:
            print(f"  BLOCKED: {b['title']}")
        if blockers:
            sys.exit(1)
        print(f"CatchBlock: OK ({report['score']}/100)")
        return
    from .scanner import scan, scan_url
    a.rules = a.rules or "default"
    target = a.args[0] if a.args else "."
    try:
        r = scan_url(target, a.rules) if _is_url(target) else scan(target, a.rules)
    except Exception as e:
        print(f"Error: {e}"); sys.exit(2)
    if a.badge:
        from .badge import badge_svg
        Path(a.badge).write_text(badge_svg(r["score"], r["verdict"]), encoding="utf-8")
    low = a.min_score is not None and r["score"] < a.min_score
    if a.json:
        print(json.dumps(r, indent=2)); sys.exit(1 if low else 0)
    if a.markdown:
        print(r["checklist"]); sys.exit(1 if low else 0)
    print(f"Score {r['score']}/100  verdict: {r['verdict'].upper()}")
    for f in r["findings"]:
        print(f"  [{f['status'].upper():4}] {f['title']}")
    qw = r["quick_wins"]
    if qw["items"]:
        print(f"\nFix first (projected {qw['projected']}/100 after the suggested fixes):")
        for q in qw["items"]:
            print(f"  +{q['gain']:<3} {q['title']}" + ("   [auto-fix]" if q["auto"] else ""))
    if low:
        print(f"\nScore {r['score']} is below the required {a.min_score}."); sys.exit(1)

if __name__ == "__main__":
    main()
