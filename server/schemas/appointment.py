from datetime import date as Date, datetime as DateTime
from typing import Optional

from pydantic import BaseModel


class AppointmentCreate(BaseModel):
    provider: str
    datetime: DateTime
    repeat: str
    end_date: Optional[Date] = None


class AppointmentUpdate(BaseModel):
    provider: Optional[str] = None
    datetime: Optional[DateTime] = None
    repeat: Optional[str] = None
    end_date: Optional[Date] = None


class AppointmentResponse(BaseModel):
    id: int
    patient_id: int
    provider: str
    datetime: DateTime
    repeat: str
    end_date: Optional[Date] = None


class AppointmentOccurrence(BaseModel):
    appointment_id: int
    patient_id: int
    provider: str
    datetime: DateTime
    repeat: str
    end_date: Optional[Date] = None
