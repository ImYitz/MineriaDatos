# Rutas del modo contrarreloj: 60 segundos para responder todas las preguntas del curso que se pueda.
#
# Cómo se evita hacer trampa:
#   - el servidor guarda la hora de inicio y rechaza respuestas fuera de tiempo,
#   - las respuestas se envían una a una y en orden; la correcta solo se revela al responder,
#   - una respuesta enviada demasiado rápido (menos de SEGUNDOS_MINIMOS_POR_PREGUNTA desde la anterior)
#     se cuenta como incorrecta: ningún humano lee y responde una pregunta en ese tiempo,
#   - XP y monedas dependen de los aciertos, con tope de partidas con recompensa al día.
import random
from datetime import datetime, time, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import modelos, esquemas, esquemas_contrarreloj as esq, logica, servicio_logros
from ..base_datos import obtener_sesion
from ..dependencias import obtener_usuario_actual
from ..modelos_contrarreloj import PartidaContrarreloj

router = APIRouter(prefix="/api/contrarreloj", tags=["contrarreloj"])

DURACION = 60                    # segundos de cada partida
GRACIA = 3                       # segundos extra que se toleran por la demora de la red
SEGUNDOS_MINIMOS_POR_PREGUNTA = 1.5   # el intervalo medido incluye la pausa de 0,3 s del navegador
PREGUNTAS_POR_PARTIDA = 15       # si las responde todas dentro del tiempo, desbloquea el logro
LIMITE_PARTIDAS_DIA = 30
LIMITE_RECOMPENSAS_DIA = 5
XP_POR_ACIERTO = 0.5
XP_MAXIMA = 10
MONEDAS_POR_ACIERTO = 1
PUNTOS_POR_ACIERTO = 10


def _inicio_de_hoy() -> datetime:
    return datetime.combine(logica.fecha_hoy(), time.min)


def _recompensas_hoy(bd: Session, usuario: modelos.Usuario) -> int:
    return (
        bd.query(func.count(PartidaContrarreloj.id))
        .filter(PartidaContrarreloj.usuario_id == usuario.id, PartidaContrarreloj.con_recompensa.is_(True),
                PartidaContrarreloj.fecha_completada >= _inicio_de_hoy())
        .scalar()
    ) or 0


def _motivo_sin_recompensa(bd: Session, usuario: modelos.Usuario) -> Optional[str]:
    if _recompensas_hoy(bd, usuario) >= LIMITE_RECOMPENSAS_DIA:
        return ("Hoy ya conseguiste las recompensas de " + str(LIMITE_RECOMPENSAS_DIA) +
                " partidas de contrarreloj. Vuelve mañana (igual puedes jugar por diversión).")
    return None


def _mejor_aciertos(bd: Session, usuario: modelos.Usuario) -> int:
    return (
        bd.query(func.max(PartidaContrarreloj.aciertos))
        .filter(PartidaContrarreloj.usuario_id == usuario.id, PartidaContrarreloj.completada.is_(True))
        .scalar()
    ) or 0


@router.get("", response_model=esq.EstadoContrarreloj)
def ver_estado(
    bd: Session = Depends(obtener_sesion),
    usuario: modelos.Usuario = Depends(obtener_usuario_actual),
):
    """Récord personal, recompensas de hoy y las últimas partidas."""
    recientes = (
        bd.query(PartidaContrarreloj)
        .filter(PartidaContrarreloj.usuario_id == usuario.id, PartidaContrarreloj.completada.is_(True),
                PartidaContrarreloj.respondidas > 0)
        .order_by(PartidaContrarreloj.id.desc())
        .limit(8)
        .all()
    )
    return esq.EstadoContrarreloj(
        duracion=DURACION,
        preguntas_por_partida=PREGUNTAS_POR_PARTIDA,
        mejor_aciertos=_mejor_aciertos(bd, usuario),
        recompensas_hoy=_recompensas_hoy(bd, usuario),
        limite_recompensas=LIMITE_RECOMPENSAS_DIA,
        aviso_recompensa=_motivo_sin_recompensa(bd, usuario),
        recientes=[
            esq.PartidaReciente(fecha=p.fecha_completada, aciertos=p.aciertos, respondidas=p.respondidas,
                                total=p.total_preguntas, termino_todas=bool(p.termino_todas))
            for p in recientes
        ],
    )


