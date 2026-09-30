import uuid
import httpx


BASE_URL = "http://localhost:8000"


def creer_membre_et_token():
    email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    password = "Test1234!"
    register = httpx.post(
        f"{BASE_URL}/auth/register",
        json={
            "nom": "Deep",
            "prenom": "Seek",
            "email": email,
            "password": password
        }
    )
    assert register.status_code == 201
    login = httpx.post(
        f"{BASE_URL}/auth/token",
        json={
            "email": email,
            "password": password
        }
    )
    assert login.status_code == 200
    return login.json()["access_token"]


def test_liste_seances():
    response = httpx.get(f"{BASE_URL}/seances")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_liste_coachs():
    response = httpx.get(f"{BASE_URL}/coachs")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_mes_abonnements():
    token = creer_membre_et_token()
    response = httpx.get(
        f"{BASE_URL}/abonnements/me",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_membre_creation_seance():
    token = creer_membre_et_token()
    response = httpx.post(
        f"{BASE_URL}/seances",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "nom": "Cours interdit",
            "coach_id": 999999,
            "date_heure": "2026-10-01T18:00:00",
            "duree_min": 60,
            "capacite_max": 10
        }
    )
    assert response.status_code == 403