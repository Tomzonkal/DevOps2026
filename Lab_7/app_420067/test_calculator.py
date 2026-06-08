import requests
import pytest

BASE_URL = "http://localhost:5000"


def test_health():
    response = requests.get(f"{BASE_URL}/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_add_positive_numbers():
    response = requests.post(
        f"{BASE_URL}/add",
        json={"a": 10, "b": 5}
    )

    assert response.status_code == 200
    assert response.json()["result"] == 15


def test_add_negative_numbers():
    response = requests.post(
        f"{BASE_URL}/add",
        json={"a": -10, "b": -5}
    )

    assert response.status_code == 200
    assert response.json()["result"] == -15


def test_add_float_numbers():
    response = requests.post(
        f"{BASE_URL}/add",
        json={"a": 2.5, "b": 1.5}
    )

    assert response.status_code == 200
    assert response.json()["result"] == pytest.approx(4.0)


def test_subtract_numbers():
    response = requests.post(
        f"{BASE_URL}/subtract",
        json={"a": 10, "b": 3}
    )

    assert response.status_code == 200
    assert response.json()["result"] == 7


def test_subtract_negative_result():
    response = requests.post(
        f"{BASE_URL}/subtract",
        json={"a": 3, "b": 10}
    )

    assert response.status_code == 200
    assert response.json()["result"] == -7


def test_multiply_numbers():
    response = requests.post(
        f"{BASE_URL}/multiply",
        json={"a": 4, "b": 5}
    )

    assert response.status_code == 200
    assert response.json()["result"] == 20


def test_multiply_by_negative_number():
    response = requests.post(
        f"{BASE_URL}/multiply",
        json={"a": -4, "b": 5}
    )

    assert response.status_code == 200
    assert response.json()["result"] == -20


def test_divide_numbers():
    response = requests.post(
        f"{BASE_URL}/divide",
        json={"a": 10, "b": 2}
    )

    assert response.status_code == 200
    assert response.json()["result"] == 5


def test_divide_float_result():
    response = requests.post(
        f"{BASE_URL}/divide",
        json={"a": 5, "b": 2}
    )

    assert response.status_code == 200
    assert response.json()["result"] == pytest.approx(2.5)


def test_divide_by_zero():
    response = requests.post(
        f"{BASE_URL}/divide",
        json={"a": 10, "b": 0}
    )

    assert response.status_code == 400
    assert "error" in response.json()


def test_missing_field_a():
    response = requests.post(
        f"{BASE_URL}/add",
        json={"b": 5}
    )

    assert response.status_code >= 400


def test_missing_field_b():
    response = requests.post(
        f"{BASE_URL}/add",
        json={"a": 10}
    )

    assert response.status_code >= 400


def test_empty_json():
    response = requests.post(
        f"{BASE_URL}/add",
        json={}
    )

    assert response.status_code >= 400