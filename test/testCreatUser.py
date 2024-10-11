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

def testRegisterUserSuccess(client):
    """Test successful user registration."""
    user_data = {
        "first_name": "Marco Antonio",
        "last_name_father": "Aguilar",
        "last_name_mother": "Cortes",
        "birth_date": "1990-01-01",
        "phone_number": "2321431642",
        "email": "marco.doe@example.com",
        "password": "securepassword",
        "license": "10315777"
    }
    response = client.post('/User', json=user_data)
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'message' in data
    assert data['message'] == 'User registered successfully'
    assert 'user_id' in data

def testRegisterUserMissingField(client):
    """Test registration error for missing fields."""
    user_data = {
        "first_name": "Jane",
        "last_name_father": "Doe",
        "last_name_mother": "",
        "birth_date": "1995-05-05",
        "phone_number": "0987654321",
        "email": "jane.doe@example.com",
        "password": "anotherpassword"
    }
    response = client.post('/User', json=user_data)
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == 'Missing field: last_name_mother'

def testRegisterUserEmailInUse(client):
    """Test registration error for email already in use."""
    user_data = {
        "first_name": "Alice",
        "last_name_father": "Wonder",
        "last_name_mother": "Land",
        "birth_date": "1992-02-02",
        "phone_number": "1122334455",
        "email": "marco.doe@example.com",
        "password": "password123"
    }
    response = client.post('/User', json=user_data)
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == 'Email is already in use'

def testRegisterUserInvalidLicense(client):
    """Test registration error for invalid license data."""
    user_data = {
        "first_name": "Luis Fernando",
        "last_name_father": "Romero",
        "last_name_mother": "Gomez",
        "birth_date": "1991-03-03",
        "phone_number": "1234567890",
        "email": "charlie.brown@example.com",
        "password": "password321",
        "license": "****" 
    }
    response = client.post('/User', json=user_data)
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == 'Could not select ID' 

def testRegisterUserNonGastronomyCareer(client):
    """Test registration error for non-gastronomy related career."""
    user_data = {
        "first_name": "Luis Fernando",
        "last_name_father": "Romero",
        "last_name_mother": "Gomez",
        "birth_date": "1985-05-05",
        "phone_number": "9876543210",
        "email": "frank.castle@example.com",
        "password": "password999",
        "license": "13356177"  
    }
    response = client.post('/User', json=user_data)
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == 'The career is not related to gastronomy'

def testRegisterUserInternalError(client):
    """Test server error response."""
    user_data = {
        "first_name": "Luis Fernando",
        "last_name_father": "Romero",
        "last_name_mother": "Gomez",
        "birth_date": "1988-01-01",  
        "phone_number": "4555555555",  
        "email": "bobcl@gmail.com", 
        "password": "bobpassword",
        "license": "4885995",
    }
    response = client.post('/User', json=user_data)
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == 'Registration error'
