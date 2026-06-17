import pytest
import requests
import time

BASE_URL = "http://127.0.0.1:5000"

def test_health():
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    assert response.json()['status'] == "ok"

def test_add():
    payload = {"a": 10, "b": 5}
    response = requests.post(f"{BASE_URL}/add", json=payload)
    assert response.status_code == 200
    assert response.json()['result'] == 15

def test_subtract():
    payload = {"a": 10, "b": 3}
    response = requests.post(f"{BASE_URL}/subtract", json=payload)
    assert response.json()['result'] == 7

def test_multiply():
    payload = {"a": 4, "b": 5}
    response = requests.post(f"{BASE_URL}/multiply", json=payload)
    assert response.json()['result'] == 20

def test_divide():
    # Normalne dzielenie
    payload = {"a": 10, "b": 2}
    response = requests.post(f"{BASE_URL}/divide", json=payload)
    assert response.json()['result'] == 5

def test_divide_by_zero():
    payload = {"a": 10, "b": 0}
    response = requests.post(f"{BASE_URL}/divide", json=payload)
    assert response.status_code == 400
    assert "error" in response.json()

def test_missing_fields():
    payload = {"a": 10} # Brak pola 'b'
    response = requests.post(f"{BASE_URL}/add", json=payload)
    assert response.status_code == 400

def test_invalid_types():
    payload = {"a": "dziesięć", "b": 5}
    response = requests.post(f"{BASE_URL}/add", json=payload)
    assert response.status_code == 400