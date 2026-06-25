from app.services.database_service import get_connection


def execute_query(query, params=None, fetchone=False):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(query, params)

    result = None

    if fetchone:
        result = cursor.fetchone()
    else:
        result = cursor.fetchall()

    conn.commit()

    cursor.close()
    conn.close()

    return result