# Datos de estudio (Etapa 9): lee el historial de la base de datos y lo convierte en variables.
#
# Lo usan el panel "Mis datos de estudio", el modelo de riesgo de abandono (modelo_abandono.py)
# y la segmentación de estudiantes (segmentacion.py). Está en un archivo aparte para que los tres
# calculen las variables exactamente igual.
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from . import modelos
from .modelos_laboratorios import ProgresoLaboratorio
from .modelos_libre import SesionLibre
from .modelos_r import ProgresoR

# Variables que usa el modelo de abandono (el orden importa)
CARACTERISTICAS = [
    "dias_sin_estudiar",   # días desde la última actividad (0 a 30)
    "actividad_14",        # fracción de los últimos 14 días en que estudió (0 a 1)
    "puntaje_medio",       # promedio de los últimos resultados (0 a 100)
    "tendencia",           # últimos resultados menos los anteriores (-50 a 50)
    "variedad",            # tipos de actividad distintos usados (0 a 4)
    "racha",               # días seguidos estudiando (0 a 14)
]

VENTANA_DIAS = 14               # "abandona" = no estudia en los 14 días siguientes a la fecha de corte
PREFIJO_SIMULADOS = "sim_"      # los estudiantes de sembrar_estudiantes.py se llaman sim_001, sim_002...


@dataclass
class Evento:
    instante: datetime
    puntaje: int
    tipo: str    # "lecciones", "laboratorios", "r" o "libre"

    @property
    def fecha(self) -> date:
        return self.instante.date()


def _leer(bd: Session, usuario_id: Optional[int] = None) -> Dict[int, List[Evento]]:
    """Actividades terminadas, por usuario (de la más antigua a la más reciente).
    Con usuario_id solo se leen las de ese usuario."""
    consultas = [
        ("lecciones", bd.query(modelos.ProgresoLeccion.usuario_id, modelos.ProgresoLeccion.fecha_completada,
                               modelos.ProgresoLeccion.puntaje), modelos.ProgresoLeccion.usuario_id),
        ("laboratorios", bd.query(ProgresoLaboratorio.usuario_id, ProgresoLaboratorio.fecha_completada,
                                  ProgresoLaboratorio.puntaje), ProgresoLaboratorio.usuario_id),
        ("r", bd.query(ProgresoR.usuario_id, ProgresoR.fecha_completada, ProgresoR.puntaje),
         ProgresoR.usuario_id),
        ("libre", bd.query(SesionLibre.usuario_id, SesionLibre.fecha_completada, SesionLibre.puntaje)
         .filter(SesionLibre.completada.is_(True)), SesionLibre.usuario_id),
    ]
    por_usuario: Dict[int, List[Evento]] = {}
    for tipo, consulta, columna in consultas:
        if usuario_id is not None:
            consulta = consulta.filter(columna == usuario_id)
        for uid, instante, puntaje in consulta:
            if instante is not None and puntaje is not None:
                por_usuario.setdefault(uid, []).append(Evento(instante, int(puntaje), tipo))
    for lista in por_usuario.values():
        lista.sort(key=lambda e: e.instante)
    return por_usuario


def obtener_eventos(bd: Session, usuario: modelos.Usuario) -> List[Evento]:
    return _leer(bd, usuario.id).get(usuario.id, [])


def _promedio(valores: List[float]) -> float:
    return sum(valores) / len(valores)


def racha_desde_eventos(eventos: List[Evento], hoy: date) -> int:
    """Días seguidos estudiando hasta hoy (o hasta ayer: la racha sigue viva hasta que termine el día)."""
    dias = sorted({e.fecha for e in eventos if e.fecha <= hoy})
    if not dias or dias[-1] < hoy - timedelta(days=1):
        return 0
    racha = 1
    for anterior, actual in zip(reversed(dias[:-1]), reversed(dias[1:])):
        if (actual - anterior).days != 1:
            break
        racha += 1
    return racha


def calcular_caracteristicas(eventos: List[Evento], fecha_registro: date, hoy: date) -> Dict[str, float]:
    """Las variables del modelo, vistas desde la fecha "hoy" (solo se usan eventos hasta ese día)."""
    eventos = [e for e in eventos if e.fecha <= hoy]
    if eventos:
        dias_sin = (hoy - eventos[-1].fecha).days
    else:
        dias_sin = (hoy - fecha_registro).days   # nunca ha estudiado: cuenta desde que se registró
    dias_sin = max(0, min(30, dias_sin))

    ventana = {hoy - timedelta(days=i) for i in range(14)}
    dias_activos_14 = len({e.fecha for e in eventos if e.fecha in ventana})

    puntajes = [e.puntaje for e in eventos]
    puntaje_medio = _promedio(puntajes[-10:]) if puntajes else 50.0

    tendencia = 0.0
    if len(puntajes) >= 4:
        tendencia = max(-50.0, min(50.0, _promedio(puntajes[-3:]) - _promedio(puntajes[-10:-3])))

    return {
        "dias_sin_estudiar": float(dias_sin),
        "actividad_14": dias_activos_14 / 14,
        "puntaje_medio": puntaje_medio,
        "tendencia": tendencia,
        "variedad": float(len({e.tipo for e in eventos})),
        "racha": float(min(14, racha_desde_eventos(eventos, hoy))),
    }


def construir_dataset(bd: Session, hoy: date) -> List[Tuple[List[float], int, bool]]:
    """Ejemplos para entrenar el modelo de abandono con datos de la base de datos.

    Se elige una fecha de corte (hace 14 días). Las variables se calculan con lo que había pasado
    HASTA el corte, y la etiqueta es lo que ocurrió DESPUÉS: abandona = 1 si no volvió a estudiar en
    los 14 días siguientes. Así el modelo aprende a predecir el futuro con datos del pasado.
    Devuelve (variables, abandona, es_simulado). Solo cuentan quienes ya habían estudiado antes del corte."""
    corte = hoy - timedelta(days=VENTANA_DIAS)
    todos = _leer(bd)
    filas = []
    for uid, nombre, registro in bd.query(
            modelos.Usuario.id, modelos.Usuario.nombre_usuario, modelos.Usuario.fecha_registro):
        eventos = todos.get(uid, [])
        antes = [e for e in eventos if e.fecha <= corte]
        if not antes:
            continue
        sigue = any(e.fecha > corte for e in eventos)
        x = calcular_caracteristicas(antes, registro.date(), corte)
        filas.append(([x[c] for c in CARACTERISTICAS], 0 if sigue else 1, nombre.startswith(PREFIJO_SIMULADOS)))
    return filas


def perfiles_actuales(bd: Session, hoy: date) -> List[Tuple[int, Dict[str, float], bool]]:
    """Cómo estudia hoy cada usuario con al menos una actividad: (id, variables, es_simulado).
    Es la base de la segmentación de estudiantes."""
    todos = _leer(bd)
    perfiles = []
    for uid, nombre, registro in bd.query(
            modelos.Usuario.id, modelos.Usuario.nombre_usuario, modelos.Usuario.fecha_registro):
        eventos = todos.get(uid, [])
        if eventos:
            perfiles.append((uid, calcular_caracteristicas(eventos, registro.date(), hoy),
                             nombre.startswith(PREFIJO_SIMULADOS)))
    return perfiles
