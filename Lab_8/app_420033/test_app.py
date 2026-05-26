import pytest
import requests
import time

BASE_URL = "http://127.0.0.1:5000"

def test_health():
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    assert response.json()['status'] == "ok"

def test_uppercase():
    payload = {"text": "hello"}
    response = requests.post(f"{BASE_URL}/uppercase", json=payload)
    assert response.json()['result'] == "HELLO"

def test_reverse():
    payload = {"text": "abcde"}
    response = requests.post(f"{BASE_URL}/reverse", json=payload)
    assert response.json()['result'] == "edcba"

def test_word_count():
    payload = {"text": "raz dwa trzy"}
    response = requests.post(f"{BASE_URL}/word-count", json=payload)
    assert response.json()['count'] == 3

def test_empty_text():
    payload = {"text": ""}
    response = requests.post(f"{BASE_URL}/word-count", json=payload)
    assert response.json()['count'] == 0

def test_missing_field():
    payload = {"not_text": "hello"}
    response = requests.post(f"{BASE_URL}/uppercase", json=payload)
    assert response.status_code == 400

def test_invalid_type():
    payload = {"text": 123}
    response = requests.post(f"{BASE_URL}/uppercase", json=payload)
    assert response.status_code == 400