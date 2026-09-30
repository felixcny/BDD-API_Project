import uuid 
import httpx

BASE_URL = "http://localhost:8000"

def email_unique():
    return f"test_{uuid.uuid4().hex[:8]}@example.com"

def test_register():
    email = email_unique()
    data = {
        "nom": "Sam",
        "prenom": "Chat",
        "email": email,
        "password": "Test1234!",
        "password_confirm": "Test1234!"
    }
    response = httpx.post(BASE_URL + "/auth/register", json=data)
    assert response.status_code == 201
    result = response.json()
    assert result["nom"] == data["nom"]
    assert result["prenom"] == data["prenom"]
    assert result["email"] == data["email"]
    assert result["role"] == "MEMBRE"
    assert "password" not in result
    assert "password_hash" not in result

def test_email_deja_utilise():
    email = email_unique()
    donnees = {
        "nom": "Claude",
        "prenom": "Sonnet",
        "email": email,
        "password": "Test1234!"
    }
    premiere_reponse = httpx.post(f"{BASE_URL}/auth/register", json=donnees)
    assert premiere_reponse.status_code == 201
    deuxieme_reponse = httpx.post(f"{BASE_URL}/auth/register", json=donnees)
    assert deuxieme_reponse.status_code == 409
    assert deuxieme_reponse.json()["detail"] == "Email déjà utilisé"

def test_login_correct():
    email = email_unique()
    password = "Test1234!"
    httpx.post(f"{BASE_URL}/auth/register", json={
        "nom": "Muse",
        "prenom": "Mark",
        "email": email,
        "password": password
    })
    response = httpx.post(f"{BASE_URL}/auth/token", json={"email": email, "password": password})
    assert response.status_code == 200
    resultat = response.json()
    assert "access_token" in resultat
    assert resultat["token_type"] == "bearer"
    assert len(resultat["access_token"]) > 20

def test_password_incorrect():
    email = email_unique()
    httpx.post(f"{BASE_URL}/auth/register", json={
        "nom": "Astra",
        "prenom": "Solair",
        "email": email,
        "password": "Test1234!"
    })
    response = httpx.post(f"{BASE_URL}/auth/token", json={
        "email": email,
        "password": "MauvaisMotDePasse!"
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Email ou mot de passe incorrect"
