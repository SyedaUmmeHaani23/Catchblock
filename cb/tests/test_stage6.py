import json, os, shutil, subprocess, tempfile, threading, unittest, urllib.request, urllib.error
from http.server import ThreadingHTTPServer
from pathlib import Path
from catchblock import gitsource, guard
from catchblock.gitsource import SourceError, parse_github_url, checkout
from catchblock.fixes import apply_with_undo, undo, make_diff
from catchblock.scanner import scan, scan_url
from catchblock.server import Handler

def git(d, *a, date="2026-10-15T12:00:00+05:30", author="Ann"):
    env = {**os.environ, "GIT_AUTHOR_DATE": date, "GIT_COMMITTER_DATE": date, "HOME": str(d)}
    return subprocess.run(["git", "-C", str(d), "-c", f"user.name={author}", "-c", "user.email=a@a", *a],
                          env=env, check=True, capture_output=True, text=True)

def make_repo(files, commit=True, **kw):
    d = Path(tempfile.mkdtemp())
    for n, t in files.items():
        p = d / n; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(t)
    git(d, "init", "-q", "-b", "main")
    if commit:
        git(d, "add", "."); git(d, "commit", "-qm", "initial import of the project", **kw)
    return d

class UrlTests(unittest.TestCase):
    def test_valid_urls(self):
        self.assertEqual(parse_github_url("https://github.com/SyedaUmmeHaani23/Catchblock"), ("SyedaUmmeHaani23", "Catchblock", None))
        self.assertEqual(parse_github_url("github.com/a/b.git/"), ("a", "b", None))
        self.assertEqual(parse_github_url("https://github.com/a/b/tree/feat/x"), ("a", "b", "feat/x"))

    def test_rejects_bad_urls(self):
        for bad in ["", "not a url", "https://gitlab.com/a/b", "https://github.com/a", "file:///etc/passwd",
                    "https://evil.com/github.com/a/b", "https://user:pw@github.com/a/b", "https://github.com/a/b?x=1",
                    "https://github.com/a/..", "https://github.com/a/b/issues", "https://github.com/a/b/tree/../x",
                    "https://github.com:8080/a/b", "--upload-pack=x", "ext::sh -c id"]:
            with self.assertRaises(SourceError, msg=bad):
                parse_github_url(bad)

class CloneTests(unittest.TestCase):
    def test_clone_scan_and_cleanup(self):
        src = make_repo({"README.md": "# x\n", "app.py": "print(1)\n"})
        seen = {}
        with checkout("https://github.com/o/r", _remote=str(src)) as (path, info):
            seen["p"] = path
            self.assertTrue((path / "app.py").exists())
            self.assertEqual(info["name"], "o/r")
        self.assertFalse(seen["p"].exists())
        self.assertFalse(seen["p"].parent.exists())

    def test_cleanup_when_scan_fails(self):
        src = make_repo({"a": "1"})
        seen = {}
        try:
            with checkout("https://github.com/o/r", _remote=str(src)) as (path, _):
                seen["p"] = path; raise RuntimeError("boom")
        except RuntimeError:
            pass
        self.assertFalse(seen["p"].parent.exists())

    def test_missing_repo_is_a_clean_error_without_paths(self):
        with self.assertRaises(SourceError) as cm:
            with checkout("https://github.com/o/r", _remote="/nonexistent/place"):
                pass
        self.assertNotIn("/nonexistent", str(cm.exception))

    def test_size_cap(self):
        src = make_repo({"big.bin": "x" * 3_000_000})
        orig = gitsource.MAX_MB
        try:
            with self.assertRaises(SourceError) as cm:
                dest = Path(tempfile.mkdtemp()) / "r"
                gitsource._clone(str(src), dest, None, allow_file=True, max_mb=1)
            self.assertEqual(cm.exception.code, "too_large")
        finally:
            gitsource.MAX_MB = orig

    def test_url_report_hides_local_path_and_flags_shallow(self):
        src = make_repo({"README.md": "# x\n"})
        r = scan_url("https://github.com/o/r", None, _remote=str(src))
        self.assertNotIn("path", r)
        self.assertEqual(r["source"]["name"], "o/r")
        self.assertIn("patch", r)

class FixTests(unittest.TestCase):
    def test_patch_applies_with_git_apply(self):
        d = make_repo({"app.py": "print(1)\n"})
        r = scan(str(d))
        self.assertTrue(r["patch"])
        (d / "p.patch").write_text(r["patch"])
        subprocess.run(["git", "-C", str(d), "apply", "--check", "p.patch"], check=True, capture_output=True)

    def test_undo_restores_exactly(self):
        d = Path(tempfile.mkdtemp()); (d / "README.md").write_text("# hi\n")
        before = scan(str(d))
        applied, _, uid = apply_with_undo(d, before["findings"])
        self.assertTrue(applied and uid)
        self.assertTrue((d / "LICENSE").exists())
        undo(uid)
        self.assertFalse((d / "LICENSE").exists())
        self.assertEqual((d / "README.md").read_text(), "# hi\n")
        self.assertFalse((d / ".github").exists())

    def test_undo_refuses_if_user_edited(self):
        d = Path(tempfile.mkdtemp())
        _, _, uid = apply_with_undo(d, scan(str(d))["findings"])
        (d / "LICENSE").write_text("mine now")
        reverted, skipped = undo(uid)
        self.assertEqual((d / "LICENSE").read_text(), "mine now")
        self.assertTrue(skipped)

