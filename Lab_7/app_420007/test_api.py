import requests
import pytest

BASE_URL = "http://localhost:5010"


# ---------- Helper ----------
def post(endpoint, payload):
    return requests.post(f"{BASE_URL}{endpoint}", json=payload)


# ---------- Health ----------
def test_health():
    res = requests.get(f"{BASE_URL}/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


# ---------- ADD ----------
def test_add_basic():
    res = post("/add", {"a": 2, "b": 3})
    assert res.status_code == 200
    assert res.json()["result"] == 5


def test_add_float():
    res = post("/add", {"a": 2.5, "b": 1.5})
    assert res.status_code == 200
    assert res.json()["result"] == 4.0


def test_add_negative():
    res = post("/add", {"a": -2, "b": -3})
    assert res.status_code == 200
    assert res.json()["result"] == -5


# ---------- SUBTRACT ----------
def test_subtract_basic():
    res = post("/subtract", {"a": 5, "b": 3})
    assert res.status_code == 200
    assert res.json()["result"] == 2


def test_subtract_negative():
    res = post("/subtract", {"a": -5, "b": -3})
    assert res.json()["result"] == -2


# ---------- MULTIPLY ----------
def test_multiply_basic():
    res = post("/multiply", {"a": 4, "b": 3})
    assert res.status_code == 200
    assert res.json()["result"] == 12


def test_multiply_float():
    res = post("/multiply", {"a": 2.5, "b": 2})
    assert res.json()["result"] == 5.0


# ---------- DIVIDE ----------
def test_divide_basic():
    res = post("/divide", {"a": 10, "b": 2})
    assert res.status_code == 200
    assert res.json()["result"] == 5


def test_divide_float():
    res = post("/divide", {"a": 5, "b": 2})
    assert res.json()["result"] == 2.5


def test_divide_negative():
    res = post("/divide", {"a": -10, "b": 2})
    assert res.json()["result"] == -5


def test_divide_by_zero():
    res = post("/divide", {"a": 10, "b": 0})
    assert res.status_code == 400
    assert res.json()["error"] == "Division by zero"


# ---------- ERRORS ----------
def test_missing_fields():
    res = post("/add", {"a": 1})
    assert res.status_code == 400
    assert "Missing fields" in res.json()["error"]


def test_invalid_types():
    res = post("/add", {"a": "x", "b": 2})
    assert res.status_code == 400
    assert "must be numbers" in res.json()["error"]

def test_no_json():
    res = requests.post(f"{BASE_URL}/add")
    assert res.status_code in (400, 415)
