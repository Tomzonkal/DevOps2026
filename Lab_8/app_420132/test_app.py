import requests
import pytest

BASE_URL = "http://127.0.0.1:5000"


# --- /uppercase ---

def test_uppercase_basic():
    r = requests.post(f"{BASE_URL}/uppercase", json={"text": "hello world"})
    assert r.status_code == 200
    assert r.json()["result"] == "HELLO WORLD"

def test_uppercase_already_upper():
    r = requests.post(f"{BASE_URL}/uppercase", json={"text": "HELLO"})
    assert r.status_code == 200
    assert r.json()["result"] == "HELLO"

def test_uppercase_with_digits():
    r = requests.post(f"{BASE_URL}/uppercase", json={"text": "abc123"})
    assert r.status_code == 200
    assert r.json()["result"] == "ABC123"

def test_uppercase_empty_string():
    r = requests.post(f"{BASE_URL}/uppercase", json={"text": ""})
    assert r.status_code == 200
    assert r.json()["result"] == ""

def test_uppercase_missing_field():
    r = requests.post(f"{BASE_URL}/uppercase", json={})
    assert r.status_code == 400
    assert "error" in r.json()

def test_uppercase_wrong_type():
    r = requests.post(f"{BASE_URL}/uppercase", json={"text": 123})
    assert r.status_code == 400
    assert "error" in r.json()


# --- /reverse ---

def test_reverse_basic():
    r = requests.post(f"{BASE_URL}/reverse", json={"text": "abcde"})
    assert r.status_code == 200
    assert r.json()["result"] == "edcba"

def test_reverse_empty_string():
    r = requests.post(f"{BASE_URL}/reverse", json={"text": ""})
    assert r.status_code == 200
    assert r.json()["result"] == ""

def test_reverse_with_digits():
    r = requests.post(f"{BASE_URL}/reverse", json={"text": "123abc"})
    assert r.status_code == 200
    assert r.json()["result"] == "cba321"

def test_reverse_missing_field():
    r = requests.post(f"{BASE_URL}/reverse", json={})
    assert r.status_code == 400
    assert "error" in r.json()

def test_reverse_wrong_type():
    r = requests.post(f"{BASE_URL}/reverse", json={"text": 99.9})
    assert r.status_code == 400
    assert "error" in r.json()


# --- /word-count ---

def test_word_count_basic():
    r = requests.post(f"{BASE_URL}/word-count", json={"text": "raz dwa trzy"})
    assert r.status_code == 200
    assert r.json()["count"] == 3

def test_word_count_single_word():
    r = requests.post(f"{BASE_URL}/word-count", json={"text": "hello"})
    assert r.status_code == 200
    assert r.json()["count"] == 1

def test_word_count_empty_string():
    r = requests.post(f"{BASE_URL}/word-count", json={"text": ""})
    assert r.status_code == 200
    assert r.json()["count"] == 0

def test_word_count_multiple_spaces():
    r = requests.post(f"{BASE_URL}/word-count", json={"text": "raz  dwa   trzy"})
    assert r.status_code == 200
    assert r.json()["count"] == 3

def test_word_count_missing_field():
    r = requests.post(f"{BASE_URL}/word-count", json={})
    assert r.status_code == 400
    assert "error" in r.json()

def test_word_count_wrong_type():
    r = requests.post(f"{BASE_URL}/word-count", json={"text": ["lista"]})
    assert r.status_code == 400
    assert "error" in r.json()


# --- /health ---

def test_health():
    r = requests.get(f"{BASE_URL}/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
