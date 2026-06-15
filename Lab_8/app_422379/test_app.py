import pytest
import requests


BASE_URL = "http://localhost:5000"
POST_ENDPOINTS = ("/uppercase", "/reverse", "/word-count")


def test_health():
    response = requests.get(f"{BASE_URL}/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_uppercase():
    response = requests.post(
        f"{BASE_URL}/uppercase",
        json={"text": "hello world"},
    )

    assert response.status_code == 200
    assert response.json() == {"result": "HELLO WORLD"}


def test_uppercase_empty_text():
    response = requests.post(
        f"{BASE_URL}/uppercase",
        json={"text": ""},
    )

    assert response.status_code == 200
    assert response.json() == {"result": ""}


def test_uppercase_with_numbers():
    response = requests.post(
        f"{BASE_URL}/uppercase",
        json={"text": "abc123"},
    )

    assert response.status_code == 200
    assert response.json() == {"result": "ABC123"}


def test_uppercase_multiple_spaces():
    response = requests.post(
        f"{BASE_URL}/uppercase",
        json={"text": "hello   world"},
    )

    assert response.status_code == 200
    assert response.json() == {"result": "HELLO   WORLD"}


def test_reverse():
    response = requests.post(
        f"{BASE_URL}/reverse",
        json={"text": "abcde"},
    )

    assert response.status_code == 200
    assert response.json() == {"result": "edcba"}


def test_reverse_empty_text():
    response = requests.post(
        f"{BASE_URL}/reverse",
        json={"text": ""},
    )

    assert response.status_code == 200
    assert response.json() == {"result": ""}


def test_reverse_with_numbers():
    response = requests.post(
        f"{BASE_URL}/reverse",
        json={"text": "abc123"},
    )

    assert response.status_code == 200
    assert response.json() == {"result": "321cba"}


def test_reverse_multiple_spaces():
    response = requests.post(
        f"{BASE_URL}/reverse",
        json={"text": "raz   dwa"},
    )

    assert response.status_code == 200
    assert response.json() == {"result": "awd   zar"}


def test_word_count():
    response = requests.post(
        f"{BASE_URL}/word-count",
        json={"text": "raz dwa trzy"},
    )

    assert response.status_code == 200
    assert response.json() == {"count": 3}


def test_word_count_empty_text():
    response = requests.post(
        f"{BASE_URL}/word-count",
        json={"text": ""},
    )

    assert response.status_code == 200
    assert response.json() == {"count": 0}


def test_word_count_multiple_spaces():
    response = requests.post(
        f"{BASE_URL}/word-count",
        json={"text": "raz   dwa     trzy"},
    )

    assert response.status_code == 200
    assert response.json() == {"count": 3}


def test_word_count_with_numbers():
    response = requests.post(
        f"{BASE_URL}/word-count",
        json={"text": "abc123 def456"},
    )

    assert response.status_code == 200
    assert response.json() == {"count": 2}


@pytest.mark.parametrize("endpoint", POST_ENDPOINTS)
def test_missing_text_field(endpoint):
    response = requests.post(
        f"{BASE_URL}{endpoint}",
        json={},
    )

    assert response.status_code == 400
    assert response.json() == {"error": "Missing field: text"}


@pytest.mark.parametrize("endpoint", POST_ENDPOINTS)
def test_invalid_text_type(endpoint):
    response = requests.post(
        f"{BASE_URL}{endpoint}",
        json={"text": 123},
    )

    assert response.status_code == 400
    assert response.json() == {"error": "Field text must be a string"}
