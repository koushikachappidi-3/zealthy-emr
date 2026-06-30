def test_get_medication_options_returns_seeded_medications(client):
    response = client.get("/options/medications")
    names = {option["name"] for option in response.json()}

    assert response.status_code == 200
    assert "Lexapro" in names
    assert "Ozempic" in names


def test_get_dosage_options_returns_seeded_dosages(client):
    response = client.get("/options/dosages")
    values = {option["value"] for option in response.json()}

    assert response.status_code == 200
    assert "5mg" in values
    assert "500mg" in values
