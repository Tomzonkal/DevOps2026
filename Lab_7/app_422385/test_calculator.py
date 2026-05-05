import pytest
import subprocess
import time
import requests

BASE_URL = "http://localhost:5000"

@pytest.fixture(scope="session", autouse=True)
def start_server():
    proc = subprocess.Popen(["python", "calculator.py"])
    time.sleep(2)
    yield
    proc.terminate()

# --- /add ---
def test_add_basic():
    r = requests.post(f"{BASE_URL}/add", json={"a": 10, "b": 5})
    assert r.status_code == 200
    assert r.json()["result"] == 15

def test_add_negative():
    r = requests.post(f"{BASE_URL}/add", json={"a": -3, "b": -7})
    assert r.status_code == 200
    assert r.json()["result"] == -10

def test_add_floats():
    r = requests.post(f"{BASE_URL}/add", json={"a": 1.5, "b": 2.5})
    assert r.status_code == 200
    assert r.json()["result"] == pytest.approx(4.0)

def test_add_missing_fields():
    r = requests.post(f"{BASE_URL}/add", json={"a": 5})
    assert r.status_code == 400
    assert "error" in r.json()

# --- /subtract ---
def test_subtract_basic():
    r = requests.post(f"{BASE_URL}/subtract", json={"a": 10, "b": 3})
    assert r.status_code == 200
    assert r.json()["result"] == 7

def test_subtract_negative():
    r = requests.post(f"{BASE_URL}/subtract", json={"a": -5, "b": -3})
    assert r.status_code == 200
    assert r.json()["result"] == -2

def test_subtract_missing_fields():
    r = requests.post(f"{BASE_URL}/subtract", json={})
    assert r.status_code == 400

# --- /multiply ---
def test_multiply_basic():
    r = requests.post(f"{BASE_URL}/multiply", json={"a": 4, "b": 5})
    assert r.status_code == 200
    assert r.json()["result"] == 20

def test_multiply_by_zero():
    r = requests.post(f"{BASE_URL}/multiply", json={"a": 99, "b": 0})
    assert r.status_code == 200
    assert r.json()["result"] == 0

def test_multiply_floats():
    r = requests.post(f"{BASE_URL}/multiply", json={"a": 2.5, "b": 4.0})
    assert r.status_code == 200
    assert r.json()["result"] == pytest.approx(10.0)

def test_multiply_missing_fields():
    r = requests.post(f"{BASE_URL}/multiply", json={"b": 5})
    assert r.status_code == 400

# --- /divide ---
def test_divide_basic():
    r = requests.post(f"{BASE_URL}/divide", json={"a": 10, "b": 2})
    assert r.status_code == 200
    assert r.json()["result"] == 5.0

def test_divide_by_zero():
    r = requests.post(f"{BASE_URL}/divide", json={"a": 10, "b": 0})
    assert r.status_code == 400
    assert "error" in r.json()

def test_divide_floats():
    r = requests.post(f"{BASE_URL}/divide", json={"a": 7.5, "b": 2.5})
    assert r.status_code == 200
    assert r.json()["result"] == pytest.approx(3.0)

def test_divide_negative():
    r = requests.post(f"{BASE_URL}/divide", json={"a": -10, "b": 2})
    assert r.status_code == 200
    assert r.json()["result"] == -5.0

def test_divide_missing_fields():
    r = requests.post(f"{BASE_URL}/divide", json={"a": 10})
    assert r.status_code == 400

# --- /health ---
def test_health():
    r = requests.get(f"{BASE_URL}/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"