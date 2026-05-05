import threading
import time

import pytest
import requests

BASE_URL = "http://localhost:5000"


def start_server():
    import calculator

    calculator.app.run(host="0.0.0.0", port=5000)


@pytest.fixture(scope="session", autouse=True)
def server():
    t = threading.Thread(target=start_server, daemon=True)
    t.start()
    time.sleep(1)


def test_health():
    r = requests.get(f"{BASE_URL}/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_add():
    r = requests.post(f"{BASE_URL}/add", json={"a": 10, "b": 5})
    assert r.status_code == 200
    assert r.json()["result"] == 15


def test_subtract():
    r = requests.post(f"{BASE_URL}/subtract", json={"a": 10, "b": 3})
    assert r.status_code == 200
    assert r.json()["result"] == 7


def test_multiply():
    r = requests.post(f"{BASE_URL}/multiply", json={"a": 4, "b": 5})
    assert r.status_code == 200
    assert r.json()["result"] == 20


def test_divide():
    r = requests.post(f"{BASE_URL}/divide", json={"a": 10, "b": 2})
    assert r.status_code == 200
    assert r.json()["result"] == 5.0


def test_divide_by_zero():
    r = requests.post(f"{BASE_URL}/divide", json={"a": 10, "b": 0})
    assert r.status_code == 400


def test_negative_numbers():
    r = requests.post(f"{BASE_URL}/add", json={"a": -5, "b": -3})
    assert r.status_code == 200
    assert r.json()["result"] == -8


def test_floats():
    r = requests.post(f"{BASE_URL}/multiply", json={"a": 2.5, "b": 4})
    assert r.status_code == 200
    assert r.json()["result"] == 10.0


def test_missing_fields():
    r = requests.post(f"{BASE_URL}/add", json={"a": 5})
    assert r.status_code == 400
