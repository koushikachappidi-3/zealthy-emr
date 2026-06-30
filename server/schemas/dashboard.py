from schemas.appointment import AppointmentOccurrence
from schemas.patient import PatientResponse
from schemas.prescription import PrescriptionResponse


class PatientDashboardResponse(PatientResponse):
    upcoming_appointments: list[AppointmentOccurrence]
    refills_due: list[PrescriptionResponse]
