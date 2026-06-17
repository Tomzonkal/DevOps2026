import requests

BASE_URL = "http://localhost:5000"


def test_health():
    response = requests.get(f"{BASE_URL}/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_uppercase_normal_text():
    response = requests.post(
        f"{BASE_URL}/uppercase",
        json={"text": "hello world"}
    )

    assert response.status_code == 200
    assert response.json() == {"result": "HELLO WORLD"}


def test_uppercase_empty_text():
    response = requests.post(
        f"{BASE_URL}/uppercase",
        json={"text": ""}
    )

    assert response.status_code == 200
    assert response.json() == {"result": ""}


def test_uppercase_text_with_many_spaces():
    response = requests.post(
        f"{BASE_URL}/uppercase",
        json={"text": "hello   world"}
    )

    assert response.status_code == 200
    assert response.json() == {"result": "HELLO   WORLD"}


def test_uppercase_text_with_numbers():
    response = requests.post(
        f"{BASE_URL}/uppercase",
        json={"text": "abc123 test"}
    )

    assert response.status_code == 200
    assert response.json() == {"result": "ABC123 TEST"}


def test_reverse_normal_text():
    response = requests.post(
        f"{BASE_URL}/reverse",
        json={"text": "hello"}
    )

    assert response.status_code == 200
    assert response.json() == {"result": "olleh"}


def test_reverse_empty_text():
    response = requests.post(
        f"{BASE_URL}/reverse",
        json={"text": ""}
    )

    assert response.status_code == 200
    assert response.json() == {"result": ""}


def test_reverse_text_with_many_spaces():
    response = requests.post(
        f"{BASE_URL}/reverse",
        json={"text": "abc   def"}
    )

    assert response.status_code == 200
    assert response.json() == {"result": "fed   cba"}


def test_reverse_text_with_numbers():
    response = requests.post(
        f"{BASE_URL}/reverse",
        json={"text": "abc123"}
    )

    assert response.status_code == 200
    assert response.json() == {"result": "321cba"}


def test_word_count_normal_text():
    response = requests.post(
        f"{BASE_URL}/word-count",
        json={"text": "hello world"}
    )

    assert response.status_code == 200
    assert response.json() == {"count": 2}


def test_word_count_empty_text():
    response = requests.post(
        f"{BASE_URL}/word-count",
        json={"text": ""}
    )

    assert response.status_code == 200
    assert response.json() == {"count": 0}


def test_word_count_text_with_many_spaces():
    response = requests.post(
        f"{BASE_URL}/word-count",
        json={"text": "hello     world   test"}
    )

    assert response.status_code == 200
    assert response.json() == {"count": 3}


def test_word_count_text_with_numbers():
    response = requests.post(
        f"{BASE_URL}/word-count",
        json={"text": "abc 123 test456"}
    )

    assert response.status_code == 200
    assert response.json() == {"count": 3}


def test_missing_text_field_uppercase():
    response = requests.post(
        f"{BASE_URL}/uppercase",
        json={}
    )

    assert response.status_code == 400
    assert response.json() == {"error": "Missing field: text"}


def test_missing_text_field_reverse():
    response = requests.post(
        f"{BASE_URL}/reverse",
        json={}
    )

    assert response.status_code == 400
    assert response.json() == {"error": "Missing field: text"}


def test_missing_text_field_word_count():
    response = requests.post(
        f"{BASE_URL}/word-count",
        json={}
    )

    assert response.status_code == 400
    assert response.json() == {"error": "Missing field: text"}


def test_invalid_text_type_uppercase():
    response = requests.post(
        f"{BASE_URL}/uppercase",
        json={"text": 123}
    )

    assert response.status_code == 400
    assert response.json() == {"error": "Field text must be a string"}


def test_invalid_text_type_reverse():
    response = requests.post(
        f"{BASE_URL}/reverse",
        json={"text": 123}
    )

    assert response.status_code == 400
    assert response.json() == {"error": "Field text must be a string"}


def test_invalid_text_type_word_count():
    response = requests.post(
        f"{BASE_URL}/word-count",
        json={"text": 123}
    )

    assert response.status_code == 400
    assert response.json() == {"error": "Field text must be a string"}