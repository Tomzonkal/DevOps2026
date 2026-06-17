from app import app


def test_health_endpoint():
    client = app.test_client()
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_home_endpoint():
    client = app.test_client()
    response = client.get("/")

    data = response.get_json()

    assert response.status_code == 200
    assert data["student_index"] == "422971"
    assert data["status"] == "running"


def test_version_endpoint():
    client = app.test_client()
    response = client.get("/version")

    assert response.status_code == 200
    assert response.get_json()["version"] == "1.0.0"