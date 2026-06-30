from database.connection import get_connection


def initialize_database():
    conn = get_connection()
    cur = conn.cursor()

    tables = [
        "patients",
        "appointments",
        "prescriptions",
        "medication_options",
        "dosage_options",
    ]

    for table in tables:
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


if __name__ == "__main__":
    initialize_database()
    print("Database initialized successfully.")
