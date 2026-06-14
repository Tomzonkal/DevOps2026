import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health(client):
    res = client.get('/health')
    assert res.status_code == 200
    assert res.get_json() == {'status': 'ok'}

def test_uppercase(client):
    res = client.post('/uppercase', json={'text': 'hello'})
    assert res.get_json()['result'] == 'HELLO'

def test_uppercase_missing_field(client):
    res = client.post('/uppercase', json={})
    assert res.status_code == 400

def test_reverse(client):
    res = client.post('/reverse', json={'text': 'abc'})
    assert res.get_json()['result'] == 'cba'

def test_word_count(client):
    res = client.post('/word-count', json={'text': 'hello world'})
    assert res.get_json()['count'] == 2

def test_word_count_empty(client):
    res = client.post('/word-count', json={'text': ''})
    assert res.get_json()['count'] == 0
