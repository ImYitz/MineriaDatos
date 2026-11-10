# Análisis del historial de estudio de un usuario (Etapa 9).
#
# Pasos (CRISP-DM): 1) reunir los datos (lecciones, laboratorios, prácticas de R y modo libre),
# 2) convertirlos en variables, 3) estimar el riesgo de abandono con el modelo de
# modelo_abandono.py y 4) recomendar qué estudiar según los resultados.
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from . import modelos, logica, esquemas_estudio as esq
from .catalogo_laboratorios import CATALOGO as LABORATORIOS
from .catalogo_r import CATALOGO as LECCIONES_R
from .modelo_abandono import CARACTERISTICAS, obtener_modelo
from .modelos_laboratorios import ProgresoLaboratorio
from .modelos_libre import SesionLibre
from .modelos_r import ProgresoR

PUNTAJE_ACEPTABLE = 70        # por debajo de esto, la lección se recomienda repasar
MINIMO_ACTIVIDADES = 3        # con menos actividades, el riesgo es poco fiable
TIPOS = ["lecciones", "laboratorios", "r", "libre"]

# Práctica sugerida para cada lección del curso (por título): (tipo, código)
RELACIONADAS = {
    "¿Qué es la minería de datos?": [("r", "r_basico")],
    "El proceso KDD": [("laboratorio", "imputacion")],
    "El proceso y la preparación de datos": [("laboratorio", "imputacion"), ("laboratorio", "normalizacion"), ("r", "r_faltantes")],
    "¿Qué es un modelo?": [("laboratorio", "arbol"), ("r", "r_regresion")],
    "Predicción": [("r", "r_regresion"), ("laboratorio", "knn")],
    "Modelos descriptivos y predictivos": [("laboratorio", "kmeans")],
    "Técnicas principales": [("laboratorio", "knn"), ("laboratorio", "kmeans")],
    "Árboles de clasificación": [("laboratorio", "arbol")],
}


@dataclass
class Evento:
    instante: datetime
    puntaje: int
    tipo: str

    @property
    def fecha(self) -> date:
        return self.instante.date()


# ---------------------------------------------------------------------------------------------
# 1) Datos
# ---------------------------------------------------------------------------------------------
def obtener_eventos(bd: Session, usuario: modelos.Usuario) -> List[Evento]:
    """Todas las actividades terminadas por el usuario, de la más antigua a la más reciente."""
    eventos: List[Evento] = []

    def agregar(filas, tipo: str) -> None:
        for instante, puntaje in filas:
            if instante is not None and puntaje is not None:
                eventos.append(Evento(instante, int(puntaje), tipo))

    agregar(
        bd.query(modelos.ProgresoLeccion.fecha_completada, modelos.ProgresoLeccion.puntaje)
        .filter(modelos.ProgresoLeccion.usuario_id == usuario.id), "lecciones")
    agregar(
        bd.query(ProgresoLaboratorio.fecha_completada, ProgresoLaboratorio.puntaje)
        .filter(ProgresoLaboratorio.usuario_id == usuario.id), "laboratorios")
    agregar(
        bd.query(ProgresoR.fecha_completada, ProgresoR.puntaje)
        .filter(ProgresoR.usuario_id == usuario.id), "r")
    agregar(
        bd.query(SesionLibre.fecha_completada, SesionLibre.puntaje)
        .filter(SesionLibre.usuario_id == usuario.id, SesionLibre.completada.is_(True)), "libre")

    eventos.sort(key=lambda e: e.instante)
    return eventos


# ---------------------------------------------------------------------------------------------
# 2) Variables
# ---------------------------------------------------------------------------------------------
def _promedio(valores: List[float]) -> float:
    return sum(valores) / len(valores)


def calcular_caracteristicas(eventos: List[Evento], usuario: modelos.Usuario, hoy: date) -> Dict[str, float]:
    if eventos:
        dias_sin = (hoy - eventos[-1].fecha).days
    else:
        dias_sin = (hoy - usuario.fecha_registro.date()).days   # nunca ha estudiado: cuenta desde que se registró
    dias_sin = max(0, min(30, dias_sin))

    ventana = {hoy - timedelta(days=i) for i in range(14)}
    dias_activos_14 = len({e.fecha for e in eventos if e.fecha in ventana})

    puntajes = [e.puntaje for e in eventos]
    puntaje_medio = _promedio(puntajes[-10:]) if puntajes else 50.0

    tendencia = 0.0
    if len(puntajes) >= 4:
        recientes = puntajes[-3:]
        anteriores = puntajes[-10:-3]
        tendencia = max(-50.0, min(50.0, _promedio(recientes) - _promedio(anteriores)))

    return {
        "dias_sin_estudiar": float(dias_sin),
        "actividad_14": dias_activos_14 / 14,
        "puntaje_medio": puntaje_medio,
        "tendencia": tendencia,
        "variedad": float(len({e.tipo for e in eventos})),
        "racha": float(min(14, logica.racha_vigente(usuario, hoy))),
    }