class SignalTests(unittest.TestCase):
    def test_ai_files_and_deps_detected(self):
        d = make_repo({"CLAUDE.md": "x", "package.json": json.dumps({"dependencies": {"openai": "*", "react": "^19"}}),
                       "README.md": "# app\nsetup usage\n"}, commit=False)
        r = scan(str(d))
        ai = [f for f in r["findings"] if f["id"] == "disclosure.ai"][0]
        self.assertEqual(ai["status"], "fail")
        self.assertIn("Claude", ai["title"]); self.assertIn("OpenAI", ai["title"])
        dep = [f for f in r["findings"] if f["id"] == "deps.hygiene"][0]
        self.assertEqual(dep["status"], "warn")
        cr = [f for f in r["findings"] if f["id"] == "credits.readme"][0]
        self.assertEqual(cr["status"], "warn")

    def test_commit_flags_and_license_first_commit(self):
        d = make_repo({"a.txt": "1\n"}, date="2026-09-01T10:00:00+05:30")  # first commit, before start: allowed
        (d / "LICENSE").write_text("MIT License\n"); git(d, "add", "."); git(d, "commit", "-qm", "add licence", date="2026-10-02T10:00:00+05:30")
        (d / "b.txt").write_text("2\n"); git(d, "add", "."); git(d, "commit", "-qm", "late work", date="2026-11-02T10:00:00+05:30", author="Bo")
        r = scan(str(d), "hacktoberfest")
        flags = [f for c in r["commits"] for f in c["flags"]]
        self.assertIn("post-freeze", flags); self.assertNotIn("pre-start", flags)
        r2 = scan(str(d), "devforge")
        lf = [f for f in r2["findings"] if f["id"] == "license.first_commit"][0]
        self.assertEqual(lf["status"], "fail")

    def test_shallow_clone_does_not_claim_first_commit_proof(self):
        d = make_repo({"LICENSE": "MIT License\n"})
        r = scan_url("https://github.com/o/r", "devforge", _remote=str(d))
        lf = [f for f in r["findings"] if f["id"] == "license.first_commit"]
        self.assertTrue(lf)  # present, and honest either way
        if r["history"]["shallow"]:
            self.assertEqual(lf[0]["status"], "warn")

class GuardTests(unittest.TestCase):
    def test_guard_blocks_leaked_secret_and_missing_licence(self):
        d = make_repo({"app.py": 'KEY = "' + "AKIA" + 'FAKEFAKEFAKE0000"\n'})
        _, blockers = guard.check(d)
        self.assertEqual({b["id"] for b in blockers}, {"secrets.scan", "license.exists"})

    def test_hook_install_blocks_push(self):
        d = make_repo({"app.py": 'KEY = "' + "AKIA" + 'FAKEFAKEFAKE0000"\n'})
        bare = Path(tempfile.mkdtemp()); subprocess.run(["git", "init", "-q", "--bare", str(bare)], check=True)
        git(d, "remote", "add", "origin", str(bare))
        guard.install(d)
        p = subprocess.run(["git", "-C", str(d), "push", "origin", "main"], capture_output=True, text=True)
        self.assertNotEqual(p.returncode, 0); self.assertIn("CatchBlock", p.stderr + p.stdout)
        guard.uninstall(d)
        p = subprocess.run(["git", "-C", str(d), "push", "origin", "main"], capture_output=True, text=True)
        self.assertEqual(p.returncode, 0)

class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.port = cls.srv.server_address[1]
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()

    def post(self, path, body, origin=None):
        h = {"Content-Type": "application/json"}
        if origin: h["Origin"] = origin
        req = urllib.request.Request(f"http://127.0.0.1:{self.port}{path}", json.dumps(body).encode(), h)
        try:
            with urllib.request.urlopen(req) as r: return r.status, json.loads(r.read())
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read())

    def test_bad_url_is_422_with_friendly_message(self):
        code, b = self.post("/scan", {"url": "https://gitlab.com/a/b"})
        self.assertEqual(code, 422); self.assertIn("github.com", b["error"])

    def test_foreign_origin_blocked(self):
        code, _ = self.post("/scan", {"path": "."}, origin="https://evil.example")
        self.assertEqual(code, 403)

    def test_fix_refuses_remote_and_roundtrips_local_with_undo(self):
        code, _ = self.post("/fix", {"url": "https://github.com/a/b"}); self.assertEqual(code, 400)
        d = Path(tempfile.mkdtemp())
        code, b = self.post("/fix", {"path": str(d), "rules": "hacktoberfest"}, origin="http://localhost:5173")
        self.assertEqual(code, 200); self.assertTrue(b["undo_id"]); self.assertTrue((d / "LICENSE").exists())
        code, u = self.post("/undo", {"id": b["undo_id"]}); self.assertEqual(code, 200)
        self.assertFalse((d / "LICENSE").exists())

    def test_rules_route_and_unknown_rulebook(self):
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/rules") as r:
            ids = {x["id"] for x in json.loads(r.read())["rules"]}
        self.assertIn("hacktoberfest", ids)
        code, _ = self.post("/scan", {"path": ".", "rules": "../../etc/passwd"}); self.assertEqual(code, 400)

if __name__ == "__main__":
    unittest.main()
