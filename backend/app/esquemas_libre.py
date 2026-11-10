# Esquemas Pydantic del modo libre. PreguntaLibre NO incluye la respuesta correcta.
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

from .esquemas import LogroPublico
from .esquemas_laboratorios import RevisionPregunta


class PreguntaLibre(BaseModel):
    id: int
    enunciado: str
    opciones: List[str]


class SesionLibreResumen(BaseModel):
    id: int
    titulo: str
    metodo: str
    fecha_creada: datetime
    completada: bool
    puntaje: Optional[int] = None


class SesionLibreDetalle(SesionLibreResumen):
    preguntas: List[PreguntaLibre]
    aviso_recompensa: Optional[str] = None   # si no habrá recompensa, el motivo


class RespuestaLibre(BaseModel):
    pregunta_id: int
    respuesta: str


class CompletarLibre(BaseModel):
    respuestas: List[RespuestaLibre]


class ResultadoLibre(BaseModel):
    """Lo que responde el servidor (todo calculado por el servidor)."""
    aciertos: int
    total: int
    puntaje: int
    con_recompensa: bool
    motivo_sin_recompensa: Optional[str] = None
    xp_ganada: int
    xp_total: int
    nivel: int
    subio_de_nivel: bool
    monedas_ganadas: int
    monedas_total: int
    racha_actual: int
    logros_nuevos: List[LogroPublico]
    revision: List[RevisionPregunta]
