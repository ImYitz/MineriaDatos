# Ruta para consultar los logros del usuario.
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import modelos, esquemas, servicio_logros
from ..base_datos import obtener_sesion
from ..dependencias import obtener_usuario_actual

router = APIRouter(prefix="/api", tags=["logros"])


@router.get("/logros", response_model=List[esquemas.LogroEstado])
def listar_logros(
    bd: Session = Depends(obtener_sesion),
    usuario: modelos.Usuario = Depends(obtener_usuario_actual),
):
    """Todos los logros del juego, indicando cuáles tiene el usuario y cuánto le falta."""
    obtenidos = {
        fila.logro_id: fila.fecha_obtenido
        for fila in bd.query(modelos.LogroUsuario).filter(
            modelos.LogroUsuario.usuario_id == usuario.id
        )
    }

    resultado = []
    for logro in bd.query(modelos.Logro).order_by(modelos.Logro.id).all():
        actual = servicio_logros.valor_actual(bd, usuario, logro.tipo_condicion)
        resultado.append(
            esquemas.LogroEstado(
                codigo=logro.codigo,
                nombre=logro.nombre,
                descripcion=logro.descripcion,
                icono=logro.icono,
                recompensa_monedas=logro.recompensa_monedas,
                obtenido=logro.id in obtenidos,
                fecha_obtenido=obtenidos.get(logro.id),
                progreso_actual=min(actual, logro.valor_objetivo),
                valor_objetivo=logro.valor_objetivo,
            )
        )
    return resultado
