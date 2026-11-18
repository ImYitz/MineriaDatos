# Generación de los dos PDF de la aplicación (Etapa 10), con reportlab:
#   1. generar_resumen(datos)       -> resumen de la cuenta de un usuario (datos y avance)
#   2. generar_documentacion(info)  -> documentación de la aplicación
#
# Este archivo SOLO dibuja: no consulta la base de datos. Los datos se reúnen en
# servicio_informes.py y llegan aquí como diccionarios simples. Así es fácil cambiar el diseño
# sin tocar las consultas (y al revés).
#
# Se usan las fuentes estándar de PDF (Helvetica y Courier): incluyen tildes y la ñ, pero no
# emojis ni flechas, por eso los textos usan solo caracteres normales.
import io
from datetime import datetime
from typing import Any, Dict, List, Optional
from xml.sax.saxutils import escape

from reportlab.graphics.shapes import Drawing, Rect
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    PageBreak, Paragraph, Preformatted, SimpleDocTemplate, Spacer, Table, TableStyle,
)

NOMBRE_APP = "Aprendizaje: Minería de datos"

# ---------- Colores y medidas ----------
VERDE = colors.HexColor("#58a700")
AZUL = colors.HexColor("#1478b0")
AZUL_OSC = colors.HexColor("#0f4f75")
AMARILLO = colors.HexColor("#ffc800")
NARANJA = colors.HexColor("#ff9600")
TEXTO = colors.HexColor("#3c3c3c")
GRIS = colors.HexColor("#777777")
BORDE = colors.HexColor("#d9d9d9")
FILA_ALT = colors.HexColor("#f4f7f2")
PUNTAJE_ACEPTABLE = 70          # igual que en el panel "Mis datos de estudio"

ANCHO = A4[0] - 4 * cm          # ancho útil de la página (márgenes de 2 cm)

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
         "septiembre", "octubre", "noviembre", "diciembre"]


class Marcado(str):
    """Texto que ya trae marcas de reportlab (<b>, <font>...). Los demás textos se escapan."""


# ---------- Utilidades de texto ----------

def fecha_larga(fecha: Optional[datetime]) -> str:
    if fecha is None:
        return "-"
    return str(fecha.day) + " de " + MESES[fecha.month - 1] + " de " + str(fecha.year)


def fecha_hora(fecha: datetime) -> str:
    return fecha_larga(fecha) + ", " + fecha.strftime("%H:%M")


def _dias(n: int) -> str:
    return str(n) + (" día" if n == 1 else " días")


def _neg(texto: str) -> Marcado:
    return Marcado("<b>" + escape(texto) + "</b>")


def _cod(texto: str) -> Marcado:
    """Fragmento de código (ya con sus marcas). Dentro de una celda, si se une con más texto,
    envuelve el resultado en Marcado(...)."""
    return Marcado('<font face="Courier" size="8.5">' + escape(texto) + "</font>")


def _porcentaje(valor: Optional[int]) -> str:
    return "-" if valor is None else str(valor) + " %"


# ---------- Estilos ----------

def _estilos() -> Dict[str, ParagraphStyle]:
    base = ParagraphStyle("base", fontName="Helvetica", fontSize=10, leading=14, textColor=TEXTO)
    return {
        "cuerpo": ParagraphStyle("cuerpo", parent=base, spaceAfter=6),
        "titulo": ParagraphStyle("titulo", parent=base, fontName="Helvetica-Bold", fontSize=24,
                                 leading=28, textColor=AZUL_OSC, spaceAfter=4),
        "subtitulo": ParagraphStyle("subtitulo", parent=base, fontSize=11.5, textColor=GRIS, spaceAfter=10),
        "h1": ParagraphStyle("h1", parent=base, fontName="Helvetica-Bold", fontSize=15, leading=19,
                             textColor=AZUL, spaceBefore=16, spaceAfter=6, keepWithNext=1),
        "h2": ParagraphStyle("h2", parent=base, fontName="Helvetica-Bold", fontSize=11.5, leading=15,
                             textColor=VERDE, spaceBefore=8, spaceAfter=4, keepWithNext=1),
        "vineta": ParagraphStyle("vineta", parent=base, leftIndent=16, bulletIndent=4, spaceAfter=3),
        "pequeno": ParagraphStyle("pequeno", parent=base, fontSize=8.5, leading=11, textColor=GRIS, spaceAfter=4),
        "td": ParagraphStyle("td", parent=base, fontSize=8.5, leading=11),
        "td_c": ParagraphStyle("td_c", parent=base, fontSize=8.5, leading=11, alignment=1),
        "th": ParagraphStyle("th", parent=base, fontName="Helvetica-Bold", fontSize=8.5, leading=11,
                             textColor=colors.white),
        "th_c": ParagraphStyle("th_c", parent=base, fontName="Helvetica-Bold", fontSize=8.5, leading=11,
                               textColor=colors.white, alignment=1),
        "kpi_v": ParagraphStyle("kpi_v", parent=base, fontName="Helvetica-Bold", fontSize=17, leading=21,
                                textColor=AZUL, alignment=1),
        "kpi_e": ParagraphStyle("kpi_e", parent=base, fontSize=8, leading=10, textColor=GRIS, alignment=1),
        "codigo": ParagraphStyle("codigo", parent=base, fontName="Courier", fontSize=7.8, leading=9.8),
    }


