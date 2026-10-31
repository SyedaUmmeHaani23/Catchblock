import json, re, threading, os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from . import history
from .badge import badge_svg
from .explain import explain, MODEL
from .fixes import apply_with_undo, undo
from .gitsource import SourceError
from .rules import list_rules, load_rules
from .scanner import scan, scan_url

LOCAL_ORIGIN = re.compile(r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$")
REMOTE_MODE = os.environ.get("CATCHBLOCK_REMOTE_MODE", "false").lower() == "true"
CLONES = threading.BoundedSemaphore(3)  # at most 3 simultaneous clones

class Handler(BaseHTTPRequestHandler):
    def _cors(self):
        o = self.headers.get("Origin")
        if not o:
            return None
        allowed = {
            x.strip().rstrip("/")
            for x in os.environ.get("CATCHBLOCK_ALLOWED_ORIGINS", "").split(",")
            if x.strip()
        }
        if LOCAL_ORIGIN.match(o) or o.rstrip("/") in allowed:
            return o
        return None

    def _send(self, code, body):
        data = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        o = self._cors()
        if o:
            self.send_header("Access-Control-Allow-Origin", o)
            self.send_header("Vary", "Origin")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    @staticmethod
    def _trended(rep, path):
        rep["trend"] = history.record(history.key_for(path=path), rep["score"])
        return rep

    def log_message(self, *a):
        pass

    def do_OPTIONS(self):
        self._send(204, {})

    def do_GET(self):
        if self.path == "/health":
            return self._send(200, {"ok": True})
        if self.path == "/rules":
            return self._send(200, {"rules": list_rules()})
        self._send(404, {"error": "not found"})

    def do_POST(self):
        if self.path not in ("/scan", "/fix", "/undo", "/explain", "/badge"):
            return self._send(404, {"error": "not found"})
        o = self.headers.get("Origin")
        if o and not self._cors():
            return self._send(403, {"error": "forbidden origin"})
        if REMOTE_MODE and self.path in ("/fix", "/undo"):
            return self._send(403, {"error": "Local file modifications are disabled on the hosted service."})
            return self._send(403, {"error": "forbidden origin"})
        try:
            n = int(self.headers.get("Content-Length", 0))
            if n > 65536:
                return self._send(413, {"error": "request too large"})
            body = json.loads(self.rfile.read(n) or b"{}")
            if self.path == "/explain":
                f = body.get("finding")
                if not isinstance(f, dict):
                    return self._send(400, {"error": "Send the finding to explain."})
                return self._send(200, explain(f))
            if self.path == "/badge":
                score = int(body.get("score"))
                return self._send(200, {"svg": badge_svg(max(0, min(100, score)), str(body.get("verdict")))})
            if self.path == "/undo":
                reverted, skipped = undo(str(body.get("id", "")))
                return self._send(200, {"reverted": reverted, "skipped": skipped})
            rules = load_rules(body.get("rules") or "default", allow_path=False)
            url, path = body.get("url"), body.get("path")
            if self.path == "/scan":
                if url:
                    if not CLONES.acquire(blocking=False):
                        return self._send(429, {"error": "Busy scanning other repositories. Try again in a moment."})
                    try:
                        rep = scan_url(url, rules)
                        rep["trend"] = history.record(history.key_for(url=url), rep["score"])
                        return self._send(200, rep)
                    finally:
                        CLONES.release()
                if not path:
                    return self._send(400, {"error": "Provide a GitHub URL or a local folder path."})
                rep = scan(path, rules)
                rep["trend"] = history.record(history.key_for(path=path), rep["score"])
                return self._send(200, rep)
            if url or not path:
                return self._send(400, {"error": "Fixes are only applied to a local working copy. For a GitHub repo, download the patch and apply it yourself."})
            before = scan(path, rules)
            applied, skipped, uid = apply_with_undo(Path(path), before["findings"], body.get("ids"))
            self._send(200, {"applied": applied, "skipped": skipped, "undo_id": uid, "report": self._trended(scan(path, rules), path)})
        except SourceError as e:
            self._send(422, {"error": str(e), "code": e.code})
        except ValueError as e:
            self._send(400, {"error": str(e)})
        except Exception:
            self._send(500, {"error": "Something went wrong while scanning."})

def serve(port=None):
    port = int(os.environ.get("PORT", port or 8000))
    host = "0.0.0.0" if REMOTE_MODE else "127.0.0.1"
    print(f"CatchBlock API running on {host}:{port}")
    ThreadingHTTPServer((host, port), Handler).serve_forever()