# ---------------------------------------------------------------------------------------------
# 3) Riesgo de abandono
# ---------------------------------------------------------------------------------------------
def _texto_factor(nombre: str, valor: float) -> str:
    if nombre == "dias_sin_estudiar":
        dias = int(round(valor))
        if dias == 0:
            return "Estudiaste hoy"
        if dias == 1:
            return "Llevas 1 día sin estudiar"
        return "Llevas " + str(dias) + " días sin estudiar" + (" (o más)" if dias >= 30 else "")
    if nombre == "actividad_14":
        n = int(round(valor * 14))
        return "Estudiaste " + str(n) + (" día" if n == 1 else " días") + " de los últimos 14"
    if nombre == "puntaje_medio":
        return "Tu puntaje medio reciente es " + str(int(round(valor))) + " %"
    if nombre == "tendencia":
        cambio = int(round(valor))
        if cambio == 0:
            return "Tus últimos resultados se mantienen igual que los anteriores"
        return ("Tus últimos resultados son " + str(abs(cambio)) + " puntos " +
                ("mejores" if cambio > 0 else "peores") + " que los anteriores")
    if nombre == "variedad":
        n = int(round(valor))
        return "Has usado " + str(n) + " de 4 tipos de actividad (lecciones, laboratorios, R y modo libre)"
    return "Tu racha actual es de " + str(int(round(valor))) + (" día" if round(valor) == 1 else " días")


def _nivel(probabilidad: float) -> str:
    if probabilidad < 0.30:
        return "bajo"
    if probabilidad < 0.60:
        return "medio"
    return "alto"


MENSAJES = {
    "bajo": "Vas muy bien: tu ritmo de estudio es constante y nada indica que vayas a dejarlo.",
    "medio": "Tu ritmo de estudio ha bajado un poco. Una lección corta hoy te ayuda a retomarlo.",
    "alto": "Hay señales de que podrías dejar de estudiar. Retomar hoy con una lección corta marca la diferencia.",
}


def evaluar_riesgo(caracteristicas: Dict[str, float], n_eventos: int) -> esq.RiesgoAbandono:
    modelo = obtener_modelo()
    x = [caracteristicas[nombre] for nombre in CARACTERISTICAS]
    probabilidad = modelo.probabilidad(x)
    contribuciones = modelo.contribuciones(x)

    factores = []
    for nombre, valor, aporte in zip(CARACTERISTICAS, x, contribuciones):
        efecto = "sube" if aporte > 0.05 else "baja" if aporte < -0.05 else "neutral"
        factores.append(esq.FactorRiesgo(
            nombre=nombre, texto=_texto_factor(nombre, valor), efecto=efecto, impacto=round(aporte, 2)))
    factores.sort(key=lambda f: abs(f.impacto), reverse=True)

    nivel = _nivel(probabilidad)
    return esq.RiesgoAbandono(
        probabilidad=int(round(probabilidad * 100)),
        nivel=nivel,
        mensaje=MENSAJES[nivel],
        datos_suficientes=n_eventos >= MINIMO_ACTIVIDADES,
        factores=factores,
    )


# ---------------------------------------------------------------------------------------------
# 4) Recomendación
# ---------------------------------------------------------------------------------------------
def _practica(tipo: str, codigo: str) -> Optional[esq.PracticaRelacionada]:
    if tipo == "laboratorio":
        for lab in LABORATORIOS:
            if lab["codigo"] == codigo:
                return esq.PracticaRelacionada(
                    titulo="Laboratorio: " + lab["titulo"], tipo="laboratorio",
                    enlace="laboratorio.html?id=" + codigo)
    else:
        for leccion in LECCIONES_R:
            if leccion["codigo"] == codigo:
                return esq.PracticaRelacionada(
                    titulo="Aprende R: " + leccion["titulo"], tipo="r",
                    enlace="leccion_r.html?id=" + codigo)
    return None


def _practica_para(titulo_leccion: str, labs_hechos: set, r_hechos: set) -> Optional[esq.PracticaRelacionada]:
    opciones = RELACIONADAS.get(titulo_leccion, [])
    for tipo, codigo in opciones:    # primero una que todavía no haya hecho
        if codigo not in (labs_hechos if tipo == "laboratorio" else r_hechos):
            return _practica(tipo, codigo)
    return _practica(*opciones[0]) if opciones else None


