import time

import pytest
import requests


BASE_URL = "http://127.0.0.1:5000"


@pytest.fixture(scope="session", autouse=True)
def wait_for_server():
    for _ in range(30):
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=1)
            if response.status_code == 200:
                return
        except requests.exceptions.RequestException:
            time.sleep(1)

    pytest.fail("Serwer Flask nie uruchomił się na porcie 5000.")


def test_health_endpoint():
    response = requests.get(f"{BASE_URL}/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.parametrize(
    "input_text, expected",
    [
        ("hello world", "HELLO WORLD"),
        ("", ""),
        ("  ala   ma kota  ", "  ALA   MA KOTA  "),
        ("abc123", "ABC123"),
    ],
)
def test_uppercase_endpoint(input_text, expected):
    response = requests.post(
        f"{BASE_URL}/uppercase",
        json={"text": input_text},
    )

    assert response.status_code == 200
    assert response.json() == {"result": expected}


@pytest.mark.parametrize(
    "input_text, expected",
    [
        ("abcde", "edcba"),
        ("", ""),
        ("  abc  ", "  cba  "),
        ("abc123", "321cba"),
    ],
)
def test_reverse_endpoint(input_text, expected):
    response = requests.post(
        f"{BASE_URL}/reverse",
        json={"text": input_text},
    )

    assert response.status_code == 200
    assert response.json() == {"result": expected}


@pytest.mark.parametrize(
    "input_text, expected",
    [
        ("raz dwa trzy", 3),
        ("", 0),
        ("   raz   dwa   ", 2),
        ("123 456", 2),
    ],
)
def test_word_count_endpoint(input_text, expected):
    response = requests.post(
        f"{BASE_URL}/word-count",
        json={"text": input_text},
    )

    assert response.status_code == 200
    assert response.json() == {"count": expected}


@pytest.mark.parametrize(
    "endpoint",
    [
        "/uppercase",
        "/reverse",
        "/word-count",
    ],
)
def test_missing_text_field_returns_error(endpoint):
    response = requests.post(
        f"{BASE_URL}{endpoint}",
        json={},
    )

    assert response.status_code in (400, 422)


@pytest.mark.parametrize(
    "endpoint",
    [
        "/uppercase",
        "/reverse",
        "/word-count",
    ],
)
def test_invalid_text_type_returns_error(endpoint):
    response = requests.post(
        f"{BASE_URL}{endpoint}",
        json={"text": 123},
    )

    assert response.status_code in (400, 422)
