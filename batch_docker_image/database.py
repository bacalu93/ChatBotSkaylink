import os
import pg8000

def setup_database_connection(secret):
    """Establish a connection to the PostgreSQL database."""
    return pg8000.connect(
        database=os.getenv('DB_NAME'),
        host=os.getenv('DB_HOST'),
        port=int(os.getenv('DB_PORT')),
        user=secret['username'],
        password=secret['password'],
    )

def create_database_schema(conn):
    """Create necessary database schema."""
    with conn.cursor() as cursor:
        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS items(
                id uuid PRIMARY KEY,
                chunks TEXT,
                metadata JSON,
                embedding VECTOR(1024),
                page_number VARCHAR(255)
            );
        """)
    conn.commit()