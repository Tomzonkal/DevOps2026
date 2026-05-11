import pytest
import requests

BASE_URL = "http://localhost:5000"


def test_health():
    r = requests.get(f"{BASE_URL}/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


# --- /uppercase ---
def test_uppercase_basic():
    r = requests.post(f"{BASE_URL}/uppercase", json={"text": "hello world"})
    assert r.status_code == 200
    assert r.json()["result"] == "HELLO WORLD"


def test_uppercase_already_upper():
    r = requests.post(f"{BASE_URL}/uppercase", json={"text": "HELLO"})
    assert r.status_code == 200
    assert r.json()["result"] == "HELLO"


def test_uppercase_empty():
    r = requests.post(f"{BASE_URL}/uppercase", json={"text": ""})
    assert r.status_code == 200
    assert r.json()["result"] == ""


def test_uppercase_numbers():
    r = requests.post(f"{BASE_URL}/uppercase", json={"text": "abc123"})
    assert r.status_code == 200
    assert r.json()["result"] == "ABC123"


def test_uppercase_missing_field():
    r = requests.post(f"{BASE_URL}/uppercase", json={"wrong": "field"})
    assert r.status_code == 400
    assert "error" in r.json()


def test_uppercase_invalid_type():
    r = requests.post(f"{BASE_URL}/uppercase", json={"text": 123})
    assert r.status_code == 400
    assert "error" in r.json()


# --- /reverse ---
def test_reverse_basic():
    r = requests.post(f"{BASE_URL}/reverse", json={"text": "abcde"})
    assert r.status_code == 200
    assert r.json()["result"] == "edcba"


def test_reverse_empty():
    r = requests.post(f"{BASE_URL}/reverse", json={"text": ""})
    assert r.status_code == 200
    assert r.json()["result"] == ""


def test_reverse_single_char():
    r = requests.post(f"{BASE_URL}/reverse", json={"text": "a"})
    assert r.status_code == 200
    assert r.json()["result"] == "a"


def test_reverse_numbers():
    r = requests.post(f"{BASE_URL}/reverse", json={"text": "12345"})
    assert r.status_code == 200
    assert r.json()["result"] == "54321"


def test_reverse_missing_field():
    r = requests.post(f"{BASE_URL}/reverse", json={"wrong": "field"})
    assert r.status_code == 400
    assert "error" in r.json()


def test_reverse_invalid_type():
    r = requests.post(f"{BASE_URL}/reverse", json={"text": 456})
    assert r.status_code == 400
    assert "error" in r.json()


# --- /word-count ---
def test_word_count_basic():
    r = requests.post(f"{BASE_URL}/word-count", json={"text": "raz dwa trzy"})
    assert r.status_code == 200
    assert r.json()["count"] == 3


def test_word_count_single():
    r = requests.post(f"{BASE_URL}/word-count", json={"text": "hello"})
    assert r.status_code == 200
    assert r.json()["count"] == 1


def test_word_count_empty():
    r = requests.post(f"{BASE_URL}/word-count", json={"text": ""})
    assert r.status_code == 200
    assert r.json()["count"] == 0


def test_word_count_multiple_spaces():
    r = requests.post(f"{BASE_URL}/word-count", json={"text": "raz   dwa"})
    assert r.status_code == 200
    assert r.json()["count"] == 2


def test_word_count_missing_field():
    r = requests.post(f"{BASE_URL}/word-count", json={"wrong": "field"})
    assert r.status_code == 400
    assert "error" in r.json()


def test_word_count_invalid_type():
    r = requests.post(f"{BASE_URL}/word-count", json={"text": 789})
    assert r.status_code == 400
    assert "error" in r.json()