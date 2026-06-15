import json
import threading
import unittest
from urllib.request import urlopen

from app.server import create_server


class HealthEndpointTest(unittest.TestCase):
    def test_health_endpoint_returns_ok(self):
        server = create_server(host="127.0.0.1", port=0)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()

        try:
            host, port = server.server_address
            with urlopen(f"http://{host}:{port}/health", timeout=5) as response:
                payload = json.loads(response.read().decode("utf-8"))

            self.assertEqual(response.status, 200)
            self.assertEqual(payload, {"status": "ok"})
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)


if __name__ == "__main__":
    unittest.main()
