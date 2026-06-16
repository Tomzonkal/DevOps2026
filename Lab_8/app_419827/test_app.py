import os
import requests

BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")


def test_health():
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_uppercase_basic_text():
    response = requests.post(f"{BASE_URL}/uppercase", json={"text": "hello world"})
    assert response.status_code == 200
    assert response.json() == {"result": "HELLO WORLD"}


def test_uppercase_empty_text():
    response = requests.post(f"{BASE_URL}/uppercase", json={"text": ""})
    assert response.status_code == 200
    assert response.json() == {"result": ""}


def test_uppercase_text_with_numbers():
    response = requests.post(f"{BASE_URL}/uppercase", json={"text": "abc123 test"})
    assert response.status_code == 200
    assert response.json() == {"result": "ABC123 TEST"}


def test_uppercase_missing_text_field():
    response = requests.post(f"{BASE_URL}/uppercase", json={})
    assert response.status_code == 400
    assert response.json() == {"error": "Missing field: text"}


def test_uppercase_invalid_text_type():
    response = requests.post(f"{BASE_URL}/uppercase", json={"text": 123})
    assert response.status_code == 400
    assert response.json() == {"error": "Field text must be a string"}


def test_reverse_basic_text():
    response = requests.post(f"{BASE_URL}/reverse", json={"text": "abcde"})
    assert response.status_code == 200
    assert response.json() == {"result": "edcba"}


def test_reverse_empty_text():
    response = requests.post(f"{BASE_URL}/reverse", json={"text": ""})
    assert response.status_code == 200
    assert response.json() == {"result": ""}


def test_reverse_text_with_numbers():
    response = requests.post(f"{BASE_URL}/reverse", json={"text": "abc123"})
    assert response.status_code == 200
    assert response.json() == {"result": "321cba"}


def test_reverse_missing_text_field():
    response = requests.post(f"{BASE_URL}/reverse", json={})
    assert response.status_code == 400
    assert response.json() == {"error": "Missing field: text"}


def test_reverse_invalid_text_type():
    response = requests.post(f"{BASE_URL}/reverse", json={"text": ["abc"]})
    assert response.status_code == 400
    assert response.json() == {"error": "Field text must be a string"}


def test_word_count_basic_text():
    response = requests.post(f"{BASE_URL}/word-count", json={"text": "raz dwa trzy"})
    assert response.status_code == 200
    assert response.json() == {"count": 3}


def test_word_count_empty_text():
    response = requests.post(f"{BASE_URL}/word-count", json={"text": ""})
    assert response.status_code == 200
    assert response.json() == {"count": 0}


def test_word_count_many_spaces():
    response = requests.post(f"{BASE_URL}/word-count", json={"text": "   raz    dwa     trzy   "})
    assert response.status_code == 200
    assert response.json() == {"count": 3}


def test_word_count_text_with_numbers():
    response = requests.post(f"{BASE_URL}/word-count", json={"text": "abc 123 test 456"})
    assert response.status_code == 200
    assert response.json() == {"count": 4}


def test_word_count_missing_text_field():
    response = requests.post(f"{BASE_URL}/word-count", json={})
    assert response.status_code == 400
    assert response.json() == {"error": "Missing field: text"}


def test_word_count_invalid_text_type():
    response = requests.post(f"{BASE_URL}/word-count", json={"text": True})
    assert response.status_code == 400
    assert response.json() == {"error": "Field text must be a string"}
