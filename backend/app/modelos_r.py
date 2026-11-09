# Tabla del progreso en las lecciones de R (Etapa 7).
# Está en un archivo aparte para no tocar modelos.py. La tabla se crea sola al arrancar
# el servidor (Base.metadata.create_all), no hace falta reiniciar la base de datos.
from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from .base_datos import Base


class ProgresoR(Base):
    """Un registro por cada vez que un usuario APRUEBA la práctica de una lección de R."""
    __tablename__ = "progreso_r"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    leccion = Column(String(50), nullable=False)          # código de la lección (p. ej. "r_basico")
    aciertos = Column(Integer, nullable=False)            # comprobaciones correctas
    total_comprobaciones = Column(Integer, nullable=False)
    puntaje = Column(Integer, nullable=False)             # porcentaje de 0 a 100
    xp_ganada = Column(Integer, nullable=False)
    fecha_completada = Column(DateTime, nullable=False, default=datetime.now)
