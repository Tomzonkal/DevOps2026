"""
Testy integracyjne dla kalkulatorowego API Flask.

Testy wykonują prawdziwe żądania HTTP (biblioteka `requests`) do DZIAŁAJĄCEGO
serwera. Przed uruchomieniem testów uruchom aplikację, np.:

    python app.py

Adres serwera można nadpisać zmienną środowiskową:

    CALC_API_URL=http://localhost:5000 pytest -v

Uruchomienie:

    pip install pytest requests
    pytest -v test_calculator_api.py
"""

import os

import pytest
import requests

BASE_URL = os.environ.get("CALC_API_URL", "http://localhost:5000").rstrip("/")
TIMEOUT = 5  # sekundy


# --------------------------------------------------------------------------- #
# Pomocnicze
# --------------------------------------------------------------------------- #
def post(endpoint, payload):
    """POST z JSON-em na wskazany endpoint."""
    return requests.post(f"{BASE_URL}{endpoint}", json=payload, timeout=TIMEOUT)


@pytest.fixture(scope="session", autouse=True)
def ensure_server_running():
    """
    Sprawdza, czy serwer odpowiada zanim ruszą testy.
    Jeśli nie — przerywa cały zestaw z czytelnym komunikatem zamiast
    rzucać ConnectionError w każdym teście z osobna.
    """
    try:
        resp = requests.get(f"{BASE_URL}/health", timeout=TIMEOUT)
        resp.raise_for_status()
    except requests.RequestException as exc:
        pytest.exit(
            f"Serwer pod {BASE_URL} nie odpowiada na /health: {exc}\n"
            "Uruchom aplikację (np. `python app.py`) i spróbuj ponownie.",
            returncode=1,
        )


# --------------------------------------------------------------------------- #
# /health
# --------------------------------------------------------------------------- #
def test_health_ok():
    resp = requests.get(f"{BASE_URL}/health", timeout=TIMEOUT)
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


# --------------------------------------------------------------------------- #
# /add
# --------------------------------------------------------------------------- #
class TestAdd:
    def test_basic(self):
        resp = post("/add", {"a": 2, "b": 3})
        assert resp.status_code == 200
        assert resp.json() == {"result": 5}

    def test_negative(self):
        resp = post("/add", {"a": -5, "b": -7})
        assert resp.status_code == 200
        assert resp.json() == {"result": -12}

    def test_negative_and_positive(self):
        resp = post("/add", {"a": -10, "b": 4})
        assert resp.status_code == 200
        assert resp.json() == {"result": -6}

    def test_floats(self):
        resp = post("/add", {"a": 0.1, "b": 0.2})
        assert resp.status_code == 200
        # uwaga na arytmetykę zmiennoprzecinkową
        assert resp.json()["result"] == pytest.approx(0.3)

    def test_zero(self):
        resp = post("/add", {"a": 0, "b": 0})
        assert resp.status_code == 200
        assert resp.json() == {"result": 0}


# --------------------------------------------------------------------------- #
# /subtract
# --------------------------------------------------------------------------- #
class TestSubtract:
    def test_basic(self):
        resp = post("/subtract", {"a": 10, "b": 3})
        assert resp.status_code == 200
        assert resp.json() == {"result": 7}

    def test_result_negative(self):
        resp = post("/subtract", {"a": 3, "b": 10})
        assert resp.status_code == 200
        assert resp.json() == {"result": -7}

    def test_negative_operands(self):
        resp = post("/subtract", {"a": -5, "b": -8})
        assert resp.status_code == 200
        assert resp.json() == {"result": 3}

    def test_floats(self):
        resp = post("/subtract", {"a": 5.5, "b": 2.25})
        assert resp.status_code == 200
        assert resp.json()["result"] == pytest.approx(3.25)


# --------------------------------------------------------------------------- #
# /multiply
# --------------------------------------------------------------------------- #
class TestMultiply:
    def test_basic(self):
        resp = post("/multiply", {"a": 4, "b": 6})
        assert resp.status_code == 200
        assert resp.json() == {"result": 24}

    def test_by_zero(self):
        resp = post("/multiply", {"a": 99, "b": 0})
        assert resp.status_code == 200
        assert resp.json() == {"result": 0}

    def test_negative(self):
        resp = post("/multiply", {"a": -3, "b": 7})
        assert resp.status_code == 200
        assert resp.json() == {"result": -21}

    def test_two_negatives(self):
        resp = post("/multiply", {"a": -3, "b": -7})
        assert resp.status_code == 200
        assert resp.json() == {"result": 21}

    def test_floats(self):
        resp = post("/multiply", {"a": 1.5, "b": 2.0})
        assert resp.status_code == 200
        assert resp.json()["result"] == pytest.approx(3.0)


