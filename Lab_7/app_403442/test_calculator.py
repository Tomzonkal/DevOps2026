"""
Integration tests for the Flask calculator API.

Uses `requests` against a real HTTP server spun up in a background thread.
The server is started once per test session (session-scoped fixture) to avoid
the overhead of repeated start/stop cycles.

Note: if you prefer faster, isolated tests without a live socket, replace the
`base_url` fixture with Flask's built-in test client — it is the idiomatic
approach for unit-testing Flask apps.
"""

import threading
import time

import pytest
import requests

from calculator import app


# ---------------------------------------------------------------------------
# Session-scoped server fixture
# ---------------------------------------------------------------------------

HOST = "127.0.0.1"
PORT = 5001  # Intentionally not 5000 to avoid collision with a running dev server


@pytest.fixture(scope="session", autouse=True)
def live_server():
    """Start the Flask app in a daemon thread for the whole test session."""
    server_thread = threading.Thread(
        target=lambda: app.run(host=HOST, port=PORT, use_reloader=False),
        daemon=True,
    )
    server_thread.start()

    # Wait until the server is actually accepting connections.
    deadline = time.time() + 5
    while time.time() < deadline:
        try:
            requests.get(f"http://{HOST}:{PORT}/health", timeout=0.5)
            break
        except requests.exceptions.ConnectionError:
            time.sleep(0.05)
    else:
        pytest.fail("Live server did not start within 5 seconds")

    yield  # tests run here


@pytest.fixture(scope="session")
def base_url():
    return f"http://{HOST}:{PORT}"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def post(base_url, endpoint, payload):
    return requests.post(f"{base_url}{endpoint}", json=payload)


# ---------------------------------------------------------------------------
# /health
# ---------------------------------------------------------------------------

