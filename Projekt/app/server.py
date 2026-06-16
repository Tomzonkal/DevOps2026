import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class AppHandler(BaseHTTPRequestHandler):
    server_version = "Lab05App/1.0"

    def do_GET(self):
        if self.path == "/health":
            self._send_json(200, {"status": "ok"})
            return

        if self.path == "/":
            self._send_json(
                200,
                {
                    "name": "devops-lab05-app",
                    "status": "running",
                    "version": os.getenv("APP_VERSION", "local"),
                },
            )
            return

        self._send_json(404, {"error": "not_found"})

    def log_message(self, format, *args):
        return

    def _send_json(self, status_code, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def create_server(host="0.0.0.0", port=8080):
    return ThreadingHTTPServer((host, port), AppHandler)


def main():
    port = int(os.getenv("PORT", "8080"))
    server = create_server(port=port)
    print(f"Listening on 0.0.0.0:{port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()

