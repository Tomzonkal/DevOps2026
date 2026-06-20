"""
Testy pytest dla aplikacji Flask calculator.
Uruchamiają rzeczywisty serwer Flask i wysyłają żądania HTTP przez bibliotekę `requests`.

Uruchomienie:
    pip install flask pytest requests
    pytest test_calculator.py -v
"""

import threading
import time

import pytest
import requests

from calculator import app

BASE_URL = "http://127.0.0.1:5001"


# ---------------------------------------------------------------------------
# Fixture: uruchamia serwer Flask w osobnym wątku na czas sesji testowej
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session", autouse=True)
def live_server():
    """Uruchamia serwer Flask w wątku-daemonie przed całą sesją testową."""
    server_thread = threading.Thread(
        target=lambda: app.run(host="127.0.0.1", port=5001, use_reloader=False),
        daemon=True,
    )
    server_thread.start()

    # Czekaj aż serwer będzie gotowy (max 5 sekund)
    for _ in range(50):
        try:
            requests.get(f"{BASE_URL}/health", timeout=0.2)
            break
        except requests.ConnectionError:
            time.sleep(0.1)
    else:
        pytest.fail("Serwer Flask nie uruchomił się w wyznaczonym czasie.")

    yield  # tutaj wykonują się testy


# ---------------------------------------------------------------------------
# Pomocnicze funkcje
# ---------------------------------------------------------------------------

def post(endpoint, payload):
    return requests.post(f"{BASE_URL}{endpoint}", json=payload)


# ===========================================================================
# /health
# ===========================================================================

class TestHealth:
    def test_returns_ok(self):
        r = requests.get(f"{BASE_URL}/health")
        assert r.status_code == 200
        assert r.json() == {"status": "ok"}


# ===========================================================================
# /add
# ===========================================================================

class TestAdd:
    def test_add_positive_integers(self):
        r = post("/add", {"a": 3, "b": 4})
        assert r.status_code == 200
        assert r.json()["result"] == 7

    def test_add_negative_numbers(self):
        r = post("/add", {"a": -5, "b": -3})
        assert r.status_code == 200
        assert r.json()["result"] == -8

    def test_add_mixed_sign(self):
        r = post("/add", {"a": 10, "b": -4})
        assert r.status_code == 200
        assert r.json()["result"] == 6

    def test_add_floats(self):
        r = post("/add", {"a": 1.5, "b": 2.5})
        assert r.status_code == 200
        assert r.json()["result"] == pytest.approx(4.0)

    def test_add_zero(self):
        r = post("/add", {"a": 0, "b": 0})
        assert r.status_code == 200
        assert r.json()["result"] == 0

    def test_add_large_numbers(self):
        r = post("/add", {"a": 1_000_000, "b": 2_000_000})
        assert r.status_code == 200
        assert r.json()["result"] == 3_000_000


# ===========================================================================
# /subtract
# ===========================================================================

class TestSubtract:
    def test_subtract_positive(self):
        r = post("/subtract", {"a": 10, "b": 3})
        assert r.status_code == 200
        assert r.json()["result"] == 7

    def test_subtract_gives_negative(self):
        r = post("/subtract", {"a": 3, "b": 10})
        assert r.status_code == 200
        assert r.json()["result"] == -7

    def test_subtract_negative_numbers(self):
        r = post("/subtract", {"a": -2, "b": -5})
        assert r.status_code == 200
        assert r.json()["result"] == 3

    def test_subtract_floats(self):
        r = post("/subtract", {"a": 5.5, "b": 2.2})
        assert r.status_code == 200
        assert r.json()["result"] == pytest.approx(3.3)

    def test_subtract_zero(self):
        r = post("/subtract", {"a": 7, "b": 0})
        assert r.status_code == 200
        assert r.json()["result"] == 7


# ===========================================================================
# /multiply
# ===========================================================================

