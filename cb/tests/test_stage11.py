"""Tests for history/trend, the health badge, the Markdown checklist and the CI score gate."""
import os, subprocess, sys, tempfile, unittest
from pathlib import Path
from catchblock import history
from catchblock.badge import badge_svg
from catchblock.scanner import scan
from catchblock.rules import load_rules
from test_stage6 import make_repo

CB = str(Path(__file__).resolve().parent.parent)

class HistoryTests(unittest.TestCase):
    def setUp(self):
        self.old = os.environ.get("CATCHBLOCK_HOME")
        os.environ["CATCHBLOCK_HOME"] = tempfile.mkdtemp()

    def tearDown(self):
        os.environ.pop("CATCHBLOCK_HOME") if self.old is None else os.environ.update(CATCHBLOCK_HOME=self.old)

    def test_first_scan_has_no_delta_then_delta(self):
        a = history.record("k", 40)
        self.assertIsNone(a["delta"])
        b = history.record("k", 55)
        self.assertEqual((b["previous"], b["delta"]), (40, 15))
        self.assertEqual([r["score"] for r in b["runs"]], [40, 55])

    def test_keeps_only_recent_runs(self):
        for i in range(40):
            t = history.record("k", i)
        self.assertEqual(len(t["runs"]), 12)

    def test_url_keys_ignore_case_slash_and_dot_git(self):
        self.assertEqual(history.key_for(url="https://GitHub.com/A/B.git/"), history.key_for(url="https://github.com/a/b"))

class BadgeAndChecklistTests(unittest.TestCase):
    def test_badge_shows_score_and_verdict_colour(self):
        svg = badge_svg(87, "green")
        self.assertIn("87/100", svg)
        self.assertIn("#2ea36f", svg)
        self.assertIn("#e5484d", badge_svg(10, "red"))

    def test_checklist_lists_open_items_as_tasks(self):
        r = scan(str(make_repo({"README.md": "# a\n"})), "default")
        self.assertIn("- [ ] **No LICENSE file**", r["checklist"])
        self.assertIn(f"{r['score']}/100", r["checklist"])

class DefaultRulesTests(unittest.TestCase):
    def test_default_rules_have_no_event(self):
        self.assertNotIn("event", load_rules("default"))
        r = scan(str(make_repo({"README.md": "# a\n"})), "default")
        self.assertIsNone(r["event"])
        self.assertNotIn("git.window", {f["id"] for f in r["findings"]})

    def test_no_event_or_rulebook_wording_in_findings(self):
        r = scan(str(make_repo({"README.md": "# a\n"})), "default")
        text = " ".join(f["title"] + " " + f["why"] for f in r["findings"]).lower()
        for bad in ("rulebook", "event", "hackathon", "freeze"):
            self.assertNotIn(bad, text)

class CliGateTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, "-m", "catchblock.cli", *args], cwd=CB, capture_output=True, text=True)

    def test_min_score_fails_below_and_passes_above(self):
        d = str(make_repo({"README.md": "# a\n"}))
        self.assertEqual(self.run_cli("scan", d, "--min-score", "100").returncode, 1)
        self.assertEqual(self.run_cli("scan", d, "--min-score", "1").returncode, 0)

    def test_badge_file_is_written(self):
        d = str(make_repo({"README.md": "# a\n"}))
        out = os.path.join(tempfile.mkdtemp(), "b.svg")
        self.assertEqual(self.run_cli("scan", d, "--badge", out).returncode, 0)
        self.assertIn("catchblock", Path(out).read_text())

if __name__ == "__main__":
    unittest.main()