@router.post("/iniciar", response_model=esq.PartidaIniciada, status_code=201)
def iniciar(
    bd: Session = Depends(obtener_sesion),
    usuario: modelos.Usuario = Depends(obtener_usuario_actual),
):
    """Crea una partida con preguntas del curso al azar. El tiempo empieza a correr en este momento."""
    hoy = (
        bd.query(func.count(PartidaContrarreloj.id))
        .filter(PartidaContrarreloj.usuario_id == usuario.id, PartidaContrarreloj.fecha_inicio >= _inicio_de_hoy())
        .scalar()
    ) or 0
    if hoy >= LIMITE_PARTIDAS_DIA:
        raise HTTPException(status_code=429, detail="Llegaste al límite de partidas por hoy. Vuelve mañana.")

    ids = [i for (i,) in bd.query(modelos.Ejercicio.id).all()]
    if len(ids) < 3:
        raise HTTPException(status_code=409, detail="Todavía no hay suficientes preguntas en el curso")
    elegidos = random.sample(ids, min(PREGUNTAS_POR_PARTIDA, len(ids)))

    partida = PartidaContrarreloj(
        usuario_id=usuario.id, fecha_inicio=datetime.now(), preguntas=elegidos, respuestas=[],
    )
    bd.add(partida)
    bd.commit()
    bd.refresh(partida)

    ejercicios = {
        e.id: e for e in bd.query(modelos.Ejercicio).filter(modelos.Ejercicio.id.in_(elegidos)).all()
    }
    return esq.PartidaIniciada(
        id=partida.id,
        duracion=DURACION,
        preguntas=[
            esq.PreguntaContrarreloj(id=i, enunciado=ejercicios[eid].enunciado,
                                     opciones=list(ejercicios[eid].opciones or []))
            for i, eid in enumerate(elegidos)
        ],
    )


def _buscar_partida(bd: Session, usuario: modelos.Usuario, partida_id: int) -> PartidaContrarreloj:
    # Se bloquea la fila: dos peticiones simultáneas no pueden registrar la misma respuesta ni cobrar dos veces
    partida = (
        bd.query(PartidaContrarreloj)
        .filter(PartidaContrarreloj.id == partida_id, PartidaContrarreloj.usuario_id == usuario.id)
        .with_for_update()
        .first()
    )
    if partida is None:
        raise HTTPException(status_code=404, detail="Partida no encontrada")
    if partida.completada:
        raise HTTPException(status_code=409, detail="Esta partida ya terminó")
    return partida


def _momento_anterior(partida: PartidaContrarreloj, respuestas: list) -> datetime:
    """Cuándo se respondió la pregunta anterior (o cuándo empezó la partida, si es la primera)."""
    if respuestas and respuestas[-1].get("t"):
        try:
            return datetime.fromisoformat(respuestas[-1]["t"])
        except ValueError:
            pass
    return partida.fecha_inicio


