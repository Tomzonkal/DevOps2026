import pytest
import requests

BASE_URL = "http://localhost:5000"

def test_health():
    """Test czy serwer w ogóle odpowiada"""
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_add_basic():
    """Test podstawowego dodawania"""
    response = requests.post(f"{BASE_URL}/add", json={"a": 10, "b": 5})
    assert response.status_code == 200
    assert response.json() == {"result": 15}

def test_add_floats_and_negatives():
    """Test ułamków i liczb ujemnych"""
    response = requests.post(f"{BASE_URL}/add", json={"a": -5.5, "b": 10.5})
    assert response.status_code == 200
    assert response.json() == {"result": 5.0}

def test_subtract():
    """Test odejmowania"""
    response = requests.post(f"{BASE_URL}/subtract", json={"a": 10, "b": 3})
    assert response.status_code == 200
    assert response.json() == {"result": 7}

def test_multiply():
    """Test mnożenia"""
    response = requests.post(f"{BASE_URL}/multiply", json={"a": 4, "b": 5})
    assert response.status_code == 200
    assert response.json() == {"result": 20}

def test_divide_basic():
    """Test dzielenia"""
    response = requests.post(f"{BASE_URL}/divide", json={"a": 10, "b": 2})
    assert response.status_code == 200
    assert response.json() == {"result": 5.0}

def test_divide_by_zero():
    """Test przypadku brzegowego: dzielenie przez zero"""
    response = requests.post(f"{BASE_URL}/divide", json={"a": 10, "b": 0})
    assert response.status_code == 400
    assert response.json() == {"error": "Division by zero"}

def test_missing_fields():
    """Test obsługi błędów: brakujące pole w JSON"""
    response = requests.post(f"{BASE_URL}/add", json={"a": 10})
    assert response.status_code == 400
    assert response.json() == {"error": "Missing fields: a, b"}

def test_invalid_types():
    """Test obsługi błędów: zły typ danych (string zamiast int/float)"""
    response = requests.post(f"{BASE_URL}/add", json={"a": "10", "b": 5})
    assert response.status_code == 400
    assert response.json() == {"error": "Fields a and b must be numbers"}
