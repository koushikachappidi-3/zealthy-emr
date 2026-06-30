from database.connection import get_connection
from psycopg2.extras import RealDictCursor


def get_medication_options():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT id, name
        FROM medication_options
        ORDER BY name;
    """)

    options = [dict(row) for row in cur.fetchall()]

    cur.close()
    conn.close()

    return options


def get_dosage_options():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT id, value
        FROM dosage_options
        ORDER BY value;
    """)

    options = [dict(row) for row in cur.fetchall()]

    cur.close()
    conn.close()

    return options
