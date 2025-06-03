import os
import psycopg2
from contextlib import contextmanager


def _dsn() -> str:
    """Build a libpq DSN from env-vars (falls back to docker-compose defaults)."""
    return (
        f"dbname={os.getenv('PGDATABASE', 'churn_db')} "
        f"user={os.getenv('PGUSER', 'churn')} "
        f"password={os.getenv('PGPASSWORD', 'churn_pwd')} "
        f"host={os.getenv('PGHOST', 'db')} "
        f"port={os.getenv('PGPORT', 5432)}"
    )


@contextmanager
def get_conn():
    """Yield a psycopg2 connection with auto-commit."""
    conn = psycopg2.connect(_dsn())
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()
