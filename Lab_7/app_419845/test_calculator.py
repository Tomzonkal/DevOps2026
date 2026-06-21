import pytest
import requests

# Definiujemy bazowy adres URL aplikacji
BASE_URL = "http://127.0.0.1:5000"

# --- TESTY ENDPOINTÓW PODSTAWOWYCH ---


def test_health():
    """Sprawdza, czy endpoint /health działa poprawnie."""
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_add_success():
    """Test dodawania liczb całkowitych."""
    payload = {"a": 10, "b": 5}
    response = requests.post(f"{BASE_URL}/add", json=payload)
    assert response.status_code == 200
    assert response.json()["result"] == 15


def test_subtract_success():
    """Test odejmowania."""
    payload = {"a": 10, "b": 3}
    response = requests.post(f"{BASE_URL}/subtract", json=payload)
    assert response.status_code == 200
    assert response.json()["result"] == 7


def test_multiply_success():
    """Test mnożenia."""
    payload = {"a": 4, "b": 5}
    response = requests.post(f"{BASE_URL}/multiply", json=payload)
    assert response.status_code == 200
    assert response.json()["result"] == 20


def test_divide_success():
    """Test dzielenia."""
    payload = {"a": 10, "b": 2}
    response = requests.post(f"{BASE_URL}/divide", json=payload)
    assert response.status_code == 200
    assert response.json()["result"] == 5.0


# --- TESTY PRZYPADKÓW BRZEGOWYCH ---


def test_divide_by_zero():
    """Sprawdza obsługę dzielenia przez zero."""
    payload = {"a": 10, "b": 0}
    response = requests.post(f"{BASE_URL}/divide", json=payload)
    assert response.status_code == 400
    assert response.json()["error"] == "Division by zero"


def test_negative_numbers():
    """Test operacji na liczbach ujemnych."""
    payload = {"a": -5, "b": -10}
    response = requests.post(f"{BASE_URL}/add", json=payload)
    assert response.status_code == 200
    assert response.json()["result"] == -15


def test_float_numbers():
    """Test operacji na liczbach zmiennoprzecinkowych."""
    payload = {"a": 2.5, "b": 2.5}
    response = requests.post(f"{BASE_URL}/multiply", json=payload)
    assert response.status_code == 200
    assert response.json()["result"] == 6.25


# --- TESTY BŁĘDÓW I WALIDACJI ---


def test_missing_fields():
    """Sprawdza błąd w przypadku braku jednego z pól w JSON."""
    payload = {"a": 10}  # Brakuje 'b'
    response = requests.post(f"{BASE_URL}/add", json=payload)
    assert response.status_code == 400
    assert "Missing fields" in response.json()["error"]


def test_invalid_data_types():
    """Sprawdza błąd w przypadku przesłania tekstu zamiast liczb."""
    payload = {"a": "dziesięć", "b": 5}
    response = requests.post(f"{BASE_URL}/add", json=payload)
    assert response.status_code == 400
    assert "must be numbers" in response.json()["error"]


def test_empty_json():
    """Sprawdza reakcję na pusty obiekt JSON."""
    response = requests.post(f"{BASE_URL}/add", json={})
    assert response.status_code == 400
