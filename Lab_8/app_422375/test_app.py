import pytest
import requests

BASE_URL = "http://localhost:5000"


# --- Testy endpointu /health ---
def test_health():
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# --- Testy endpointu /uppercase ---
def test_uppercase_normal():
    response = requests.post(f"{BASE_URL}/uppercase", json={"text": "hello world"})
    assert response.status_code == 200
    assert response.json() == {"result": "HELLO WORLD"}


def test_uppercase_with_numbers():
    response = requests.post(f"{BASE_URL}/uppercase", json={"text": "test 123!"})
    assert response.status_code == 200
    assert response.json() == {"result": "TEST 123!"}


# --- Testy endpointu /reverse ---
def test_reverse_normal():
    response = requests.post(f"{BASE_URL}/reverse", json={"text": "abcde"})
    assert response.status_code == 200
    assert response.json() == {"result": "edcba"}


def test_reverse_empty():
    response = requests.post(f"{BASE_URL}/reverse", json={"text": ""})
    assert response.status_code == 200
    assert response.json() == {"result": ""}


# --- Testy endpointu /word-count ---
def test_word_count_normal():
    response = requests.post(f"{BASE_URL}/word-count", json={"text": "raz dwa trzy"})
    assert response.status_code == 200
    assert response.json() == {"count": 3}


def test_word_count_multiple_spaces():
    response = requests.post(f"{BASE_URL}/word-count", json={"text": "  raz   dwa  "})
    assert response.status_code == 200
    assert response.json() == {"count": 2}


def test_word_count_empty_or_spaces():
    response = requests.post(f"{BASE_URL}/word-count", json={"text": "   "})
    assert response.status_code == 200
    assert response.json() == {"count": 0}


# --- Testy błędów i przypadków brzegowych ---
def test_missing_text_field():
    response = requests.post(f"{BASE_URL}/uppercase", json={"wrong_key": "hello"})
    assert response.status_code == 400
    assert response.json() == {"error": "Missing field: text"}


def test_invalid_data_type():
    response = requests.post(f"{BASE_URL}/reverse", json={"text": 12345})
    assert response.status_code == 400
    assert response.json() == {"error": "Field text must be a string"}


def test_empty_json_body():
    response = requests.post(f"{BASE_URL}/word-count", json={})
    assert response.status_code == 400
    assert response.json() == {"error": "Missing field: text"}
