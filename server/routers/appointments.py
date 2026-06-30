from fastapi import APIRouter, HTTPException, status

from database.appointment_queries import (
    create_appointment,
    delete_appointment,
    get_appointment_by_id,
    get_appointments_by_patient_id,
    get_upcoming_appointments,
    update_appointment,
)
from database.patient_queries import get_patient_by_id
from schemas.appointment import (
    AppointmentCreate,
    AppointmentOccurrence,
    AppointmentResponse,
    AppointmentUpdate,
)

router = APIRouter(tags=["Appointments"])


@router.get(
    "/patients/{patient_id}/appointments",
    response_model=list[AppointmentResponse],
)
def list_patient_appointments(patient_id: int):
    patient = get_patient_by_id(patient_id)

    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")

    return get_appointments_by_patient_id(patient_id)


@router.get(
    "/patients/{patient_id}/appointments/upcoming",
    response_model=list[AppointmentOccurrence],
)
def list_patient_upcoming_appointments(patient_id: int):
    patient = get_patient_by_id(patient_id)

    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")

    return get_upcoming_appointments(patient_id, days=90)


@router.post(
    "/patients/{patient_id}/appointments",
    response_model=AppointmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_patient_appointment(patient_id: int, appointment: AppointmentCreate):
    patient = get_patient_by_id(patient_id)

    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")

    return create_appointment(
        patient_id,
        appointment.provider,
        appointment.datetime,
        appointment.repeat,
        appointment.end_date,
    )


@router.put(
    "/appointments/{appointment_id}",
    response_model=AppointmentResponse,
)
def edit_appointment(appointment_id: int, appointment: AppointmentUpdate):
    existing = get_appointment_by_id(appointment_id)

    if existing is None:
        raise HTTPException(status_code=404, detail="Appointment not found")

    update_data = appointment.model_dump(exclude_unset=True)

    return update_appointment(
        appointment_id,
        update_data.get("provider"),
        update_data.get("datetime"),
        update_data.get("repeat"),
        update_data.get("end_date", existing["end_date"]),
    )


@router.delete("/appointments/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_appointment(appointment_id: int):
    appointment = delete_appointment(appointment_id)

    if appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")

    return None
