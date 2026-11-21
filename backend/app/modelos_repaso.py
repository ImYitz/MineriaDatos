# Tabla del repaso de errores (Etapa 12): una fila por cada ejercicio que el usuario ha fallado.
# Se crea sola al arrancar el servidor (Base.metadata.create_all); no hace falta tocar la base de datos.
from datetime import datetime
from sqlalchemy import Column, Integer, Boolean, ForeignKey, DateTime
from .base_datos import Base


class ErrorEjercicio(Base):
    """Un ejercicio fallado por un usuario, con su estado de repaso (cajas tipo Leitner)."""
    __tablename__ = "errores_ejercicio"

    usuario_id = Column(Integer, ForeignKey("usuarios.id"), primary_key=True)
    ejercicio_id = Column(Integer, ForeignKey("ejercicios.id"), primary_key=True)
    caja = Column(Integer, nullable=False, default=0)         # aciertos seguidos en el repaso
    fallos = Column(Integer, nullable=False, default=1)       # veces que lo ha fallado en total
    dominado = Column(Boolean, nullable=False, default=False)
    proxima_revision = Column(DateTime, nullable=False, default=datetime.now)
    fecha_ultimo_fallo = Column(DateTime, nullable=False, default=datetime.now)
