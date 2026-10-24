# Conexión a MySQL con SQLAlchemy.
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Lee las variables del archivo .env
load_dotenv()
URL_BASE_DATOS = os.getenv("URL_BASE_DATOS")

# El "motor" es la conexión real con MySQL.
# pool_pre_ping evita errores si MySQL cierra una conexión inactiva.
motor = create_engine(URL_BASE_DATOS, pool_pre_ping=True)

# Cada petición a la API usará su propia "sesión" (una conversación con la BD).
SesionLocal = sessionmaker(bind=motor, autoflush=False)

# Todas las tablas heredan de esta clase.
Base = declarative_base()


def obtener_sesion():
    """Abre una sesión para cada petición y la cierra al terminar."""
    sesion = SesionLocal()
    try:
        yield sesion
    finally:
        sesion.close()
