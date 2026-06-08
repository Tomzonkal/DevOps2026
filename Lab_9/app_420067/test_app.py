import requests
import pytest

BASE_URL = "http://localhost:5000"


# --- /health ---

def test_health():
    r = requests.get(f"{BASE_URL}/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


# --- /fibonacci ---

def test_fibonacci_zero():
    r = requests.post(f"{BASE_URL}/fibonacci", json={"n": 0})
    assert r.status_code == 200
    assert r.json()["result"] == 0


def test_fibonacci_one():
    r = requests.post(f"{BASE_URL}/fibonacci", json={"n": 1})
    assert r.status_code == 200
    assert r.json()["result"] == 1


def test_fibonacci_ten():
    r = requests.post(f"{BASE_URL}/fibonacci", json={"n": 10})
    assert r.status_code == 200
    assert r.json()["result"] == 55


def test_fibonacci_missing_field():
    r = requests.post(f"{BASE_URL}/fibonacci", json={})
    assert r.status_code == 400


def test_fibonacci_negative():
    r = requests.post(f"{BASE_URL}/fibonacci", json={"n": -1})
    assert r.status_code == 400


# --- /is-prime ---

def test_is_prime_seven():
    r = requests.post(f"{BASE_URL}/is-prime", json={"n": 7})
    assert r.status_code == 200
    assert r.json()["is_prime"] is True


def test_is_prime_four():
    r = requests.post(f"{BASE_URL}/is-prime", json={"n": 4})
    assert r.status_code == 200
    assert r.json()["is_prime"] is False


def test_is_prime_one():
    r = requests.post(f"{BASE_URL}/is-prime", json={"n": 1})
    assert r.status_code == 200
    assert r.json()["is_prime"] is False


def test_is_prime_two():
    r = requests.post(f"{BASE_URL}/is-prime", json={"n": 2})
    assert r.status_code == 200
    assert r.json()["is_prime"] is True


def test_is_prime_missing_field():
    r = requests.post(f"{BASE_URL}/is-prime", json={})
    assert r.status_code == 400


# --- /sum-digits ---

def test_sum_digits_basic():
    r = requests.post(f"{BASE_URL}/sum-digits", json={"number": 123})
    assert r.status_code == 200
    assert r.json()["result"] == 6


def test_sum_digits_single():
    r = requests.post(f"{BASE_URL}/sum-digits", json={"number": 9})
    assert r.status_code == 200
    assert r.json()["result"] == 9


def test_sum_digits_zero():
    r = requests.post(f"{BASE_URL}/sum-digits", json={"number": 0})
    assert r.status_code == 200
    assert r.json()["result"] == 0


def test_sum_digits_missing_field():
    r = requests.post(f"{BASE_URL}/sum-digits", json={})
    assert r.status_code == 400
