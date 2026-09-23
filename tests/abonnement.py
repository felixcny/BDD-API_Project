import httpx


BASE_URL = "http://localhost:8000"


def test_admin_creation_abo(admin, membre):
    response = httpx.post(
        f"{BASE_URL}/abonnements",
        headers={
            "Authorization": f"Bearer {admin['token']}"
        },
        json={
            "utilisateur_id": membre["utilisateur_id"],
            "type_abonnement": "MENSUEL",
            "date_debut": "2026-10-01",
            "date_fin": "2026-11-01",
            "prix": 39.90,
            "statut": "ACTIF",
        },
    )
    assert response.status_code == 201
    resultat = response.json()
    assert resultat["utilisateur_id"] == membre["utilisateur_id"]
    assert resultat["type_abonnement"] == "MENSUEL"
    assert resultat["statut"] == "ACTIF"


def test_membre_creation_abo(membre):
    response = httpx.post(
        f"{BASE_URL}/abonnements",
        headers={
            "Authorization": f"Bearer {membre['token']}"
        },
        json={
            "utilisateur_id": membre["utilisateur_id"],
            "type_abonnement": "MENSUEL",
            "date_debut": "2026-10-01",
            "date_fin": "2026-11-01",
            "prix": 39.90,
            "statut": "ACTIF",
        },
    )
    assert response.status_code == 403


def test_membre_voir_son_abo(admin, membre):
    creation = httpx.post(
        f"{BASE_URL}/abonnements",
        headers={
            "Authorization": f"Bearer {admin['token']}"
        },
        json={
            "utilisateur_id": membre["utilisateur_id"],
            "type_abonnement": "PREMIUM",
            "date_debut": "2026-10-01",
            "date_fin": "2027-10-01",
            "prix": 299.90,
            "statut": "ACTIF",
        },
    )
    assert creation.status_code == 201
    response = httpx.get(
        f"{BASE_URL}/abonnements/me",
        headers={
            "Authorization": f"Bearer {membre['token']}"
        },
    )
    assert response.status_code == 200
    abonnements = response.json()
    assert any(
        abo["utilisateur_id"] == membre["utilisateur_id"]
        and abo["type_abonnement"] == "PREMIUM"
        and abo["statut"] == "ACTIF"
        for abo in abonnements
    )