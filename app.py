import json, os, subprocess, tempfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

class H(BaseHTTPRequestHandler):
    def _send(self, code, obj):
        b = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_OPTIONS(self):
        self._send(200, {})

    def do_GET(self):
        self._send(200, {"ok": True})

    def do_POST(self):
        try:
            n = int(self.headers.get("Content-Length", 0))
            if n > 200000:
                return self._send(413, {"error": "kode terlalu besar"})
            data = json.loads(self.rfile.read(n))
            code = data.get("code", "")
            with tempfile.TemporaryDirectory() as d:
                sk = os.path.join(d, "sketch")
                os.makedirs(sk)
                with open(os.path.join(sk, "sketch.ino"), "w") as f:
                    f.write(code)
                out = os.path.join(d, "out")
                r = subprocess.run(
                    ["arduino-cli", "compile", "--fqbn", "arduino:avr:uno",
                     "--output-dir", out, sk],
                    capture_output=True, text=True, timeout=120)
                if r.returncode != 0:
                    return self._send(200, {"error": (r.stderr or r.stdout)[-1500:]})
                with open(os.path.join(out, "sketch.ino.hex")) as f:
                    self._send(200, {"hex": f.read()})
        except Exception as e:
            self._send(500, {"error": str(e)})

ThreadingHTTPServer(("0.0.0.0", int(os.environ.get("PORT", 10000))), H).serve_forever()
