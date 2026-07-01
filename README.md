# Zealthy EMR Mini Electronic Medical Record System

## Overview

Zealthy EMR is a full-stack mini Electronic Medical Record system built for the Zealthy full-stack engineering exercise. It includes a React/Vite frontend, FastAPI backend, PostgreSQL database, an Admin EMR, and a Patient Portal.

Administrators can manage patients, appointments, and prescriptions. Patients can log in with seeded credentials or admin-created credentials to view dashboard summaries and drill down into appointments and prescriptions.

## Highlights

- React + Vite frontend
- FastAPI REST API
- PostgreSQL database
- Admin EMR and Patient Portal
- Patient, appointment, and prescription management
- 33 automated backend tests
- 93% backend code coverage

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Demo Credentials](#demo-credentials)
- [Folder Structure](#folder-structure)
- [Database Setup](#database-setup)
- [Backend Setup](#backend-setup)
- [Frontend Setup](#frontend-setup)
- [Running the Application](#running-the-application)
- [Running Tests](#running-tests)
- [API Endpoints](#api-endpoints)
- [Deployment](#deployment)
- [Screenshots](#screenshots)
- [Future Improvements](#future-improvements)
- [Author](#author)

## Features

- Admin EMR at `/admin`
  - Patient table with at-a-glance appointment and prescription summary data
  - Patient create and update flows
  - Appointment create, read, update, and delete flows
  - Prescription create, read, update, and delete flows
  - Medication and dosage option lists seeded from JSON data
- Patient Portal at `/`
  - Patient login with seeded or admin-created credentials
  - Dashboard with patient info, next-7-day appointments, and next-7-day refills
  - Appointments tab with upcoming schedule through 3 months
  - Prescriptions tab with all prescriptions
- Backend API test suite with pytest and coverage

## Tech Stack

- Backend: Python, FastAPI, Pydantic, psycopg2, PostgreSQL
- Frontend: React, Vite, CSS
- Testing: pytest, pytest-cov, FastAPI TestClient

## Architecture

```text
React + Vite Frontend
↓
FastAPI Backend
↓
PostgreSQL Database
```

- `/` serves the Patient Portal.
- `/admin` serves the Admin EMR.
- `/docs` exposes Swagger API docs.

## Demo Credentials

Patient Portal seeded account:

```text
Email: mark@some-email-provider.net
Password: Password123!
```

Additional patients can be created from the Admin EMR and can immediately log into the Patient Portal using the credentials entered during creation.

Admin EMR:

```text
No authentication required for this take-home assignment.
Local URL: https://zealthy-emr-9u7d.onrender.com/admin
```

## Folder Structure

```text
.
├── client/
│   ├── src/
│   ├── index.html
│   ├── package.json
│   ├── package-lock.json
│   └── vite.config.js
├── database/
│   ├── schema.sql
│   ├── seed.py
│   └── seed.json
├── screenshots/
└── server/
    ├── config/
    ├── database/
    ├── routers/
    ├── schemas/
    ├── tests/
    ├── main.py
    ├── requirements.txt
    ├── pytest.ini
    └── .coveragerc
```

## Database Setup

Create a local PostgreSQL database, then apply the schema and seed data.

```bash
createdb zealthy_emr
psql zealthy_emr < database/schema.sql
python database/seed.py
```

The seed data includes sample patient credentials:

```text
mark@some-email-provider.net / Password123!
lisa@some-email-provider.net / Password123!
```

## Backend Setup

Create a `server/.env` file with your PostgreSQL connection details:

```env
DATABASE_NAME=zealthy_emr
DATABASE_USER=your_postgres_username
DATABASE_PASSWORD=your_postgres_password
DATABASE_HOST=localhost
DATABASE_PORT=5432
```

> **Note:** For local development, use your local PostgreSQL credentials.  
> For deployment (e.g., Render), configure the database connection using the environment variables provided by your hosting platform.

Install dependencies:

```bash
cd server
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Frontend Setup

```bash
cd client
npm install
npm run build
```

The FastAPI app serves the built React files from `client/dist`.

## Running the Application

```bash
cd server
source venv/bin/activate
uvicorn main:app --reload --port 8001
```

Open:

- Patient Portal: `http://localhost:8001/`
- Admin EMR: `http://localhost:8001/admin`
- Swagger API docs: `http://localhost:8001/docs`
- API health check: `http://localhost:8001/health`

## Running Tests

The project includes a comprehensive backend test suite built with **pytest**.

### Run all tests

```bash
cd server
source venv/bin/activate
pytest -v
```

### Run tests with code coverage

```bash
pytest -v --cov=. --cov-report=term-missing
```

### Current Test Status

- ✅ 33 automated backend tests
- ✅ 93% backend code coverage

The test suite includes:

- Authentication tests
- Patient CRUD tests
- Appointment CRUD tests
- Prescription CRUD tests
- Dashboard/Summary endpoint tests
- Medication and dosage option endpoint tests
- Happy-path and negative test cases

## API Endpoints

### Auth

- `POST /auth/login`

### Patients

- `GET /patients`
- `GET /patients/{patient_id}`
- `POST /patients`
- `PUT /patients/{patient_id}`
- `GET /patients/{patient_id}/dashboard`
- `GET /patients/{patient_id}/summary`

### Appointments

- `GET /patients/{patient_id}/appointments`
- `GET /patients/{patient_id}/appointments/upcoming`
- `POST /patients/{patient_id}/appointments`
- `PUT /appointments/{appointment_id}`
- `DELETE /appointments/{appointment_id}`

### Prescriptions

- `GET /patients/{patient_id}/prescriptions`
- `POST /patients/{patient_id}/prescriptions`
- `PUT /prescriptions/{prescription_id}`
- `DELETE /prescriptions/{prescription_id}`

### Options

- `GET /options/medications`
- `GET /options/dosages`

## Deployment

Recommended deployment shape:

1. Provision a PostgreSQL database.
2. Configure backend environment variables for the deployed database.
3. Build the React frontend with `npm run build`.
4. Deploy the FastAPI server so it serves both API routes and the React build.
5. Run schema and seed setup against the production database.

Potential hosts include Render, Railway, Fly.io, Heroku, AWS, or Azure.

## Demo URLs

### Live Application

- **Patient Portal:** https://zealthy-emr-9u7d.onrender.com/
- **Admin EMR:** https://zealthy-emr-9u7d.onrender.com/admin

### Source Code

- **GitHub Repository:** : https://github.com/koushikachappidi-3/zealthy-emr


## Screenshots

### 1. Patient Login

> **Description**
>
> Patient login screen where seeded or admin-created patients authenticate using their email and password.

<img width="1010" height="557" alt="image" src="https://github.com/user-attachments/assets/c88bd3e3-d497-465d-a24b-41ebe93e5ac9" />



---

### 2. Patient Dashboard

> **Description**
>
> Patient dashboard showing basic patient information, appointments in the next 7 days, and medication refills in the next 7 days.
<img width="994" height="547" alt="image" src="https://github.com/user-attachments/assets/6ef30946-1748-4a59-a175-a1cf6969e483" />





---

### 3. Patient Appointments

> **Description**
>
> Patient Portal Appointments tab showing the full upcoming appointment schedule up to 3 months.

<img width="997" height="555" alt="image" src="https://github.com/user-attachments/assets/6c6e069b-6d95-4c3a-8918-5efb6cafb389" />



---

### 4. Patient Prescriptions

> **Description**
>
> Patient Portal Prescriptions tab showing all prescriptions for the logged-in patient.


<img width="1003" height="545" alt="image" src="https://github.com/user-attachments/assets/3c342bb2-ea58-44dd-b7f3-b53cfa1f988c" />



---

### 5. Admin Dashboard

> **Description**
>
> Admin EMR dashboard showing the patient table with at-a-glance appointment and prescription data.

<img width="1002" height="553" alt="image" src="https://github.com/user-attachments/assets/eee9373e-84fa-4b58-b609-e7523bb55618" />



---

### 6. Patient Management

> **Description**
>
> Admin selected-patient workspace showing the Patient Info tab and update patient form.

<img width="1006" height="550" alt="image" src="https://github.com/user-attachments/assets/94502411-4559-43f6-9cdb-c8a86576d00a" />
<img width="1005" height="542" alt="image" src="https://github.com/user-attachments/assets/7740beec-19ed-46a8-ad5a-b0ae9501b589" />





---

### 7. Appointment Management

> **Description**
>
> Admin selected-patient Appointments tab showing appointment list and create, edit, and delete controls.

<img width="1007" height="559" alt="image" src="https://github.com/user-attachments/assets/39389044-71b2-4f75-9435-e3ef223dc5b1" />



---

### 8. Prescription Management

> **Description**
>
> Admin selected-patient Prescriptions tab showing prescription list and create, edit, and delete controls.
<img width="997" height="553" alt="image" src="https://github.com/user-attachments/assets/bdb28521-957f-4d36-acfb-71e04808aef5" />



---

### 9. FastAPI Swagger API Docs

> **Description**
>
> FastAPI Swagger documentation at `/docs` showing the available backend API endpoints.

<img width="1280" height="2701" alt="image" src="https://github.com/user-attachments/assets/f3ce57bb-42d1-4eab-8555-f1d8e1eb29b4" />


---

### 10. Backend Test Suite / Coverage

> **Description**
>
> Terminal output showing pytest coverage with 33 passing tests and 93% backend coverage.

<img width="1280" height="1328" alt="image" src="https://github.com/user-attachments/assets/997eac04-0155-4403-906d-ad0eed8fe77e" />


## Future Improvements

- bcrypt password hashing
- JWT authentication
- RBAC for admin
- audit logging
- HTTPS
- CI/CD
- pagination/filtering

## Author

Koushikach
