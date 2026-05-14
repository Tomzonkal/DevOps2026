import pytest
import requests

BASE_URL = "http://localhost:5000"

# --- Testy dla endpointu /health ---


def test_health_check():
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# --- Testy dla endpointu /uppercase ---


def test_uppercase_standard():
    response = requests.post(f"{BASE_URL}/uppercase", json={"text": "hello world"})
    assert response.status_code == 200
    assert response.json() == {"result": "HELLO WORLD"}


def test_uppercase_empty_string():
    response = requests.post(f"{BASE_URL}/uppercase", json={"text": ""})
    assert response.status_code == 200
    assert response.json() == {"result": ""}


def test_uppercase_with_numbers_and_symbols():
    response = requests.post(f"{BASE_URL}/uppercase", json={"text": "test 123 !@#"})
    assert response.status_code == 200
    assert response.json() == {"result": "TEST 123 !@#"}


# --- Testy dla endpointu /reverse ---


def test_reverse_standard():
    response = requests.post(f"{BASE_URL}/reverse", json={"text": "flask"})
    assert response.status_code == 200
    assert response.json() == {"result": "ksalf"}


def test_reverse_empty_string():
    response = requests.post(f"{BASE_URL}/reverse", json={"text": ""})
    assert response.status_code == 200
    assert response.json() == {"result": ""}


def test_reverse_multiple_spaces():
    response = requests.post(f"{BASE_URL}/reverse", json={"text": "a  b   c"})
    assert response.status_code == 200
    assert response.json() == {"result": "c   b  a"}


def test_reverse_with_numbers():
    response = requests.post(f"{BASE_URL}/reverse", json={"text": "12345"})
    assert response.status_code == 200
    assert response.json() == {"result": "54321"}


# --- Testy dla endpointu /word-count ---


def test_word_count_standard():
    response = requests.post(
        f"{BASE_URL}/word-count", json={"text": "to jest testowy tekst"}
    )
    assert response.status_code == 200
    assert response.json() == {"count": 4}


def test_word_count_multiple_spaces():
    response = requests.post(
        f"{BASE_URL}/word-count", json={"text": "jedno    słowo     i   kolejne"}
    )
    assert response.status_code == 200
    # Funkcja split() poprawnie ignoruje wielokrotne spacje
    assert response.json() == {"count": 4}


def test_word_count_empty_string():
    response = requests.post(f"{BASE_URL}/word-count", json={"text": ""})
    assert response.status_code == 200
    assert response.json() == {"count": 0}


def test_word_count_only_spaces():
    response = requests.post(f"{BASE_URL}/word-count", json={"text": "     "})
    assert response.status_code == 200
    assert response.json() == {"count": 0}


def test_word_count_with_numbers():
    response = requests.post(
        f"{BASE_URL}/word-count", json={"text": "rok 2023 był rokiem 1"}
    )
    assert response.status_code == 200
    assert response.json() == {"count": 5}


# --- Testy dla przypadków błędnych (wspólne dla wszystkich endpointów POST) ---


@pytest.mark.parametrize("endpoint", ["/uppercase", "/reverse", "/word-count"])
def test_missing_text_field(endpoint):
    # Brakuje klucza 'text'
    response = requests.post(f"{BASE_URL}{endpoint}", json={"wrong_key": "test"})
    assert response.status_code == 400
    assert response.json() == {"error": "Missing field: text"}


@pytest.mark.parametrize("endpoint", ["/uppercase", "/reverse", "/word-count"])
def test_empty_json_body(endpoint):
    # Puste ciało żądania JSON
    response = requests.post(f"{BASE_URL}{endpoint}", json={})
    assert response.status_code == 400
    assert response.json() == {"error": "Missing field: text"}


@pytest.mark.parametrize("endpoint", ["/uppercase", "/reverse", "/word-count"])
def test_invalid_data_type_integer(endpoint):
    # Liczba całkowita zamiast stringa
    response = requests.post(f"{BASE_URL}{endpoint}", json={"text": 123})
    assert response.status_code == 400
    assert response.json() == {"error": "Field text must be a string"}


@pytest.mark.parametrize("endpoint", ["/uppercase", "/reverse", "/word-count"])
def test_invalid_data_type_list(endpoint):
    # Lista zamiast stringa
    response = requests.post(f"{BASE_URL}{endpoint}", json={"text": ["a", "b"]})
    assert response.status_code == 400
    assert response.json() == {"error": "Field text must be a string"}


@pytest.mark.parametrize("endpoint", ["/uppercase", "/reverse", "/word-count"])
def test_invalid_data_type_none(endpoint):
    # Null (None) zamiast stringa
    response = requests.post(f"{BASE_URL}{endpoint}", json={"text": None})
    assert response.status_code == 400
    assert response.json() == {"error": "Field text must be a string"}
