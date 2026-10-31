import subprocess, tempfile, unittest
from pathlib import Path
from catchblock.scanner import scan

RULES = str(Path(__file__).parent.parent / "rules" / "devforge.toml")

def repo(files):
    d = Path(tempfile.mkdtemp())
    for name, text in files.items():
        p = d / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
    return d

class ScannerTests(unittest.TestCase):
    def test_empty_repo_is_red(self):
        self.assertEqual(scan(str(repo({})))["verdict"], "red")

    def test_leaked_key_forces_red(self):
        d = repo({"LICENSE": "MIT License", "README.md": "setup usage contribute claude credits",
                  ".gitignore": "x", "app.py": 'KEY = "' + 'AKIA' + 'FAKEFAKEFAKE0000' + '"'})
        r = scan(str(d))
        self.assertEqual(r["verdict"], "red")
        self.assertIn("secret", [f for f in r["findings"] if f["id"] == "secrets.scan"][0]["title"])

    def test_healthy_repo_passes_rules(self):
        d = repo({"LICENSE": "MIT License", "README.md": "setup usage contribute\nAI tools: Claude\nCredits: none",
                  ".gitignore": "x", "CONTRIBUTING.md": "hi", "tests/test_a.py": "pass",
                  ".github/workflows/ci.yml": "name: ci"})
        r = scan(str(d), RULES)
        bad = [f["id"] for f in r["findings"] if f["status"] != "pass" and not f["id"].startswith("git.")]
        self.assertEqual(bad, [])

    def test_git_timeline_and_window(self):
        d = repo({"a.txt": "1"})
        env = {"GIT_AUTHOR_DATE": "2026-10-30T10:00:00+05:30", "GIT_COMMITTER_DATE": "2026-10-30T10:00:00+05:30",
               "PATH": "/usr/bin:/bin", "HOME": str(d)}
        g = lambda *a, e=env: subprocess.run(["git", "-C", str(d), "-c", "user.name=A", "-c", "user.email=a@a", *a], env=e, check=True, capture_output=True)
        g("init"); g("add", "."); g("commit", "-m", "init")
        (d / "b.txt").write_text("2"); g("add", "."); g("commit", "-m", "fix")
        r = scan(str(d), RULES)
        w = [f for f in r["findings"] if f["id"] == "git.window"][0]
        self.assertEqual(w["status"], "fail")  # second commit is before the 10 PM start
        self.assertTrue(r["timeline"])

if __name__ == "__main__":
    unittest.main()
