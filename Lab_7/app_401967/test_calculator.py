"""
Testy integracyjne dla Flask Calculator API.
Używają biblioteki `requests` do komunikacji z działającym serwerem.
"""

import multiprocessing
import time

import pytest
import requests

# ── Uruchomienie serwera ─────────────────────────────────────────────────────

HOST = "127.0.0.1"
PORT = 5001
BASE_URL = f"http://{HOST}:{PORT}"


def _run_server():
    """Uruchamia aplikację Flask w osobnym procesie."""
    import sys
    import os

    sys.path.insert(0, "/mnt/user-data/uploads")
    # Wyciszamy logi Flask podczas testów
    import logging
    log = logging.getLogger("werkzeug")
    log.setLevel(logging.ERROR)

    from calculator import app
    app.run(host=HOST, port=PORT, use_reloader=False, debug=False)


@pytest.fixture(scope="session", autouse=True)
def live_server():
    """Uruchamia serwer raz dla całej sesji testowej."""
    proc = multiprocessing.Process(target=_run_server, daemon=True)
    proc.start()

    # Czekamy aż serwer będzie gotowy (max 5 sekund)
    for _ in range(50):
        try:
            requests.get(f"{BASE_URL}/health", timeout=0.5)
            break
        except requests.exceptions.ConnectionError:
            time.sleep(0.1)
    else:
        proc.terminate()
        pytest.fail("Serwer Flask nie uruchomił się w czasie 5 sekund.")

    yield

    proc.terminate()
    proc.join(timeout=2)


# ── Pomocnik ─────────────────────────────────────────────────────────────────

def post(endpoint: str, payload: dict) -> requests.Response:
    return requests.post(f"{BASE_URL}{endpoint}", json=payload, timeout=5)


# ── /health ───────────────────────────────────────────────────────────────────

class TestHealth:
    def test_health_returns_ok(self):
        resp = requests.get(f"{BASE_URL}/health", timeout=5)
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}


# ── /add ──────────────────────────────────────────────────────────────────────

class TestAdd:
    def test_add_positive_integers(self):
        resp = post("/add", {"a": 3, "b": 4})
        assert resp.status_code == 200
        assert resp.json()["result"] == 7

    def test_add_negative_numbers(self):
        resp = post("/add", {"a": -10, "b": -5})
        assert resp.status_code == 200
        assert resp.json()["result"] == -15

    def test_add_floats(self):
        resp = post("/add", {"a": 1.5, "b": 2.5})
        assert resp.status_code == 200
        assert resp.json()["result"] == pytest.approx(4.0)

    def test_add_mixed_sign(self):
        resp = post("/add", {"a": -3, "b": 10})
        assert resp.status_code == 200
        assert resp.json()["result"] == 7

    def test_add_zero(self):
        resp = post("/add", {"a": 0, "b": 0})
        assert resp.status_code == 200
        assert resp.json()["result"] == 0

    def test_add_large_numbers(self):
        resp = post("/add", {"a": 1_000_000, "b": 2_000_000})
        assert resp.status_code == 200
        assert resp.json()["result"] == 3_000_000

    # -- błędy

    def test_add_missing_field_a(self):
        resp = post("/add", {"b": 5})
        assert resp.status_code == 400
        assert "error" in resp.json()

    def test_add_missing_field_b(self):
        resp = post("/add", {"a": 5})
        assert resp.status_code == 400
        assert "error" in resp.json()

    def test_add_missing_both_fields(self):
        resp = post("/add", {})
        assert resp.status_code == 400
        assert "error" in resp.json()

    def test_add_null_body(self):
        """Brak body i nagłówka Content-Type – Flask zwraca 415 (Unsupported Media Type)."""
        resp = requests.post(f"{BASE_URL}/add", timeout=5)
        assert resp.status_code in (400, 415)

    def test_add_string_values(self):
        resp = post("/add", {"a": "jeden", "b": 2})
        assert resp.status_code == 400
        assert "error" in resp.json()


# ── /subtract ─────────────────────────────────────────────────────────────────

