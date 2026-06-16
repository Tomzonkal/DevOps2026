import pytest
import requests

BASE_URL = "http://localhost:5000"


def test_health_check():
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_add_positive_numbers():
    payload = {"a": 10, "b": 5}
    response = requests.post(f"{BASE_URL}/add", json=payload)
    assert response.status_code == 200
    assert response.json() == {"result": 15}


def test_add_floats_and_negatives():
    payload = {"a": -2.5, "b": 5.0}
    response = requests.post(f"{BASE_URL}/add", json=payload)
    assert response.status_code == 200
    assert response.json() == {"result": 2.5}


def test_subtract_numbers():
    payload = {"a": 10, "b": 3}
    response = requests.post(f"{BASE_URL}/subtract", json=payload)
    assert response.status_code == 200
    assert response.json() == {"result": 7}


def test_multiply_numbers():
    payload = {"a": 4, "b": 5}
    response = requests.post(f"{BASE_URL}/multiply", json=payload)
    assert response.status_code == 200
    assert response.json() == {"result": 20}


def test_divide_numbers():
    payload = {"a": 10, "b": 2}
    response = requests.post(f"{BASE_URL}/divide", json=payload)
    assert response.status_code == 200
    assert response.json() == {"result": 5.0}


def test_divide_by_zero():
    payload = {"a": 10, "b": 0}
    response = requests.post(f"{BASE_URL}/divide", json=payload)
    assert response.status_code == 400
    assert response.json()["error"] == "Division by zero"


def test_missing_fields():
    payload = {"a": 10}
    response = requests.post(f"{BASE_URL}/add", json=payload)
    assert response.status_code == 400
    assert response.json()["error"] == "Missing fields: a, b"


def test_empty_payload():
    payload = {}
    response = requests.post(f"{BASE_URL}/multiply", json=payload)
    assert response.status_code == 400
    assert response.json()["error"] == "Missing fields: a, b"


def test_invalid_data_types():
    payload = {"a": "dziesięć", "b": 5}
    response = requests.post(f"{BASE_URL}/subtract", json=payload)
    assert response.status_code == 400
    assert response.json()["error"] == "Fields a and b must be numbers"
