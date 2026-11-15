# Rutas del panel "Mis datos de estudio" y de la recomendación de la pantalla de inicio.
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import modelos, esquemas_estudio as esq, servicio_estudio
from ..base_datos import obtener_sesion
from ..dependencias import obtener_usuario_actual

router = APIRouter(prefix="/api/estudio", tags=["mis datos de estudio"])


@router.get("", response_model=esq.ResumenEstudio)
def ver_estudio(
    bd: Session = Depends(obtener_sesion),
    usuario: modelos.Usuario = Depends(obtener_usuario_actual),
):
    """Resumen del estudio del usuario: actividad, riesgo de abandono, perfil y recomendación."""
    return servicio_estudio.resumen(bd, usuario)


@router.get("/inicio", response_model=esq.RecomendacionInicio)
def ver_recomendacion_inicio(
    bd: Session = Depends(obtener_sesion),
    usuario: modelos.Usuario = Depends(obtener_usuario_actual),
):
    """Versión corta para la pantalla de inicio: clasificación del usuario y qué hacer ahora."""
    return servicio_estudio.resumen_inicio(bd, usuario)
