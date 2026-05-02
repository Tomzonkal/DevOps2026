import requests

BASE_URL = "http://localhost:5010"

def post(endpoint, data):
    return requests.post(
        f"{BASE_URL}/{endpoint}",
        json=data,
        headers={"Content-Type": "application/json"}
    )

def test_add():
    response = post("add", {"a": 10, "b": 5})
    assert response.status_code == 200
    assert response.json()["result"] == 15

def test_subtract():
    response = post("subtract", {"a": 10, "b": 5})
    assert response.status_code == 200
    assert response.json()["result"] == 5

def test_multiply():
    response = post("multiply", {"a": 10, "b": 5})
    assert response.status_code == 200
    assert response.json()["result"] == 50

def test_divide():
    response = post("divide", {"a": 10, "b": 5})
    assert response.status_code == 200
    assert response.json()["result"] == 2

def test_divide_by_zero():
    response = post("divide", {"a": 10, "b": 0})
    assert response.status_code != 200

def test_negative_numbers():
    response = post("add", {"a": -10, "b": -5})
    assert response.status_code == 200
    assert response.json()["result"] == -15

def test_float_numbers():
    response = post("add", {"a": 2.5, "b": 3.5})
    assert response.status_code == 200
    assert response.json()["result"] == 6.0

def test_missing_fields():
    response = post("add", {"a": 10})
    assert response.status_code != 200
