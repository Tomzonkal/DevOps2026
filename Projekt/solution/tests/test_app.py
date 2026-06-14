import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../app"))
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


# --- Health & index ---

def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.get_json()["status"] == "ok"


def test_index(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "Calculator API" in r.get_json()["service"]


# --- Add ---

def test_add(client):
    r = client.post("/add", json={"a": 3, "b": 4})
    assert r.status_code == 200
    assert r.get_json()["result"] == 7.0

def test_add_negative(client):
    r = client.post("/add", json={"a": -5, "b": 3})
    assert r.get_json()["result"] == -2.0

def test_add_missing_field(client):
    r = client.post("/add", json={"a": 1})
    assert r.status_code == 400


# --- Subtract ---

def test_subtract(client):
    r = client.post("/subtract", json={"a": 10, "b": 3})
    assert r.get_json()["result"] == 7.0

def test_subtract_negative_result(client):
    r = client.post("/subtract", json={"a": 2, "b": 5})
    assert r.get_json()["result"] == -3.0


# --- Multiply ---

def test_multiply(client):
    r = client.post("/multiply", json={"a": 6, "b": 7})
    assert r.get_json()["result"] == 42.0

def test_multiply_by_zero(client):
    r = client.post("/multiply", json={"a": 999, "b": 0})
    assert r.get_json()["result"] == 0.0


# --- Divide ---

def test_divide(client):
    r = client.post("/divide", json={"a": 10, "b": 4})
    assert r.get_json()["result"] == 2.5

def test_divide_by_zero(client):
    r = client.post("/divide", json={"a": 5, "b": 0})
    assert r.status_code == 400
    assert "zero" in r.get_json()["error"].lower()

def test_divide_missing_fields(client):
    r = client.post("/divide", json={})
    assert r.status_code == 400
