# Tabla del progreso en los laboratorios interactivos (Etapa 6).
# Está en un archivo aparte para no tocar modelos.py. La tabla se crea sola al arrancar
# el servidor (Base.metadata.create_all), no hace falta reiniciar la base de datos.
from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from .base_datos import Base


class ProgresoLaboratorio(Base):
    """Un registro por cada vez que un usuario termina un laboratorio."""
    __tablename__ = "progreso_laboratorios"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    laboratorio = Column(String(50), nullable=False)      # código del laboratorio (p. ej. "kmeans")
    aciertos = Column(Integer, nullable=False)
    total_preguntas = Column(Integer, nullable=False)
    puntaje = Column(Integer, nullable=False)             # porcentaje de 0 a 100
    xp_ganada = Column(Integer, nullable=False)
    fecha_completada = Column(DateTime, nullable=False, default=datetime.now)
