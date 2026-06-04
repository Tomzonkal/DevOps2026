import pytest
import requests

BASE_URL = "http://localhost:5000"

# --- 1. TESTY PODSTAWOWYCH ENDPOINTÓW (Happy Path) ---

def test_add_success():
    payload = {"a": 10, "b": 5}
    response = requests.post(f"{BASE_URL}/add", json=payload)
    assert response.status_code == 200
    assert response.json() == {"result": 15}

def test_subtract_success():
    payload = {"a": 10, "b": 3}
    response = requests.post(f"{BASE_URL}/subtract", json=payload)
    assert response.status_code == 200
    assert response.json() == {"result": 7}

def test_multiply_success():
    payload = {"a": 4, "b": 5}
    response = requests.post(f"{BASE_URL}/multiply", json=payload)
    assert response.status_code == 200
    assert response.json() == {"result": 20}

def test_divide_success():
    payload = {"a": 10, "b": 2}
    response = requests.post(f"{BASE_URL}/divide", json=payload)
    assert response.status_code == 200
    assert response.json() == {"result": 5.0}

def test_health_check():
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# --- 2. PRZYPADKI BRZEGOWE (Liczby ujemne i zmiennoprzecinkowe) ---

def test_negative_numbers():
    payload = {"a": -5, "b": -3}
    response = requests.post(f"{BASE_URL}/add", json=payload)
    assert response.status_code == 200
    assert response.json() == {"result": -8}

def test_float_numbers():
    payload = {"a": 2.5, "b": 1.5}
    response = requests.post(f"{BASE_URL}/multiply", json=payload)
    assert response.status_code == 200
    assert response.json() == {"result": 3.75}


# --- 3. PRZYPADKI BŁĘDÓW I WALIDACJI (Główny cel dydaktyczny) ---

def test_divide_by_zero():
    payload = {"a": 10, "b": 0}
    response = requests.post(f"{BASE_URL}/divide", json=payload)
    assert response.status_code == 400
    assert "error" in response.json()
    assert response.json()["error"] == "Division by zero"

def test_missing_fields():
    payload = {"a": 10}  # Brak pola 'b'
    response = requests.post(f"{BASE_URL}/add", json=payload)
    assert response.status_code == 400
    assert "error" in response.json()
    assert response.json()["error"] == "Missing fields: a, b"

def test_invalid_data_type():
    payload = {"a": "dziesięć", "b": 5}  # Tekst zamiast liczby
    response = requests.post(f"{BASE_URL}/add", json=payload)
    assert response.status_code == 400
    assert "error" in response.json()
    assert response.json()["error"] == "Fields a and b must be numbers"