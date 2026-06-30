from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from routers import appointments, auth, options, patients, prescriptions

BASE_DIR = Path(__file__).resolve().parent.parent
CLIENT_DIR = BASE_DIR / "client"
CLIENT_DIST_DIR = CLIENT_DIR / "dist"
CLIENT_INDEX = CLIENT_DIST_DIR / "index.html"

app = FastAPI(
    title="Zealthy EMR API"
)

app.mount("/assets", StaticFiles(directory=CLIENT_DIST_DIR / "assets"), name="assets")

app.include_router(auth.router)
app.include_router(patients.router)
app.include_router(appointments.router)
app.include_router(prescriptions.router)
app.include_router(options.router)


@app.get("/")
def patient_portal():
    return FileResponse(CLIENT_INDEX)


@app.get("/admin")
def admin_portal():
    return FileResponse(CLIENT_INDEX)


@app.get("/health")
def health_check():
    return {"message": "Zealthy EMR API is running"}
