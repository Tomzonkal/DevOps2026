from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os


class AppHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            response = {
                "status": "ok",
                "service": "devops-project-419534"
            }
            status_code = 200
        elif self.path == "/":
            response = {
                "message": "Projekt DevOps 2026",
                "student": "419534"
            }
            status_code = 200
        else:
            response = {
                "error": "Not found"
            }
            status_code = 404

        body = json.dumps(response).encode("utf-8")

        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return


def run_server():
    port = int(os.getenv("PORT", "8080"))
    server = HTTPServer(("0.0.0.0", port), AppHandler)
    print(f"Application running on port {port}")
    server.serve_forever()


if __name__ == "__main__":
    run_server()
