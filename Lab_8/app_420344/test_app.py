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
    "text,expected",
    [
        ("hello world", "HELLO WORLD"),
        ("", ""),
        ("abc123", "ABC123"),
        ("Hello 123 test", "HELLO 123 TEST"),
    ],
)
def test_uppercase_endpoint(text, expected):
    response = post("/uppercase", {"text": text})

    assert response.status_code == 200
    assert response.json()["result"] == expected


@pytest.mark.parametrize(
    "text,expected",
    [
        ("abcde", "edcba"),
        ("", ""),
        ("abc123", "321cba"),
        ("raz dwa", "awd zar"),
    ],
)
def test_reverse_endpoint(text, expected):
    response = post("/reverse", {"text": text})

    assert response.status_code == 200
    assert response.json()["result"] == expected


@pytest.mark.parametrize(
    "text,expected_count",
    [
        ("raz dwa trzy", 3),
        ("", 0),
        ("   ", 0),
        ("raz   dwa     trzy", 3),
        ("abc 123 def", 3),
    ],
)
def test_word_count_endpoint(text, expected_count):
    response = post("/word-count", {"text": text})

    assert response.status_code == 200
    assert response.json()["count"] == expected_count


@pytest.mark.parametrize(
    "endpoint",
    [
        "/uppercase",
        "/reverse",
        "/word-count",
    ],
)
def test_missing_text_field_returns_error(endpoint):
    response = post(endpoint, {})

    assert response.status_code >= 400


@pytest.mark.parametrize(
    "endpoint,payload",
    [
        ("/uppercase", {"text": 123}),
        ("/reverse", {"text": 123}),
        ("/word-count", {"text": 123}),
    ],
)
def test_invalid_text_type_returns_error(endpoint, payload):
    response = post(endpoint, payload)

    assert response.status_code >= 400