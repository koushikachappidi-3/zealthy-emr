def test_create_appointment_for_test_patient(client, test_patient, appointment_payload):
    response = client.post(
        f"/patients/{test_patient['id']}/appointments",
        json=appointment_payload,
    )

    assert response.status_code == 201
    assert response.json()["provider"] == appointment_payload["provider"]


def test_list_patient_appointments(client, test_patient, appointment_payload):
    client.post(f"/patients/{test_patient['id']}/appointments", json=appointment_payload)
    response = client.get(f"/patients/{test_patient['id']}/appointments")

    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_update_appointment(client, test_patient, appointment_payload):
    created = client.post(
        f"/patients/{test_patient['id']}/appointments",
        json=appointment_payload,
    ).json()
    response = client.put(
        f"/appointments/{created['id']}",
        json={
            "provider": "Dr Updated",
        },
    )

    assert response.status_code == 200
    assert response.json()["provider"] == "Dr Updated"


def test_delete_appointment(client, test_patient, appointment_payload):
    created = client.post(
        f"/patients/{test_patient['id']}/appointments",
        json=appointment_payload,
    ).json()
    response = client.delete(f"/appointments/{created['id']}")

    assert response.status_code == 204
    assert client.put(f"/appointments/{created['id']}", json={"provider": "Nope"}).status_code == 404


def test_create_appointment_invalid_patient_id_returns_404(client, appointment_payload):
    response = client.post("/patients/999999/appointments", json=appointment_payload)

    assert response.status_code == 404


def test_update_invalid_appointment_id_returns_404(client):
    response = client.put(
        "/appointments/999999",
        json={
            "provider": "Missing Appointment",
        },
    )

    assert response.status_code == 404


def test_create_appointment_missing_body_returns_422(client, test_patient):
    response = client.post(f"/patients/{test_patient['id']}/appointments")

    assert response.status_code == 422
