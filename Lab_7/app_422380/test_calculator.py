import subprocess
import time

import pytest
import requests

BASE_URL = "http://localhost:5000"


@pytest.fixture(scope="session", autouse=True)
def start_server():
    proc = subprocess.Popen(["python3", "calculator.py"])
    time.sleep(2)
    yield
    proc.terminate()
    proc.wait()


# --- /add ---


def test_add_positive():
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


def test_add_missing_field():
    r = requests.post(f"{BASE_URL}/add", json={"a": 5})
    assert r.status_code == 400
    assert "error" in r.json()


def test_add_invalid_type():
    r = requests.post(f"{BASE_URL}/add", json={"a": "x", "b": 2})
    assert r.status_code == 400


# --- /subtract ---


def test_subtract_basic():
    r = requests.post(f"{BASE_URL}/subtract", json={"a": 10, "b": 3})
    assert r.status_code == 200
    assert r.json()["result"] == 7


def test_subtract_negative_result():
    r = requests.post(f"{BASE_URL}/subtract", json={"a": 3, "b": 10})
    assert r.status_code == 200
    assert r.json()["result"] == -7


def test_subtract_floats():
    r = requests.post(f"{BASE_URL}/subtract", json={"a": 5.5, "b": 2.2})
    assert r.status_code == 200
    assert r.json()["result"] == pytest.approx(3.3)


def test_subtract_missing_field():
    r = requests.post(f"{BASE_URL}/subtract", json={"b": 3})
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


def test_multiply_negatives():
    r = requests.post(f"{BASE_URL}/multiply", json={"a": -3, "b": -4})
    assert r.status_code == 200
    assert r.json()["result"] == 12


def test_multiply_missing_field():
    r = requests.post(f"{BASE_URL}/multiply", json={"a": 5})
    assert r.status_code == 400


# --- /divide ---


def test_divide_basic():
    r = requests.post(f"{BASE_URL}/divide", json={"a": 10, "b": 2})
    assert r.status_code == 200
    assert r.json()["result"] == pytest.approx(5.0)


def test_divide_by_zero():
    r = requests.post(f"{BASE_URL}/divide", json={"a": 10, "b": 0})
    assert r.status_code == 400
    assert r.json()["error"] == "Division by zero"


def test_divide_floats():
    r = requests.post(f"{BASE_URL}/divide", json={"a": 7.0, "b": 2.0})
    assert r.status_code == 200
    assert r.json()["result"] == pytest.approx(3.5)


def test_divide_negative():
    r = requests.post(f"{BASE_URL}/divide", json={"a": -10, "b": 2})
    assert r.status_code == 200
    assert r.json()["result"] == pytest.approx(-5.0)


def test_divide_missing_field():
    r = requests.post(f"{BASE_URL}/divide", json={"a": 10})
    assert r.status_code == 400


# --- /health ---


def test_health():
    r = requests.get(f"{BASE_URL}/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
