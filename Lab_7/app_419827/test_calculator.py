import os
import requests
import pytest

BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")


def test_health():
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.parametrize("endpoint, data, expected", [
    ("/add", {"a": 10, "b": 5}, 15),
    ("/subtract", {"a": 10, "b": 3}, 7),
    ("/multiply", {"a": 4, "b": 5}, 20),
    ("/divide", {"a": 10, "b": 2}, 5),
])
def test_basic_operations(endpoint, data, expected):
    response = requests.post(f"{BASE_URL}{endpoint}", json=data)
    assert response.status_code == 200
    assert response.json()["result"] == expected


def test_divide_by_zero():
    response = requests.post(f"{BASE_URL}/divide", json={"a": 10, "b": 0})
    assert response.status_code == 400
    assert response.json()["error"] == "Division by zero"


def test_negative_numbers():
    response = requests.post(f"{BASE_URL}/add", json={"a": -10, "b": -5})
    assert response.status_code == 200
    assert response.json()["result"] == -15


def test_float_numbers():
    response = requests.post(f"{BASE_URL}/multiply", json={"a": 2.5, "b": 4})
    assert response.status_code == 200
    assert response.json()["result"] == 10.0


@pytest.mark.parametrize("endpoint", ["/add", "/subtract", "/multiply", "/divide"])
def test_missing_field_b(endpoint):
    response = requests.post(f"{BASE_URL}{endpoint}", json={"a": 10})
    assert response.status_code == 400
    assert response.json()["error"] == "Missing fields: a, b"


@pytest.mark.parametrize("endpoint", ["/add", "/subtract", "/multiply", "/divide"])
def test_missing_field_a(endpoint):
    response = requests.post(f"{BASE_URL}{endpoint}", json={"b": 5})
    assert response.status_code == 400
    assert response.json()["error"] == "Missing fields: a, b"


@pytest.mark.parametrize("endpoint", ["/add", "/subtract", "/multiply", "/divide"])
def test_non_numeric_fields(endpoint):
    response = requests.post(f"{BASE_URL}{endpoint}", json={"a": "abc", "b": 5})
    assert response.status_code == 400
    assert response.json()["error"] == "Fields a and b must be numbers"
