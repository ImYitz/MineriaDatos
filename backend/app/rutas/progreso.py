# Rutas del usuario: su perfil, su progreso y el cierre de una lección.
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import modelos, esquemas, logica, servicio_logros
from ..base_datos import obtener_sesion
from ..dependencias import obtener_usuario_actual

router = APIRouter(prefix="/api", tags=["progreso"])


@router.get("/usuario/actual", response_model=esquemas.PerfilUsuario)
def ver_perfil(usuario: modelos.Usuario = Depends(obtener_usuario_actual)):
    """Datos del usuario que está estudiando: XP, nivel, monedas y racha."""
    return esquemas.PerfilUsuario(
        id=usuario.id,
        nombre_usuario=usuario.nombre_usuario,
        correo=usuario.correo,
        fecha_registro=usuario.fecha_registro,
        xp_total=usuario.xp_total,
        nivel=usuario.nivel,
        xp_en_nivel=usuario.xp_total % logica.XP_POR_NIVEL,
        xp_por_nivel=logica.XP_POR_NIVEL,
        monedas=usuario.monedas,
        racha_actual=logica.racha_vigente(usuario, logica.fecha_hoy()),
        racha_maxima=usuario.racha_maxima,
    )


@router.get("/progreso", response_model=List[esquemas.ProgresoResumen])
def ver_progreso(
    bd: Session = Depends(obtener_sesion),
    usuario: modelos.Usuario = Depends(obtener_usuario_actual),
):
    """Por cada lección completada: cuántas veces y el mejor puntaje."""
    filas = (
        bd.query(
            modelos.ProgresoLeccion.leccion_id,
            func.count(modelos.ProgresoLeccion.id),
            func.max(modelos.ProgresoLeccion.puntaje),
        )
        .filter(modelos.ProgresoLeccion.usuario_id == usuario.id)
        .group_by(modelos.ProgresoLeccion.leccion_id)
        .all()
    )
    return [
        esquemas.ProgresoResumen(
            leccion_id=leccion_id, veces_completada=veces, mejor_puntaje=mejor
        )
        for leccion_id, veces, mejor in filas
    ]


@router.post(
    "/lecciones/{leccion_id}/completar", response_model=esquemas.ResultadoLeccion
)
def completar_leccion(
    leccion_id: int,
    datos: esquemas.CompletarLeccion,
    bd: Session = Depends(obtener_sesion),
    usuario: modelos.Usuario = Depends(obtener_usuario_actual),
):
    """Corrige la lección completa, guarda el progreso y reparte XP, monedas, racha y logros."""
    leccion = bd.get(modelos.Leccion, leccion_id)
    if leccion is None:
        raise HTTPException(status_code=404, detail="Lección no encontrada")

    # 1) El servidor corrige las respuestas (no confiamos en el navegador)
    enviadas = {r.ejercicio_id: r.respuesta for r in datos.respuestas}
    aciertos = 0
    for ejercicio in leccion.ejercicios:
        respuesta = enviadas.get(ejercicio.id)
        if respuesta is not None and logica.es_respuesta_correcta(
            respuesta, ejercicio.respuesta_correcta
        ):
            aciertos += 1
    total = len(leccion.ejercicios)
    puntaje = round(aciertos * 100 / total) if total > 0 else 0

    # 2) ¿Es la primera vez que este usuario completa esta lección?
    ya_completada = (
        bd.query(modelos.ProgresoLeccion)
        .filter(
            modelos.ProgresoLeccion.usuario_id == usuario.id,
            modelos.ProgresoLeccion.leccion_id == leccion.id,
        )
        .first()
        is not None
    )
    es_primera_vez = not ya_completada

    # 3) XP, nivel, monedas y racha diaria
    xp_ganada = logica.calcular_xp_ganada(leccion.xp_recompensa, es_primera_vez)
    monedas_ganadas = logica.calcular_monedas(aciertos, es_primera_vez)
    nivel_anterior = usuario.nivel
    usuario.xp_total += xp_ganada
    usuario.nivel = logica.calcular_nivel(usuario.xp_total)
    usuario.monedas += monedas_ganadas
    logica.actualizar_racha(usuario, logica.fecha_hoy())

    # 4) Guardar el registro de progreso
    bd.add(
        modelos.ProgresoLeccion(
            usuario_id=usuario.id,
            leccion_id=leccion.id,
            aciertos=aciertos,
            total_ejercicios=total,
            puntaje=puntaje,
            xp_ganada=xp_ganada,
        )
    )
    bd.flush()   # "escribe" el progreso en la transacción para que los logros ya lo vean

    # 5) Revisar si se desbloqueó algún logro (suma sus monedas de recompensa)
    logros_nuevos = servicio_logros.revisar_logros(bd, usuario)

    bd.commit()   # guarda todo junto: o se guarda todo o no se guarda nada

    return esquemas.ResultadoLeccion(
        aciertos=aciertos,
        total=total,
        puntaje=puntaje,
        es_primera_vez=es_primera_vez,
        xp_ganada=xp_ganada,
        xp_total=usuario.xp_total,
        nivel=usuario.nivel,
        subio_de_nivel=usuario.nivel > nivel_anterior,
        monedas_ganadas=monedas_ganadas,
        monedas_total=usuario.monedas,
        racha_actual=usuario.racha_actual,
        logros_nuevos=[
            esquemas.LogroPublico(
                codigo=l.codigo,
                nombre=l.nombre,
                descripcion=l.descripcion,
                icono=l.icono,
                recompensa_monedas=l.recompensa_monedas,
            )
            for l in logros_nuevos
        ],
    )