class TestHealth:
    def test_returns_ok(self, base_url):
        response = requests.get(f"{base_url}/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


# ---------------------------------------------------------------------------
# /add
# ---------------------------------------------------------------------------

class TestAdd:
    def test_integers(self, base_url):
        r = post(base_url, "/add", {"a": 3, "b": 4})
        assert r.status_code == 200
        assert r.json()["result"] == 7

    def test_floats(self, base_url):
        r = post(base_url, "/add", {"a": 1.5, "b": 2.5})
        assert r.status_code == 200
        assert r.json()["result"] == pytest.approx(4.0)

    def test_negative_numbers(self, base_url):
        r = post(base_url, "/add", {"a": -10, "b": -5})
        assert r.status_code == 200
        assert r.json()["result"] == -15

    def test_negative_and_positive(self, base_url):
        r = post(base_url, "/add", {"a": -3, "b": 7})
        assert r.status_code == 200
        assert r.json()["result"] == 4

    def test_zero_operands(self, base_url):
        r = post(base_url, "/add", {"a": 0, "b": 0})
        assert r.status_code == 200
        assert r.json()["result"] == 0

    def test_missing_field_a(self, base_url):
        r = post(base_url, "/add", {"b": 5})
        assert r.status_code == 400
        assert "error" in r.json()

    def test_missing_field_b(self, base_url):
        r = post(base_url, "/add", {"a": 5})
        assert r.status_code == 400
        assert "error" in r.json()

    def test_missing_both_fields(self, base_url):
        r = post(base_url, "/add", {})
        assert r.status_code == 400

    def test_non_numeric_a(self, base_url):
        r = post(base_url, "/add", {"a": "two", "b": 3})
        assert r.status_code == 400
        assert "error" in r.json()

    def test_non_numeric_b(self, base_url):
        r = post(base_url, "/add", {"a": 3, "b": None})
        assert r.status_code == 400

    def test_no_body(self, base_url):
        # Flask returns 415 Unsupported Media Type when Content-Type is absent,
        # before our validation code even runs. Both 4xx responses are acceptable.
        r = requests.post(f"{base_url}/add")
        assert r.status_code in (400, 415)


# ---------------------------------------------------------------------------
# /subtract
# ---------------------------------------------------------------------------

class TestSubtract:
    def test_basic(self, base_url):
        r = post(base_url, "/subtract", {"a": 10, "b": 3})
        assert r.status_code == 200
        assert r.json()["result"] == 7

    def test_result_is_negative(self, base_url):
        r = post(base_url, "/subtract", {"a": 3, "b": 10})
        assert r.status_code == 200
        assert r.json()["result"] == -7

    def test_floats(self, base_url):
        r = post(base_url, "/subtract", {"a": 5.5, "b": 2.2})
        assert r.status_code == 200
        assert r.json()["result"] == pytest.approx(3.3)

    def test_negative_operands(self, base_url):
        r = post(base_url, "/subtract", {"a": -4, "b": -6})
        assert r.status_code == 200
        assert r.json()["result"] == 2

    def test_subtract_zero(self, base_url):
        r = post(base_url, "/subtract", {"a": 7, "b": 0})
        assert r.status_code == 200
        assert r.json()["result"] == 7

    def test_missing_fields(self, base_url):
        r = post(base_url, "/subtract", {"a": 5})
        assert r.status_code == 400

    def test_non_numeric(self, base_url):
        r = post(base_url, "/subtract", {"a": "x", "b": 1})
        assert r.status_code == 400


# ---------------------------------------------------------------------------
# /multiply
# ---------------------------------------------------------------------------

class TestMultiply:
    def test_basic(self, base_url):
        r = post(base_url, "/multiply", {"a": 4, "b": 5})
        assert r.status_code == 200
        assert r.json()["result"] == 20

    def test_multiply_by_zero(self, base_url):
        r = post(base_url, "/multiply", {"a": 99, "b": 0})
        assert r.status_code == 200
        assert r.json()["result"] == 0

    def test_negative_times_positive(self, base_url):
        r = post(base_url, "/multiply", {"a": -3, "b": 4})
        assert r.status_code == 200
        assert r.json()["result"] == -12

    def test_negative_times_negative(self, base_url):
        r = post(base_url, "/multiply", {"a": -3, "b": -4})
        assert r.status_code == 200
        assert r.json()["result"] == 12

    def test_floats(self, base_url):
        r = post(base_url, "/multiply", {"a": 2.5, "b": 4.0})
        assert r.status_code == 200
        assert r.json()["result"] == pytest.approx(10.0)

    def test_missing_fields(self, base_url):
        r = post(base_url, "/multiply", {})
        assert r.status_code == 400

    def test_non_numeric(self, base_url):
        r = post(base_url, "/multiply", {"a": 3, "b": [1, 2]})
        assert r.status_code == 400


# ---------------------------------------------------------------------------
# /divide
# ---------------------------------------------------------------------------

class TestDivide:
    def test_basic(self, base_url):
        r = post(base_url, "/divide", {"a": 10, "b": 2})
        assert r.status_code == 200
        assert r.json()["result"] == 5.0

    def test_non_integer_result(self, base_url):
        r = post(base_url, "/divide", {"a": 7, "b": 2})
        assert r.status_code == 200
        assert r.json()["result"] == pytest.approx(3.5)

    def test_floats(self, base_url):
        r = post(base_url, "/divide", {"a": 9.0, "b": 4.0})
        assert r.status_code == 200
        assert r.json()["result"] == pytest.approx(2.25)

    def test_negative_dividend(self, base_url):
        r = post(base_url, "/divide", {"a": -10, "b": 2})
        assert r.status_code == 200
        assert r.json()["result"] == pytest.approx(-5.0)

    def test_negative_divisor(self, base_url):
        r = post(base_url, "/divide", {"a": 10, "b": -2})
        assert r.status_code == 200
        assert r.json()["result"] == pytest.approx(-5.0)

    def test_both_negative(self, base_url):
        r = post(base_url, "/divide", {"a": -10, "b": -2})
        assert r.status_code == 200
        assert r.json()["result"] == pytest.approx(5.0)

    def test_divide_by_zero_integer(self, base_url):
        r = post(base_url, "/divide", {"a": 5, "b": 0})
        assert r.status_code == 400
        assert r.json()["error"] == "Division by zero"

    def test_divide_by_zero_float(self, base_url):
        r = post(base_url, "/divide", {"a": 5.0, "b": 0.0})
        assert r.status_code == 400
        assert r.json()["error"] == "Division by zero"

    def test_zero_divided_by_number(self, base_url):
        r = post(base_url, "/divide", {"a": 0, "b": 5})
        assert r.status_code == 200
        assert r.json()["result"] == pytest.approx(0.0)

    def test_missing_fields(self, base_url):
        r = post(base_url, "/divide", {"a": 10})
        assert r.status_code == 400

    def test_non_numeric(self, base_url):
        r = post(base_url, "/divide", {"a": "ten", "b": 2})
        assert r.status_code == 400