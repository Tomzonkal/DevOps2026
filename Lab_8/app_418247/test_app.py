import pytest
import requests

BASE_URL = "http://localhost:5000"

# --- Testy dla endpointu /health ---

def test_health():
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# --- Testy dla endpointu /uppercase ---

def test_uppercase_normal():
    response = requests.post(f"{BASE_URL}/uppercase", json={"text": "hello world"})
    assert response.status_code == 200
    assert response.json() == {"result": "HELLO WORLD"}

def test_uppercase_empty_string():
    # Przypadek brzegowy: pusty tekst
    response = requests.post(f"{BASE_URL}/uppercase", json={"text": ""})
    assert response.status_code == 200
    assert response.json() == {"result": ""}

def test_uppercase_with_numbers():
    # Przypadek brzegowy: tekst zawierający cyfry i znaki specjalne
    response = requests.post(f"{BASE_URL}/uppercase", json={"text": "devops 2026!"})
    assert response.status_code == 200
    assert response.json() == {"result": "DEVOPS 2026!"}


# --- Testy dla endpointu /reverse ---

def test_reverse_normal():
    response = requests.post(f"{BASE_URL}/reverse", json={"text": "abcde"})
    assert response.status_code == 200
    assert response.json() == {"result": "edcba"}

def test_reverse_empty_string():
    # Przypadek brzegowy: pusty tekst
    response = requests.post(f"{BASE_URL}/reverse", json={"text": ""})
    assert response.status_code == 200
    assert response.json() == {"result": ""}

def test_reverse_multiple_spaces():
    # Przypadek brzegowy: tekst z wieloma spacjami
    response = requests.post(f"{BASE_URL}/reverse", json={"text": "a  b  c"})
    assert response.status_code == 200
    assert response.json() == {"result": "c  b  a"}


# --- Testy dla endpointu /word-count ---

def test_word_count_normal():
    response = requests.post(f"{BASE_URL}/word-count", json={"text": "raz dwa trzy"})
    assert response.status_code == 200
    assert response.json() == {"count": 3}

def test_word_count_empty_string():
    # Przypadek brzegowy: pusty tekst
    response = requests.post(f"{BASE_URL}/word-count", json={"text": ""})
    assert response.status_code == 200
    assert response.json() == {"count": 0}

def test_word_count_multiple_spaces():
    # Przypadek brzegowy: tekst z wieloma spacjami między słowami i na końcach
    response = requests.post(f"{BASE_URL}/word-count", json={"text": "  raz    dwa  "})
    assert response.status_code == 200
    assert response.json() == {"count": 2}


# --- Testy obsługi błędów (Errors) ---

def test_error_missing_text_field():
    # Błąd: brak wymaganego pola 'text'
    response = requests.post(f"{BASE_URL}/uppercase", json={"wrong_key": "hello"})
    assert response.status_code == 400
    assert response.json() == {"error": "Missing field: text"}

def test_error_empty_json():
    # Błąd: całkowicie pusty JSON
    response = requests.post(f"{BASE_URL}/reverse", json={})
    assert response.status_code == 400
    assert response.json() == {"error": "Missing field: text"}

def test_error_invalid_data_type():
    # Błąd: wartość pod kluczem 'text' nie jest stringiem (np. liczba)
    response = requests.post(f"{BASE_URL}/word-count", json={"text": 12345})
    assert response.status_code == 400
    assert response.json() == {"error": "Field text must be a string"}

def test_error_null_value():
    # Błąd: wartość null zamiast stringa
    response = requests.post(f"{BASE_URL}/uppercase", json={"text": None})
    assert response.status_code == 400
    assert response.json() == {"error": "Field text must be a string"}