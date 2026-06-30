def test_seeded_login_succeeds(client, sample_patient_credentials):
    response = client.post("/auth/login", json=sample_patient_credentials)

    assert response.status_code == 200
    assert response.json()["email"] == sample_patient_credentials["email"]


def test_wrong_password_returns_401(client, sample_patient_credentials):
    response = client.post(
        "/auth/login",
        json={
            "email": sample_patient_credentials["email"],
            "password": "wrong-password",
        },
    )

    assert response.status_code == 401


def test_unknown_email_returns_401(client):
    response = client.post(
        "/auth/login",
        json={
            "email": "missing-patient@example.com",
            "password": "Password123!",
        },
    )

    assert response.status_code == 401


def test_invalid_email_format_returns_422(client):
    response = client.post(
        "/auth/login",
        json={
            "email": "not-an-email",
            "password": "Password123!",
        },
    )

    assert response.status_code == 422


def test_missing_password_returns_422(client):
    response = client.post(
        "/auth/login",
        json={
            "email": "mark@some-email-provider.net",
        },
    )

    assert response.status_code == 422
