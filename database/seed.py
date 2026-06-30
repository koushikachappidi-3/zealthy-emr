import json
import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
SEED_FILE = BASE_DIR / "seed.json"

load_dotenv(PROJECT_DIR / "server" / ".env")

conn = psycopg2.connect(
    dbname=os.getenv("DATABASE_NAME", "zealthy_emr"),
    user=os.getenv("DATABASE_USER"),
    password=os.getenv("DATABASE_PASSWORD"),
    host=os.getenv("DATABASE_HOST", "localhost"),
    port=os.getenv("DATABASE_PORT", "5432"),
)

cur = conn.cursor()

with open(SEED_FILE, "r") as file:
    data = json.load(file)

for medication in data["medications"]:
    cur.execute(
        "INSERT INTO medication_options (name) VALUES (%s) ON CONFLICT (name) DO NOTHING;",
        (medication,)
    )

for dosage in data["dosages"]:
    cur.execute(
        "INSERT INTO dosage_options (value) VALUES (%s) ON CONFLICT (value) DO NOTHING;",
        (dosage,)
    )

for user in data["users"]:
    cur.execute(
        """
        INSERT INTO patients (id, name, email, password)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (email) DO NOTHING;
        """,
        (user["id"], user["name"], user["email"], user["password"])
    )

    for appointment in user["appointments"]:
        cur.execute(
            """
            INSERT INTO appointments (id, patient_id, provider, datetime, repeat)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING;
            """,
            (
                appointment["id"],
                user["id"],
                appointment["provider"],
                appointment["datetime"],
                appointment["repeat"]
            )
        )

    for prescription in user["prescriptions"]:
        cur.execute(
            """
            INSERT INTO prescriptions (
                id, patient_id, medication, dosage, quantity, refill_on, refill_schedule
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING;
            """,
            (
                prescription["id"],
                user["id"],
                prescription["medication"],
                prescription["dosage"],
                prescription["quantity"],
                prescription["refill_on"],
                prescription["refill_schedule"]
            )
        )

for table in [
    "patients",
    "appointments",
    "prescriptions",
    "medication_options",
    "dosage_options",
]:
    cur.execute(f"""
        SELECT setval(
            pg_get_serial_sequence('{table}', 'id'),
            COALESCE((SELECT MAX(id) FROM {table}), 1),
            true
        );
    """)

conn.commit()
cur.close()
conn.close()

print("Database seeded successfully.")
