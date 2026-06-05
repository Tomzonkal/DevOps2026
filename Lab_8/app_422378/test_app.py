import pytest
import requests

BASE_URL = "http://localhost:5000"

def test_health():
    """Test czy serwer w ogóle odpowiada"""
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_uppercase_basic():
    """Test zamiany na wielkie litery - podstawowy przypadek"""
    response = requests.post(f"{BASE_URL}/uppercase", json={"text": "hello world"})
    assert response.status_code == 200
    assert response.json() == {"result": "HELLO WORLD"}

def test_uppercase_edge_cases():
    """Test przypadków brzegowych dla uppercase: pusty ciąg, liczby i znaki specjalne"""
    # Pusty tekst
    res_empty = requests.post(f"{BASE_URL}/uppercase", json={"text": ""})
    assert res_empty.json() == {"result": ""}
    # Cyfry (nie powinny się zmienić)
    res_nums = requests.post(f"{BASE_URL}/uppercase", json={"text": "123 testing"})
    assert res_nums.json() == {"result": "123 TESTING"}

def test_reverse_basic():
    """Test odwracania tekstu - podstawowy przypadek"""
    response = requests.post(f"{BASE_URL}/reverse", json={"text": "abcde"})
    assert response.status_code == 200
    assert response.json() == {"result": "edcba"}

def test_reverse_edge_cases():
    """Test przypadków brzegowych dla reverse: palindrom, wiele spacji"""
    # Tekst z wieloma spacjami
    res_spaces = requests.post(f"{BASE_URL}/reverse", json={"text": "a  b"})
    assert res_spaces.json() == {"result": "b  a"}

def test_word_count_basic():
    """Test liczenia słów - podstawowy przypadek"""
    response = requests.post(f"{BASE_URL}/word-count", json={"text": "raz dwa trzy"})
    assert response.status_code == 200
    assert response.json() == {"count": 3}

def test_word_count_edge_cases():
    """Test przypadków brzegowych dla liczenia słów: pusty ciąg, dziwne spacje"""
    # Pusty tekst (powinien zwrócić 0 słów)
    res_empty = requests.post(f"{BASE_URL}/word-count", json={"text": ""})
    assert res_empty.json() == {"count": 0}
    # Wiele spacji między słowami
    res_spaces = requests.post(f"{BASE_URL}/word-count", json={"text": "raz    dwa"})
    assert res_spaces.json() == {"count": 2}

def test_error_missing_field():
    """Test błędu walidacji: całkowity brak wymaganego pola 'text' w JSON"""
    response = requests.post(f"{BASE_URL}/uppercase", json={"zly_klucz": "hello"})
    assert response.status_code == 400
    assert "Missing field: text" in response.json().get("error", "")

def test_error_invalid_type():
    """Test błędu walidacji: przesyłanie liczby całkowitej zamiast stringa"""
    response = requests.post(f"{BASE_URL}/reverse", json={"text": 12345})
    assert response.status_code == 400
    assert "Field text must be a string" in response.json().get("error", "")