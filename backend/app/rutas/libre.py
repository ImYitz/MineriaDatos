# Rutas del modo libre: subir un PDF, generar preguntas y completarlas (con XP, monedas y racha).
#
# El PDF no se guarda: se lee el texto, se generan las preguntas y solo se guardan estas.
# Para que no se pueda "cultivar" XP subiendo cualquier cosa:
#   - el mismo documento solo da recompensa la primera vez que se completa,
#   - como máximo LIMITE_RECOMPENSAS_DIA prácticas con recompensa al día,
#   - la XP es proporcional al porcentaje de aciertos y las monedas son 1 por acierto.
import hashlib
import os
import re
from datetime import datetime, time
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import modelos, esquemas_libre as esq, logica, servicio_logros
from ..base_datos import obtener_sesion
from ..dependencias import obtener_usuario_actual
from ..esquemas_laboratorios import RevisionPregunta
from ..esquemas import LogroPublico
from ..extractor_pdf import ErrorPdf, extraer_texto
from ..generador_preguntas import ErrorGeneracion, generar_preguntas
from ..modelos_libre import SesionLibre

router = APIRouter(prefix="/api/libre", tags=["modo libre"])

TAMANO_MAXIMO = 10 * 1024 * 1024      # 10 MB
LIMITE_GENERACIONES_DIA = 20
LIMITE_RECOMPENSAS_DIA = 3
XP_LIBRE = 8                          # XP máxima por práctica (se multiplica por el % de aciertos)
MONEDAS_POR_ACIERTO = 1


def _inicio_de_hoy() -> datetime:
    return datetime.combine(logica.fecha_hoy(), time.min)


def _motivo_sin_recompensa(bd: Session, usuario: modelos.Usuario, huella: str) -> Optional[str]:
    ya = (
        bd.query(SesionLibre.id)
        .filter(SesionLibre.usuario_id == usuario.id, SesionLibre.huella_documento == huella,
                SesionLibre.completada.is_(True))
        .first()
    )
    if ya is not None:
        return "Ya completaste una práctica con este documento: repetirla no da recompensas."
    hoy = (
        bd.query(func.count(SesionLibre.id))
        .filter(SesionLibre.usuario_id == usuario.id, SesionLibre.con_recompensa.is_(True),
                SesionLibre.fecha_completada >= _inicio_de_hoy())
        .scalar()
    ) or 0
    if hoy >= LIMITE_RECOMPENSAS_DIA:
        return "Hoy ya conseguiste las recompensas de " + str(LIMITE_RECOMPENSAS_DIA) + " prácticas libres. Vuelve mañana."
    return None


def _resumen(s: SesionLibre) -> esq.SesionLibreResumen:
    return esq.SesionLibreResumen(
        id=s.id, titulo=s.titulo, metodo=s.metodo, fecha_creada=s.fecha_creada,
        completada=s.completada, puntaje=s.puntaje,
    )


def _detalle(bd: Session, usuario: modelos.Usuario, s: SesionLibre) -> esq.SesionLibreDetalle:
    return esq.SesionLibreDetalle(
        **_resumen(s).model_dump(),
        preguntas=[
            esq.PreguntaLibre(id=i, enunciado=p["enunciado"], opciones=p["opciones"])
            for i, p in enumerate(s.preguntas)
        ],
        aviso_recompensa=_motivo_sin_recompensa(bd, usuario, s.huella_documento),
    )


@router.get("", response_model=List[esq.SesionLibreResumen])
def listar(
    bd: Session = Depends(obtener_sesion),
    usuario: modelos.Usuario = Depends(obtener_usuario_actual),
):
    """Las últimas 10 prácticas del usuario."""
    filas = (
        bd.query(SesionLibre)
        .filter(SesionLibre.usuario_id == usuario.id)
        .order_by(SesionLibre.id.desc())
        .limit(10)
        .all()
    )
    return [_resumen(s) for s in filas]


@router.post("/generar", response_model=esq.SesionLibreDetalle, status_code=201)
def generar(
    archivo: UploadFile = File(...),
    cantidad: int = Form(8),
    bd: Session = Depends(obtener_sesion),
    usuario: modelos.Usuario = Depends(obtener_usuario_actual),
):
    """Lee el PDF, genera las preguntas y las guarda en una práctica nueva."""
    nombre = os.path.basename(archivo.filename or "documento.pdf")
    if not nombre.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="El archivo debe ser un PDF")
    contenido = archivo.file.read(TAMANO_MAXIMO + 1)
    if len(contenido) > TAMANO_MAXIMO:
        raise HTTPException(status_code=413, detail="El PDF pesa más de 10 MB")
    if not contenido.startswith(b"%PDF"):
        raise HTTPException(status_code=400, detail="El archivo no parece un PDF válido")
    cantidad = max(3, min(10, cantidad))

    hoy = (
        bd.query(func.count(SesionLibre.id))
        .filter(SesionLibre.usuario_id == usuario.id, SesionLibre.fecha_creada >= _inicio_de_hoy())
        .scalar()
    ) or 0
    if hoy >= LIMITE_GENERACIONES_DIA:
        raise HTTPException(status_code=429, detail="Llegaste al límite de PDFs por hoy. Vuelve mañana.")

    try:
        texto = extraer_texto(contenido)
        preguntas, metodo = generar_preguntas(texto, cantidad)
    except (ErrorPdf, ErrorGeneracion) as error:
        raise HTTPException(status_code=422, detail=str(error))

    huella = hashlib.sha256(re.sub(r"\s+", " ", texto).strip().lower().encode("utf-8")).hexdigest()
    titulo = re.sub(r"[_\-]+", " ", os.path.splitext(nombre)[0]).strip()[:100] or "Documento"

    sesion = SesionLibre(
        usuario_id=usuario.id, titulo=titulo, huella_documento=huella,
        metodo=metodo, preguntas=preguntas,
    )
    bd.add(sesion)
    bd.commit()
    bd.refresh(sesion)
    return _detalle(bd, usuario, sesion)


