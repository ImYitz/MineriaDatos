# Ruta del panel "Mis datos de estudio": análisis del historial del usuario con minería de datos.
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
    """Resumen del estudio del usuario: actividad, riesgo de abandono y recomendación."""
    return servicio_estudio.resumen(bd, usuario)
