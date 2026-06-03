import pytest
import requests

# Zmienna definiująca adres działającego serwera
BASE_URL = "http://localhost:5000"


def test_health_check():
    """Test endpointu /health sprawdzającego status API."""
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.parametrize(
    "a, b, expected",
    [
        (10, 5, 15),  # Liczby dodatnie
        (-10, -5, -15),  # Liczby ujemne
        (10.5, 5.2, 15.7),  # Liczby zmiennoprzecinkowe
        (-10, 5, -5),  # Mieszane znaki
        (0, 0, 0),  # Zera
    ],
)
def test_add(a, b, expected):
    """Testy dodawania dla różnych typów liczb."""
    response = requests.post(f"{BASE_URL}/add", json={"a": a, "b": b})
    assert response.status_code == 200
    # Używamy pytest.approx dla ułamków, aby uniknąć błędów precyzji zmiennoprzecinkowej
    assert response.json()["result"] == pytest.approx(expected)


@pytest.mark.parametrize(
    "a, b, expected", [(10, 5, 5), (-10, -5, -5), (10.5, 5.2, 5.3), (0, 5, -5)]
)
def test_subtract(a, b, expected):
    """Testy odejmowania dla różnych typów liczb."""
    response = requests.post(f"{BASE_URL}/subtract", json={"a": a, "b": b})
    assert response.status_code == 200
    assert response.json()["result"] == pytest.approx(expected)


@pytest.mark.parametrize(
    "a, b, expected",
    [(10, 5, 50), (-10, -5, 50), (-10, 5, -50), (10.5, 2.0, 21.0), (10, 0, 0)],
)
def test_multiply(a, b, expected):
    """Testy mnożenia dla różnych typów liczb."""
    response = requests.post(f"{BASE_URL}/multiply", json={"a": a, "b": b})
    assert response.status_code == 200
    assert response.json()["result"] == pytest.approx(expected)


@pytest.mark.parametrize(
    "a, b, expected",
    [(10, 5, 2.0), (-10, -5, 2.0), (-10, 5, -2.0), (10.5, 2.0, 5.25), (0, 5, 0.0)],
)
def test_divide(a, b, expected):
    """Testy dzielenia dla różnych typów liczb (bez zera)."""
    response = requests.post(f"{BASE_URL}/divide", json={"a": a, "b": b})
    assert response.status_code == 200
    assert response.json()["result"] == pytest.approx(expected)


def test_divide_by_zero():
    """Test przypadku brzegowego - dzielenie przez zero."""
    response = requests.post(f"{BASE_URL}/divide", json={"a": 10, "b": 0})
    assert response.status_code == 400
    assert response.json() == {"error": "Division by zero"}


@pytest.mark.parametrize("endpoint", ["/add", "/subtract", "/multiply", "/divide"])
def test_missing_fields(endpoint):
    """Test sprawdzający błąd, gdy brakuje jednego z pól w JSON."""
    # Brakuje pola 'b'
    response = requests.post(f"{BASE_URL}{endpoint}", json={"a": 10})
    assert response.status_code == 400
    assert response.json() == {"error": "Missing fields: a, b"}

    # Całkowicie pusty JSON
    response_empty = requests.post(f"{BASE_URL}{endpoint}", json={})
    assert response_empty.status_code == 400
    assert response_empty.json() == {"error": "Missing fields: a, b"}


@pytest.mark.parametrize("endpoint", ["/add", "/subtract", "/multiply", "/divide"])
def test_invalid_types(endpoint):
    """Test sprawdzający błąd, gdy przekazane dane nie są liczbami."""
    # Przekazanie stringa zamiast liczby
    response = requests.post(f"{BASE_URL}{endpoint}", json={"a": 10, "b": "pięć"})
    assert response.status_code == 400
    assert response.json() == {"error": "Fields a and b must be numbers"}

    # Przekazanie nulla
    response_null = requests.post(f"{BASE_URL}{endpoint}", json={"a": None, "b": 5})
    assert response_null.status_code == 400
    assert response_null.json() == {"error": "Fields a and b must be numbers"}
