import pytest
import requests

BASE_URL = "http://localhost:5000"

# --- Testy endpointu /health ---
def test_health():
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

# --- Testy endpointu /add ---
def test_add_integers():
    response = requests.post(f"{BASE_URL}/add", json={"a": 10, "b": 5})
    assert response.status_code == 200
    assert response.json() == {"result": 15}

def test_add_floats_and_negatives():
    response = requests.post(f"{BASE_URL}/add", json={"a": -2.5, "b": 5.5})
    assert response.status_code == 200
    assert response.json() == {"result": 3.0}

# --- Testy endpointu /subtract ---
def test_subtract_integers():
    response = requests.post(f"{BASE_URL}/subtract", json={"a": 10, "b": 3})
    assert response.status_code == 200
    assert response.json() == {"result": 7}

def test_subtract_negatives():
    response = requests.post(f"{BASE_URL}/subtract", json={"a": -5, "b": -10})
    assert response.status_code == 200
    assert response.json() == {"result": 5}

# --- Testy endpointu /multiply ---
def test_multiply_integers():
    response = requests.post(f"{BASE_URL}/multiply", json={"a": 4, "b": 5})
    assert response.status_code == 200
    assert response.json() == {"result": 20}

def test_multiply_floats():
    response = requests.post(f"{BASE_URL}/multiply", json={"a": 2.5, "b": 2.0})
    assert response.status_code == 200
    assert response.json() == {"result": 5.0}

# --- Testy endpointu /divide ---
def test_divide_integers():
    response = requests.post(f"{BASE_URL}/divide", json={"a": 10, "b": 2})
    assert response.status_code == 200
    assert response.json() == {"result": 5.0} # Dzielenie w Pythonie zwraca float

def test_divide_float_result():
    response = requests.post(f"{BASE_URL}/divide", json={"a": 10, "b": 4})
    assert response.status_code == 200
    assert response.json() == {"result": 2.5}

def test_divide_by_zero():
    response = requests.post(f"{BASE_URL}/divide", json={"a": 10, "b": 0})
    assert response.status_code == 400
    data = response.json()
    assert "error" in data
    assert data["error"] == "Division by zero"

# --- Testy obsługi błędów (walidacja JSON) ---
def test_missing_field():
    # Brakuje pola 'b'
    response = requests.post(f"{BASE_URL}/add", json={"a": 10})
    assert response.status_code == 400
    assert "error" in response.json()

def test_empty_json():
    # Pusty JSON
    response = requests.post(f"{BASE_URL}/add", json={})
    assert response.status_code == 400
    assert "error" in response.json()

def test_invalid_type():
    # Przesłanie stringa zamiast liczby
    response = requests.post(f"{BASE_URL}/add", json={"a": "10", "b": 5})
    assert response.status_code == 400
    assert "error" in response.json()