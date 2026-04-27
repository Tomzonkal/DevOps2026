"""
Testy jednostkowe kalkulatora REST API (student 000001)
Używa pytest + requests z wbudowanym klientem testowym Flask.
"""

import pytest
from app import app as flask_app


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client


# ---------------------------------------------------------------------------
# /health
# ---------------------------------------------------------------------------

def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "ok"


# ---------------------------------------------------------------------------
# /add
# ---------------------------------------------------------------------------

def test_add_integers(client):
    resp = client.post("/add", json={"a": 3, "b": 5})
    assert resp.status_code == 200
    assert resp.get_json()["result"] == 8


def test_add_floats(client):
    resp = client.post("/add", json={"a": 1.5, "b": 2.5})
    assert resp.status_code == 200
    assert resp.get_json()["result"] == pytest.approx(4.0)


def test_add_negative(client):
    resp = client.post("/add", json={"a": -10, "b": 3})
    assert resp.status_code == 200
    assert resp.get_json()["result"] == -7


def test_add_missing_field(client):
    resp = client.post("/add", json={"a": 5})
    assert resp.status_code == 400


def test_add_no_json(client):
    resp = client.post("/add")
    assert resp.status_code == 400


# ---------------------------------------------------------------------------
# /subtract
# ---------------------------------------------------------------------------

def test_subtract_integers(client):
    resp = client.post("/subtract", json={"a": 10, "b": 4})
    assert resp.status_code == 200
    assert resp.get_json()["result"] == 6


def test_subtract_floats(client):
    resp = client.post("/subtract", json={"a": 5.5, "b": 2.2})
    assert resp.status_code == 200
    assert resp.get_json()["result"] == pytest.approx(3.3)


def test_subtract_negative(client):
    resp = client.post("/subtract", json={"a": -3, "b": -7})
    assert resp.status_code == 200
    assert resp.get_json()["result"] == 4


def test_subtract_missing_field(client):
    resp = client.post("/subtract", json={"b": 2})
    assert resp.status_code == 400


def test_subtract_no_json(client):
    resp = client.post("/subtract")
    assert resp.status_code == 400


# ---------------------------------------------------------------------------
# /multiply
# ---------------------------------------------------------------------------

def test_multiply_integers(client):
    resp = client.post("/multiply", json={"a": 6, "b": 7})
    assert resp.status_code == 200
    assert resp.get_json()["result"] == 42


def test_multiply_floats(client):
    resp = client.post("/multiply", json={"a": 2.5, "b": 4.0})
    assert resp.status_code == 200
    assert resp.get_json()["result"] == pytest.approx(10.0)


def test_multiply_negative(client):
    resp = client.post("/multiply", json={"a": -3, "b": 5})
    assert resp.status_code == 200
    assert resp.get_json()["result"] == -15


def test_multiply_missing_field(client):
    resp = client.post("/multiply", json={"a": 3})
    assert resp.status_code == 400


def test_multiply_no_json(client):
    resp = client.post("/multiply")
    assert resp.status_code == 400


# ---------------------------------------------------------------------------
# /divide
# ---------------------------------------------------------------------------

def test_divide_integers(client):
    resp = client.post("/divide", json={"a": 10, "b": 2})
    assert resp.status_code == 200
    assert resp.get_json()["result"] == 5.0


def test_divide_floats(client):
    resp = client.post("/divide", json={"a": 7.5, "b": 2.5})
    assert resp.status_code == 200
    assert resp.get_json()["result"] == pytest.approx(3.0)


def test_divide_negative(client):
    resp = client.post("/divide", json={"a": -9, "b": 3})
    assert resp.status_code == 200
    assert resp.get_json()["result"] == pytest.approx(-3.0)


def test_divide_by_zero(client):
    resp = client.post("/divide", json={"a": 5, "b": 0})
    assert resp.status_code == 400
    data = resp.get_json()
    assert "error" in data


def test_divide_float_by_zero(client):
    resp = client.post("/divide", json={"a": 3.14, "b": 0})
    assert resp.status_code == 400


def test_divide_missing_field(client):
    resp = client.post("/divide", json={"a": 8})
    assert resp.status_code == 400


def test_divide_no_json(client):
    resp = client.post("/divide")
    assert resp.status_code == 400
