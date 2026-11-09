# Esquemas Pydantic de las lecciones de R (qué datos entran y salen de la API).
# Fíjate en que ComprobacionPublica NO incluye el valor esperado ni la pista.
from typing import List, Optional
from pydantic import BaseModel, field_validator

from .esquemas import LogroPublico


class SeccionTeoria(BaseModel):
    titulo: str
    texto: str
    codigo: str


class ComprobacionPublica(BaseModel):
    id: int
    expresion: str        # expresión de R que evalúa el navegador después del código del estudiante
    descripcion: str


class TareaPublica(BaseModel):
    id: int
    enunciado: str
    plantilla: str
    comprobaciones: List[ComprobacionPublica]


class LeccionRResumen(BaseModel):
    codigo: str
    titulo: str
    descripcion: str
    icono: str
    xp_recompensa: int
    veces_completada: int
    mejor_puntaje: Optional[int] = None    # None = todavía no la ha aprobado


class LeccionRDetalle(LeccionRResumen):
    puntaje_minimo: int
    teoria: List[SeccionTeoria]
    practica: List[TareaPublica]


class TareaEnviada(BaseModel):
    """Lo que calculó el navegador al ejecutar el código del estudiante."""
    tarea_id: int
    error: Optional[str] = None            # error de R, si el código falló
    valores: List[str] = []                # resultado de cada comprobación, como texto

    @field_validator("error")
    @classmethod
    def _recortar_error(cls, valor):
        return valor[:500] if valor else valor

    @field_validator("valores")
    @classmethod
    def _recortar_valores(cls, valores):
        if len(valores) > 50:
            raise ValueError("Demasiados valores")
        return [v[:2000] for v in valores]


class EvaluarPractica(BaseModel):
    tareas: List[TareaEnviada]


class RevisionComprobacion(BaseModel):
    tarea_id: int
    comprobacion_id: int
    correcta: bool
    pista: Optional[str] = None            # solo si falló


class ResultadoPractica(BaseModel):
    """Lo que responde el servidor (todo calculado por el servidor)."""
    aprobado: bool
    aciertos: int
    total: int
    puntaje: int
    puntaje_minimo: int
    es_primera_vez: bool
    xp_ganada: int
    xp_total: int
    nivel: int
    subio_de_nivel: bool
    monedas_ganadas: int
    monedas_total: int
    racha_actual: int
    logros_nuevos: List[LogroPublico]
    revision: List[RevisionComprobacion]
