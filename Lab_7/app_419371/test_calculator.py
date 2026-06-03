import requests

BASE_URL = "http://localhost:5000"


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
    assert r.json()["result"] == 5


def test_divide_by_zero():
    r = requests.post(f"{BASE_URL}/divide", json={"a": 10, "b": 0})
    assert r.status_code == 400
    assert "Division by zero" in r.json()["error"]


def test_missing_fields():
    r = requests.post(f"{BASE_URL}/add", json={"a": 10})
    assert r.status_code == 400
    assert "Missing fields" in r.json()["error"]


def test_invalid_types():
    r = requests.post(f"{BASE_URL}/add", json={"a": "x", "b": 5})
    assert r.status_code == 400
    assert "must be numbers" in r.json()["error"]


def test_health():
    r = requests.get(f"{BASE_URL}/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"