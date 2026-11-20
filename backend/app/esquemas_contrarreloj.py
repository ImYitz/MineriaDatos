# Esquemas Pydantic del modo contrarreloj. PreguntaContrarreloj NO incluye la respuesta correcta.
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

from .esquemas import LogroPublico


class PreguntaContrarreloj(BaseModel):
    id: int                       # posición dentro de la partida (0, 1, 2...)
    enunciado: str
    opciones: List[str]


class PartidaIniciada(BaseModel):
    id: int
    duracion: int                 # segundos
    preguntas: List[PreguntaContrarreloj]


class RespuestaContrarreloj(BaseModel):
    pregunta_id: int
    respuesta: str


class PartidaReciente(BaseModel):
    fecha: datetime
    aciertos: int
    respondidas: int
    total: int
    termino_todas: bool


class EstadoContrarreloj(BaseModel):
    duracion: int
    preguntas_por_partida: int
    mejor_aciertos: int
    recompensas_hoy: int
    limite_recompensas: int
    aviso_recompensa: Optional[str] = None
    recientes: List[PartidaReciente]


class ResultadoContrarreloj(BaseModel):
    """Lo que responde el servidor al terminar (todo calculado por el servidor)."""
    aciertos: int
    respondidas: int
    total: int
    puntos: int
    puntaje: int
    es_record: bool
    mejor_anterior: int
    termino_todas: bool
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
