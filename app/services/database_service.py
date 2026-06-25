import mysql.connector
from app.config import Config
import io


def get_connection():
    return mysql.connector.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME
    )
    
def user_owns_business(user_id, business_id):

    conn = get_connection()

    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT id
        FROM businesses
        WHERE id=%s
        AND user_id=%s
        """,
        (business_id, user_id)
    )

    business = cursor.fetchone()

    cursor.close()
    conn.close()

    return business is not None