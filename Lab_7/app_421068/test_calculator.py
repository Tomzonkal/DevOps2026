import pytest
import requests

BASE_URL = "http://localhost:5000"

# --- /add ---
def test_add_integers():
    r = requests.post(f"{BASE_URL}/add", json={"a": 2, "b": 3})
    assert r.status_code == 200
    assert r.json()["result"] == 5

def test_add_floats():
    r = requests.post(f"{BASE_URL}/add", json={"a": 1.5, "b": 2.5})
    assert r.json()["result"] == 4.0

def test_add_negative():
    r = requests.post(f"{BASE_URL}/add", json={"a": -3, "b": -7})
    assert r.json()["result"] == -10

def test_add_missing_field():
    r = requests.post(f"{BASE_URL}/add", json={"a": 1})
    assert r.status_code == 400

# --- /subtract ---
def test_subtract():
    r = requests.post(f"{BASE_URL}/subtract", json={"a": 10, "b": 4})
    assert r.json()["result"] == 6

def test_subtract_negative_result():
    r = requests.post(f"{BASE_URL}/subtract", json={"a": 3, "b": 7})
    assert r.json()["result"] == -4

# --- /multiply ---
def test_multiply():
    r = requests.post(f"{BASE_URL}/multiply", json={"a": 3, "b": 4})
    assert r.json()["result"] == 12

def test_multiply_by_zero():
    r = requests.post(f"{BASE_URL}/multiply", json={"a": 99, "b": 0})
    assert r.json()["result"] == 0

def test_multiply_floats():
    r = requests.post(f"{BASE_URL}/multiply", json={"a": 2.5, "b": 4.0})
    assert r.json()["result"] == 10.0

# --- /divide ---
def test_divide():
    r = requests.post(f"{BASE_URL}/divide", json={"a": 10, "b": 2})
    assert r.json()["result"] == 5.0

def test_divide_by_zero():
    r = requests.post(f"{BASE_URL}/divide", json={"a": 5, "b": 0})
    assert r.status_code == 400
    assert "error" in r.json()

def test_divide_float_result():
    r = requests.post(f"{BASE_URL}/divide", json={"a": 7, "b": 2})
    assert r.json()["result"] == 3.5

def test_divide_invalid_type():
    r = requests.post(f"{BASE_URL}/divide", json={"a": "abc", "b": 2})
    assert r.status_code == 400

# --- /health ---
def test_health():
    r = requests.get(f"{BASE_URL}/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
