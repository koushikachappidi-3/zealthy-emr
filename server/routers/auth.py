from fastapi import APIRouter, HTTPException

from database.patient_queries import get_patient_by_email
from schemas.auth import LoginRequest, LoginResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest):
    patient = get_patient_by_email(request.email)

    if patient is None or patient["password"] != request.password:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {
        "id": patient["id"],
        "name": patient["name"],
        "email": patient["email"],
    }
