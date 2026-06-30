def test_get_patients_returns_seeded_patients(client):
    response = client.get("/patients")
    emails = {patient["email"] for patient in response.json()}

    assert response.status_code == 200
    assert "mark@some-email-provider.net" in emails
    assert "lisa@some-email-provider.net" in emails


def test_get_patient_by_id_succeeds(client):
    response = client.get("/patients/1")

    assert response.status_code == 200
    assert response.json()["email"] == "mark@some-email-provider.net"


def test_get_nonexistent_patient_returns_404(client):
    response = client.get("/patients/999999")

    assert response.status_code == 404


def test_create_patient_succeeds(client, unique_email, cleanup_patient_by_id):
    response = client.post(
        "/patients",
        json={
            "name": "Created By Pytest",
            "email": unique_email,
            "password": "Created123!",
        },
    )

    assert response.status_code == 201
    assert response.json()["email"] == unique_email
    cleanup_patient_by_id(response.json()["id"])


def test_duplicate_email_returns_409(client, test_patient):
    response = client.post(
        "/patients",
        json={
            "name": "Duplicate Patient",
            "email": test_patient["email"],
            "password": "Created123!",
        },
    )

    assert response.status_code == 409


def test_create_patient_invalid_email_returns_422(client):
    response = client.post(
        "/patients",
        json={
            "name": "Invalid Email",
            "email": "not-an-email",
            "password": "Created123!",
        },
    )

    assert response.status_code == 422


def test_update_patient_succeeds(client, test_patient):
    response = client.put(
        f"/patients/{test_patient['id']}",
        json={
            "name": "Updated Pytest Patient",
        },
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Updated Pytest Patient"


def test_update_nonexistent_patient_returns_404(client):
    response = client.put(
        "/patients/999999",
        json={
            "name": "Nobody",
        },
    )

    assert response.status_code == 404