# --------------------------------------------------------------------------- #
# /divide
# --------------------------------------------------------------------------- #
class TestDivide:
    def test_basic(self):
        resp = post("/divide", {"a": 10, "b": 2})
        assert resp.status_code == 200
        assert resp.json() == {"result": 5}

    def test_non_integer_result(self):
        resp = post("/divide", {"a": 7, "b": 2})
        assert resp.status_code == 200
        assert resp.json()["result"] == pytest.approx(3.5)

    def test_negative(self):
        resp = post("/divide", {"a": -9, "b": 3})
        assert resp.status_code == 200
        assert resp.json()["result"] == pytest.approx(-3)

    def test_floats(self):
        resp = post("/divide", {"a": 1.0, "b": 4.0})
        assert resp.status_code == 200
        assert resp.json()["result"] == pytest.approx(0.25)

    def test_by_zero(self):
        resp = post("/divide", {"a": 5, "b": 0})
        assert resp.status_code == 400
        assert resp.json() == {"error": "Division by zero"}

    def test_zero_float_by_zero(self):
        resp = post("/divide", {"a": 5, "b": 0.0})
        assert resp.status_code == 400
        assert resp.json() == {"error": "Division by zero"}


# --------------------------------------------------------------------------- #
# Przypadki błędów — walidacja wejścia.
# Parametryzacja po wszystkich endpointach, które używają _parse_numbers.
# --------------------------------------------------------------------------- #
ARITHMETIC_ENDPOINTS = ["/add", "/subtract", "/multiply", "/divide"]


class TestValidationErrors:
    @pytest.mark.parametrize("endpoint", ARITHMETIC_ENDPOINTS)
    def test_missing_both_fields(self, endpoint):
        resp = post(endpoint, {})
        assert resp.status_code == 400
        assert resp.json() == {"error": "Missing fields: a, b"}

    @pytest.mark.parametrize("endpoint", ARITHMETIC_ENDPOINTS)
    def test_missing_field_b(self, endpoint):
        resp = post(endpoint, {"a": 1})
        assert resp.status_code == 400
        assert resp.json() == {"error": "Missing fields: a, b"}

    @pytest.mark.parametrize("endpoint", ARITHMETIC_ENDPOINTS)
    def test_missing_field_a(self, endpoint):
        resp = post(endpoint, {"b": 1})
        assert resp.status_code == 400
        assert resp.json() == {"error": "Missing fields: a, b"}

    @pytest.mark.parametrize("endpoint", ARITHMETIC_ENDPOINTS)
    def test_string_value(self, endpoint):
        resp = post(endpoint, {"a": "10", "b": 2})
        assert resp.status_code == 400
        assert resp.json() == {"error": "Fields a and b must be numbers"}

    @pytest.mark.parametrize("endpoint", ARITHMETIC_ENDPOINTS)
    def test_null_value(self, endpoint):
        resp = post(endpoint, {"a": None, "b": 2})
        assert resp.status_code == 400
        assert resp.json() == {"error": "Fields a and b must be numbers"}

    @pytest.mark.parametrize("endpoint", ARITHMETIC_ENDPOINTS)
    def test_list_value(self, endpoint):
        resp = post(endpoint, {"a": [1, 2], "b": 3})
        assert resp.status_code == 400
        assert resp.json() == {"error": "Fields a and b must be numbers"}

    @pytest.mark.parametrize("endpoint", ARITHMETIC_ENDPOINTS)
    def test_empty_body(self, endpoint):
        # Puste ciało z Content-Type: application/json jest niepoprawnym JSON-em.
        # request.get_json() (domyślnie silent=False) rzuca wtedy BadRequest,
        # więc to SAM Flask zwraca 400 — i to jako stronę HTML, nie nasz JSON.
        # Sprawdzamy zatem tylko status; ciała nie parsujemy jako JSON.
        resp = requests.post(
            f"{BASE_URL}{endpoint}",
            data="",
            headers={"Content-Type": "application/json"},
            timeout=TIMEOUT,
        )
        assert resp.status_code == 400

    @pytest.mark.parametrize("endpoint", ARITHMETIC_ENDPOINTS)
    def test_no_json_body_at_all(self, endpoint):
        # POST bez nagłówka Content-Type: application/json. Flask uznaje typ
        # zawartości za nieobsługiwany i request.get_json() rzuca
        # UnsupportedMediaType -> odpowiedź 415, NIE 400.
        resp = requests.post(f"{BASE_URL}{endpoint}", timeout=TIMEOUT)
        assert resp.status_code == 415

    @pytest.mark.parametrize("endpoint", ARITHMETIC_ENDPOINTS)
    def test_malformed_json(self, endpoint):
        # Składniowo zepsuty JSON -> Flask odrzuca z 400 (strona HTML).
        resp = requests.post(
            f"{BASE_URL}{endpoint}",
            data="{not valid json",
            headers={"Content-Type": "application/json"},
            timeout=TIMEOUT,
        )
        assert resp.status_code == 400


# --------------------------------------------------------------------------- #
# Uwaga o typie bool: w Pythonie bool jest podtypem int, więc isinstance(True, int)
# == True. Ten test dokumentuje aktualne zachowanie API (True traktowane jak 1).
# --------------------------------------------------------------------------- #
def test_bool_treated_as_number_documenting_behavior():
    resp = post("/add", {"a": True, "b": 1})
    # True == 1, więc API to akceptuje i zwraca 2
    assert resp.status_code == 200
    assert resp.json() == {"result": 2}