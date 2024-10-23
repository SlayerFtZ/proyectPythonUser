import pytest
import json
from main import app
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def testDeleteUserSuccess(client):
    """Test successful deletion of a user."""
    email = "11marco.doe@example.com"  # Cambia esto al correo de un usuario existente
    response = client.delete('/deleteUser', json={'email': email})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'message' in data
    assert data['message'] == 'User and associated profile pictures successfully deleted'

def testDeleteUserNotFound(client):
    """Test deletion error when user is not found."""
    email = "nonexistent@example.com"  # Cambia esto a un correo que no exista
    response = client.delete('/deleteUser', json={'email': email})
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == 'User not found'
