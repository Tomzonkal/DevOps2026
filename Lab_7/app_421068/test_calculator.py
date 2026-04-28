import pytest
from calculator import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_add_integers(client):
    r = client.post("/add", json={"a": 2, "b": 3})
    assert r.status_code == 200
    assert r.get_json()["result"] == 5


def test_add_floats(client):
    r = client.post("/add", json={"a": 1.5, "b": 2.5})
    assert r.get_json()["result"] == 4.0


def test_add_negative(client):
    r = client.post("/add", json={"a": -3, "b": -7})
    assert r.get_json()["result"] == -10


def test_add_missing_field(client):
    r = client.post("/add", json={"a": 1})
    assert r.status_code == 400


def test_subtract(client):
    r = client.post("/subtract", json={"a": 10, "b": 4})
    assert r.get_json()["result"] == 6


def test_subtract_negative_result(client):
    r = client.post("/subtract", json={"a": 3, "b": 7})
    assert r.get_json()["result"] == -4


def test_multiply(client):
    r = client.post("/multiply", json={"a": 3, "b": 4})
    assert r.get_json()["result"] == 12


def test_multiply_by_zero(client):
    r = client.post("/multiply", json={"a": 99, "b": 0})
    assert r.get_json()["result"] == 0


def test_multiply_floats(client):
    r = client.post("/multiply", json={"a": 2.5, "b": 4.0})
    assert r.get_json()["result"] == 10.0


def test_divide(client):
    r = client.post("/divide", json={"a": 10, "b": 2})
    assert r.get_json()["result"] == 5.0


def test_divide_by_zero(client):
    r = client.post("/divide", json={"a": 5, "b": 0})
    assert r.status_code == 400
    assert "error" in r.get_json()


def test_divide_float_result(client):
    r = client.post("/divide", json={"a": 7, "b": 2})
    assert r.get_json()["result"] == 3.5


def test_divide_invalid_type(client):
    r = client.post("/divide", json={"a": "abc", "b": 2})
    assert r.status_code == 400


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.get_json()["status"] == "ok"
