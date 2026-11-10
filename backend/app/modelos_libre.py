# Tabla del modo libre (Etapa 8): una fila por cada práctica generada a partir de un PDF.
# Se crea sola al arrancar el servidor (Base.metadata.create_all). El PDF NO se guarda:
# solo las preguntas generadas (con su respuesta correcta, que nunca sale del servidor).
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, JSON
from .base_datos import Base


class SesionLibre(Base):
    __tablename__ = "sesiones_libres"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    titulo = Column(String(100), nullable=False)             # sale del nombre del archivo
    huella_documento = Column(String(64), nullable=False, index=True)   # SHA-256 del texto del PDF
    metodo = Column(String(20), nullable=False)              # "ia" o "local"
    preguntas = Column(JSON, nullable=False)                 # [{enunciado, opciones, respuesta_correcta, explicacion}]
    fecha_creada = Column(DateTime, nullable=False, default=datetime.now)

    completada = Column(Boolean, nullable=False, default=False)
    con_recompensa = Column(Boolean, nullable=False, default=False)
    aciertos = Column(Integer)
    total_preguntas = Column(Integer)
    puntaje = Column(Integer)                                # porcentaje de 0 a 100
    xp_ganada = Column(Integer)
    fecha_completada = Column(DateTime)
