from datetime import date, timedelta

from database.connection import get_connection
from psycopg2.extras import RealDictCursor


def get_prescriptions_by_patient_id(patient_id: int):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT id, patient_id, medication, dosage, quantity, refill_on, refill_schedule
        FROM prescriptions
        WHERE patient_id = %s
        ORDER BY refill_on;
    """, (patient_id,))

    prescriptions = [dict(row) for row in cur.fetchall()]

    cur.close()
    conn.close()

    return prescriptions


def get_prescription_by_id(prescription_id: int):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT id, patient_id, medication, dosage, quantity, refill_on, refill_schedule
        FROM prescriptions
        WHERE id = %s;
    """, (prescription_id,))

    prescription = cur.fetchone()

    cur.close()
    conn.close()

    return dict(prescription) if prescription else None


def create_prescription(
    patient_id: int,
    medication: str,
    dosage: str,
    quantity: int,
    refill_on: date,
    refill_schedule: str,
):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        INSERT INTO prescriptions (
            patient_id, medication, dosage, quantity, refill_on, refill_schedule
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id, patient_id, medication, dosage, quantity, refill_on, refill_schedule;
    """, (patient_id, medication, dosage, quantity, refill_on, refill_schedule))

    prescription = dict(cur.fetchone())

    conn.commit()

    cur.close()
    conn.close()

    return prescription


def update_prescription(
    prescription_id: int,
    medication: str | None,
    dosage: str | None,
    quantity: int | None,
    refill_on: date | None,
    refill_schedule: str | None,
):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        UPDATE prescriptions
        SET
            medication = COALESCE(%s, medication),
            dosage = COALESCE(%s, dosage),
            quantity = COALESCE(%s, quantity),
            refill_on = COALESCE(%s, refill_on),
            refill_schedule = COALESCE(%s, refill_schedule)
        WHERE id = %s
        RETURNING id, patient_id, medication, dosage, quantity, refill_on, refill_schedule;
    """, (
        medication,
        dosage,
        quantity,
        refill_on,
        refill_schedule,
        prescription_id,
    ))

    prescription = cur.fetchone()

    conn.commit()

    cur.close()
    conn.close()

    return dict(prescription) if prescription else None


def delete_prescription(prescription_id: int):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        DELETE FROM prescriptions
        WHERE id = %s
        RETURNING id;
    """, (prescription_id,))

    prescription = cur.fetchone()

    conn.commit()

    cur.close()
    conn.close()

    return dict(prescription) if prescription else None


def get_refills_due(patient_id: int, days: int = 7):
    today = date.today()
    end_date = today + timedelta(days=days)

    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT id, patient_id, medication, dosage, quantity, refill_on, refill_schedule
        FROM prescriptions
        WHERE patient_id = %s
            AND refill_on BETWEEN %s AND %s
        ORDER BY refill_on;
    """, (patient_id, today, end_date))

    prescriptions = [dict(row) for row in cur.fetchall()]

    cur.close()
    conn.close()

    return prescriptions
