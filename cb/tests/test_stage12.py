"""Every finding carries a built-in plain-English explanation."""
import unittest
from catchblock.plain import PLAIN, plain_for
from catchblock.scanner import scan
from test_stage6 import make_repo

class PlainTests(unittest.TestCase):
    def test_every_scanned_finding_has_a_plain_explanation(self):
        r = scan(str(make_repo({"README.md": "# a\n", "package.json": '{"dependencies": {"x": "*"}}'})), "default")
        for f in r["findings"]:
            self.assertTrue(f["plain"]["mean"] and f["plain"]["step"], f["id"])
            self.assertIn(f["id"], PLAIN, f"{f['id']} falls back to the generic text")

    def test_unknown_id_falls_back_safely(self):
        self.assertTrue(plain_for("something.new")["step"])

    def test_texts_are_short_and_plain(self):
        for k, (mean, step) in PLAIN.items():
            self.assertLess(len(mean), 220, k)
            self.assertLess(len(step), 220, k)

if __name__ == "__main__":
    unittest.main()
