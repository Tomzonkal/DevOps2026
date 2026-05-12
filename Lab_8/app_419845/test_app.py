import pytest
import requests

BASE_URL = "http://localhost:5000"


def test_health():
    """Sprawdza czy serwis żyje."""
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_uppercase_success():
    """Test zamiany na wielkie litery."""
    payload = {"text": "hello world"}
    response = requests.post(f"{BASE_URL}/uppercase", json=payload)
    assert response.status_code == 200
    assert response.json()["result"] == "HELLO WORLD"


def test_reverse_success():
    """Test odwracania tekstu."""
    payload = {"text": "python"}
    response = requests.post(f"{BASE_URL}/reverse", json=payload)
    assert response.status_code == 200
    assert response.json()["result"] == "nohtyp"


def test_word_count_success():
    """Test liczenia słów."""
    payload = {"text": "raz dwa trzy cztery"}
    response = requests.post(f"{BASE_URL}/word-count", json=payload)
    assert response.status_code == 200
    assert response.json()["count"] == 4


def test_empty_string():
    """Test dla pustego ciągu znaków."""
    payload = {"text": ""}
    # Sprawdzamy uppercase
    res_up = requests.post(f"{BASE_URL}/uppercase", json=payload)
    assert res_up.json()["result"] == ""
    # Sprawdzamy word-count (powinno być 0)
    res_count = requests.post(f"{BASE_URL}/word-count", json=payload)
    assert res_count.json()["count"] == 0


def test_multiple_spaces():
    """Test dla tekstu z wieloma spacjami."""
    payload = {"text": "  duzo    spacji  "}
    response = requests.post(f"{BASE_URL}/word-count", json=payload)
    assert response.status_code == 200
    assert response.json()["count"] == 2  # split() powinien zignorować puste spacje


def test_text_with_digits():
    """Test dla tekstu zawierającego cyfry."""
    payload = {"text": "rok 2026"}
    response = requests.post(f"{BASE_URL}/reverse", json=payload)
    assert response.status_code == 200
    assert response.json()["result"] == "6202 kor"


def test_missing_field_text():
    """Błąd: brak klucza 'text' w JSON."""
    payload = {"not_text": "hello"}
    response = requests.post(f"{BASE_URL}/uppercase", json=payload)
    assert response.status_code == 400
    assert response.json()["error"] == "Missing field: text"


def test_invalid_type_not_string():
    """Błąd: wysłanie liczby zamiast stringa."""
    payload = {"text": 12345}
    response = requests.post(f"{BASE_URL}/uppercase", json=payload)
    assert response.status_code == 400
    assert response.json()["error"] == "Field text must be a string"


def test_no_json_body():
    """Błąd: wysłanie pustego żądania."""
    response = requests.post(f"{BASE_URL}/uppercase", json={})
    assert response.status_code == 400
