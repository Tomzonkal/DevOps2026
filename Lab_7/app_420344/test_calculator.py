import pytest
import requests


BASE_URL = "http://127.0.0.1:5000"


def post(endpoint, payload):
    return requests.post(f"{BASE_URL}{endpoint}", json=payload, timeout=5)


def test_health_endpoint():
    response = requests.get(f"{BASE_URL}/health", timeout=5)

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.parametrize(
    "a,b,expected",
    [
        (10, 5, 15),
        (-2, 3, 1),
        (1.5, 2.5, 4.0),
    ],
)
def test_add_endpoint(a, b, expected):
    response = post("/add", {"a": a, "b": b})

    assert response.status_code == 200
    assert response.json()["result"] == pytest.approx(expected)


@pytest.mark.parametrize(
    "a,b,expected",
    [
        (10, 3, 7),
        (-2, -3, 1),
        (5.5, 2.0, 3.5),
    ],
)
def test_subtract_endpoint(a, b, expected):
    response = post("/subtract", {"a": a, "b": b})

    assert response.status_code == 200
    assert response.json()["result"] == pytest.approx(expected)


@pytest.mark.parametrize(
    "a,b,expected",
    [
        (4, 5, 20),
        (-2, 3, -6),
        (2.5, 4, 10.0),
    ],
)
def test_multiply_endpoint(a, b, expected):
    response = post("/multiply", {"a": a, "b": b})

    assert response.status_code == 200
    assert response.json()["result"] == pytest.approx(expected)


@pytest.mark.parametrize(
    "a,b,expected",
    [
        (10, 2, 5),
        (-10, 2, -5),
        (7.5, 2.5, 3.0),
    ],
)
def test_divide_endpoint(a, b, expected):
    response = post("/divide", {"a": a, "b": b})

    assert response.status_code == 200
    assert response.json()["result"] == pytest.approx(expected)


def test_divide_by_zero_returns_error():
    response = post("/divide", {"a": 10, "b": 0})

    assert response.status_code == 400
    assert "error" in response.json()


@pytest.mark.parametrize(
    "endpoint,payload",
    [
        ("/add", {"a": 10}),
        ("/subtract", {"b": 5}),
        ("/multiply", {}),
        ("/divide", {"a": 10}),
    ],
)
def test_missing_json_fields_return_error(endpoint, payload):
    response = post(endpoint, payload)

    assert response.status_code >= 400