# ---------- Piezas reutilizables ----------

def _celda(valor: Any, estilo: ParagraphStyle):
    if isinstance(valor, Marcado):
        return Paragraph(str(valor), estilo)
    if isinstance(valor, str):
        return Paragraph(escape(valor), estilo)
    if valor is None:
        return Paragraph("-", estilo)
    return valor    # ya es un elemento de reportlab (por ejemplo una barra)


def _tabla(st, encabezados: List[str], filas: List[list], proporciones: List[float],
           centradas=(), color=AZUL) -> Table:
    """Tabla con encabezado de color y filas alternas. 'proporciones' reparte el ancho."""
    total = float(sum(proporciones))
    anchos = [ANCHO * p / total for p in proporciones]
    datos = [[Paragraph(escape(h), st["th_c"] if i in centradas else st["th"])
              for i, h in enumerate(encabezados)]]
    for fila in filas:
        datos.append([_celda(v, st["td_c"] if i in centradas else st["td"]) for i, v in enumerate(fila)])
    tabla = Table(datos, colWidths=anchos, repeatRows=1)
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), color),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, FILA_ALT]),
        ("GRID", (0, 0), (-1, -1), 0.4, BORDE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return tabla


def _barra(porcentaje: Optional[int], ancho: int = 60, alto: int = 8, color=VERDE) -> Drawing:
    """Barra de progreso dibujada (de 0 a 100)."""
    dibujo = Drawing(ancho, alto)
    dibujo.add(Rect(0, 0, ancho, alto, rx=4, ry=4, fillColor=colors.HexColor("#e5e5e5"), strokeColor=None))
    p = max(0, min(100, porcentaje or 0))
    if p > 0:
        dibujo.add(Rect(0, 0, max(alto, ancho * p / 100.0), alto, rx=4, ry=4, fillColor=color, strokeColor=None))
    return dibujo


def _barra_puntaje(mejor: Optional[int]) -> Drawing:
    color = VERDE if (mejor or 0) >= PUNTAJE_ACEPTABLE else NARANJA
    return _barra(mejor, color=color)


def _kpis(st, items: List[tuple]) -> Table:
    """Fila de cifras destacadas: [(valor, etiqueta), ...]."""
    n = len(items)
    datos = [[Paragraph(escape(str(v)), st["kpi_v"]) for v, _ in items],
             [Paragraph(escape(e), st["kpi_e"]) for _, e in items]]
    tabla = Table(datos, colWidths=[ANCHO / n] * n)
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), FILA_ALT),
        ("BOX", (0, 0), (-1, -1), 0.6, BORDE),
        ("LINEAFTER", (0, 0), (-2, -1), 0.4, BORDE),
        ("TOPPADDING", (0, 0), (-1, 0), 8), ("BOTTOMPADDING", (0, 1), (-1, 1), 8),
        ("TOPPADDING", (0, 1), (-1, 1), 0), ("BOTTOMPADDING", (0, 0), (-1, 0), 0),
    ]))
    return tabla


def _vinetas(story, st, textos: List[str]) -> None:
    for t in textos:
        story.append(Paragraph(t, st["vineta"], bulletText="•"))


def _bloque_codigo(st, texto: str) -> Table:
    caja = Table([[Preformatted(texto, st["codigo"])]], colWidths=[ANCHO])
    caja.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
        ("BOX", (0, 0), (-1, -1), 0.6, BORDE),
        ("LEFTPADDING", (0, 0), (-1, -1), 8), ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return caja


def _construir(story, titulo_documento: str, pie: str) -> bytes:
    """Convierte la lista de elementos en un PDF y devuelve sus bytes."""
    def dibujar_pie(lienzo, doc):
        lienzo.saveState()
        lienzo.setStrokeColor(BORDE)
        lienzo.line(2 * cm, 1.6 * cm, A4[0] - 2 * cm, 1.6 * cm)
        lienzo.setFont("Helvetica", 8)
        lienzo.setFillColor(GRIS)
        lienzo.drawString(2 * cm, 1.1 * cm, pie)
        lienzo.drawRightString(A4[0] - 2 * cm, 1.1 * cm, "Página " + str(doc.page))
        lienzo.restoreState()

    memoria = io.BytesIO()
    doc = SimpleDocTemplate(
        memoria, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=2 * cm, bottomMargin=2.2 * cm,
        title=titulo_documento, author=NOMBRE_APP, subject=titulo_documento,
    )
    doc.build(story, onFirstPage=dibujar_pie, onLaterPages=dibujar_pie)
    return memoria.getvalue()


# ======================================================================================
# PDF 1: resumen de la cuenta
# ======================================================================================

