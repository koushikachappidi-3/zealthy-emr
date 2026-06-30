def test_create_prescription_for_test_patient(client, test_patient, prescription_payload):
    response = client.post(
        f"/patients/{test_patient['id']}/prescriptions",
        json=prescription_payload,
    )

    assert response.status_code == 201
    assert response.json()["medication"] == prescription_payload["medication"]


def test_list_patient_prescriptions(client, test_patient, prescription_payload):
    client.post(f"/patients/{test_patient['id']}/prescriptions", json=prescription_payload)
    response = client.get(f"/patients/{test_patient['id']}/prescriptions")

    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_update_prescription(client, test_patient, prescription_payload):
    created = client.post(
        f"/patients/{test_patient['id']}/prescriptions",
        json=prescription_payload,
    ).json()
    response = client.put(
        f"/prescriptions/{created['id']}",
        json={
            "quantity": 2,
        },
    )

    assert response.status_code == 200
    assert response.json()["quantity"] == 2


def test_delete_prescription(client, test_patient, prescription_payload):
    created = client.post(
        f"/patients/{test_patient['id']}/prescriptions",
        json=prescription_payload,
    ).json()
    response = client.delete(f"/prescriptions/{created['id']}")

    assert response.status_code == 204
    assert client.put(f"/prescriptions/{created['id']}", json={"quantity": 3}).status_code == 404


def test_create_prescription_invalid_patient_id_returns_404(client, prescription_payload):
    response = client.post("/patients/999999/prescriptions", json=prescription_payload)

    assert response.status_code == 404


def test_update_invalid_prescription_id_returns_404(client):
    response = client.put(
        "/prescriptions/999999",
        json={
            "quantity": 2,
        },
    )

    assert response.status_code == 404


def test_create_prescription_missing_body_returns_422(client, test_patient):
    response = client.post(f"/patients/{test_patient['id']}/prescriptions")

    assert response.status_code == 422
