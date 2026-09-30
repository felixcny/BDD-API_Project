import uuid 
import httpx
import os 





BASE_URL = "http://localhost:8000"

def test_reservation_valide(membre_abonnement, seance):
    response = httpx.post(
        f"{BASE_URL}/reservations",
        headers={
            "Authorization": f"Bearer {membre_abonnement['token']}"
        },
        json={
            "seance_id": seance["seance_id"]
        },
    )
    assert response.status_code == 201
    resultat = response.json()
    assert resultat["seance_id"] == seance["seance_id"]
    assert resultat["utilisateur_id"] == membre_abonnement["utilisateur_id"]
    assert resultat["statut"] == "CONFIRMEE"

def test_reservation_refus(membre, seance):
    response = httpx.post(
        f"{BASE_URL}/reservations",
        headers={
            "Authorization": f"Bearer {membre['token']}"
        },
        json={
            "seance_id": seance["seance_id"]
        },
    )
    assert response.status_code == 409

def test_double_reservation(membre_abonnement, seance):
    headers = {
        "Authorization": f"Bearer {membre_abonnement['token']}"
    }
    premier_test = httpx.post(
        f"{BASE_URL}/reservations",
        headers=headers,
        json={
            "seance_id": seance["seance_id"]
        },
    )
    assert premier_test.status_code == 201
    deuxieme_test = httpx.post(
        f"{BASE_URL}/reservations",
        headers=headers,
        json={
            "seance_id": seance["seance_id"]
        },
    )
    assert deuxieme_test.status_code == 409

def test_annule_reservation(membre_abonnement, seance):
    headers = {
        "Authorization": f"Bearer {membre_abonnement['token']}"
    }
    reservation = httpx.post(
        f"{BASE_URL}/reservations",
        headers=headers,
        json={
            "seance_id": seance["seance_id"]
        },
    )
    assert reservation.status_code == 201
    reservation_id = reservation.json()["reservation_id"]
    annulation = httpx.delete(
        f"{BASE_URL}/reservations/{reservation_id}",
        headers=headers,
    )
    assert annulation.status_code == 200
    assert annulation.json()["statut"] == "ANNULEE"
    deuxieme_annulation = httpx.delete(
        f"{BASE_URL}/reservations/{reservation_id}",
        headers=headers,
    )
    assert deuxieme_annulation.status_code == 409

    
def test_reservation_pleine(seance_capacite_pleine, membre_abonnement, second_abonnement):
    premier = httpx.post(
        f"{BASE_URL}/reservations",
        headers={
            "Authorization": f"Bearer {membre_abonnement['token']}"
        },
        json={
            "seance_id": seance_capacite_pleine["seance_id"]
        },
    )
    assert premier.status_code == 201
    deuxieme = httpx.post(
        f"{BASE_URL}/reservations",
        headers={
            "Authorization": f"Bearer {second_abonnement['token']}"
        },
        json={
            "seance_id": seance_capacite_pleine["seance_id"]
        },
    )
    assert deuxieme.status_code == 409

def test_annule_autre_membre(seance, membre_abonnement, second_abonnement):
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
    reservation_id = creation.json()["reservation_id"]
    annulation = httpx.delete(
        f"{BASE_URL}/reservations/{reservation_id}",
        headers={
            "Authorization": f"Bearer {second_abonnement['token']}"
        },
    )
    assert annulation.status_code == 403

def test_admin_annuler(admin, seance, membre_abonnement):
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
    reservation_id = creation.json()["reservation_id"]
    annulation = httpx.delete(
        f"{BASE_URL}/reservations/{reservation_id}",
        headers={
            "Authorization": f"Bearer {admin['token']}"
        },
    )
    assert annulation.status_code == 200
    assert annulation.json()["statut"] == "ANNULEE"
    
