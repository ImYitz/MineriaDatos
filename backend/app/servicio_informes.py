# Reúne los datos que necesitan los dos PDF de informes (Etapa 10).
#
# Aquí están las consultas a la base de datos y a los catálogos; el dibujo del PDF está en
# generador_pdf.py, que recibe estos diccionarios y no sabe nada de la base de datos.
from datetime import datetime
from typing import Dict, List

from sqlalchemy import func
from sqlalchemy.orm import Session

from . import modelos, logica, servicio_logros
from .catalogo_items import CATALOGO as ITEMS
from .catalogo_laboratorios import CATALOGO as LABORATORIOS
from .catalogo_lecciones import LECCIONES
from .catalogo_logros import CATALOGO as LOGROS
from .catalogo_r import CATALOGO as LECCIONES_R, PUNTAJE_MINIMO as PUNTAJE_MINIMO_R
from .datos_estudio import _promedio, obtener_eventos
from .modelos_laboratorios import ProgresoLaboratorio
from .modelos_libre import SesionLibre
from .modelos_r import ProgresoR
from .rutas import libre as _libre

TIPOS = ["lecciones", "laboratorios", "r", "libre"]

# Unidades del curso: deben coincidir con UNIDADES en frontend/js/inicio.js
UNIDADES = [
    (1, "Unidad 1: Conceptos sobre minería de datos"),
    (9, "Unidad 2: Modelos y técnicas de la minería de datos"),
]


def _por_clave(bd: Session, usuario: modelos.Usuario, clave, modelo) -> Dict:
    """{valor de la clave: (veces, mejor puntaje)} del usuario para una tabla de progreso."""
    filas = (
        bd.query(clave, func.count(modelo.id), func.max(modelo.puntaje))
        .filter(modelo.usuario_id == usuario.id)
        .group_by(clave)
        .all()
    )
    return {k: (veces, mejor) for k, veces, mejor in filas}


