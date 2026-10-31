POINTS = {"pass": 1.0, "warn": 0.5, "fail": 0.0}
def _pct(fs):
    total = sum(f.weight for f in fs)
    return sum(f.weight * POINTS[f.status] for f in fs) / total if total else 0

def compute(findings):
    score = round(100 * _pct(findings))
    verdict = "green" if score >= 80 else "amber" if score >= 50 else "red"
    if any(f.id.startswith("secrets.") and f.status == "fail" for f in findings):
        verdict = "red"  # a leaked secret always forces red
    return score, verdict