def generar_resumen(d: Dict[str, Any]) -> bytes:
    """d: datos reunidos por servicio_informes.datos_resumen()."""
    st = _estilos()
    p = d["perfil"]
    act = d["actividad"]
    story: list = []

    story.append(Paragraph("Resumen de cuenta", st["titulo"]))
    story.append(Paragraph(escape(NOMBRE_APP) + " · generado el " + escape(fecha_hora(d["generado"])), st["subtitulo"]))

    # ---- Datos de la cuenta ----
    story.append(Paragraph("Datos de la cuenta", st["h1"]))
    filas = [
        [_neg("Usuario"), p["nombre_usuario"]],
        [_neg("Correo"), p["correo"] or "-"],
        [_neg("Miembro desde"), fecha_larga(p["fecha_registro"])],
        [_neg("Nivel"), str(p["nivel"])],
        [_neg("XP total"), str(p["xp_total"])],
        [_neg("Monedas"), str(p["monedas"])],
        [_neg("Racha actual"), _dias(p["racha_actual"])],
        [_neg("Mejor racha"), _dias(p["racha_maxima"])],
    ]
    story.append(_tabla(st, ["Dato", "Valor"], filas, [30, 70]))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "Progreso hacia el nivel " + str(p["nivel"] + 1) + ": " + str(p["xp_en_nivel"]) + " / " +
        str(p["xp_por_nivel"]) + " XP", st["cuerpo"]))
    story.append(_barra(100 * p["xp_en_nivel"] // max(1, p["xp_por_nivel"]), ancho=300, alto=10, color=AMARILLO))

    # ---- Avance general ----
    lecciones, labs, rr = d["lecciones"], d["laboratorios"], d["r"]
    hechas_lecciones = sum(1 for x in lecciones if x["veces"] > 0)
    hechos_labs = sum(1 for x in labs if x["veces"] > 0)
    hechas_r = sum(1 for x in rr if x["veces"] > 0)
    logros = d["logros"]
    obtenidos = [x for x in logros if x["obtenido"]]

    story.append(Paragraph("Avance general", st["h1"]))
    story.append(_kpis(st, [
        (str(hechas_lecciones) + " de " + str(len(lecciones)), "Lecciones del curso"),
        (str(hechos_labs) + " de " + str(len(labs)), "Laboratorios"),
        (str(hechas_r) + " de " + str(len(rr)), "Lecciones de R aprobadas"),
        (str(d["libre"]["completadas"]), "Prácticas del modo libre"),
    ]))
    story.append(Spacer(1, 6))
    story.append(_kpis(st, [
        (str(act["total"]), "Actividades terminadas"),
        (str(act["dias_activos"]), "Días en que estudiaste"),
        (_porcentaje(act["puntaje_medio"]), "Puntaje medio"),
        (str(len(obtenidos)) + " de " + str(len(logros)), "Logros obtenidos"),
    ]))

    # ---- Lecciones del curso ----
    story.append(Paragraph("Lecciones del curso", st["h1"]))
    if lecciones:
        filas = [[str(x["orden"]), x["titulo"], "Completada" if x["veces"] else "Pendiente", str(x["veces"]),
                  _porcentaje(x["mejor"]), _barra_puntaje(x["mejor"])] for x in lecciones]
        story.append(_tabla(st, ["#", "Lección", "Estado", "Veces", "Mejor puntaje", ""],
                            filas, [5, 41, 13, 8, 12, 21], centradas=(0, 2, 3, 4)))
    else:
        story.append(Paragraph("Todavía no hay lecciones cargadas en la base de datos.", st["cuerpo"]))
    story.append(Paragraph("Las barras en naranja marcan los puntajes por debajo del " + str(PUNTAJE_ACEPTABLE) +
                           " %: son las lecciones que más conviene repasar.", st["pequeno"]))

    # ---- Laboratorios y R ----
    story.append(Paragraph("Laboratorios interactivos", st["h1"]))
    story.append(_tabla(st, ["Laboratorio", "Estado", "Veces", "Mejor puntaje", ""],
                        [[x["titulo"], "Completado" if x["veces"] else "Pendiente", str(x["veces"]),
                          _porcentaje(x["mejor"]), _barra_puntaje(x["mejor"])] for x in labs],
                        [42, 14, 9, 13, 22], centradas=(1, 2, 3)))

    story.append(Paragraph("Aprende R", st["h1"]))
    story.append(_tabla(st, ["Lección de R", "Estado", "Veces", "Mejor puntaje", ""],
                        [[x["titulo"], "Aprobada" if x["veces"] else "Pendiente", str(x["veces"]),
                          _porcentaje(x["mejor"]), _barra_puntaje(x["mejor"])] for x in rr],
                        [42, 14, 9, 13, 22], centradas=(1, 2, 3)))

    # ---- Modo libre ----
    story.append(Paragraph("Modo libre", st["h1"]))
    libre = d["libre"]
    if libre["recientes"]:
        story.append(Paragraph("Prácticas completadas: " + str(libre["completadas"]) +
                               ". Se muestran las 10 más recientes.", st["cuerpo"]))
        story.append(_tabla(st, ["Documento", "Fecha", "Puntaje", "¿Con recompensa?"],
                            [[x["titulo"], fecha_larga(x["fecha"]), _porcentaje(x["puntaje"]),
                              "Sí" if x["con_recompensa"] else "No"] for x in libre["recientes"]],
                            [44, 26, 12, 18], centradas=(2, 3)))
    else:
        story.append(Paragraph("Todavía no has completado ninguna práctica del modo libre.", st["cuerpo"]))

    # ---- Actividad por tipo ----
    story.append(Paragraph("Actividad por tipo", st["h1"]))
    nombres = [("lecciones", "Lecciones del curso"), ("laboratorios", "Laboratorios"),
               ("r", "Aprende R"), ("libre", "Modo libre")]
    story.append(_tabla(st, ["Tipo de actividad", "Terminadas"],
                        [[n, str(act["por_tipo"].get(c, 0))] for c, n in nombres], [70, 30], centradas=(1,)))

    # ---- Logros ----
    story.append(Paragraph("Logros", st["h1"]))
    story.append(Paragraph("Has desbloqueado " + str(len(obtenidos)) + " de " + str(len(logros)) + " logros.",
                           st["cuerpo"]))
    if obtenidos:
        story.append(Paragraph("Obtenidos", st["h2"]))
        story.append(_tabla(st, ["Logro", "Descripción", "Fecha", "Monedas"],
                            [[x["nombre"], x["descripcion"], fecha_larga(x["fecha"]), "+" + str(x["recompensa"])]
                             for x in obtenidos],
                            [22, 44, 22, 12], centradas=(3,), color=VERDE))
    pendientes = [x for x in logros if not x["obtenido"]]
    if pendientes:
        story.append(Paragraph("Por conseguir", st["h2"]))
        story.append(_tabla(st, ["Logro", "Descripción", "Avance", "", "Monedas"],
                            [[x["nombre"], x["descripcion"], str(x["progreso"]) + " / " + str(x["objetivo"]),
                              _barra(100 * x["progreso"] // max(1, x["objetivo"]), color=AZUL),
                              "+" + str(x["recompensa"])] for x in pendientes],
                            [20, 38, 11, 19, 12], centradas=(2, 4), color=GRIS))

    story.append(Spacer(1, 12))
    story.append(Paragraph("Este resumen refleja el estado de la cuenta en el momento en que se generó.",
                           st["pequeno"]))
    return _construir(story, "Resumen de cuenta - " + p["nombre_usuario"], NOMBRE_APP + " · Resumen de cuenta")


# ======================================================================================
# PDF 2: documentación de la aplicación
# ======================================================================================

ARBOL = """aprendizaje/
|-- README.md
|-- .gitignore
|-- backend/
|   |-- app/
|   |   |-- main.py               arranca la aplicación y registra las rutas
|   |   |-- base_datos.py         conexión a MySQL (SQLAlchemy)
|   |   |-- modelos*.py           tablas (base, laboratorios, R y modo libre)
|   |   |-- esquemas*.py          datos que entran y salen de la API (Pydantic)
|   |   |-- logica.py             reglas del juego: XP, nivel, monedas y racha
|   |   |-- seguridad.py          contraseñas (bcrypt) y tokens (JWT)
|   |   |-- dependencias.py       identifica al usuario a partir del token
|   |   |-- servicio_*.py         logros, tienda y avatar, estudio, informes
|   |   |-- catalogo_*.py         lecciones, logros, objetos, laboratorios y R
|   |   |-- datos_estudio.py      historial convertido en variables
|   |   |-- modelo_abandono.py    regresión logística (riesgo de abandono)
|   |   |-- segmentacion.py       K-means (perfiles de estudiante)
|   |   |-- generador_preguntas.py / extractor_pdf.py   modo libre
|   |   |-- generador_pdf.py      dibuja los dos PDF de informes
|   |   `-- rutas/                un archivo por grupo de endpoints
|   |-- sembrar_datos.py          carga el curso inicial
|   |-- sembrar_estudiantes.py    crea estudiantes simulados (opcional)
|   |-- crear_base_datos.sql      crea la base de datos y el usuario de MySQL
|   |-- requirements.txt          dependencias de Python
|   `-- .env.ejemplo              modelo del archivo .env
`-- frontend/
    |-- *.html                    una página por pantalla
    |-- css/                      estilos, animaciones, temas y menú lateral
    `-- js/                       un archivo por página, api.js, avatar.js, labs/..."""


def generar_documentacion(info: Dict[str, Any]) -> bytes:
    """info: datos reunidos por servicio_informes.datos_documentacion()."""
    st = _estilos()
    r = info["reglas"]
    story: list = []

    # ---------- Portada e índice ----------
    story.append(Spacer(1, 60))
    story.append(Paragraph(escape(NOMBRE_APP), st["titulo"]))
    story.append(Paragraph("Documentación de la aplicación", st["subtitulo"]))
    story.append(Paragraph("Documento generado el " + escape(fecha_hora(info["generado"])) + ".", st["pequeno"]))
    story.append(Spacer(1, 20))
    story.append(Paragraph("Contenido", st["h2"]))
    secciones = [
        "Descripción general", "Tecnologías", "Funcionalidades", "Reglas del juego",
        "Contenido de aprendizaje", "Minería de datos aplicada en la propia app", "Arquitectura",
        "Estructura del proyecto", "Modelo de datos", "API", "Informes en PDF",
        "Seguridad y límites actuales", "Instalación y ejecución", "Dónde cambiar cada cosa",
    ]
    for i, nombre in enumerate(secciones, start=1):
        story.append(Paragraph(str(i) + ". " + escape(nombre), st["cuerpo"]))
    story.append(PageBreak())

    # ---------- 1. Descripción general ----------
    story.append(Paragraph("1. Descripción general", st["h1"]))
    story.append(Paragraph(
        "Aplicación web de aprendizaje gamificada, al estilo Duolingo, que enseña <b>minería de datos</b> y temas "
        "relacionados con lecciones cortas, ejercicios, puntos de experiencia, rachas diarias, logros y un avatar "
        "(un robot) que se personaliza con las monedas que se ganan al estudiar.", st["cuerpo"]))
    story.append(Paragraph(
        "Además del curso, la aplicación incluye laboratorios interactivos con gráficos, lecciones de programación "
        "en R que se ejecutan en el navegador, un modo libre que genera preguntas a partir de un PDF propio y un "
        "panel que aplica minería de datos al historial de cada estudiante.", st["cuerpo"]))
    story.append(Paragraph(
        "Un principio importante recorre toda la aplicación: <b>el servidor corrige las respuestas y calcula la XP, "
        "las monedas y los logros</b>. El navegador nunca recibe las respuestas correctas antes de enviar las suyas.",
        st["cuerpo"]))

    # ---------- 2. Tecnologías ----------
    story.append(Paragraph("2. Tecnologías", st["h1"]))
    story.append(_tabla(st, ["Capa", "Tecnología", "Para qué se usa"], [
        ["Servidor", "Python 3.12 y FastAPI", "API REST y entrega de las páginas del frontend"],
        ["Base de datos", "MySQL 8 y SQLAlchemy", "Usuarios, curso, progreso, logros, tienda y prácticas"],
        ["Seguridad", "bcrypt y PyJWT", "Contraseñas cifradas y sesión con token"],
        ["Frontend", "HTML, CSS y JavaScript", "Todas las pantallas, sin frameworks"],
        ["Gráficos", "SVG y canvas", "Avatar, laboratorios y gráficos del panel de estudio"],
        ["R en el navegador", "WebR (R en WebAssembly)", "Ejecutar código R sin instalar nada"],
        ["Modo libre", "pypdf y Anthropic (opcional)", "Leer PDF y redactar preguntas con IA"],
        ["Informes", "reportlab", "Generar los PDF de resumen y de documentación"],
    ], [20, 30, 50]))

    # ---------- 3. Funcionalidades ----------
    story.append(Paragraph("3. Funcionalidades", st["h1"]))
    story.append(_tabla(st, ["Función", "Qué hace"], [
        [_neg("Cuentas"), "Registro e inicio de sesión (usuario o correo), perfil y cierre de sesión."],
        [_neg("Curso y lecciones"), str(info["n_lecciones"]) + " lecciones de opción múltiple en dos unidades."],
        [_neg("Progreso"), "Cada lección terminada se guarda con su puntaje y su fecha."],
        [_neg("XP y niveles"), "XP por lección; el nivel sube con la XP acumulada."],
        [_neg("Racha diaria"), "Días seguidos en que se completa al menos una actividad."],
        [_neg("Monedas"), "Se ganan por respuestas correctas y por logros; se gastan en la tienda."],
        [_neg("Logros"), str(info["n_logros"]) + " logros con avance visible y recompensa en monedas."],
        [_neg("Avatar y tienda"), "Robot en SVG con " + str(info["n_items"]) +
         " objetos (colores, ropa y accesorios), por monedas o por nivel."],
        [_neg("Laboratorios"), str(len(info["laboratorios"])) +
         " laboratorios interactivos donde se ve cómo cambian los datos."],
        [_neg("Aprende R"), str(len(info["r"])) + " lecciones con teoría, ejemplos ejecutables y práctica corregida."],
        [_neg("Modo libre"), "Sube un PDF y genera preguntas sobre su contenido."],
        [_neg("Mis datos de estudio"), "Riesgo de abandono, perfil de estudiante y recomendación de qué estudiar."],
        [_neg("Temas y animaciones"), "Siete temas de color por usuario y animaciones de recompensa."],
        [_neg("Informes en PDF"), "Resumen de la cuenta y esta documentación, descargables."],
    ], [24, 76]))

    # ---------- 4. Reglas del juego ----------
    story.append(Paragraph("4. Reglas del juego", st["h1"]))
    story.append(_tabla(st, ["Regla", "Valor"], [
        ["Nivel", "Cada " + str(r["xp_por_nivel"]) + " XP se sube de nivel (nivel 1 con 0 a " +
         str(r["xp_por_nivel"] - 1) + " XP)."],
        ["Primera vez que se completa algo", "Se gana la XP completa de la actividad."],
        ["Repeticiones", "Se gana el " + str(int(round(r["repeticion"] * 100))) + " % de la XP y de las monedas."],
        ["Monedas por acierto", str(r["monedas_acierto"]) + " por respuesta correcta (primera vez)."],
        ["Racha", "Suma un día por cada jornada con al menos una actividad; si se salta un día, vuelve a 1."],
        ["Práctica de R", "Se aprueba con al menos " + str(r["puntaje_minimo_r"]) +
         " % de comprobaciones correctas; sin aprobar no se reparte nada."],
        ["Modo libre", "XP máxima de " + str(r["xp_libre"]) + " por práctica (proporcional al puntaje) y " +
         str(r["monedas_libre"]) + " moneda por acierto."],
        ["Límites del modo libre", "Máximo " + str(r["limite_recompensas"]) + " prácticas con recompensa al día y " +
         str(r["limite_generaciones"]) + " PDF por día; el mismo documento solo da recompensa una vez."],
    ], [32, 68]))

    # ---------- 5. Contenido de aprendizaje ----------
    story.append(Paragraph("5. Contenido de aprendizaje", st["h1"]))
    story.append(Paragraph("Lecciones del curso", st["h2"]))
    for titulo_unidad, titulos in info["unidades"]:
        story.append(Paragraph("<b>" + escape(titulo_unidad) + "</b>", st["cuerpo"]))
        _vinetas(story, st, [escape(t) for t in titulos])
    story.append(Paragraph("Laboratorios interactivos", st["h2"]))
    story.append(_tabla(st, ["Laboratorio", "Qué se observa"],
                        [[_neg(t), d_] for t, d_ in info["laboratorios"]], [30, 70]))
    story.append(Paragraph("Lecciones de R", st["h2"]))
    story.append(_tabla(st, ["Lección", "Contenido"],
                        [[_neg(t), d_] for t, d_ in info["r"]], [30, 70]))

    # ---------- 6. Minería de datos aplicada ----------
    story.append(Paragraph("6. Minería de datos aplicada en la propia app", st["h1"]))
    story.append(Paragraph(
        "El panel «Mis datos de estudio» aplica el proceso de minería de datos (datos, preparación, modelo, "
        "evaluación y uso) al historial de los propios estudiantes.", st["cuerpo"]))
    _vinetas(story, st, [
        "<b>Riesgo de abandono.</b> Regresión logística escrita a mano. Estima la probabilidad de que una persona no "
        "estudie en los próximos 14 días a partir de seis variables: días sin estudiar, constancia en los últimos 14 "
        "días, puntaje medio, tendencia de los resultados, variedad de actividades y racha. Se entrena con el 70 % de "
        "los estudiantes y se evalúa con el 30 % restante (exactitud, precisión, sensibilidad y matriz de confusión).",
        "<b>Segmentación de estudiantes.</b> K-means sobre cuatro variables estandarizadas. Se prueban de 3 a 5 grupos "
        "y se elige el de mejor silueta. Los grupos se nombran según su centroide: Constantes, Perfeccionistas, "
        "Esporádicos y En pausa.",
        "<b>Recomendación.</b> Sugiere repasar la lección con peor puntaje, continuar con la siguiente pendiente o, si "
        "el curso está terminado, practicar con laboratorios, R o el modo libre.",
        "<b>Generador de preguntas.</b> Con una clave de Anthropic, la IA redacta preguntas del PDF; sin clave, un "
        "generador local crea preguntas de definiciones y de completar frases.",
        "<b>Estudiantes simulados.</b> " + _cod("sembrar_estudiantes.py") + " crea estudiantes ficticios (sim_001, "
        "sim_002...) para tener datos con los que entrenar y practicar. Los usuarios reales nunca se tocan.",
    ])

    # ---------- 7. Arquitectura ----------
    story.append(Paragraph("7. Arquitectura", st["h1"]))
    story.append(Paragraph(
        "La aplicación tiene dos partes que se ejecutan con un solo comando: el <b>backend</b> (FastAPI), que expone "
        "la API bajo la ruta " + _cod("/api") + " y además sirve los archivos del <b>frontend</b>. No hace falta un "
        "segundo servidor.", st["cuerpo"]))
    _vinetas(story, st, [
        "El navegador guarda el token de sesión y lo envía en la cabecera " + _cod("Authorization: Bearer <token>") +
        " en cada petición protegida.",
        "Las rutas protegidas usan la dependencia " + _cod("obtener_usuario_actual") +
        ", que lee el token y devuelve el usuario o responde 401.",
        "Las reglas del juego viven en un solo lugar (" + _cod("logica.py") + ") y las comparten lecciones, "
        "laboratorios, prácticas de R y modo libre.",
        "Al terminar una actividad, todo se guarda en una sola transacción: progreso, XP, monedas, racha y logros. "
        "O se guarda todo o no se guarda nada.",
        "Los catálogos de logros, objetos y lecciones se cargan o actualizan solos al arrancar el servidor, sin "
        "borrar usuarios ni progreso.",
        "El código R se ejecuta en el navegador con WebR; el servidor solo compara los resultados con los valores "
        "esperados, que nunca salen del servidor.",
    ])

    # ---------- 8. Estructura ----------
    story.append(Paragraph("8. Estructura del proyecto", st["h1"]))
    story.append(_bloque_codigo(st, ARBOL))

    # ---------- 9. Modelo de datos ----------
    story.append(Paragraph("9. Modelo de datos", st["h1"]))
    story.append(_tabla(st, ["Tabla", "Contenido"], [
        [_cod("cursos"), "Cursos disponibles."],
        [_cod("lecciones"), "Lecciones de cada curso, con su orden y su XP."],
        [_cod("ejercicios"), "Ejercicios de cada lección, con opciones, respuesta correcta y explicación."],
        [_cod("usuarios"), "Cuenta, XP, nivel, monedas y racha de cada persona."],
        [_cod("progreso_lecciones"), "Un registro por cada vez que se termina una lección."],
        [_cod("logros / logros_usuario"), "Catálogo de logros y los que ha desbloqueado cada usuario."],
        [_cod("items_avatar / items_usuario"), "Catálogo de objetos y los que cada usuario compró."],
        [_cod("avatar_usuario"), "Lo que lleva puesto cada usuario."],
        [_cod("progreso_laboratorios"), "Un registro por cada laboratorio terminado."],
        [_cod("progreso_r"), "Un registro por cada práctica de R aprobada."],
        [_cod("sesiones_libres"), "Prácticas del modo libre: preguntas generadas y resultado (el PDF no se guarda)."],
    ], [32, 68]))
    story.append(Paragraph(
        "Las tablas se crean solas al arrancar el servidor. Los laboratorios y las lecciones de R viven en "
        "catálogos de Python, no en la base de datos.", st["pequeno"]))

    # ---------- 10. API ----------
    story.append(Paragraph("10. API", st["h1"]))
    story.append(_tabla(st, ["Método y ruta", "Qué hace", "Sesión"], [
        [_cod("POST /api/auth/registro"), "Crea una cuenta y devuelve el token.", "No"],
        [_cod("POST /api/auth/login"), "Inicia sesión con usuario o correo.", "No"],
        [_cod("GET /api/cursos, /api/lecciones/{id}"), "Contenido (sin respuestas correctas).", "No"],
        [_cod("POST /api/ejercicios/{id}/responder"), "Corrige una respuesta.", "No"],
        [_cod("GET /api/usuario/actual"), "Perfil: XP, nivel, monedas y racha.", "Sí"],
        [_cod("GET /api/progreso"), "Lecciones completadas.", "Sí"],
        [_cod("POST /api/lecciones/{id}/completar"), "Guarda la lección y reparte recompensas.", "Sí"],
        [_cod("GET /api/logros"), "Logros y avance de cada uno.", "Sí"],
        [_cod("GET /api/tienda, POST /api/tienda/comprar/{id}"), "Ver y comprar objetos.", "Sí"],
        [_cod("GET/PUT /api/avatar"), "Ver y guardar el avatar.", "Sí"],
        [_cod("GET /api/laboratorios, /{codigo}"), "Lista y detalle de laboratorios.", "Sí"],
        [_cod("POST /api/laboratorios/{codigo}/completar"), "Corrige y reparte recompensas.", "Sí"],
        [_cod("GET /api/r, /api/r/{codigo}"), "Lecciones de R (sin valores esperados).", "Sí"],
        [_cod("POST /api/r/{codigo}/evaluar"), "Corrige la práctica de R.", "Sí"],
        [_cod("GET /api/libre, POST /api/libre/generar"), "Historial y generación de preguntas desde un PDF.", "Sí"],
        [_cod("GET /api/libre/{id}, POST .../completar"), "Retomar y completar una práctica libre.", "Sí"],
        [_cod("GET /api/estudio, /api/estudio/inicio"), "Panel de estudio y recomendación.", "Sí"],
        [_cod("GET /api/informes/resumen"), "PDF con el resumen de la cuenta.", "Sí"],
        [_cod("GET /api/informes/documentacion"), "PDF con esta documentación.", "Sí"],
    ], [40, 48, 12], centradas=(2,)))
    story.append(Paragraph(
        "La documentación interactiva de la API está en " + _cod("/docs") + " cuando el servidor está en marcha.",
        st["pequeno"]))

    # ---------- 11. Informes en PDF ----------
    story.append(Paragraph("11. Informes en PDF", st["h1"]))
    story.append(Paragraph(
        "La pantalla «Informes PDF» del menú permite descargar dos documentos. Los PDF se generan en el servidor "
        "al momento de pedirlos (no se guardan en disco), así que siempre reflejan el estado actual.", st["cuerpo"]))
    _vinetas(story, st, [
        "<b>Resumen de la cuenta:</b> datos del usuario, nivel y XP, avance en lecciones, laboratorios, R y modo "
        "libre, actividad por tipo y logros obtenidos o pendientes.",
        "<b>Documentación de la aplicación:</b> este documento.",
        "El navegador los pide con el token de sesión y los descarga; sin sesión iniciada no se pueden obtener.",
        "El diseño de ambos está en " + _cod("generador_pdf.py") + "; las consultas, en " +
        _cod("servicio_informes.py") + "; las rutas, en " + _cod("rutas/informes.py") + ".",
    ])

    # ---------- 12. Seguridad ----------
    story.append(Paragraph("12. Seguridad y límites actuales", st["h1"]))
    _vinetas(story, st, [
        "Las contraseñas se guardan con <b>bcrypt</b>, nunca en texto plano.",
        "La sesión usa un <b>token JWT</b> que dura 24 horas y el navegador lo guarda en " + _cod("localStorage") + ".",
        "El archivo " + _cod(".env") + " es secreto y nunca se sube a GitHub (está en " + _cod(".gitignore") + ").",
        "Es un proyecto de aprendizaje. Antes de publicarlo en internet habría que añadir HTTPS, límite de intentos "
        "de inicio de sesión y guardar el token en una cookie HttpOnly.",
        "La racha usa la fecha del equipo donde corre el servidor; en un servidor de otra zona horaria habría que "
        "fijar la zona.",
        "Los modelos del panel de estudio son una demostración del proceso de minería de datos: con estudiantes "
        "simulados no son un diagnóstico real.",
    ])

    # ---------- 13. Instalación ----------
    story.append(Paragraph("13. Instalación y ejecución", st["h1"]))
    story.append(Paragraph(
        "Requisitos: Python 3.11 o superior (se recomienda 3.12), MySQL 8 y un navegador moderno. "
        "Los comandos de ejemplo son para Windows (PowerShell).", st["cuerpo"]))
    _vinetas(story, st, [
        "<b>1. Base de datos.</b> Cambia la clave en " + _cod("backend/crear_base_datos.sql") +
        " y ejecútalo con " + _cod("mysql -u root -p -e \"source backend/crear_base_datos.sql\"") + ".",
        "<b>2. Entorno.</b> Crea un entorno con Python 3.12 (conda o venv) y, desde " + _cod("backend") +
        ", instala con " + _cod("pip install -r requirements.txt") + ".",
        "<b>3. Variables.</b> Copia " + _cod(".env.ejemplo") + " a " + _cod(".env") + " y completa los valores.",
        "<b>4. Contenido.</b> La primera vez, ejecuta " + _cod("python sembrar_datos.py") + ".",
        "<b>5. Servidor.</b> Ejecuta " + _cod("uvicorn app.main:app --reload") + " y abre " +
        _cod("http://127.0.0.1:8000/") + ".",
    ])
    story.append(Spacer(1, 4))
    story.append(_tabla(st, ["Variable del .env", "¿Obligatoria?", "Para qué sirve"], [
        [_cod("URL_BASE_DATOS"), "Sí", "Conexión a MySQL: mysql+pymysql://USUARIO:CLAVE@servidor:3306/aprendizaje"],
        [_cod("CLAVE_SECRETA"), "Sí", "Firma los tokens de sesión. Genérala con secrets.token_hex(32)."],
        [_cod("CLAVE_ANTHROPIC"), "No", "Permite que una IA redacte las preguntas del modo libre."],
        [_cod("MODELO_IA"), "No", "Modelo de IA a usar en el modo libre."],
    ], [26, 14, 60], centradas=(1,)))
    story.append(Paragraph(
        "Para tener datos con los que practicar el panel de estudio, ejecuta " + _cod("python sembrar_estudiantes.py") +
        " y reinicia el servidor.", st["pequeno"]))

    # ---------- 14. Dónde cambiar ----------
    story.append(Paragraph("14. Dónde cambiar cada cosa", st["h1"]))
    story.append(_tabla(st, ["Quiero cambiar...", "Archivo"], [
        ["Preguntas, lecciones o cursos", Marcado(_cod("backend/app/catalogo_lecciones.py") + " y " + _cod("sembrar_datos.py"))],
        ["XP por nivel, % de repetición, monedas por acierto", _cod("backend/app/logica.py")],
        ["Logros", _cod("backend/app/catalogo_logros.py")],
        ["Objetos de la tienda", _cod("backend/app/catalogo_items.py")],
        ["Laboratorios (preguntas y XP)", Marcado(_cod("backend/app/catalogo_laboratorios.py") + " y " + _cod("frontend/js/labs/"))],
        ["Lecciones y prácticas de R", _cod("backend/app/catalogo_r.py")],
        ["Dibujo del robot, ropa y accesorios", _cod("frontend/js/avatar.js")],
        ["Colores de los temas", Marcado(_cod("frontend/css/temas.css") + " y " + _cod("frontend/js/tema.js"))],
        ["Duración de la sesión", Marcado(_cod("backend/app/seguridad.py") + " (MINUTOS_EXPIRACION)")],
        ["Diseño de los PDF", _cod("backend/app/generador_pdf.py")],
    ], [45, 55]))
    story.append(Paragraph(
        "Si cambias un archivo .js o .css, recarga con Ctrl + F5 para que el navegador no use la versión guardada.",
        st["pequeno"]))

    return _construir(story, "Documentación - " + NOMBRE_APP, NOMBRE_APP + " · Documentación")