# ---------------------------------------------------------------------------------------------
# PDF 1: resumen de la cuenta
# ---------------------------------------------------------------------------------------------
def datos_resumen(bd: Session, usuario: modelos.Usuario) -> dict:
    # Actividad total (de cualquier tipo)
    eventos = obtener_eventos(bd, usuario)
    por_tipo = {tipo: 0 for tipo in TIPOS}
    for e in eventos:
        por_tipo[e.tipo] += 1

    # Lecciones del curso
    est = _por_clave(bd, usuario, modelos.ProgresoLeccion.leccion_id, modelos.ProgresoLeccion)
    lecciones = []
    for leccion in bd.query(modelos.Leccion).order_by(modelos.Leccion.orden).all():
        veces, mejor = est.get(leccion.id, (0, None))
        lecciones.append({"orden": leccion.orden, "titulo": leccion.titulo, "veces": veces, "mejor": mejor})

    # Laboratorios y lecciones de R (sus catálogos viven en Python)
    est_labs = _por_clave(bd, usuario, ProgresoLaboratorio.laboratorio, ProgresoLaboratorio)
    laboratorios = [
        {"titulo": lab["titulo"], "veces": est_labs.get(lab["codigo"], (0, None))[0],
         "mejor": est_labs.get(lab["codigo"], (0, None))[1]}
        for lab in LABORATORIOS
    ]
    est_r = _por_clave(bd, usuario, ProgresoR.leccion, ProgresoR)
    r = [
        {"titulo": leccion["titulo"], "veces": est_r.get(leccion["codigo"], (0, None))[0],
         "mejor": est_r.get(leccion["codigo"], (0, None))[1]}
        for leccion in LECCIONES_R
    ]

    # Modo libre: total y las 10 prácticas más recientes
    completadas = (
        bd.query(func.count(SesionLibre.id))
        .filter(SesionLibre.usuario_id == usuario.id, SesionLibre.completada.is_(True))
        .scalar()
    ) or 0
    recientes = (
        bd.query(SesionLibre)
        .filter(SesionLibre.usuario_id == usuario.id, SesionLibre.completada.is_(True))
        .order_by(SesionLibre.fecha_completada.desc())
        .limit(10)
        .all()
    )

    # Logros: los obtenidos (con fecha) y, de los demás, cuánto lleva el usuario
    obtenidos = {
        fila.logro_id: fila.fecha_obtenido
        for fila in bd.query(modelos.LogroUsuario).filter(modelos.LogroUsuario.usuario_id == usuario.id)
    }
    logros = []
    for logro in bd.query(modelos.Logro).order_by(modelos.Logro.id).all():
        obtenido = logro.id in obtenidos
        actual = logro.valor_objetivo if obtenido else servicio_logros.valor_actual(bd, usuario, logro.tipo_condicion)
        logros.append({
            "nombre": logro.nombre,
            "descripcion": logro.descripcion,
            "obtenido": obtenido,
            "fecha": obtenidos.get(logro.id),
            "progreso": min(actual, logro.valor_objetivo),
            "objetivo": logro.valor_objetivo,
            "recompensa": logro.recompensa_monedas,
        })
    # Los obtenidos, del más antiguo al más reciente
    logros.sort(key=lambda x: (not x["obtenido"], x["fecha"] or datetime.min))

    return {
        "generado": datetime.now(),
        "perfil": {
            "nombre_usuario": usuario.nombre_usuario,
            "correo": usuario.correo,
            "fecha_registro": usuario.fecha_registro,
            "xp_total": usuario.xp_total,
            "nivel": usuario.nivel,
            "xp_en_nivel": usuario.xp_total % logica.XP_POR_NIVEL,
            "xp_por_nivel": logica.XP_POR_NIVEL,
            "monedas": usuario.monedas,
            "racha_actual": logica.racha_vigente(usuario, logica.fecha_hoy()),
            "racha_maxima": usuario.racha_maxima,
        },
        "actividad": {
            "total": len(eventos),
            "dias_activos": len({e.fecha for e in eventos}),
            "puntaje_medio": int(round(_promedio([e.puntaje for e in eventos]))) if eventos else None,
            "por_tipo": por_tipo,
        },
        "lecciones": lecciones,
        "laboratorios": laboratorios,
        "r": r,
        "libre": {
            "completadas": completadas,
            "recientes": [
                {"titulo": s.titulo, "fecha": s.fecha_completada, "puntaje": s.puntaje,
                 "con_recompensa": bool(s.con_recompensa)}
                for s in recientes
            ],
        },
        "logros": logros,
    }


# ---------------------------------------------------------------------------------------------
# PDF 2: documentación de la aplicación
# ---------------------------------------------------------------------------------------------
def datos_documentacion() -> dict:
    """No usa la base de datos: lee los catálogos y las constantes del código, así la documentación
    siempre coincide con lo que la aplicación realmente tiene."""
    ordenadas = sorted(LECCIONES, key=lambda x: x["orden"])
    unidades: List[tuple] = []
    for i, (desde, titulo) in enumerate(UNIDADES):
        hasta = UNIDADES[i + 1][0] if i + 1 < len(UNIDADES) else 10 ** 6
        unidades.append((titulo, [x["titulo"] for x in ordenadas if desde <= x["orden"] < hasta]))

    return {
        "generado": datetime.now(),
        "n_lecciones": len(LECCIONES),
        "n_logros": len(LOGROS),
        "n_items": len(ITEMS),
        "unidades": unidades,
        "laboratorios": [(lab["titulo"], lab["descripcion"]) for lab in LABORATORIOS],
        "r": [(leccion["titulo"], leccion["descripcion"]) for leccion in LECCIONES_R],
        "reglas": {
            "xp_por_nivel": logica.XP_POR_NIVEL,
            "repeticion": logica.PORCENTAJE_REPETICION,
            "monedas_acierto": logica.MONEDAS_POR_ACIERTO,
            "puntaje_minimo_r": PUNTAJE_MINIMO_R,
            "xp_libre": _libre.XP_LIBRE,
            "monedas_libre": _libre.MONEDAS_POR_ACIERTO,
            "limite_recompensas": _libre.LIMITE_RECOMPENSAS_DIA,
            "limite_generaciones": _libre.LIMITE_GENERACIONES_DIA,
        },
    }
