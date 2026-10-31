import tempfile, unittest
from pathlib import Path
from catchblock.scanner import scan
from catchblock.fixes import apply_fixes

RULES = str(Path(__file__).parent.parent / "rules" / "devforge.toml")

class FixTests(unittest.TestCase):
    def test_fix_all_raises_score_and_never_overwrites(self):
        d = Path(tempfile.mkdtemp())
        (d / "app.py").write_text("print('hi')")
        before = scan(str(d), RULES)
        applied, _ = apply_fixes(d, before["findings"])
        after = scan(str(d), RULES)
        self.assertTrue(applied)
        self.assertGreater(after["score"], before["score"])
        self.assertTrue((d / "LICENSE").exists())
        (d / "LICENSE").write_text("keep me")
        apply_fixes(d, before["findings"])
        self.assertEqual((d / "LICENSE").read_text(), "keep me")

    def test_placeholder_readme_still_asks_for_real_list(self):
        d = Path(tempfile.mkdtemp())
        apply_fixes(d, scan(str(d), RULES)["findings"])
        f = [x for x in scan(str(d), RULES)["findings"] if x["id"] == "disclosure.ai"][0]
        self.assertEqual(f["status"], "warn")

    def test_path_escape_is_blocked(self):
        d = Path(tempfile.mkdtemp())
        fake = [{"id": "x", "status": "fail", "fix": {"path": "../evil.txt", "content": "x"}}]
        applied, skipped = apply_fixes(d, fake)
        self.assertEqual(applied, [])
        self.assertEqual(len(skipped), 1)

if __name__ == "__main__":
    unittest.main()
