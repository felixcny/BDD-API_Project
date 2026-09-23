import httpx


BASE_URL = "http://localhost:8000"


def test_admin_creation_coach(coach):
    response = httpx.get(
        f"{BASE_URL}/coachs/{coach['coach_id']}"
    )
    assert response.status_code == 200
    resultat = response.json()
    assert resultat["coach_id"] == coach["coach_id"]
    assert resultat["utilisateur_id"] == coach["utilisateur_id"]
    assert resultat["specialite"] == "Musculation"


def test_admin_creation_seance(admin, coach):
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
    resultat = response.json()
    assert resultat["nom"] == "Renforcement musculaire"
    assert resultat["coach_id"] == coach["coach_id"]
    assert resultat["duree_min"] == 60
    assert resultat["capacite_max"] == 10


def test_membre_creation_coach(membre):
    response = httpx.post(
        f"{BASE_URL}/coachs",
        headers={
            "Authorization": f"Bearer {membre['token']}"
        },
        json={
            "utilisateur_id": membre["utilisateur_id"],
            "specialite": "Cardio",
        },
    )
    assert response.status_code == 403