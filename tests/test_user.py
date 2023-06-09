# tests/test_user.py
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from fastapi.testclient import TestClient
from main import app  # Import app-instance from main.py

client = TestClient(app)

def test_create_user():
    # Create a testuser and add it to the DB
    test_user = {
        "username": "john.doe",
        "email": "john.doe@freehci.com",
        "password": "secret123"
    }
    response = client.post("/users/", json=test_user)
    assert response.status_code == 200
    
    

def test_get_user_by_id():
    # Create a testuser and add it to the DB
    test_user_id = 3
    # Test for a valid user-ID
    response = client.get(f"/users/{test_user_id}")
    assert response.status_code == 200
    
    # Deactivated because of database changes
    #assert response.json() == {
    #    "id": test_user_id,
    #    "username": "john.doe",
    #    "email": "john.doe@freehci.org",
    #    "password": "$2b$12$4gbE0DqWsl/yKkW6gN0M6e1RGLJKWsJc.41Jl8A7tELO1vvL7xXTC"
    #}

    # Test for a invalid user-ID
    response = client.get("/users/0")
    assert response.status_code == 404
