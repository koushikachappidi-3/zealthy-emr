from datetime import date, datetime, timedelta
from pathlib import Path
import sys
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

SERVER_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SERVER_DIR))

from database.connection import get_connection
from main import app


@pytest.fixture()
def client():
    return TestClient(app)


@pytest.fixture()
def unique_email():
    return f"pytest-{uuid4().hex}@example.com"


@pytest.fixture()
def sample_patient_credentials():
    return {
        "email": "mark@some-email-provider.net",
        "password": "Password123!",
    }


@pytest.fixture()
def test_patient(client, unique_email):
    payload = {
        "name": "Pytest Patient",
        "email": unique_email,
        "password": "Test123!",
    }
    response = client.post("/patients", json=payload)
    assert response.status_code == 201
    patient = response.json()
    patient["password"] = payload["password"]

    yield patient

    cleanup_patient(patient["id"])


@pytest.fixture()
def cleanup_patient_by_id():
    created_patient_ids = []

    yield created_patient_ids.append

    for patient_id in created_patient_ids:
        cleanup_patient(patient_id)


@pytest.fixture()
def appointment_payload():
    return {
        "provider": "Dr Py Test",
        "datetime": (datetime.now() + timedelta(days=2)).isoformat(),
        "repeat": "weekly",
        "end_date": (date.today() + timedelta(days=30)).isoformat(),
    }


@pytest.fixture()
def prescription_payload():
    return {
        "medication": "Lexapro",
        "dosage": "5mg",
        "quantity": 1,
        "refill_on": (date.today() + timedelta(days=3)).isoformat(),
        "refill_schedule": "monthly",
    }


def cleanup_patient(patient_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM patients WHERE id = %s;", (patient_id,))

    conn.commit()
    cur.close()
    conn.close()
