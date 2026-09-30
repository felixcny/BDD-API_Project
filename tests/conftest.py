import os
import uuid
from urllib.parse import quote_plus

import httpx
import pytest
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from datetime import date, timedelta


load_dotenv()

BASE_URL = "http://localhost:8000"
ORACLE_HOST_PORT = os.getenv("ORACLE_HOST_PORT", "1522")
GYM_DB_PASSWORD = os.getenv("GYM_DB_PASSWORD")

password_encode = quote_plus(GYM_DB_PASSWORD)

TEST_DATABASE_URL = (
    f"oracle+oracledb://gym_app:{password_encode}"
    f"@localhost:{ORACLE_HOST_PORT}/?service_name=FREEPDB1"
)

engine = create_engine(TEST_DATABASE_URL)


@pytest.fixture
def admin():
    email = f"admin_{uuid.uuid4().hex[:8]}@example.com"
    password = "AdminTest1234!"
    register = httpx.post(
        f"{BASE_URL}/auth/register",
        json={
            "nom": "Admin",
            "prenom": "Test",
            "email": email,
            "password": password,
        },
    )
    assert register.status_code == 201
    utilisateur_id = register.json()["utilisateur_id"]
    with engine.begin() as connexion:
        connexion.execute(
            text(
                """
                UPDATE utilisateur
                SET role = 'ADMIN'
                WHERE utilisateur_id = :utilisateur_id
                """
            ),
            {"utilisateur_id": utilisateur_id},
        )
    login = httpx.post(
        f"{BASE_URL}/auth/token",
        json={
            "email": email,
            "password": password,
        },
    )
    assert login.status_code == 200
    return {
        "utilisateur_id": utilisateur_id,
        "email": email,
        "token": login.json()["access_token"],
    }

@pytest.fixture
def membre():
    email = f"membre_{uuid.uuid4().hex[:8]}@example.com"
    password = "MembreTest1234!"
    register = httpx.post(
        f"{BASE_URL}/auth/register",
        json={
            "nom": "Membre",
            "prenom": "Test",
            "email": email,
            "password": password,
        },
    )
    assert register.status_code == 201
    utilisateur_id = register.json()["utilisateur_id"]
    login = httpx.post(
        f"{BASE_URL}/auth/token",
        json={
            "email": email,
            "password": password,
        },
    )
    assert login.status_code == 200
    return {
        "utilisateur_id": utilisateur_id,
        "email": email,
        "token": login.json()["access_token"],
    }

@pytest.fixture
def coach(admin, membre):
    response_role = httpx.put(
        f"{BASE_URL}/utilisateurs/{membre['utilisateur_id']}/role",
        headers={
            "Authorization": f"Bearer {admin['token']}"
        },
        json={
            "role": "COACH"
        },
    )
    assert response_role.status_code == 200
    response_coach = httpx.post(
        f"{BASE_URL}/coachs",
        headers={
            "Authorization": f"Bearer {admin['token']}"
        },
        json={
            "utilisateur_id": membre["utilisateur_id"],
            "specialite": "Musculation",
        },
    )
    assert response_coach.status_code == 201
    resultat = response_coach.json()
    return {
        "coach_id": resultat["coach_id"],
        "utilisateur_id": membre["utilisateur_id"],
        "token": membre["token"],
    }

@pytest.fixture
def membre_abonnement(admin, membre):
    aujourdhui = date.today()
    response = httpx.post(
        f"{BASE_URL}/abonnements",
        headers={
            "Authorization": f"Bearer {admin['token']}"
        },
        json={
            "utilisateur_id": membre["utilisateur_id"],
            "type_abonnement": "MENSUEL",
            "date_debut": str(aujourdhui),
            "date_fin": str(aujourdhui + timedelta(days=30)),
            "prix": 39.90,
            "statut": "ACTIF",
        },
    )
    assert response.status_code == 201
    return membre

@pytest.fixture
def second_abonnement(admin):
    email = f"membre_{uuid.uuid4().hex[:8]}@example.com"
    password = "MembreTest1234!"
    register = httpx.post(
        f"{BASE_URL}/auth/register",
        json={
            "nom": "Membre",
            "prenom": "Test",
            "email": email,
            "password": password,
        },
    )
    assert register.status_code == 201
    utilisateur_id = register.json()["utilisateur_id"]
    login = httpx.post(
        f"{BASE_URL}/auth/token",
        json={
            "email": email,
            "password": password,
        },
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    aujourdhui = date.today()
    response = httpx.post(
        f"{BASE_URL}/abonnements",
        headers={
            "Authorization": f"Bearer {admin['token']}"
        },
        json={
            "utilisateur_id": utilisateur_id,
            "type_abonnement": "PREMIUM",
            "date_debut": str(aujourdhui),
            "date_fin": str(aujourdhui + timedelta(days=365)),
            "prix": 299.90,
            "statut": "ACTIF",
        },
    )
    assert response.status_code == 201
    return {
        "utilisateur_id": utilisateur_id,
        "email": email,
        "token": token,
    }

@pytest.fixture
def seance(admin, coach):
    response = httpx.post(
        f"{BASE_URL}/seances",
        headers={
            "Authorization": f"Bearer {admin['token']}"
        },
        json={
            "nom": "Renforcement musculaire",
            "coach_id": coach["coach_id"],
            "date_heure": "2026-10-15T18:00:00",
            "duree_min": 60,
            "capacite_max": 10,
        },
    )
    assert response.status_code == 201
    return response.json()

@pytest.fixture
def seance_capacite_pleine(admin, coach):
    response = httpx.post(
        f"{BASE_URL}/seances",
        headers={
            "Authorization": f"Bearer {admin['token']}"
        },
        json={
            "nom": "Renforcement musculaire",
            "coach_id": coach["coach_id"],
            "date_heure": "2026-10-15T18:00:00",
            "duree_min": 60,
            "capacite_max": 1,
        },
    )
    assert response.status_code == 201
    return response.json()