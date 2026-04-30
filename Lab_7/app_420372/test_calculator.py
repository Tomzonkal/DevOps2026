import threading
import time

import pytest
import requests
from calculator import app

BASE_URL = "http://localhost:5000"


@pytest.fixture(scope="session", autouse=True)
def start_server():
    """Start Flask server in a background thread for the test session."""
    server = threading.Thread(
        target=lambda: app.run(host="0.0.0.0", port=5000), daemon=True
    )
    server.start()
    time.sleep(1)  # Give the server time to start
    yield


def post(endpoint, payload):
    return requests.post(f"{BASE_URL}{endpoint}", json=payload)


# ── /health ────────────────────────────────────────────────────────────────────


class TestHealth:
    def test_health_ok(self):
        r = requests.get(f"{BASE_URL}/health")
        assert r.status_code == 200
        assert r.json() == {"status": "ok"}


# ── /add ───────────────────────────────────────────────────────────────────────


class TestAdd:
    def test_add_positive(self):
        r = post("/add", {"a": 3, "b": 4})
        assert r.status_code == 200
        assert r.json()["result"] == 7

    def test_add_negative(self):
        r = post("/add", {"a": -5, "b": -3})
        assert r.status_code == 200
        assert r.json()["result"] == -8

    def test_add_floats(self):
        r = post("/add", {"a": 1.5, "b": 2.5})
        assert r.status_code == 200
        assert pytest.approx(r.json()["result"]) == 4.0

    def test_add_mixed_sign(self):
        r = post("/add", {"a": -10, "b": 3})
        assert r.status_code == 200
        assert r.json()["result"] == -7

    def test_add_zeros(self):
        r = post("/add", {"a": 0, "b": 0})
        assert r.status_code == 200
        assert r.json()["result"] == 0


# ── /subtract ─────────────────────────────────────────────────────────────────


class TestSubtract:
    def test_subtract_positive(self):
        r = post("/subtract", {"a": 10, "b": 3})
        assert r.status_code == 200
        assert r.json()["result"] == 7

    def test_subtract_negative(self):
        r = post("/subtract", {"a": -5, "b": -3})
        assert r.status_code == 200
        assert r.json()["result"] == -2

    def test_subtract_floats(self):
        r = post("/subtract", {"a": 5.5, "b": 2.2})
        assert r.status_code == 200
        assert pytest.approx(r.json()["result"]) == 3.3

    def test_subtract_result_negative(self):
        r = post("/subtract", {"a": 3, "b": 10})
        assert r.status_code == 200
        assert r.json()["result"] == -7

    def test_subtract_zero(self):
        r = post("/subtract", {"a": 5, "b": 0})
        assert r.status_code == 200
        assert r.json()["result"] == 5


# ── /multiply ─────────────────────────────────────────────────────────────────


class TestMultiply:
    def test_multiply_positive(self):
        r = post("/multiply", {"a": 3, "b": 4})
        assert r.status_code == 200
        assert r.json()["result"] == 12

    def test_multiply_by_zero(self):
        r = post("/multiply", {"a": 999, "b": 0})
        assert r.status_code == 200
        assert r.json()["result"] == 0

    def test_multiply_negative(self):
        r = post("/multiply", {"a": -3, "b": 4})
        assert r.status_code == 200
        assert r.json()["result"] == -12

    def test_multiply_two_negatives(self):
        r = post("/multiply", {"a": -3, "b": -4})
        assert r.status_code == 200
        assert r.json()["result"] == 12

    def test_multiply_floats(self):
        r = post("/multiply", {"a": 2.5, "b": 4.0})
        assert r.status_code == 200
        assert pytest.approx(r.json()["result"]) == 10.0


# ── /divide ───────────────────────────────────────────────────────────────────


class TestDivide:
    def test_divide_positive(self):
        r = post("/divide", {"a": 10, "b": 2})
        assert r.status_code == 200
        assert r.json()["result"] == 5.0

    def test_divide_by_zero(self):
        r = post("/divide", {"a": 10, "b": 0})
        assert r.status_code == 400
        assert r.json()["error"] == "Division by zero"

    def test_divide_floats(self):
        r = post("/divide", {"a": 7.5, "b": 2.5})
        assert r.status_code == 200
        assert pytest.approx(r.json()["result"]) == 3.0

    def test_divide_negative(self):
        r = post("/divide", {"a": -9, "b": 3})
        assert r.status_code == 200
        assert r.json()["result"] == -3.0

    def test_divide_result_fraction(self):
        r = post("/divide", {"a": 1, "b": 3})
        assert r.status_code == 200
        assert pytest.approx(r.json()["result"]) == pytest.approx(1 / 3)

    def test_divide_zero_numerator(self):
        r = post("/divide", {"a": 0, "b": 5})
        assert r.status_code == 200
        assert r.json()["result"] == 0.0


# ── Przypadki błędów (wszystkie endpointy) ────────────────────────────────────

MATH_ENDPOINTS = ["/add", "/subtract", "/multiply", "/divide"]


@pytest.mark.parametrize("endpoint", MATH_ENDPOINTS)
class TestErrorCases:
    def test_missing_field_a(self, endpoint):
        r = post(endpoint, {"b": 5})
        assert r.status_code == 400
        assert "error" in r.json()

    def test_missing_field_b(self, endpoint):
        r = post(endpoint, {"a": 5})
        assert r.status_code == 400
        assert "error" in r.json()

    def test_missing_both_fields(self, endpoint):
        r = post(endpoint, {})
        assert r.status_code == 400
        assert "error" in r.json()

    def test_non_numeric_a(self, endpoint):
        r = post(endpoint, {"a": "foo", "b": 2})
        assert r.status_code == 400
        assert r.json()["error"] == "Fields a and b must be numbers"

    def test_non_numeric_b(self, endpoint):
        r = post(endpoint, {"a": 2, "b": "bar"})
        assert r.status_code == 400
        assert r.json()["error"] == "Fields a and b must be numbers"

    def test_no_json_body(self, endpoint):
        r = requests.post(f"{BASE_URL}{endpoint}")  # brak Content-Type i body
        assert r.status_code in (400, 415)

    def test_null_values(self, endpoint):
        r = post(endpoint, {"a": None, "b": 2})
        assert r.status_code == 400
        assert "error" in r.json()
