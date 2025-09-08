import os
import psycopg
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:123@localhost:5432/tarea1")

@contextmanager
def get_conn():
    """
    Context manager para obtener conexión a la base de datos.
    
    Yields:
        psycopg.Connection: Conexión a la base de datos PostgreSQL.
        
    Note:
        La conexión se cierra automáticamente al salir del contexto.
        Las transacciones se confirman automáticamente si no hay errores.
    """
    with psycopg.connect(DATABASE_URL, autocommit=False) as conn:
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
