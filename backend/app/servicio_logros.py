# Evaluación de logros: decide cuáles ha desbloqueado un usuario.
#
# Cómo funciona: cada logro del catálogo dice "tipo de condición + valor objetivo".
# Aquí calculamos el valor ACTUAL del usuario para ese tipo y, si llega al
# objetivo, el logro se desbloquea. Se revisa cada vez que se completa una lección.
from typing import List
from sqlalchemy import func
from sqlalchemy.orm import Session

from . import modelos, logica


def valor_actual(bd: Session, usuario: modelos.Usuario, tipo_condicion: str) -> int:
    """Cuánto lleva el usuario en un tipo de condición."""
    if tipo_condicion == "lecciones_completadas":
        return (
            bd.query(func.count(func.distinct(modelos.ProgresoLeccion.leccion_id)))
            .filter(modelos.ProgresoLeccion.usuario_id == usuario.id)
            .scalar()
        ) or 0
    if tipo_condicion == "leccion_perfecta":
        return (
            bd.query(func.count(modelos.ProgresoLeccion.id))
            .filter(
                modelos.ProgresoLeccion.usuario_id == usuario.id,
                modelos.ProgresoLeccion.puntaje == 100,
            )
            .scalar()
        ) or 0
    if tipo_condicion == "racha":
        return logica.racha_vigente(usuario, logica.fecha_hoy())
    if tipo_condicion == "nivel":
        return usuario.nivel
    return 0   # tipo desconocido: nunca se cumple


def revisar_logros(bd: Session, usuario: modelos.Usuario) -> List[modelos.Logro]:
    """Desbloquea los logros que el usuario ya cumple y todavía no tenía.
    Suma las monedas de recompensa y devuelve la lista de logros nuevos.

    IMPORTANTE: quien la llame debe haber hecho bd.flush() antes, para que el
    progreso recién guardado ya cuente. Y debe hacer bd.commit() después.
    """
    ya_obtenidos = {
        fila.logro_id
        for fila in bd.query(modelos.LogroUsuario).filter(
            modelos.LogroUsuario.usuario_id == usuario.id
        )
    }

    nuevos = []
    for logro in bd.query(modelos.Logro).order_by(modelos.Logro.id).all():
        if logro.id in ya_obtenidos:
            continue
        if valor_actual(bd, usuario, logro.tipo_condicion) >= logro.valor_objetivo:
            bd.add(modelos.LogroUsuario(usuario_id=usuario.id, logro_id=logro.id))
            usuario.monedas += logro.recompensa_monedas
            nuevos.append(logro)
    return nuevos
