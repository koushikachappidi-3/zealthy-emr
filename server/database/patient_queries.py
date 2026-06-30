from database.connection import get_connection
from psycopg2.extras import RealDictCursor


def get_all_patients():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT id, name, email
        FROM patients
        ORDER BY id;
    """)

    patients = [dict(row) for row in cur.fetchall()]

    cur.close()
    conn.close()

    return patients

def get_patient_by_email(email: str):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT id, name, email, password
        FROM patients
        WHERE email = %s;
    """, (email,))

    patient = cur.fetchone()

    cur.close()
    conn.close()

    return dict(patient) if patient else None

def get_patient_by_id(patient_id: int):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT id, name, email
        FROM patients
        WHERE id = %s;
    """, (patient_id,))

    patient = cur.fetchone()

    cur.close()
    conn.close()

    return dict(patient) if patient else None

def create_patient(name: str, email: str, password: str):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        INSERT INTO patients (name, email, password)
        VALUES (%s, %s, %s)
        RETURNING id, name, email;
    """, (name, email, password))

    patient = dict(cur.fetchone())

    conn.commit()

    cur.close()
    conn.close()

    return patient

def update_patient(patient_id: int, name: str, email: str, password: str):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        UPDATE patients
        SET
            name = COALESCE(%s, name),
            email = COALESCE(%s, email),
            password = COALESCE(%s, password)
        WHERE id = %s
        RETURNING id, name, email;
    """, (name, email, password, patient_id))

    patient = cur.fetchone()

    conn.commit()

    cur.close()
    conn.close()

    return dict(patient) if patient else None