def recomendar(bd: Session, usuario: modelos.Usuario, puntajes: List[esq.PuntajeLeccion],
               ids: Dict[int, int]) -> esq.Recomendacion:
    labs_hechos = {c for (c,) in bd.query(ProgresoLaboratorio.laboratorio)
                   .filter(ProgresoLaboratorio.usuario_id == usuario.id).distinct()}
    r_hechos = {c for (c,) in bd.query(ProgresoR.leccion)
                .filter(ProgresoR.usuario_id == usuario.id).distinct()}

    # 1) Lo más débil: lecciones completadas con puntaje bajo
    debiles = [p for p in puntajes if p.mejor_puntaje is not None and p.mejor_puntaje < PUNTAJE_ACEPTABLE]
    if debiles:
        peor = min(debiles, key=lambda p: (p.mejor_puntaje, p.orden))
        return esq.Recomendacion(
            tipo="repasar",
            titulo="Repasa «" + peor.titulo + "»",
            texto=("Es la lección donde más te cuesta: tu mejor puntaje es " + str(peor.mejor_puntaje) +
                   " %. Reforzarla ahora te ayudará con los temas que dependen de ella."),
            enlace="leccion.html?id=" + str(ids[peor.orden]),
            boton="Repasar la lección",
            relacionada=_practica_para(peor.titulo, labs_hechos, r_hechos),
        )

    # 2) La siguiente lección que no ha hecho
    pendiente = next((p for p in puntajes if p.mejor_puntaje is None), None)
    if pendiente is not None:
        return esq.Recomendacion(
            tipo="continuar",
            titulo="Continúa con «" + pendiente.titulo + "»",
            texto="Es la siguiente lección del curso que todavía no completas.",
            enlace="leccion.html?id=" + str(ids[pendiente.orden]),
            boton="Empezar la lección",
            relacionada=_practica_para(pendiente.titulo, labs_hechos, r_hechos),
        )

    # 3) Curso terminado: laboratorios y prácticas de R pendientes
    for lab in LABORATORIOS:
        if lab["codigo"] not in labs_hechos:
            return esq.Recomendacion(
                tipo="practicar", titulo="Practica en el laboratorio «" + lab["titulo"] + "»",
                texto="Ya dominas las lecciones. Aplica lo aprendido de forma interactiva.",
                enlace="laboratorio.html?id=" + lab["codigo"], boton="Abrir el laboratorio")
    for leccion in LECCIONES_R:
        if leccion["codigo"] not in r_hechos:
            return esq.Recomendacion(
                tipo="practicar", titulo="Aprende R: «" + leccion["titulo"] + "»",
                texto="Ya dominas las lecciones. Ahora aplica la minería de datos escribiendo código.",
                enlace="leccion_r.html?id=" + leccion["codigo"], boton="Abrir la lección de R")

    return esq.Recomendacion(
        tipo="libre", titulo="Estudia tu propio material",
        texto="Lo completaste todo. Sube un PDF en el modo libre y practica con preguntas sobre tus apuntes.",
        enlace="libre.html", boton="Ir al modo libre")


# ---------------------------------------------------------------------------------------------
# Resumen completo
# ---------------------------------------------------------------------------------------------
def resumen(bd: Session, usuario: modelos.Usuario) -> esq.ResumenEstudio:
    hoy = logica.fecha_hoy()
    eventos = obtener_eventos(bd, usuario)
    caracteristicas = calcular_caracteristicas(eventos, usuario, hoy)

    por_tipo = {tipo: 0 for tipo in TIPOS}
    for e in eventos:
        por_tipo[e.tipo] += 1

    por_dia: Dict[date, int] = {}
    for e in eventos:
        por_dia[e.fecha] = por_dia.get(e.fecha, 0) + 1
    actividad_14 = [
        esq.DiaActividad(fecha=hoy - timedelta(days=i), actividades=por_dia.get(hoy - timedelta(days=i), 0))
        for i in range(13, -1, -1)
    ]

    # Mejor puntaje y veces por lección del curso
    estadisticas = {
        leccion_id: (veces, mejor)
        for leccion_id, veces, mejor in bd.query(
            modelos.ProgresoLeccion.leccion_id,
            func.count(modelos.ProgresoLeccion.id),
            func.max(modelos.ProgresoLeccion.puntaje),
        ).filter(modelos.ProgresoLeccion.usuario_id == usuario.id)
        .group_by(modelos.ProgresoLeccion.leccion_id)
    }
    puntajes = []
    ids: Dict[int, int] = {}      # orden -> id de la lección
    for leccion in bd.query(modelos.Leccion).order_by(modelos.Leccion.orden).all():
        veces, mejor = estadisticas.get(leccion.id, (0, None))
        puntajes.append(esq.PuntajeLeccion(
            orden=leccion.orden, titulo=leccion.titulo, mejor_puntaje=mejor, veces=veces))
        ids[leccion.orden] = leccion.id

    return esq.ResumenEstudio(
        total_actividades=len(eventos),
        dias_activos=len({e.fecha for e in eventos}),
        puntaje_medio=int(round(_promedio([e.puntaje for e in eventos]))) if eventos else None,
        racha_actual=logica.racha_vigente(usuario, hoy),
        por_tipo=por_tipo,
        actividad_14=actividad_14,
        puntajes_lecciones=puntajes,
        riesgo=evaluar_riesgo(caracteristicas, len(eventos)),
        recomendacion=recomendar(bd, usuario, puntajes, ids),
        modelo=esq.MetricasModelo(**obtener_modelo().metricas),
    )