@router.get("/{sesion_id}", response_model=esq.SesionLibreDetalle)
def abrir(
    sesion_id: int,
    bd: Session = Depends(obtener_sesion),
    usuario: modelos.Usuario = Depends(obtener_usuario_actual),
):
    """Retoma una práctica pendiente (sin las respuestas correctas)."""
    sesion = bd.query(SesionLibre).filter(
        SesionLibre.id == sesion_id, SesionLibre.usuario_id == usuario.id).first()
    if sesion is None:
        raise HTTPException(status_code=404, detail="Práctica no encontrada")
    if sesion.completada:
        raise HTTPException(status_code=409, detail="Esta práctica ya se completó")
    return _detalle(bd, usuario, sesion)


@router.post("/{sesion_id}/completar", response_model=esq.ResultadoLibre)
def completar(
    sesion_id: int,
    datos: esq.CompletarLibre,
    bd: Session = Depends(obtener_sesion),
    usuario: modelos.Usuario = Depends(obtener_usuario_actual),
):
    """Corrige la práctica, la guarda y reparte XP, monedas, racha y logros."""
    # Se bloquea la fila: dos envíos simultáneos no pueden cobrar la recompensa dos veces
    sesion = (
        bd.query(SesionLibre)
        .filter(SesionLibre.id == sesion_id, SesionLibre.usuario_id == usuario.id)
        .with_for_update()
        .first()
    )
    if sesion is None:
        raise HTTPException(status_code=404, detail="Práctica no encontrada")
    if sesion.completada:
        raise HTTPException(status_code=409, detail="Esta práctica ya se completó")

    # 1) El servidor corrige (el navegador nunca recibe las respuestas correctas antes)
    enviadas = {r.pregunta_id: r.respuesta for r in datos.respuestas}
    aciertos = 0
    revision = []
    for i, p in enumerate(sesion.preguntas):
        respuesta = enviadas.get(i)
        correcta = respuesta is not None and logica.es_respuesta_correcta(respuesta, p["respuesta_correcta"])
        if correcta:
            aciertos += 1
        revision.append(RevisionPregunta(
            pregunta_id=i, correcta=correcta,
            respuesta_correcta=p["respuesta_correcta"], explicacion=p.get("explicacion") or "",
        ))
    total = len(sesion.preguntas)
    puntaje = round(aciertos * 100 / total) if total > 0 else 0

    # 2) ¿Da recompensa?
    motivo = _motivo_sin_recompensa(bd, usuario, sesion.huella_documento)
    con_recompensa = motivo is None
    xp_ganada = int(XP_LIBRE * puntaje / 100 + 0.5) if con_recompensa else 0
    monedas_ganadas = aciertos * MONEDAS_POR_ACIERTO if con_recompensa else 0

    # 3) XP, nivel, monedas y racha (estudiar cuenta para la racha aunque no haya recompensa)
    nivel_anterior = usuario.nivel
    usuario.xp_total += xp_ganada
    usuario.nivel = logica.calcular_nivel(usuario.xp_total)
    usuario.monedas += monedas_ganadas
    logica.actualizar_racha(usuario, logica.fecha_hoy())

    # 4) Guardar el resultado
    sesion.completada = True
    sesion.con_recompensa = con_recompensa
    sesion.aciertos = aciertos
    sesion.total_preguntas = total
    sesion.puntaje = puntaje
    sesion.xp_ganada = xp_ganada
    sesion.fecha_completada = datetime.now()
    bd.flush()

    logros_nuevos = servicio_logros.revisar_logros(bd, usuario)
    bd.commit()

    return esq.ResultadoLibre(
        aciertos=aciertos, total=total, puntaje=puntaje,
        con_recompensa=con_recompensa, motivo_sin_recompensa=motivo,
        xp_ganada=xp_ganada, xp_total=usuario.xp_total, nivel=usuario.nivel,
        subio_de_nivel=usuario.nivel > nivel_anterior,
        monedas_ganadas=monedas_ganadas, monedas_total=usuario.monedas,
        racha_actual=usuario.racha_actual,
        logros_nuevos=[
            LogroPublico(codigo=l.codigo, nombre=l.nombre, descripcion=l.descripcion,
                         icono=l.icono, recompensa_monedas=l.recompensa_monedas)
            for l in logros_nuevos
        ],
        revision=revision,
    )
