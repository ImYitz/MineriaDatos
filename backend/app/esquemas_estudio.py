# Esquemas Pydantic del panel "Mis datos de estudio" (Etapa 9).
from datetime import date
from typing import Dict, List, Optional
from pydantic import BaseModel


class FactorRiesgo(BaseModel):
    nombre: str
    texto: str          # frase lista para mostrar, con el valor del usuario
    efecto: str         # "sube" (aumenta el riesgo), "baja" (lo reduce) o "neutral"
    impacto: float      # cuánto empuja el modelo (mayor valor absoluto = más influencia)


class RiesgoAbandono(BaseModel):
    probabilidad: int   # 0 a 100
    nivel: str          # "bajo", "medio" o "alto"
    mensaje: str
    datos_suficientes: bool
    factores: List[FactorRiesgo]


class PracticaRelacionada(BaseModel):
    titulo: str
    enlace: str
    tipo: str           # "laboratorio" o "r"


class Recomendacion(BaseModel):
    tipo: str           # "repasar", "continuar", "practicar" o "libre"
    titulo: str
    texto: str
    enlace: str
    boton: str
    relacionada: Optional[PracticaRelacionada] = None


class DiaActividad(BaseModel):
    fecha: date
    actividades: int


class PuntajeLeccion(BaseModel):
    orden: int
    titulo: str
    mejor_puntaje: Optional[int] = None    # None = todavía no la completa
    veces: int


class MetricasModelo(BaseModel):
    algoritmo: str
    datos_entrenamiento: int
    datos_prueba: int
    exactitud: int
    precision: int
    sensibilidad: int
    exactitud_base: int
    matriz: List[List[int]]   # [real][predicho]; 0 = continúa, 1 = abandona


class ResumenEstudio(BaseModel):
    total_actividades: int
    dias_activos: int
    puntaje_medio: Optional[int] = None
    racha_actual: int
    por_tipo: Dict[str, int]
    actividad_14: List[DiaActividad]
    puntajes_lecciones: List[PuntajeLeccion]
    riesgo: RiesgoAbandono
    recomendacion: Recomendacion
    modelo: MetricasModelo
