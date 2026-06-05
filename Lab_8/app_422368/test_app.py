import pytest
import requests

BASE_URL = "http://localhost:5000"


# --- 1. TESTY PODSTAWOWYCH ENDPOINTÓW (Happy Path) ---

def test_uppercase_success():
    payload = {"text": "hello"}
    response = requests.post(f"{BASE_URL}/uppercase", json=payload)
    assert response.status_code == 200
    assert response.json() == {"result": "HELLO"}


def test_reverse_success():
    payload = {"text": "abcde"}
    response = requests.post(f"{BASE_URL}/reverse", json=payload)
    assert response.status_code == 200
    assert response.json() == {"result": "edcba"}


def test_word_count_success():
    payload = {"text": "raz dwa"}
    response = requests.post(f"{BASE_URL}/word-count", json=payload)
    assert response.status_code == 200
    assert response.json() == {"count": 2}


def test_health_check():
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# --- 2. PRZYPADKI BRZEGOWE (Pusty tekst, spacje, cyfry) ---

def test_empty_text():
    payload = {"text": ""}
    # Test dla /uppercase
    response_up = requests.post(f"{BASE_URL}/uppercase", json=payload)
    assert response_up.status_code == 200
    assert response_up.json() == {"result": ""}

    # Test dla /word-count (powinien zwrócić 0)
    response_count = requests.post(f"{BASE_URL}/word-count", json=payload)
    assert response_count.status_code == 200
    assert response_count.json() == {"count": 0}


def test_multiple_spaces():
    payload = {"text": "   raz   dwa   trzy   "}
    # Word-count powinien zignorować wielokrotne spacje i policzyć słowa poprawnie
    response = requests.post(f"{BASE_URL}/word-count", json=payload)
    assert response.status_code == 200
    assert response.json() == {"count": 3}


def test_text_with_digits():
    payload = {"text": "wersja 2026"}
    response = requests.post(f"{BASE_URL}/uppercase", json=payload)
    assert response.status_code == 200
    assert response.json() == {"result": "WERSJA 2026"}


# --- 3. PRZYPADKI BŁĘDÓW (Walidacja wejścia) ---

def test_missing_field_text():
    payload = {"message": "hello"}  # Brak klucza 'text'
    response = requests.post(f"{BASE_URL}/reverse", json=payload)
    assert response.status_code == 400
    assert "error" in response.json()
    assert response.json()["error"] == "Missing field: text"


def test_invalid_data_type():
    payload = {"text": 12345}  # Liczba zamiast stringa
    response = requests.post(f"{BASE_URL}/uppercase", json=payload)
    assert response.status_code == 400
    assert "error" in response.json()
    assert response.json()["error"] == "Field text must be a string"