from fastapi import APIRouter

from database.option_queries import get_dosage_options, get_medication_options

router = APIRouter(prefix="/options", tags=["Options"])


@router.get("/medications")
def list_medication_options():
    return get_medication_options()


@router.get("/dosages")
def list_dosage_options():
    return get_dosage_options()
