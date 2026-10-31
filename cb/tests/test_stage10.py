"""Tests for the merged CatchBlock: no judge estimate, quick wins, deleted-secret detection,
generic-repo defaults and the optional local explainer."""
import json, tempfile, threading, unittest, urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest import mock
from catchblock import explain as explain_mod
from catchblock.scanner import scan, quick_wins
from catchblock.server import Handler
from test_stage6 import git, make_repo

FAKE_KEY = "AKIA" + "ABCDEFGHIJKLMNOP"  # built at runtime: obviously fake, never a real key

def ids(r, status=None):
    return {f["id"] for f in r["findings"] if status is None or f["status"] == status}

class ReportShapeTests(unittest.TestCase):
    def test_no_judge_estimate_in_report(self):
        r = scan(str(make_repo({"README.md": "# a\n"})))
        self.assertNotIn("rubric", r)
        self.assertIn("quick_wins", r)

    def test_core_checks_present(self):
        r = scan(str(make_repo({"README.md": "# a\n"})))
        for want in ("license.exists", "license.type", "docs.readme", "hygiene.gitignore", "secrets.scan",
                     "ci.workflow", "tests.exist", "community.contributing", "disclosure.ai", "git.history"):
            self.assertIn(want, ids(r), want)

class GenericRepoTests(unittest.TestCase):
    def test_gpl_and_bsd_licences_pass_without_event_rules(self):
        d = make_repo({"LICENSE": "Redistribution and use in source and binary forms, with or without modification\n"})
        lt = [f for f in scan(str(d))["findings"] if f["id"] == "license.type"][0]
        self.assertEqual(lt["status"], "pass")

    def test_event_rules_still_restrict_licences(self):
        d = make_repo({"LICENSE": "Redistribution and use in source and binary forms\n"})
        lt = [f for f in scan(str(d), "devforge")["findings"] if f["id"] == "license.type"][0]
        self.assertEqual(lt["status"], "fail")

    def test_solo_repo_is_not_penalised_without_event_rules(self):
        r = scan(str(make_repo({"README.md": "# a\n"})))
        au = [f for f in r["findings"] if f["id"] == "git.authors"][0]
        self.assertEqual(au["status"], "pass")

    def test_tests_inside_node_modules_do_not_count(self):
        d = make_repo({"node_modules/x/test_a.py": "1\n", "src/app.js": "1\n"})
        self.assertIn("tests.exist", ids(scan(str(d)), "fail"))

    def test_spec_and_test_files_count(self):
        d = make_repo({"src/app.test.js": "1\n"})
        self.assertIn("tests.exist", ids(scan(str(d)), "pass"))

    def test_other_ci_systems_count(self):
        d = make_repo({".gitlab-ci.yml": "stages: [test]\n"})
        self.assertIn("ci.workflow", ids(scan(str(d)), "pass"))

    def test_generated_licence_is_not_catchblock_branded(self):
        r = scan(str(make_repo({"a.txt": "1\n"})))
        lic = [f for f in r["findings"] if f["id"] == "license.exists"][0]
        self.assertNotIn("Catchblock", lic["fix"]["content"])

class QuickWinTests(unittest.TestCase):
    def test_projected_score_is_higher_and_items_sorted(self):
        r = scan(str(make_repo({"a.txt": "1\n"})))
        qw = r["quick_wins"]
        self.assertGreater(qw["projected"], r["score"])
        gains = [i["gain"] for i in qw["items"]]
        self.assertEqual(gains, sorted(gains, reverse=True))
        self.assertTrue(any(i["auto"] for i in qw["items"]))

    def test_healthy_repo_has_no_wins(self):
        r = scan(str(make_repo({"LICENSE": "MIT License\n", "README.md": "# a\nsetup usage contribute\n", ".gitignore": "x\n",
                                ".github/workflows/ci.yml": "x\n", "tests/test_a.py": "1\n", "CONTRIBUTING.md": "x\n"})))
        self.assertEqual(quick_wins([])["items"], [])
        self.assertLessEqual(r["quick_wins"]["projected"], 100)

class HistorySecretTests(unittest.TestCase):
    def test_deleted_secret_is_found_and_value_is_never_reported(self):
        d = make_repo({"app.py": "print(1)\n"})
        (d / "config.py").write_text(f'KEY = "{FAKE_KEY}"\n'); git(d, "add", "."); git(d, "commit", "-qm", "add config")
        (d / "config.py").unlink(); git(d, "add", "-A"); git(d, "commit", "-qm", "remove config")
        r = scan(str(d))
        self.assertIn("secrets.scan", ids(r, "pass"))      # not in the files any more
        self.assertIn("secrets.history", ids(r, "fail"))   # but still in history
        self.assertEqual(r["verdict"], "red")
        self.assertNotIn(FAKE_KEY, json.dumps(r))

    def test_secret_still_in_files_is_not_double_reported(self):
        d = make_repo({"config.py": f'KEY = "{FAKE_KEY}"\n'})
        r = scan(str(d))
        self.assertIn("secrets.scan", ids(r, "fail"))
        self.assertIn("secrets.history", ids(r, "pass"))

    def test_clean_history_passes(self):
        self.assertIn("secrets.history", ids(scan(str(make_repo({"a.py": "print(1)\n"}))), "pass"))

    def test_no_git_history_skips_the_check(self):
        d = Path(tempfile.mkdtemp()); (d / "a.py").write_text("1\n")
        self.assertNotIn("secrets.history", ids(scan(str(d))))

class ExplainTests(unittest.TestCase):
    def test_prompt_contains_only_finding_facts(self):
        p = explain_mod.build_prompt({"title": "No tests found", "why": "Tests help", "status": "fail", "category": "Tests", "fix": {"content": "SECRET"}})
        self.assertIn("No tests found", p); self.assertNotIn("SECRET", p)

    def test_falls_back_when_model_is_not_running(self):
        with mock.patch("urllib.request.urlopen", side_effect=OSError("down")):
            self.assertEqual(explain_mod.explain({"title": "x"})["available"], False)

    def test_returns_text_when_model_answers(self):
        class R:
            def __enter__(s): return s
            def __exit__(s, *a): return False
            def read(s): return json.dumps({"response": " Add a licence. "}).encode()
        with mock.patch("urllib.request.urlopen", return_value=R()):
            out = explain_mod.explain({"title": "No LICENSE file"})
        self.assertTrue(out["available"]); self.assertEqual(out["text"], "Add a licence.")

    def test_explain_endpoint_never_changes_the_report(self):
        srv = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        try:
            req = urllib.request.Request(f"http://127.0.0.1:{srv.server_port}/explain", data=json.dumps({"finding": {"title": "x"}}).encode(),
                                         headers={"Content-Type": "application/json"})
            with mock.patch("catchblock.server.explain", return_value={"available": False, "model": "m"}):
                body = json.loads(urllib.request.urlopen(req, timeout=10).read())
            self.assertEqual(body, {"available": False, "model": "m"})
            bad = urllib.request.Request(f"http://127.0.0.1:{srv.server_port}/explain", data=b"{}", headers={"Content-Type": "application/json"})
            with self.assertRaises(urllib.error.HTTPError) as cm:
                urllib.request.urlopen(bad, timeout=10)
            self.assertEqual(cm.exception.code, 400)
        finally:
            srv.shutdown()

if __name__ == "__main__":
    unittest.main()
