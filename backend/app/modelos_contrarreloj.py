# Tabla del modo contrarreloj (Etapa 11): una fila por cada partida de 60 segundos.
# Se crea sola al arrancar el servidor (Base.metadata.create_all); no hace falta tocar la base de datos.
from datetime import datetime
from sqlalchemy import Column, Integer, Boolean, ForeignKey, DateTime, JSON
from .base_datos import Base


class PartidaContrarreloj(Base):
    __tablename__ = "partidas_contrarreloj"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    fecha_inicio = Column(DateTime, nullable=False, default=datetime.now)   # el servidor controla el tiempo
    preguntas = Column(JSON, nullable=False)       # ids de los ejercicios, en el orden en que se muestran
    respuestas = Column(JSON, nullable=False)      # [{ejercicio_id, correcta}] en el orden en que se respondieron

    completada = Column(Boolean, nullable=False, default=False)
    con_recompensa = Column(Boolean, nullable=False, default=False)
    aciertos = Column(Integer)
    respondidas = Column(Integer)
    total_preguntas = Column(Integer)
    puntaje = Column(Integer)                      # precisión (0 a 100) sobre lo respondido
    termino_todas = Column(Boolean, nullable=False, default=False)   # respondió todas dentro del tiempo
    xp_ganada = Column(Integer)
    fecha_completada = Column(DateTime)
