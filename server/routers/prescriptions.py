from fastapi import APIRouter, HTTPException, status

from database.patient_queries import get_patient_by_id
from database.prescription_queries import (
    create_prescription,
    delete_prescription,
    get_prescription_by_id,
    get_prescriptions_by_patient_id,
    update_prescription,
)
from schemas.prescription import (
    PrescriptionCreate,
    PrescriptionResponse,
    PrescriptionUpdate,
)

router = APIRouter(tags=["Prescriptions"])


@router.get(
    "/patients/{patient_id}/prescriptions",
    response_model=list[PrescriptionResponse],
)
def list_patient_prescriptions(patient_id: int):
    patient = get_patient_by_id(patient_id)

    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")

    return get_prescriptions_by_patient_id(patient_id)


@router.post(
    "/patients/{patient_id}/prescriptions",
    response_model=PrescriptionResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_patient_prescription(patient_id: int, prescription: PrescriptionCreate):
    patient = get_patient_by_id(patient_id)

    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")

    return create_prescription(
        patient_id,
        prescription.medication,
        prescription.dosage,
        prescription.quantity,
        prescription.refill_on,
        prescription.refill_schedule,
    )


@router.put(
    "/prescriptions/{prescription_id}",
    response_model=PrescriptionResponse,
)
def edit_prescription(prescription_id: int, prescription: PrescriptionUpdate):
    existing = get_prescription_by_id(prescription_id)

    if existing is None:
        raise HTTPException(status_code=404, detail="Prescription not found")

    return update_prescription(
        prescription_id,
        prescription.medication,
        prescription.dosage,
        prescription.quantity,
        prescription.refill_on,
        prescription.refill_schedule,
    )


@router.delete(
    "/prescriptions/{prescription_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_prescription(prescription_id: int):
    prescription = delete_prescription(prescription_id)

    if prescription is None:
        raise HTTPException(status_code=404, detail="Prescription not found")

    return None
