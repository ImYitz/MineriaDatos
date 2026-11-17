# Evaluación de logros: decide cuáles ha desbloqueado un usuario.
#
# Cómo funciona: cada logro del catálogo dice "tipo de condición + valor objetivo".
# Aquí calculamos el valor ACTUAL del usuario para ese tipo y, si llega al
# objetivo, el logro se desbloquea. Se revisa cada vez que se completa una lección,
# un laboratorio, una práctica de R o una práctica del modo libre.
from typing import List
from sqlalchemy import func
from sqlalchemy.orm import Session

from . import modelos, logica
from .datos_estudio import obtener_eventos
from .modelos_laboratorios import ProgresoLaboratorio
from .modelos_r import ProgresoR


def _eventos(bd: Session, usuario: modelos.Usuario):
    """Todas las actividades terminadas del usuario (fecha, hora y tipo). Se calculan una sola vez
    por petición, aunque haya muchos logros que las necesiten."""
    cache = bd.info.setdefault("eventos_logros", {})
    if usuario.id not in cache:
        cache[usuario.id] = obtener_eventos(bd, usuario)
    return cache[usuario.id]


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
    if tipo_condicion == "laboratorios_completados":
        return (
            bd.query(func.count(func.distinct(ProgresoLaboratorio.laboratorio)))
            .filter(ProgresoLaboratorio.usuario_id == usuario.id)
            .scalar()
        ) or 0
    if tipo_condicion == "laboratorio_perfecto":
        return (
            bd.query(func.count(ProgresoLaboratorio.id))
            .filter(
                ProgresoLaboratorio.usuario_id == usuario.id,
                ProgresoLaboratorio.puntaje == 100,
            )
            .scalar()
        ) or 0
    if tipo_condicion == "lecciones_r_completadas":
        return (
            bd.query(func.count(func.distinct(ProgresoR.leccion)))
            .filter(ProgresoR.usuario_id == usuario.id)
            .scalar()
        ) or 0
    if tipo_condicion == "practica_r_perfecta":
        return (
            bd.query(func.count(ProgresoR.id))
            .filter(ProgresoR.usuario_id == usuario.id, ProgresoR.puntaje == 100)
            .scalar()
        ) or 0
    if tipo_condicion == "racha":
        return logica.racha_vigente(usuario, logica.fecha_hoy())
    if tipo_condicion == "nivel":
        return usuario.nivel

    # ---- Tipos que salen del historial completo de actividades ----
    if tipo_condicion == "libre_completadas":
        return sum(1 for e in _eventos(bd, usuario) if e.tipo == "libre")
    if tipo_condicion == "actividades_totales":
        return len(_eventos(bd, usuario))
    if tipo_condicion == "tipos_actividad":
        return len({e.tipo for e in _eventos(bd, usuario)})
    if tipo_condicion == "dias_activos":
        return len({e.fecha for e in _eventos(bd, usuario)})
    if tipo_condicion == "dias_fin_de_semana":
        return len({e.fecha for e in _eventos(bd, usuario) if e.fecha.weekday() >= 5})
    if tipo_condicion == "madrugador":
        return sum(1 for e in _eventos(bd, usuario) if e.instante.hour < 7)
    if tipo_condicion == "noctambulo":
        return sum(1 for e in _eventos(bd, usuario) if e.instante.hour >= 22)
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
