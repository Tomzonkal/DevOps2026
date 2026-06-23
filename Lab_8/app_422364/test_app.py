import requests

BASE_URL = "http://localhost:5000"


# --- /health ---

def test_health():
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# --- /uppercase ---

def test_uppercase_normal_text():
    response = requests.post(f"{BASE_URL}/uppercase", json={"text": "hello world"})
    assert response.status_code == 200
    assert response.json() == {"result": "HELLO WORLD"}


def test_uppercase_empty_text():
    response = requests.post(f"{BASE_URL}/uppercase", json={"text": ""})
    assert response.status_code == 200
    assert response.json() == {"result": ""}


def test_uppercase_text_with_many_spaces():
    response = requests.post(f"{BASE_URL}/uppercase", json={"text": "hello   world"})
    assert response.status_code == 200
    assert response.json() == {"result": "HELLO   WORLD"}


def test_uppercase_text_with_numbers():
    response = requests.post(f"{BASE_URL}/uppercase", json={"text": "abc123"})
    assert response.status_code == 200
    assert response.json() == {"result": "ABC123"}


def test_uppercase_missing_field():
    response = requests.post(f"{BASE_URL}/uppercase", json={"wrong": "field"})
    assert response.status_code == 400


def test_uppercase_invalid_type():
    response = requests.post(f"{BASE_URL}/uppercase", json={"text": 123})
    assert response.status_code == 400


# --- /reverse ---

def test_reverse_normal_text():
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


def test_reverse_missing_field():
    response = requests.post(f"{BASE_URL}/reverse", json={"wrong": "field"})
    assert response.status_code == 400


def test_reverse_invalid_type():
    response = requests.post(f"{BASE_URL}/reverse", json={"text": 123})
    assert response.status_code == 400


# --- /word-count ---

def test_word_count_normal_text():
    response = requests.post(f"{BASE_URL}/word-count", json={"text": "raz dwa trzy"})
    assert response.status_code == 200
    assert response.json() == {"count": 3}


def test_word_count_empty_text():
    response = requests.post(f"{BASE_URL}/word-count", json={"text": ""})
    assert response.status_code == 200
    assert response.json() == {"count": 0}


def test_word_count_text_with_many_spaces():
    response = requests.post(f"{BASE_URL}/word-count", json={"text": "raz  dwa  trzy"})
    assert response.status_code == 200
    assert response.json() == {"count": 3}


def test_word_count_text_with_numbers():
    response = requests.post(f"{BASE_URL}/word-count", json={"text": "raz 2 trzy"})
    assert response.status_code == 200
    assert response.json() == {"count": 3}


def test_word_count_missing_field():
    response = requests.post(f"{BASE_URL}/word-count", json={"wrong": "field"})
    assert response.status_code == 400


def test_word_count_invalid_type():
    response = requests.post(f"{BASE_URL}/word-count", json={"text": 123})
    assert response.status_code == 400