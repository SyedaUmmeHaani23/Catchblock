from dataclasses import asdict, replace
from pathlib import Path
from .checks import files, security, project, gitlog, ai, deps
from .fixes import make_diff
from .plain import plain_for
from .report_md import checklist_md
from .rules import load_rules
from .score import POINTS, compute

CHECKS = [files.check_license, project.check_license_type, files.check_readme, files.check_gitignore,
          security.check_secrets, project.check_ci, project.check_tests, project.check_contributing,
          ai.check_ai_disclosure, ai.check_credits, deps.check_deps]

def quick_wins(findings, limit=5):
    """What to fix first. Gains are exact for the weighting we use; the projected score assumes each
    suggested fix is applied (an AI-disclosure fix only adds a placeholder, so it is counted as half)."""
    total = sum(f.weight for f in findings) or 1
    license_fix = any(f.id == "license.exists" and f.status != "pass" and f.fix for f in findings)
    after, rows = [], []
    for f in findings:
        new = f.status
        if f.status != "pass":
            if f.fix:
                new = "warn" if f.id == "disclosure.ai" else "pass"
            elif f.id == "license.type" and license_fix:
                new = "pass"  # the generated MIT licence satisfies this too
        after.append(replace(f, status=new))
        if f.status != "pass":
            auto = new != f.status
            target = new if auto else "pass"
            gain = 100 * f.weight * (POINTS[target] - POINTS[f.status]) / total
            if gain > 0:
                rows.append({"id": f.id, "title": f.title, "severity": f.severity, "auto": auto, "gain": gain})
    if license_fix:  # one row for "add a licence": its type check passes automatically once it exists
        lic = next((r for r in rows if r["id"] == "license.exists"), None)
        typ = next((r for r in rows if r["id"] == "license.type"), None)
        if lic and typ:
            lic["gain"] += typ["gain"]
            rows.remove(typ)
    for r in rows:
        r["gain"] = max(1, round(r["gain"]))
    rows.sort(key=lambda r: (-r["gain"], not r["auto"]))
    projected, verdict = compute(after)
    return {"items": rows[:limit], "projected": projected, "projected_verdict": verdict,
            "auto_count": sum(1 for r in rows if r["auto"])}

def scan(path: str, rules=None, source=None, expose_path=True) -> dict:
    root = Path(path).resolve()
    if not root.is_dir():
        raise ValueError("That folder does not exist")
    rules = load_rules(rules)
    findings = [f for f in (c(root, rules) for c in CHECKS) if f]
    commits = gitlog.read_log(root)
    shallow = gitlog.is_shallow(root) if commits else False
    findings += gitlog.check_git(root, rules, commits, shallow)
    hs = security.check_history_secrets(root, rules, has_history=bool(commits))
    if hs:
        findings.append(hs)
    score, verdict = compute(findings)
    out = []
    for f in findings:
        d = asdict(f)
        d["plain"] = plain_for(f.id)
        if f.fix and f.status != "pass":
            d["fix"]["diff"] = make_diff(root, f.fix)
        elif f.fix:
            d["fix"] = None
        out.append(d)
    ev = rules.get("event", {})
    report = {"source": source or {"type": "local", "name": root.name},
              "score": score, "verdict": verdict, "quick_wins": quick_wins(findings),
              "event": {"name": ev.get("name"), "start": ev.get("start"), "freeze": ev.get("freeze")} if ev else None,
              "history": {"commits": len(commits or []), "shallow": shallow,
                          "authors": len({c["author"] for c in commits or []})},
              "timeline": gitlog.timeline(commits or []), "commits": gitlog.flag_commits(commits or [], rules),
              "findings": out,
              "patch": "".join(d["fix"]["diff"] for d in out if d["fix"] and d["fix"]["diff"])}
    report["checklist"] = checklist_md(report)
    if expose_path:
        report["path"] = str(root)
    return report

def scan_url(url: str, rules=None, _remote=None) -> dict:
    from .gitsource import checkout
    with checkout(url, _remote=_remote) as (path, info):
        return scan(str(path), rules, source=info, expose_path=False)