@router.post("/{partida_id}/responder", response_model=esquemas.ResultadoRespuesta)
def responder(
    partida_id: int,
    datos: esq.RespuestaContrarreloj,
    bd: Session = Depends(obtener_sesion),
    usuario: modelos.Usuario = Depends(obtener_usuario_actual),
):
    """Corrige una respuesta. Solo se acepta dentro del tiempo y en el orden de las preguntas."""
    partida = _buscar_partida(bd, usuario, partida_id)

    ahora = datetime.now()
    if ahora > partida.fecha_inicio + timedelta(seconds=DURACION + GRACIA):
        raise HTTPException(status_code=409, detail="Se acabó el tiempo")
    respuestas = list(partida.respuestas or [])
    if datos.pregunta_id != len(respuestas) or datos.pregunta_id >= len(partida.preguntas):
        raise HTTPException(status_code=400, detail="Pregunta fuera de orden")

    ejercicio = bd.get(modelos.Ejercicio, partida.preguntas[datos.pregunta_id])
    if ejercicio is None:
        raise HTTPException(status_code=404, detail="Ejercicio no encontrado")
    correcta = logica.es_respuesta_correcta(datos.respuesta, ejercicio.respuesta_correcta)

    # Demasiado rápido para haber leído la pregunta: no cuenta como acierto
    segundos = (ahora - _momento_anterior(partida, respuestas)).total_seconds()
    if segundos < SEGUNDOS_MINIMOS_POR_PREGUNTA:
        correcta = False

    respuestas.append({"ejercicio_id": ejercicio.id, "correcta": correcta, "t": ahora.isoformat()})
    partida.respuestas = respuestas          # se asigna una lista nueva para que SQLAlchemy detecte el cambio
    bd.commit()

    return esquemas.ResultadoRespuesta(
        correcto=correcta,
        respuesta_correcta=ejercicio.respuesta_correcta,
        explicacion=ejercicio.explicacion,
    )


@router.post("/{partida_id}/terminar", response_model=esq.ResultadoContrarreloj)
def terminar(
    partida_id: int,
    bd: Session = Depends(obtener_sesion),
    usuario: modelos.Usuario = Depends(obtener_usuario_actual),
):
    """Cierra la partida, guarda el resultado y reparte XP, monedas, racha y logros."""
    partida = _buscar_partida(bd, usuario, partida_id)

    respuestas = partida.respuestas or []
    aciertos = sum(1 for r in respuestas if r["correcta"])
    respondidas = len(respuestas)
    total = len(partida.preguntas)
    termino_todas = total > 0 and respondidas == total     # las respuestas solo se aceptan dentro del tiempo

    mejor_anterior = _mejor_aciertos(bd, usuario)
    es_record = aciertos > mejor_anterior

    if respondidas == 0:
        motivo = "No respondiste ninguna pregunta, así que no hay recompensas."
    else:
        motivo = _motivo_sin_recompensa(bd, usuario)
    con_recompensa = motivo is None
    xp_ganada = min(XP_MAXIMA, int(aciertos * XP_POR_ACIERTO + 0.5)) if con_recompensa else 0
    monedas_ganadas = aciertos * MONEDAS_POR_ACIERTO if con_recompensa else 0

    nivel_anterior = usuario.nivel
    usuario.xp_total += xp_ganada
    usuario.nivel = logica.calcular_nivel(usuario.xp_total)
    usuario.monedas += monedas_ganadas
    if respondidas > 0:
        logica.actualizar_racha(usuario, logica.fecha_hoy())

    partida.completada = True
    partida.con_recompensa = con_recompensa
    partida.aciertos = aciertos
    partida.respondidas = respondidas
    partida.total_preguntas = total
    partida.puntaje = round(aciertos * 100 / respondidas) if respondidas else 0
    partida.termino_todas = termino_todas
    partida.xp_ganada = xp_ganada
    partida.fecha_completada = datetime.now()
    bd.flush()   # para que los logros ya vean esta partida

    logros_nuevos = servicio_logros.revisar_logros(bd, usuario)
    bd.commit()

    return esq.ResultadoContrarreloj(
        aciertos=aciertos, respondidas=respondidas, total=total,
        puntos=aciertos * PUNTOS_POR_ACIERTO, puntaje=partida.puntaje,
        es_record=es_record, mejor_anterior=mejor_anterior, termino_todas=termino_todas,
        con_recompensa=con_recompensa, motivo_sin_recompensa=motivo,
        xp_ganada=xp_ganada, xp_total=usuario.xp_total, nivel=usuario.nivel,
        subio_de_nivel=usuario.nivel > nivel_anterior,
        monedas_ganadas=monedas_ganadas, monedas_total=usuario.monedas,
        racha_actual=usuario.racha_actual,
        logros_nuevos=[
            esquemas.LogroPublico(codigo=l.codigo, nombre=l.nombre, descripcion=l.descripcion,
                                  icono=l.icono, recompensa_monedas=l.recompensa_monedas)
            for l in logros_nuevos
        ],
    )
