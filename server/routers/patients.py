from fastapi import APIRouter, HTTPException, status

from database.patient_queries import (
    create_patient,
    get_all_patients,
    get_patient_by_email,
    get_patient_by_id,
    update_patient,
)
from database.appointment_queries import get_upcoming_appointments
from database.prescription_queries import get_refills_due
from schemas.dashboard import PatientDashboardResponse
from schemas.patient import PatientCreate, PatientResponse, PatientUpdate

router = APIRouter(
    prefix="/patients",
    tags=["Patients"]
)


@router.get("", response_model=list[PatientResponse])
def list_patients():
    return get_all_patients()


@router.get("/{patient_id}", response_model=PatientResponse)
def retrieve_patient(patient_id: int):
    patient = get_patient_by_id(patient_id)

    if patient is None:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    return patient


@router.get("/{patient_id}/dashboard", response_model=PatientDashboardResponse)
def retrieve_patient_dashboard(patient_id: int):
    return _build_patient_summary(patient_id)


@router.get("/{patient_id}/summary", response_model=PatientDashboardResponse)
def retrieve_patient_summary(patient_id: int):
    return _build_patient_summary(patient_id)


def _build_patient_summary(patient_id: int):
    patient = get_patient_by_id(patient_id)

    if patient is None:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    return {
        **patient,
        "upcoming_appointments": get_upcoming_appointments(patient_id, days=7),
        "refills_due": get_refills_due(patient_id, days=7),
    }


@router.post(
    "",
    response_model=PatientResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_patient(patient: PatientCreate):

    existing = get_patient_by_email(patient.email)

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Email already exists"
        )

    return create_patient(
        patient.name,
        patient.email,
        patient.password
    )


@router.put("/{patient_id}", response_model=PatientResponse)
def edit_patient(
    patient_id: int,
    patient: PatientUpdate,
):

    existing = get_patient_by_id(patient_id)

    if existing is None:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    return update_patient(
        patient_id,
        patient.name,
        patient.email,
        patient.password,
    )
