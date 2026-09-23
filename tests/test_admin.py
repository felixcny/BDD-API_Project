import httpx

BASE_URL = "http://localhost:8000"

def test_admin_lister_utilisateurs(admin):
    response = httpx.get(
        f"{BASE_URL}/utilisateurs",
        headers={
            "Authorization": f"Bearer {admin['token']}"
        },
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_admin_reconnu(admin):
    response = httpx.get(
        f"{BASE_URL}/utilisateurs/me",
        headers={
            "Authorization": f"Bearer {admin['token']}"
        },
    )
    assert response.status_code == 200
    resultat = response.json()
    assert resultat["utilisateur_id"] == admin["utilisateur_id"]
    assert resultat["email"] == admin["email"]
    assert resultat["role"] == "ADMIN"