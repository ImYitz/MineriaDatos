# Rutas de las lecciones de R: listarlas, abrir una y evaluar su práctica de código.
#
# El código R se ejecuta en el navegador (WebR). Aquí solo se COMPARA lo que el navegador
# calculó con los valores esperados, que nunca salen del servidor.
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import modelos, esquemas, esquemas_r as esq, logica, servicio_logros
from ..base_datos import obtener_sesion
from ..catalogo_r import CATALOGO, PUNTAJE_MINIMO, buscar_leccion_r
from ..dependencias import obtener_usuario_actual
from ..modelos_r import ProgresoR

router = APIRouter(prefix="/api/r", tags=["aprende R"])

TOLERANCIA = 1e-3   # diferencia numérica aceptada (los valores ya vienen redondeados desde R)


def _son_iguales(enviado: str, esperado: str) -> bool:
    """Compara dos resultados convertidos a texto (listas separadas por comas).
    Los números se comparan con una pequeña tolerancia; el resto, como texto exacto."""
    a = [x.strip() for x in enviado.split(",")]
    b = [x.strip() for x in esperado.split(",")]
    if len(a) != len(b):
        return False
    for x, y in zip(a, b):
        try:
            fx, fy = float(x), float(y)
        except ValueError:
            if x != y:
                return False
            continue
        if abs(fx - fy) > TOLERANCIA * max(1.0, abs(fy)):
            return False
    return True


def _avance_del_usuario(bd: Session, usuario: modelos.Usuario) -> dict:
    """{codigo: (veces aprobada, mejor puntaje)} para este usuario."""
    filas = (
        bd.query(ProgresoR.leccion, func.count(ProgresoR.id), func.max(ProgresoR.puntaje))
        .filter(ProgresoR.usuario_id == usuario.id)
        .group_by(ProgresoR.leccion)
        .all()
    )
    return {codigo: (veces, mejor) for codigo, veces, mejor in filas}


def _campos_resumen(leccion: dict, avance: dict) -> dict:
    veces, mejor = avance.get(leccion["codigo"], (0, None))
    return dict(
        codigo=leccion["codigo"],
        titulo=leccion["titulo"],
        descripcion=leccion["descripcion"],
        icono=leccion["icono"],
        xp_recompensa=leccion["xp_recompensa"],
        veces_completada=veces,
        mejor_puntaje=mejor,
    )


@router.get("", response_model=List[esq.LeccionRResumen])
def listar_lecciones(
    bd: Session = Depends(obtener_sesion),
    usuario: modelos.Usuario = Depends(obtener_usuario_actual),
):
    """Todas las lecciones de R, con el avance de este usuario."""
    avance = _avance_del_usuario(bd, usuario)
    return [esq.LeccionRResumen(**_campos_resumen(l, avance)) for l in CATALOGO]


@router.get("/{codigo}", response_model=esq.LeccionRDetalle)
def obtener_leccion(
    codigo: str,
    bd: Session = Depends(obtener_sesion),
    usuario: modelos.Usuario = Depends(obtener_usuario_actual),
):
    """Una lección con su teoría y su práctica (sin valores esperados ni soluciones)."""
    leccion = buscar_leccion_r(codigo)
    if leccion is None:
        raise HTTPException(status_code=404, detail="Lección no encontrada")
    avance = _avance_del_usuario(bd, usuario)
    return esq.LeccionRDetalle(
        **_campos_resumen(leccion, avance),
        puntaje_minimo=PUNTAJE_MINIMO,
        teoria=[esq.SeccionTeoria(**s) for s in leccion["teoria"]],
        practica=[
            esq.TareaPublica(
                id=i,
                enunciado=t["enunciado"],
                plantilla=t["plantilla"],
                comprobaciones=[
                    esq.ComprobacionPublica(id=j, expresion=c["expresion"], descripcion=c["descripcion"])
                    for j, c in enumerate(t["comprobaciones"])
                ],
            )
            for i, t in enumerate(leccion["practica"])
        ],
    )