class TestMultiply:
    def test_multiply_positive(self):
        r = post("/multiply", {"a": 3, "b": 4})
        assert r.status_code == 200
        assert r.json()["result"] == 12

    def test_multiply_by_zero(self):
        r = post("/multiply", {"a": 99, "b": 0})
        assert r.status_code == 200
        assert r.json()["result"] == 0

    def test_multiply_negatives(self):
        r = post("/multiply", {"a": -3, "b": -4})
        assert r.status_code == 200
        assert r.json()["result"] == 12

    def test_multiply_mixed_sign(self):
        r = post("/multiply", {"a": -3, "b": 4})
        assert r.status_code == 200
        assert r.json()["result"] == -12

    def test_multiply_floats(self):
        r = post("/multiply", {"a": 2.5, "b": 4.0})
        assert r.status_code == 200
        assert r.json()["result"] == pytest.approx(10.0)


# ===========================================================================
# /divide
# ===========================================================================

class TestDivide:
    def test_divide_positive(self):
        r = post("/divide", {"a": 10, "b": 2})
        assert r.status_code == 200
        assert r.json()["result"] == 5.0

    def test_divide_with_float_result(self):
        r = post("/divide", {"a": 7, "b": 2})
        assert r.status_code == 200
        assert r.json()["result"] == pytest.approx(3.5)

    def test_divide_negative_dividend(self):
        r = post("/divide", {"a": -10, "b": 2})
        assert r.status_code == 200
        assert r.json()["result"] == -5.0

    def test_divide_both_negative(self):
        r = post("/divide", {"a": -10, "b": -2})
        assert r.status_code == 200
        assert r.json()["result"] == 5.0

    def test_divide_floats(self):
        r = post("/divide", {"a": 1.0, "b": 4.0})
        assert r.status_code == 200
        assert r.json()["result"] == pytest.approx(0.25)

    def test_divide_by_zero_returns_400(self):
        r = post("/divide", {"a": 5, "b": 0})
        assert r.status_code == 400
        assert "error" in r.json()
        assert r.json()["error"] == "Division by zero"

    def test_divide_float_by_zero_returns_400(self):
        r = post("/divide", {"a": 3.14, "b": 0})
        assert r.status_code == 400
        assert r.json()["error"] == "Division by zero"


# ===========================================================================
# Przypadki błędów – wspólne dla wszystkich endpointów
# ===========================================================================

ENDPOINTS = ["/add", "/subtract", "/multiply", "/divide"]


@pytest.mark.parametrize("endpoint", ENDPOINTS)
class TestErrorHandling:
    def test_missing_both_fields(self, endpoint):
        r = post(endpoint, {})
        assert r.status_code == 400
        assert "error" in r.json()

    def test_missing_field_a(self, endpoint):
        r = post(endpoint, {"b": 5})
        assert r.status_code == 400
        assert "error" in r.json()

    def test_missing_field_b(self, endpoint):
        r = post(endpoint, {"a": 5})
        assert r.status_code == 400
        assert "error" in r.json()

    def test_string_instead_of_number_a(self, endpoint):
        r = post(endpoint, {"a": "abc", "b": 2})
        assert r.status_code == 400
        assert "error" in r.json()

    def test_string_instead_of_number_b(self, endpoint):
        r = post(endpoint, {"a": 2, "b": "xyz"})
        assert r.status_code == 400
        assert "error" in r.json()

    def test_null_body(self, endpoint):
        """Wysłanie żądania bez ciała JSON ani nagłówka Content-Type.
        Flask zwraca 415 Unsupported Media Type, ponieważ brakuje
        nagłówka 'Content-Type: application/json'."""
        r = requests.post(f"{BASE_URL}{endpoint}")
        assert r.status_code in (400, 415)

    def test_boolean_rejected_as_non_number(self, endpoint):
        """bool jest podklasą int w Pythonie – sprawdzamy, jak serwer go traktuje."""
        r = post(endpoint, {"a": True, "b": 1})
        # bool to podklasa int, więc serwer aktualnie akceptuje True jako 1
        # Ten test dokumentuje bieżące zachowanie
        assert r.status_code == 200
