from datetime import date
from typing import Optional

from pydantic import BaseModel


class PrescriptionCreate(BaseModel):
    medication: str
    dosage: str
    quantity: int
    refill_on: date
    refill_schedule: str


class PrescriptionUpdate(BaseModel):
    medication: Optional[str] = None
    dosage: Optional[str] = None
    quantity: Optional[int] = None
    refill_on: Optional[date] = None
    refill_schedule: Optional[str] = None


class PrescriptionResponse(BaseModel):
    id: int
    patient_id: int
    medication: str
    dosage: str
    quantity: int
    refill_on: date
    refill_schedule: str