@router.post("/{codigo}/evaluar", response_model=esq.ResultadoPractica)
def evaluar_practica(
    codigo: str,
    datos: esq.EvaluarPractica,
    bd: Session = Depends(obtener_sesion),
    usuario: modelos.Usuario = Depends(obtener_usuario_actual),
):
    """Corrige la práctica. Si alcanza el puntaje mínimo, la guarda y reparte XP, monedas,
    racha y logros. Si no, solo devuelve las pistas para que el estudiante lo intente de nuevo."""
    leccion = buscar_leccion_r(codigo)
    if leccion is None:
        raise HTTPException(status_code=404, detail="Lección no encontrada")

    # 1) El servidor compara lo que calculó el navegador con los valores esperados
    enviadas = {t.tarea_id: t for t in datos.tareas}
    aciertos = 0
    total = 0
    revision = []
    for i, tarea in enumerate(leccion["practica"]):
        enviada = enviadas.get(i)
        for j, comprobacion in enumerate(tarea["comprobaciones"]):
            total += 1
            correcta = (
                enviada is not None
                and enviada.error is None
                and j < len(enviada.valores)
                and _son_iguales(enviada.valores[j], comprobacion["esperado"])
            )
            if correcta:
                aciertos += 1
            revision.append(
                esq.RevisionComprobacion(
                    tarea_id=i,
                    comprobacion_id=j,
                    correcta=correcta,
                    pista=None if correcta else comprobacion["pista"],
                )
            )
    puntaje = round(aciertos * 100 / total) if total > 0 else 0
    aprobado = puntaje >= PUNTAJE_MINIMO

    es_primera_vez = (
        bd.query(ProgresoR)
        .filter(ProgresoR.usuario_id == usuario.id, ProgresoR.leccion == codigo)
        .first()
        is None
    )

    # 2) Sin aprobar no se guarda nada ni se reparte nada
    if not aprobado:
        return esq.ResultadoPractica(
            aprobado=False,
            aciertos=aciertos,
            total=total,
            puntaje=puntaje,
            puntaje_minimo=PUNTAJE_MINIMO,
            es_primera_vez=es_primera_vez,
            xp_ganada=0,
            xp_total=usuario.xp_total,
            nivel=usuario.nivel,
            subio_de_nivel=False,
            monedas_ganadas=0,
            monedas_total=usuario.monedas,
            racha_actual=logica.racha_vigente(usuario, logica.fecha_hoy()),
            logros_nuevos=[],
            revision=revision,
        )

    # 3) XP, nivel, monedas y racha diaria (mismas reglas que las lecciones y los laboratorios)
    xp_ganada = logica.calcular_xp_ganada(leccion["xp_recompensa"], es_primera_vez)
    monedas_ganadas = logica.calcular_monedas(aciertos, es_primera_vez)
    nivel_anterior = usuario.nivel
    usuario.xp_total += xp_ganada
    usuario.nivel = logica.calcular_nivel(usuario.xp_total)
    usuario.monedas += monedas_ganadas
    logica.actualizar_racha(usuario, logica.fecha_hoy())

    # 4) Guardar el registro de progreso
    bd.add(
        ProgresoR(
            usuario_id=usuario.id,
            leccion=codigo,
            aciertos=aciertos,
            total_comprobaciones=total,
            puntaje=puntaje,
            xp_ganada=xp_ganada,
        )
    )
    bd.flush()   # para que los logros ya vean esta práctica

    # 5) Logros nuevos (suman sus monedas de recompensa)
    logros_nuevos = servicio_logros.revisar_logros(bd, usuario)

    bd.commit()   # o se guarda todo o no se guarda nada

    return esq.ResultadoPractica(
        aprobado=True,
        aciertos=aciertos,
        total=total,
        puntaje=puntaje,
        puntaje_minimo=PUNTAJE_MINIMO,
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
