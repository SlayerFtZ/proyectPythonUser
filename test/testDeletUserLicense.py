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
def testDeleteProfessionalLicenseSuccess(client):
    """Test successful deletion of a professional license."""
    # Suponiendo que ya existe una licencia en la base de datos
    license = "10315777"  # Cambia esto a una licencia válida en tu base de datos
    response = client.delete(f'/deleteUserProfessionalLicense/{license}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'message' in data
    assert data['message'] == 'License and associated user successfully deleted'

def testDeleteProfessionalLicenseNotFound(client):
    """Test deletion error when license is not found."""
    license = "98465145"  # Cambia esto a una licencia que no exista
    response = client.delete(f'/deleteUserProfessionalLicense/{license}')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == 'License not found'

