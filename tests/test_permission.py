import uuid
import httpx


BASE_URL = "http://localhost:8000"


def creer_utilisateur():
    email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    password = "Test1234!"
    response_register = httpx.post(
        f"{BASE_URL}/auth/register",
        json={
            "nom": "Sol",
            "prenom": "Fable",
            "email": email,
            "password": password
        }
    )
    assert response_register.status_code == 201
    response_login = httpx.post(
        f"{BASE_URL}/auth/token",
        json={
            "email": email,
            "password": password
        }
    )
    assert response_login.status_code == 200
    return email, response_login.json()["access_token"]

def test_utilisateur_avec_token():
    email, token = creer_utilisateur()
    response = httpx.get(
        f"{BASE_URL}/utilisateurs/me",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    assert response.status_code == 200
    resultat = response.json()
    assert resultat["email"] == email
    assert resultat["role"] == "MEMBRE"

def test_utilisateur_token_invalide():
    response = httpx.get(
        f"{BASE_URL}/utilisateurs/me",
        headers={
            "Authorization": "Bearer ceci_est_un_faux_token"
        }
    )
    assert response.status_code == 401

def test_permission():
    _, token = creer_utilisateur()
    response = httpx.get(
        f"{BASE_URL}/utilisateurs",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    assert response.status_code == 403