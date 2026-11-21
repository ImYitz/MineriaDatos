# Rutas del repaso de errores (repetición espaciada, cajas tipo Leitner).
#
# Cada ejercicio fallado en una lección entra en el repaso con caja 0 y toca repasarlo ya.
# Cada acierto sube la caja y aleja la siguiente revisión (1, 3 y 7 días); con 4 aciertos seguidos el
# ejercicio queda "dominado". Un fallo lo devuelve a la caja 0.
# El repaso no da XP ni monedas: solo existen preguntas que el propio usuario falló, y así no se puede
# "cultivar" recompensa fallando a propósito.
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import modelos, esquemas, logica
from ..base_datos import obtener_sesion
from ..dependencias import obtener_usuario_actual
from ..modelos_repaso import ErrorEjercicio

router = APIRouter(prefix="/api/repaso", tags=["repaso"])

INTERVALOS_DIAS = [1, 3, 7]        # días hasta la siguiente revisión tras el 1.º, 2.º y 3.º acierto seguido
TAMANO_SESION = 10


class PreguntaRepaso(BaseModel):
    id: int
    enunciado: str
    opciones: List[str]


class EstadoRepaso(BaseModel):
    pendientes: int
    en_repaso: int
    dominados: int
    proxima_revision: Optional[datetime] = None   # cuándo toca la siguiente, si hoy no queda nada
    ejercicios: List[PreguntaRepaso]


class RespuestaRepaso(BaseModel):
    ejercicio_id: int
    respuesta: str


class ResultadoRepaso(esquemas.ResultadoRespuesta):
    dominado: bool = False
    proxima_en_dias: Optional[int] = None


def _pendientes(bd: Session, usuario: modelos.Usuario):
    return bd.query(ErrorEjercicio).filter(
        ErrorEjercicio.usuario_id == usuario.id,
        ErrorEjercicio.dominado.is_(False),
        ErrorEjercicio.proxima_revision <= datetime.now(),
    )


@router.get("", response_model=EstadoRepaso)
def ver_repaso(
    bd: Session = Depends(obtener_sesion),
    usuario: modelos.Usuario = Depends(obtener_usuario_actual),
):
    """Cuántas preguntas hay en repaso y las que tocan ahora (sin las respuestas correctas)."""
    base = bd.query(func.count(ErrorEjercicio.ejercicio_id)).filter(ErrorEjercicio.usuario_id == usuario.id)
    en_repaso = base.filter(ErrorEjercicio.dominado.is_(False)).scalar() or 0
    dominados = base.filter(ErrorEjercicio.dominado.is_(True)).scalar() or 0
    pendientes = _pendientes(bd, usuario).count()

    ejercicios = []
    for fila in _pendientes(bd, usuario).order_by(ErrorEjercicio.proxima_revision).limit(TAMANO_SESION).all():
        ej = bd.get(modelos.Ejercicio, fila.ejercicio_id)
        if ej is not None:
            ejercicios.append(PreguntaRepaso(id=ej.id, enunciado=ej.enunciado, opciones=list(ej.opciones or [])))

    proxima = None
    if pendientes == 0 and en_repaso > 0:
        proxima = (
            bd.query(func.min(ErrorEjercicio.proxima_revision))
            .filter(ErrorEjercicio.usuario_id == usuario.id, ErrorEjercicio.dominado.is_(False))
            .scalar()
        )
    return EstadoRepaso(pendientes=pendientes, en_repaso=en_repaso, dominados=dominados,
                        proxima_revision=proxima, ejercicios=ejercicios)


@router.post("/responder", response_model=ResultadoRepaso)
def responder(
    datos: RespuestaRepaso,
    bd: Session = Depends(obtener_sesion),
    usuario: modelos.Usuario = Depends(obtener_usuario_actual),
):
    """Corrige una pregunta del repaso y reprograma su próxima revisión."""
    fila = (
        bd.query(ErrorEjercicio)
        .filter(ErrorEjercicio.usuario_id == usuario.id, ErrorEjercicio.ejercicio_id == datos.ejercicio_id)
        .with_for_update()
        .first()
    )
    ejercicio = bd.get(modelos.Ejercicio, datos.ejercicio_id)
    if fila is None or ejercicio is None or fila.dominado:
        raise HTTPException(status_code=404, detail="Esa pregunta no está en tu repaso")
    ahora = datetime.now()
    if fila.proxima_revision > ahora:
        raise HTTPException(status_code=409, detail="Todavía no toca repasar esta pregunta")

    correcta = logica.es_respuesta_correcta(datos.respuesta, ejercicio.respuesta_correcta)
    dominado = False
    dias: Optional[int] = None
    if correcta:
        fila.caja += 1
        if fila.caja > len(INTERVALOS_DIAS):
            fila.dominado = True
            dominado = True
        else:
            dias = INTERVALOS_DIAS[fila.caja - 1]
            fila.proxima_revision = ahora + timedelta(days=dias)
    else:
        fila.caja = 0
        fila.fallos += 1
        fila.fecha_ultimo_fallo = ahora
        fila.proxima_revision = ahora
    bd.commit()

    return ResultadoRepaso(
        correcto=correcta,
        respuesta_correcta=ejercicio.respuesta_correcta,
        explicacion=ejercicio.explicacion,
        dominado=dominado,
        proxima_en_dias=dias,
    )
