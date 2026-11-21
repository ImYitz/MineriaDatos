# Rutas del usuario: su perfil, su progreso y el cierre de una lección.
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import modelos, esquemas, logica, servicio_logros
from ..base_datos import obtener_sesion
from ..dependencias import obtener_usuario_actual
from ..modelos_repaso import ErrorEjercicio

router = APIRouter(prefix="/api", tags=["progreso"])


class ResultadoLeccionCompleta(esquemas.ResultadoLeccion):
    """El resultado de siempre, más: si la lección se dio por aprobada y por qué no hubo recompensa."""
    aprobada: bool = True
    puntaje_minimo: int = logica.PUNTAJE_MINIMO_LECCION
    motivo_sin_recompensa: Optional[str] = None


def _registrar_errores(bd: Session, usuario: modelos.Usuario, leccion: modelos.Leccion, enviadas: dict) -> None:
    """Los ejercicios fallados entran (o vuelven) al repaso de errores, listos para repasar ya."""
    ahora = datetime.now()
    for ejercicio in leccion.ejercicios:
        respuesta = enviadas.get(ejercicio.id)
        if respuesta is None or logica.es_respuesta_correcta(respuesta, ejercicio.respuesta_correcta):
            continue
        fila = bd.get(ErrorEjercicio, (usuario.id, ejercicio.id))
        if fila is None:
            bd.add(ErrorEjercicio(usuario_id=usuario.id, ejercicio_id=ejercicio.id, caja=0, fallos=1,
                                  dominado=False, proxima_revision=ahora, fecha_ultimo_fallo=ahora))
        else:
            fila.caja = 0
            fila.fallos += 1
            fila.dominado = False
            fila.proxima_revision = ahora
            fila.fecha_ultimo_fallo = ahora


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
    "/lecciones/{leccion_id}/completar", response_model=ResultadoLeccionCompleta
)
def completar_leccion(
    leccion_id: int,
    datos: esquemas.CompletarLeccion,
    bd: Session = Depends(obtener_sesion),
    usuario: modelos.Usuario = Depends(obtener_usuario_actual),
):
    """Corrige la lección completa, guarda el progreso y reparte XP, monedas, racha y logros.

    Reglas contra el abuso:
      - Hace falta un mínimo de aciertos (PUNTAJE_MINIMO_LECCION); si no se alcanza, no se guarda
        nada y no se reparte nada (como en las prácticas de R).
      - Repetir la misma lección más de una vez al día no da XP ni monedas.
    """
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

    # 2) ¿Es la primera vez que este usuario completa esta lección? ¿Ya la hizo hoy?
    es_primera_vez = (
        bd.query(modelos.ProgresoLeccion.id)
        .filter(
            modelos.ProgresoLeccion.usuario_id == usuario.id,
            modelos.ProgresoLeccion.leccion_id == leccion.id,
        )
        .first()
        is None
    )

    # 3) Sin el mínimo de aciertos no se guarda ni se reparte nada
    _registrar_errores(bd, usuario, leccion, enviadas)   # los fallos van al repaso aunque no se apruebe

    if puntaje < logica.PUNTAJE_MINIMO_LECCION:
        bd.commit()
        return ResultadoLeccionCompleta(
            aciertos=aciertos,
            total=total,
            puntaje=puntaje,
            es_primera_vez=es_primera_vez,
            xp_ganada=0,
            xp_total=usuario.xp_total,
            nivel=usuario.nivel,
            subio_de_nivel=False,
            monedas_ganadas=0,
            monedas_total=usuario.monedas,
            racha_actual=logica.racha_vigente(usuario, logica.fecha_hoy()),
            logros_nuevos=[],
            aprobada=False,
            motivo_sin_recompensa=(
                "Necesitas al menos " + str(logica.PUNTAJE_MINIMO_LECCION) +
                " % de aciertos para completar la lección. ¡Inténtalo otra vez!"
            ),
        )

    ya_hoy = (
        not es_primera_vez
        and bd.query(modelos.ProgresoLeccion.id)
        .filter(
            modelos.ProgresoLeccion.usuario_id == usuario.id,
            modelos.ProgresoLeccion.leccion_id == leccion.id,
            modelos.ProgresoLeccion.fecha_completada >= logica.inicio_de_hoy(),
        )
        .first()
        is not None
    )
    motivo: Optional[str] = None
    if ya_hoy:
        motivo = "Ya repetiste esta lección hoy: otra repetición hoy no da XP ni monedas. Vuelve mañana."

    # 4) XP, nivel, monedas y racha diaria (estudiar cuenta para la racha aunque no haya recompensa)
    xp_ganada = 0 if ya_hoy else logica.calcular_xp_ganada(leccion.xp_recompensa, es_primera_vez)
    monedas_ganadas = 0 if ya_hoy else logica.calcular_monedas(aciertos, es_primera_vez)
    nivel_anterior = usuario.nivel
    usuario.xp_total += xp_ganada
    usuario.nivel = logica.calcular_nivel(usuario.xp_total)
    usuario.monedas += monedas_ganadas
    logica.actualizar_racha(usuario, logica.fecha_hoy())

    # 5) Guardar el registro de progreso
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

    # 6) Revisar si se desbloqueó algún logro (suma sus monedas de recompensa)
    logros_nuevos = servicio_logros.revisar_logros(bd, usuario)

    bd.commit()   # guarda todo junto: o se guarda todo o no se guarda nada

    return ResultadoLeccionCompleta(
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
        aprobada=True,
        motivo_sin_recompensa=motivo,
    )
