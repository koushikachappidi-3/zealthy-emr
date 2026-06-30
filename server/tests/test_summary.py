def test_patient_summary_succeeds(client, test_patient, appointment_payload, prescription_payload):
    client.post(f"/patients/{test_patient['id']}/appointments", json=appointment_payload)
    client.post(f"/patients/{test_patient['id']}/prescriptions", json=prescription_payload)

    response = client.get(f"/patients/{test_patient['id']}/summary")

    assert response.status_code == 200


def test_patient_summary_includes_patient_info(client, test_patient):
    response = client.get(f"/patients/{test_patient['id']}/summary")
    body = response.json()

    assert body["id"] == test_patient["id"]
    assert body["email"] == test_patient["email"]


def test_patient_summary_includes_next_seven_day_keys(client, test_patient):
    response = client.get(f"/patients/{test_patient['id']}/summary")
    body = response.json()

    assert "upcoming_appointments" in body
    assert "refills_due" in body


def test_patient_summary_invalid_patient_id_returns_404(client):
    response = client.get("/patients/999999/summary")

    assert response.status_code == 404
