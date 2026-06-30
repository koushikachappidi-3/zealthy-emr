from typing import Optional

from pydantic import BaseModel, EmailStr


class PatientCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


class PatientUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None


class PatientResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
