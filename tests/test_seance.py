import httpx

BASE_URL = "http://localhost:8000"

def test_statistique_capacite(membre_abonnement, seance):
    creation = httpx.post(
        f"{BASE_URL}/reservations",
        headers={
            "Authorization": f"Bearer {membre_abonnement['token']}"
        },
        json={
            "seance_id": seance["seance_id"]
        },
    )
    assert creation.status_code == 201
    response = httpx.get(
        f"{BASE_URL}/seances/{seance['seance_id']}/stats"
    )
    assert response.status_code == 200

def test_reduction_capacite(seance, admin, membre_abonnement, second_abonnement):
    for utilisateur in [membre_abonnement, second_abonnement]:
        creation = httpx.post(
            f"{BASE_URL}/reservations",
            headers={
                "Authorization": f"Bearer {utilisateur['token']}"
            },
            json={
                "seance_id": seance["seance_id"]
            },
        )
        assert creation.status_code == 201
    modif = httpx.put(
        f"{BASE_URL}/seances/{seance['seance_id']}",
        headers={
            "Authorization": f"Bearer {admin['token']}"
        },
        json={
            "nom": "Cours de Yoga",
            "date_heure": seance["date_heure"],
            "capacite_max": 1,
            "coach_id": seance["coach_id"],
            "duree_min": seance["duree_min"]
        },
    )
    assert modif.status_code == 409

def test_suppr_seance_avec_resa(seance, admin, membre_abonnement):
    creation = httpx.post(
        f"{BASE_URL}/reservations",
        headers={
            "Authorization": f"Bearer {membre_abonnement['token']}"
        },
        json={
            "seance_id": seance["seance_id"]
        },
    )
    assert creation.status_code == 201
    suppression = httpx.delete(
        f"{BASE_URL}/seances/{seance['seance_id']}",
        headers={
            "Authorization": f"Bearer {admin['token']}"
        },
    )
    assert suppression.status_code == 409