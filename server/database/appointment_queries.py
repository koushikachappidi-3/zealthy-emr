from datetime import date, datetime, timedelta

from database.connection import get_connection
from psycopg2.extras import RealDictCursor


def _add_month(value: datetime) -> datetime:
    month = value.month + 1
    year = value.year

    if month > 12:
        month = 1
        year += 1

    days_by_month = {
        1: 31,
        2: 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28,
        3: 31,
        4: 30,
        5: 31,
        6: 30,
        7: 31,
        8: 31,
        9: 30,
        10: 31,
        11: 30,
        12: 31,
    }
    day = min(value.day, days_by_month[month])

    return value.replace(year=year, month=month, day=day)


def _next_occurrence(value: datetime, repeat: str) -> datetime | None:
    normalized_repeat = repeat.lower()

    if normalized_repeat in {"none", "no repeat", "once"}:
        return None

    if normalized_repeat == "weekly":
        return value + timedelta(weeks=1)

    if normalized_repeat == "monthly":
        return _add_month(value)

    return None


def expand_appointment_occurrences(
    appointments: list[dict],
    start_at: datetime,
    end_at: datetime,
):
    occurrences = []

    for appointment in appointments:
        current_datetime = appointment["datetime"]
        end_date = appointment["end_date"]
        final_datetime = end_at

        if end_date is not None:
            final_datetime = min(
                final_datetime,
                datetime.combine(end_date, datetime.max.time()),
            )

        while current_datetime < start_at:
            next_datetime = _next_occurrence(current_datetime, appointment["repeat"])

            if next_datetime is None:
                break

            current_datetime = next_datetime

        while start_at <= current_datetime <= final_datetime:
            occurrence = dict(appointment)
            occurrence["appointment_id"] = appointment["id"]
            occurrence["datetime"] = current_datetime
            occurrences.append(occurrence)

            next_datetime = _next_occurrence(current_datetime, appointment["repeat"])

            if next_datetime is None:
                break

            current_datetime = next_datetime

    return sorted(occurrences, key=lambda item: item["datetime"])


def get_appointments_by_patient_id(patient_id: int):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT id, patient_id, provider, datetime, repeat, end_date
        FROM appointments
        WHERE patient_id = %s
        ORDER BY datetime;
    """, (patient_id,))

    appointments = [dict(row) for row in cur.fetchall()]

    cur.close()
    conn.close()

    return appointments


def get_appointment_by_id(appointment_id: int):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT id, patient_id, provider, datetime, repeat, end_date
        FROM appointments
        WHERE id = %s;
    """, (appointment_id,))

    appointment = cur.fetchone()

    cur.close()
    conn.close()

    return dict(appointment) if appointment else None


def create_appointment(
    patient_id: int,
    provider: str,
    appointment_datetime: datetime,
    repeat: str,
    end_date: date | None,
):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        INSERT INTO appointments (patient_id, provider, datetime, repeat, end_date)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id, patient_id, provider, datetime, repeat, end_date;
    """, (patient_id, provider, appointment_datetime, repeat, end_date))

    appointment = dict(cur.fetchone())

    conn.commit()

    cur.close()
    conn.close()

    return appointment


def update_appointment(
    appointment_id: int,
    provider: str | None,
    appointment_datetime: datetime | None,
    repeat: str | None,
    end_date: date | None,
):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        UPDATE appointments
        SET
            provider = COALESCE(%s, provider),
            datetime = COALESCE(%s, datetime),
            repeat = COALESCE(%s, repeat),
            end_date = %s
        WHERE id = %s
        RETURNING id, patient_id, provider, datetime, repeat, end_date;
    """, (provider, appointment_datetime, repeat, end_date, appointment_id))

    appointment = cur.fetchone()

    conn.commit()

    cur.close()
    conn.close()

    return dict(appointment) if appointment else None


def delete_appointment(appointment_id: int):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        DELETE FROM appointments
        WHERE id = %s
        RETURNING id;
    """, (appointment_id,))

    appointment = cur.fetchone()

    conn.commit()

    cur.close()
    conn.close()

    return dict(appointment) if appointment else None


def get_upcoming_appointments(patient_id: int, days: int = 90):
    start_at = datetime.now()
    end_at = start_at + timedelta(days=days)
    appointments = get_appointments_by_patient_id(patient_id)

    return expand_appointment_occurrences(appointments, start_at, end_at)
