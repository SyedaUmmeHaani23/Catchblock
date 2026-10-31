from pathlib import Path
from ..models import Finding, Fix

MIT = """MIT License

Copyright (c) 2026 The project authors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the \"Software\"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

def _find(root: Path, stem: str):
    for p in root.iterdir():
        if p.is_file() and p.name.lower().split(".")[0] == stem:
            return p
    return None

def check_license(root: Path, rules=None):
    ok = _find(root, "license") is not None
    return Finding(
        id="license.exists", category="Licence",
        status="pass" if ok else "fail", severity="high", weight=15,
        title="LICENSE file found" if ok else "No LICENSE file",
        why="Without a licence, nobody can legally reuse your code.",
        fix=None if ok else Fix("LICENSE", MIT),
    )

def check_readme(root: Path, rules=None):
    p = _find(root, "readme")
    if p is None:
        return Finding("docs.readme", "Docs", "fail", "high", 15,
                       "No README", "A README is the first thing every visitor opens.",
                       Fix("README.md", "# Project\n\n## Setup\n\n## Usage\n"))
    text = p.read_text(encoding="utf-8", errors="ignore").lower()
    wanted = {"setup": ("setup", "install", "getting started", "quickstart", "quick start"),
              "usage": ("usage", "example", "how to", "quickstart", "quick start", "demo"),
              "contributing": ("contribut",)}
    missing = [k for k, words in wanted.items() if not any(w in text for w in words)]
    return Finding("docs.readme", "Docs", "warn" if missing else "pass", "medium", 15,
                   "README missing: " + ", ".join(missing) if missing else "README looks complete",
                   "Setup, usage and contributing sections help people run and join your project.")

def check_gitignore(root: Path, rules=None):
    ok = (root / ".gitignore").exists()
    return Finding("hygiene.gitignore", "Hygiene", "pass" if ok else "warn", "low", 5,
                   ".gitignore found" if ok else "No .gitignore",
                   "Without it you may commit node_modules, .env files or build output.",
                   None if ok else Fix(".gitignore", "node_modules/\n.env\n__pycache__/\n.venv/\ndist/\n"))
