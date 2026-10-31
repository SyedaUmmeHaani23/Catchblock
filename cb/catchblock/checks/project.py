import os
from pathlib import Path
from ..models import Finding, Fix
from .files import _find

CI = "name: ci\non: [push, pull_request]\njobs:\n  test:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v4\n      - run: python3 -m unittest discover -s tests\n        if: hashFiles('tests/**') != ''\n"

def detect_license(text: str):
    t = text.lower()
    if "mit license" in t or "permission is hereby granted, free of charge" in t: return "MIT"
    if "apache license" in t: return "Apache-2.0"
    if "gnu general public license" in t and "version 3" in t: return "GPL-3.0"
    if "mozilla public license" in t: return "MPL-2.0"
    if "redistribution and use in source and binary forms" in t: return "BSD-3-Clause"
    if "permission to use, copy, modify, and/or distribute" in t: return "ISC"
    return None

OTHER_CI = (".gitlab-ci.yml", ".circleci/config.yml", "azure-pipelines.yml", "Jenkinsfile", ".travis.yml", "bitbucket-pipelines.yml")
PRUNE = {".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build", ".next"}
TEST_DIRS = {"tests", "test", "__tests__", "spec"}

def _has_tests(root: Path) -> bool:
    seen = 0
    for dp, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in PRUNE]
        if any(d in TEST_DIRS for d in dirs):
            return True
        for f in files:
            seen += 1
            low = f.lower()
            if low.startswith("test_") or low.endswith(("_test.py", "_test.go")) or ".test." in low or ".spec." in low:
                return True
        if seen > 20000:
            break
    return False

def check_ci(root: Path, rules=None):
    wf = root / ".github" / "workflows"
    ok = (wf.is_dir() and any(wf.glob("*.y*ml"))) or any((root / f).exists() for f in OTHER_CI)
    return Finding("ci.workflow", "CI", "pass" if ok else "warn", "medium", 10,
                   "CI workflow found" if ok else "No CI workflow",
                   "CI runs your tests on every push so broken code is caught early.",
                   None if ok else Fix(".github/workflows/ci.yml", CI))

def check_tests(root: Path, rules=None):
    ok = _has_tests(root)
    return Finding("tests.exist", "Tests", "pass" if ok else "fail", "high", 15,
                   "Tests found" if ok else "No tests found",
                   "Tests prove the code works and let others change it safely.")

def check_contributing(root: Path, rules=None):
    ok = _find(root, "contributing") is not None
    return Finding("community.contributing", "Community", "pass" if ok else "warn", "low", 5,
                   "CONTRIBUTING found" if ok else "No CONTRIBUTING.md",
                   "Tell newcomers how to help: it makes your project easy to join.",
                   None if ok else Fix("CONTRIBUTING.md", "# Contributing\n\n1. Fork and create a branch.\n2. Make small commits.\n3. Open a pull request.\n"))

OSI_COMMON = ["MIT", "Apache-2.0", "GPL-3.0", "BSD-3-Clause", "ISC", "MPL-2.0"]

def check_license_type(root: Path, rules=None):
    custom = (rules or {}).get("requirements", {}).get("licenses")
    allowed = custom or OSI_COMMON
    p = _find(root, "license")
    text = p.read_text(encoding="utf-8", errors="ignore").lower() if p else ""
    found = detect_license(text)
    ok = found in allowed
    if found and not ok:
        title = f"Licence is {found}, which is not in the allowed list" if custom else f"Licence is {found}"
    elif found:
        title = f"Licence is {found}"
    else:
        title = f"Licence not recognised: use one of {', '.join(allowed)}"
    return Finding("license.type", "Licence", "pass" if ok else "fail", "high", 5, title,
                   "An open-source licence (OSI-approved) tells people what they may do with your code.")
