# Esquemas Pydantic de los laboratorios (qué datos entran y salen de la API).
# Fíjate en que PreguntaLab NO incluye la respuesta correcta.
from typing import List, Optional
from pydantic import BaseModel

from .esquemas import LogroPublico


class PreguntaLab(BaseModel):
    id: int
    enunciado: str
    opciones: List[str]


class LaboratorioResumen(BaseModel):
    codigo: str
    titulo: str
    descripcion: str
    icono: str
    xp_recompensa: int
    veces_completado: int
    mejor_puntaje: Optional[int] = None    # None = todavía no lo ha completado


class LaboratorioDetalle(LaboratorioResumen):
    instrucciones: str
    preguntas: List[PreguntaLab]


class RespuestaLab(BaseModel):
    pregunta_id: int
    respuesta: str


class CompletarLaboratorio(BaseModel):
    respuestas: List[RespuestaLab]


class RevisionPregunta(BaseModel):
    pregunta_id: int
    correcta: bool
    respuesta_correcta: str
    explicacion: str


class ResultadoLaboratorio(BaseModel):
    """Lo que responde el servidor (todo calculado por el servidor)."""
    aciertos: int
    total: int
    puntaje: int
    es_primera_vez: bool
    xp_ganada: int
    xp_total: int
    nivel: int
    subio_de_nivel: bool
    monedas_ganadas: int
    monedas_total: int
    racha_actual: int
    logros_nuevos: List[LogroPublico]
    revision: List[RevisionPregunta]