class TestSubtract:
    def test_subtract_positive_integers(self):
        resp = post("/subtract", {"a": 10, "b": 3})
        assert resp.status_code == 200
        assert resp.json()["result"] == 7

    def test_subtract_result_negative(self):
        resp = post("/subtract", {"a": 3, "b": 10})
        assert resp.status_code == 200
        assert resp.json()["result"] == -7

    def test_subtract_negative_numbers(self):
        resp = post("/subtract", {"a": -5, "b": -3})
        assert resp.status_code == 200
        assert resp.json()["result"] == -2

    def test_subtract_floats(self):
        resp = post("/subtract", {"a": 5.5, "b": 2.2})
        assert resp.status_code == 200
        assert resp.json()["result"] == pytest.approx(3.3)

    def test_subtract_zero(self):
        resp = post("/subtract", {"a": 7, "b": 0})
        assert resp.status_code == 200
        assert resp.json()["result"] == 7

    # -- błędy

    def test_subtract_missing_fields(self):
        resp = post("/subtract", {"a": 5})
        assert resp.status_code == 400

    def test_subtract_string_values(self):
        resp = post("/subtract", {"a": "abc", "b": 1})
        assert resp.status_code == 400


# ── /multiply ─────────────────────────────────────────────────────────────────

class TestMultiply:
    def test_multiply_positive_integers(self):
        resp = post("/multiply", {"a": 3, "b": 4})
        assert resp.status_code == 200
        assert resp.json()["result"] == 12

    def test_multiply_by_zero(self):
        resp = post("/multiply", {"a": 999, "b": 0})
        assert resp.status_code == 200
        assert resp.json()["result"] == 0

    def test_multiply_negative_numbers(self):
        resp = post("/multiply", {"a": -3, "b": -4})
        assert resp.status_code == 200
        assert resp.json()["result"] == 12

    def test_multiply_mixed_sign(self):
        resp = post("/multiply", {"a": -3, "b": 4})
        assert resp.status_code == 200
        assert resp.json()["result"] == -12

    def test_multiply_floats(self):
        resp = post("/multiply", {"a": 2.5, "b": 4.0})
        assert resp.status_code == 200
        assert resp.json()["result"] == pytest.approx(10.0)

    # -- błędy

    def test_multiply_missing_fields(self):
        resp = post("/multiply", {})
        assert resp.status_code == 400

    def test_multiply_boolean_treated_as_number(self):
        """bool jest podklasą int w Pythonie – serwer akceptuje True (1) i False (0)."""
        resp = post("/multiply", {"a": True, "b": 5})
        assert resp.status_code == 200
        assert resp.json()["result"] == 5


# ── /divide ───────────────────────────────────────────────────────────────────

class TestDivide:
    def test_divide_positive_integers(self):
        resp = post("/divide", {"a": 10, "b": 2})
        assert resp.status_code == 200
        assert resp.json()["result"] == 5.0

    def test_divide_result_float(self):
        resp = post("/divide", {"a": 7, "b": 2})
        assert resp.status_code == 200
        assert resp.json()["result"] == pytest.approx(3.5)

    def test_divide_negative_numerator(self):
        resp = post("/divide", {"a": -9, "b": 3})
        assert resp.status_code == 200
        assert resp.json()["result"] == -3.0

    def test_divide_both_negative(self):
        resp = post("/divide", {"a": -6, "b": -2})
        assert resp.status_code == 200
        assert resp.json()["result"] == 3.0

    def test_divide_float_operands(self):
        resp = post("/divide", {"a": 7.5, "b": 2.5})
        assert resp.status_code == 200
        assert resp.json()["result"] == pytest.approx(3.0)

    def test_divide_zero_numerator(self):
        resp = post("/divide", {"a": 0, "b": 5})
        assert resp.status_code == 200
        assert resp.json()["result"] == 0.0

    # -- przypadek brzegowy: dzielenie przez zero

    def test_divide_by_zero_returns_400(self):
        resp = post("/divide", {"a": 10, "b": 0})
        assert resp.status_code == 400

    def test_divide_by_zero_error_message(self):
        resp = post("/divide", {"a": 10, "b": 0})
        body = resp.json()
        assert "error" in body
        assert "zero" in body["error"].lower()

    def test_divide_by_zero_float(self):
        resp = post("/divide", {"a": 5.5, "b": 0.0})
        assert resp.status_code == 400

    # -- błędy

    def test_divide_missing_fields(self):
        resp = post("/divide", {"a": 10})
        assert resp.status_code == 400

    def test_divide_string_denominator(self):
        resp = post("/divide", {"a": 10, "b": "dwa"})
        assert resp.status_code == 400


# ── Content-Type ──────────────────────────────────────────────────────────────

class TestContentType:
    def test_response_is_json(self):
        resp = post("/add", {"a": 1, "b": 2})
        assert "application/json" in resp.headers.get("Content-Type", "")

    def test_error_response_is_json(self):
        resp = post("/divide", {"a": 1, "b": 0})
        assert "application/json" in resp.headers.get("Content-Type", "")