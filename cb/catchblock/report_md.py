"""Turns a report into a Markdown checklist you can paste into a GitHub issue or pull request."""
ORDER = {"fail": 0, "warn": 1}
SEV = {"critical": 0, "high": 1, "medium": 2, "low": 3}

def checklist_md(report: dict) -> str:
    name = (report.get("source") or {}).get("name", "repository")
    todo = sorted((f for f in report["findings"] if f["status"] != "pass"),
                  key=lambda f: (ORDER[f["status"]], SEV.get(f["severity"], 9)))
    passed = sum(1 for f in report["findings"] if f["status"] == "pass")
    lines = [f"## CatchBlock report for {name}: {report['score']}/100 ({report['verdict']})", ""]
    if todo:
        lines.append("### To do")
        lines += [f"- [ ] **{f['title']}** ({f['severity']}): {f['why']}" for f in todo]
    else:
        lines.append("Nothing to fix. Every check passed.")
    lines += ["", f"{passed} check(s) passed. Findings are signals for review, not proof."]
    return "\n".join(lines) + "\n"
