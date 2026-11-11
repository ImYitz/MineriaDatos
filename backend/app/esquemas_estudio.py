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
    origen: str               # "base_datos" (entrenado con la base de datos) o "memoria" (estudiantes simulados en memoria)
    simulados: int            # cuántos de los estudiantes usados para entrenar son simulados (sim_...)
    datos_entrenamiento: int
    datos_prueba: int
    exactitud: int
    precision: int
    sensibilidad: int
    exactitud_base: int
    matriz: List[List[int]]   # [real][predicho]; 0 = continúa, 1 = abandona


class SiluetaK(BaseModel):
    k: int
    silueta: float


class GrupoEstudio(BaseModel):
    id: int
    nombre: str
    descripcion: str
    tamano: int
    porcentaje: int
    dias_activos_14: float     # promedio de días con estudio en los últimos 14
    dias_sin_estudiar: float
    puntaje_medio: int
    variedad: float


class PuntoGrupo(BaseModel):
    x: float                   # días con estudio en los últimos 14
    y: float                   # puntaje medio
    grupo: int


class Segmentacion(BaseModel):
    k: int
    silueta: float
    siluetas: List[SiluetaK]
    grupos: List[GrupoEstudio]
    puntos: List[PuntoGrupo]
    total: int                 # estudiantes agrupados
    simulados: int             # cuántos son simulados
    mi_grupo: Optional[int] = None
    mi_punto: Optional[PuntoGrupo] = None


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
    segmentacion: Optional[Segmentacion] = None
