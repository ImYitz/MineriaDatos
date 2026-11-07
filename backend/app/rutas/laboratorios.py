# Rutas de los laboratorios: listarlos, abrir uno y completarlo (con XP, monedas, racha y logros).
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import modelos, esquemas, esquemas_laboratorios as esq, logica, servicio_logros
from ..base_datos import obtener_sesion
from ..catalogo_laboratorios import CATALOGO, buscar_laboratorio
from ..dependencias import obtener_usuario_actual
from ..modelos_laboratorios import ProgresoLaboratorio

router = APIRouter(prefix="/api/laboratorios", tags=["laboratorios"])


def _avance_del_usuario(bd: Session, usuario: modelos.Usuario) -> dict:
    """{codigo: (veces completado, mejor puntaje)} para este usuario."""
    filas = (
        bd.query(
            ProgresoLaboratorio.laboratorio,
            func.count(ProgresoLaboratorio.id),
            func.max(ProgresoLaboratorio.puntaje),
        )
        .filter(ProgresoLaboratorio.usuario_id == usuario.id)
        .group_by(ProgresoLaboratorio.laboratorio)
        .all()
    )
    return {codigo: (veces, mejor) for codigo, veces, mejor in filas}


def _campos_resumen(lab: dict, avance: dict) -> dict:
    veces, mejor = avance.get(lab["codigo"], (0, None))
    return dict(
        codigo=lab["codigo"],
        titulo=lab["titulo"],
        descripcion=lab["descripcion"],
        icono=lab["icono"],
        xp_recompensa=lab["xp_recompensa"],
        veces_completado=veces,
        mejor_puntaje=mejor,
    )


@router.get("", response_model=List[esq.LaboratorioResumen])
def listar_laboratorios(
    bd: Session = Depends(obtener_sesion),
    usuario: modelos.Usuario = Depends(obtener_usuario_actual),
):
    """Todos los laboratorios, con el avance de este usuario."""
    avance = _avance_del_usuario(bd, usuario)
    return [esq.LaboratorioResumen(**_campos_resumen(lab, avance)) for lab in CATALOGO]


@router.get("/{codigo}", response_model=esq.LaboratorioDetalle)
def obtener_laboratorio(
    codigo: str,
    bd: Session = Depends(obtener_sesion),
    usuario: modelos.Usuario = Depends(obtener_usuario_actual),
):
    """Un laboratorio con sus preguntas (sin las respuestas correctas)."""
    lab = buscar_laboratorio(codigo)
    if lab is None:
        raise HTTPException(status_code=404, detail="Laboratorio no encontrado")
    avance = _avance_del_usuario(bd, usuario)
    return esq.LaboratorioDetalle(
        **_campos_resumen(lab, avance),
        instrucciones=lab["instrucciones"],
        preguntas=[
            esq.PreguntaLab(id=i, enunciado=p["enunciado"], opciones=p["opciones"])
            for i, p in enumerate(lab["preguntas"])
        ],
    )


@router.post("/{codigo}/completar", response_model=esq.ResultadoLaboratorio)
def completar_laboratorio(
    codigo: str,
    datos: esq.CompletarLaboratorio,
    bd: Session = Depends(obtener_sesion),
    usuario: modelos.Usuario = Depends(obtener_usuario_actual),
):
    """Corrige las preguntas, guarda el progreso y reparte XP, monedas, racha y logros."""
    lab = buscar_laboratorio(codigo)
    if lab is None:
        raise HTTPException(status_code=404, detail="Laboratorio no encontrado")

    # 1) El servidor corrige las respuestas (no confiamos en el navegador)
    enviadas = {r.pregunta_id: r.respuesta for r in datos.respuestas}
    aciertos = 0
    revision = []
    for i, pregunta in enumerate(lab["preguntas"]):
        respuesta = enviadas.get(i)
        correcta = respuesta is not None and logica.es_respuesta_correcta(
            respuesta, pregunta["respuesta_correcta"]
        )
        if correcta:
            aciertos += 1
        revision.append(
            esq.RevisionPregunta(
                pregunta_id=i,
                correcta=correcta,
                respuesta_correcta=pregunta["respuesta_correcta"],
                explicacion=pregunta["explicacion"],
            )
        )
    total = len(lab["preguntas"])
    puntaje = round(aciertos * 100 / total) if total > 0 else 0

    # 2) ¿Es la primera vez que este usuario completa este laboratorio?
    es_primera_vez = (
        bd.query(ProgresoLaboratorio)
        .filter(
            ProgresoLaboratorio.usuario_id == usuario.id,
            ProgresoLaboratorio.laboratorio == codigo,
        )
        .first()
        is None
    )

    # 3) XP, nivel, monedas y racha diaria (mismas reglas que las lecciones)
    xp_ganada = logica.calcular_xp_ganada(lab["xp_recompensa"], es_primera_vez)
    monedas_ganadas = logica.calcular_monedas(aciertos, es_primera_vez)
    nivel_anterior = usuario.nivel
    usuario.xp_total += xp_ganada
    usuario.nivel = logica.calcular_nivel(usuario.xp_total)
    usuario.monedas += monedas_ganadas
    logica.actualizar_racha(usuario, logica.fecha_hoy())

    # 4) Guardar el registro de progreso
    bd.add(
        ProgresoLaboratorio(
            usuario_id=usuario.id,
            laboratorio=codigo,
            aciertos=aciertos,
            total_preguntas=total,
            puntaje=puntaje,
            xp_ganada=xp_ganada,
        )
    )
    bd.flush()   # para que los logros ya vean este laboratorio

    # 5) Logros nuevos (suman sus monedas de recompensa)
    logros_nuevos = servicio_logros.revisar_logros(bd, usuario)

    bd.commit()   # o se guarda todo o no se guarda nada

    return esq.ResultadoLaboratorio(
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
        revision=revision,
    )
