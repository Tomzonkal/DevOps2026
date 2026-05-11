import time

import pytest
import requests

BASE_URL = "http://127.0.0.1:5000"


@pytest.fixture(scope="session", autouse=True)
def wait_for_server():
    deadline = time.time() + 10
    last_error = None

    while time.time() < deadline:
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=1)
            if response.status_code == 200:
                return
        except requests.RequestException as exc:
            last_error = exc
        time.sleep(0.2)

    pytest.fail(f"Server is not available at {BASE_URL}: {last_error}")


def post_json(endpoint, payload):
    return requests.post(f"{BASE_URL}{endpoint}", json=payload, timeout=5)


def test_add_returns_sum():
    response = post_json("/add", {"a": 10, "b": 5})

    assert response.status_code == 200
    assert response.json() == {"result": 15}


def test_subtract_returns_difference():
    response = post_json("/subtract", {"a": 10, "b": 3})

    assert response.status_code == 200
    assert response.json() == {"result": 7}


def test_multiply_returns_product():
    response = post_json("/multiply", {"a": 4, "b": 5})

    assert response.status_code == 200
    assert response.json() == {"result": 20}


def test_divide_returns_quotient():
    response = post_json("/divide", {"a": 10, "b": 2})

    assert response.status_code == 200
    assert response.json() == {"result": 5}


def test_divide_by_zero_returns_bad_request():
    response = post_json("/divide", {"a": 10, "b": 0})

    assert response.status_code == 400
    assert response.json() == {"error": "Division by zero"}


def test_operations_accept_negative_numbers():
    cases = [
        ("/add", {"a": -10, "b": 5}, -5),
        ("/subtract", {"a": -10, "b": -3}, -7),
        ("/multiply", {"a": -4, "b": 5}, -20),
        ("/divide", {"a": -10, "b": 2}, -5),
    ]

    for endpoint, payload, expected_result in cases:
        response = post_json(endpoint, payload)

        assert response.status_code == 200
        assert response.json() == {"result": expected_result}


def test_operations_accept_float_numbers():
    cases = [
        ("/add", {"a": 1.5, "b": 2.25}, 3.75),
        ("/subtract", {"a": 5.5, "b": 2.25}, 3.25),
        ("/multiply", {"a": 1.5, "b": 2.0}, 3.0),
        ("/divide", {"a": 7.5, "b": 2.5}, 3.0),
    ]

    for endpoint, payload, expected_result in cases:
        response = post_json(endpoint, payload)

        assert response.status_code == 200
        assert response.json()["result"] == pytest.approx(expected_result)


@pytest.mark.parametrize("endpoint", ["/add", "/subtract", "/multiply", "/divide"])
@pytest.mark.parametrize("payload", [{"a": 10}, {"b": 5}, {}])
def test_missing_json_fields_return_bad_request(endpoint, payload):
    response = post_json(endpoint, payload)

    assert response.status_code == 400
    assert response.json() == {"error": "Missing fields: a, b"}
