# Catálogo de logros del juego.
#
# Para agregar un logro nuevo basta con añadir una línea a esta lista y reiniciar
# el servidor. Los tipos de condición que existen hoy son:
#   "lecciones_completadas"    -> cuántas lecciones DISTINTAS ha completado
#   "leccion_perfecta"         -> cuántas veces ha terminado una lección sin errores
#   "laboratorios_completados" -> cuántos laboratorios DISTINTOS ha completado
#   "laboratorio_perfecto"     -> cuántas veces ha respondido bien todo un laboratorio
#   "racha"                    -> días seguidos estudiando
#   "nivel"                    -> nivel alcanzado
# (Si quieres un tipo nuevo, hay que añadirlo también en servicio_logros.py)
#
# Icono "matraz": para que se vea 🧪 añade  matraz: "🧪",  a ICONOS_LOGRO en frontend/js/api.js
# (si no lo añades, se muestra el icono por defecto 🏅).
from sqlalchemy.orm import Session
from . import modelos

CATALOGO = [
    {"codigo": "primera_leccion", "nombre": "Primer paso",
     "descripcion": "Completa tu primera lección", "icono": "estrella",
     "tipo_condicion": "lecciones_completadas", "valor_objetivo": 1, "recompensa_monedas": 10},
    {"codigo": "leccion_perfecta", "nombre": "Lección perfecta",
     "descripcion": "Termina una lección sin ningún error", "icono": "diana",
     "tipo_condicion": "leccion_perfecta", "valor_objetivo": 1, "recompensa_monedas": 15},
    {"codigo": "nivel_2", "nombre": "Subiendo",
     "descripcion": "Alcanza el nivel 2", "icono": "medalla",
     "tipo_condicion": "nivel", "valor_objetivo": 2, "recompensa_monedas": 10},
    {"codigo": "tres_lecciones", "nombre": "Aprendiz",
     "descripcion": "Completa 3 lecciones distintas", "icono": "trofeo",
     "tipo_condicion": "lecciones_completadas", "valor_objetivo": 3, "recompensa_monedas": 30},
    {"codigo": "racha_3", "nombre": "Constancia",
     "descripcion": "Estudia 3 días seguidos", "icono": "fuego",
     "tipo_condicion": "racha", "valor_objetivo": 3, "recompensa_monedas": 15},
    {"codigo": "racha_7", "nombre": "Semana completa",
     "descripcion": "Estudia 7 días seguidos", "icono": "calendario",
     "tipo_condicion": "racha", "valor_objetivo": 7, "recompensa_monedas": 40},
    # ---- Laboratorios (Etapa 6) ----
    {"codigo": "primer_laboratorio", "nombre": "Manos a la obra",
     "descripcion": "Completa tu primer laboratorio", "icono": "matraz",
     "tipo_condicion": "laboratorios_completados", "valor_objetivo": 1, "recompensa_monedas": 15},
    {"codigo": "laboratorio_perfecto", "nombre": "Experimento perfecto",
     "descripcion": "Responde bien todas las preguntas de un laboratorio", "icono": "diana",
     "tipo_condicion": "laboratorio_perfecto", "valor_objetivo": 1, "recompensa_monedas": 20},
    {"codigo": "todos_laboratorios", "nombre": "Científico de datos",
     "descripcion": "Completa los 4 laboratorios distintos", "icono": "trofeo",
     "tipo_condicion": "laboratorios_completados", "valor_objetivo": 4, "recompensa_monedas": 50},
    # ---- Avance en el curso ----
    {"codigo": "siete_lecciones", "nombre": "Mitad del camino",
     "descripcion": "Completa 7 lecciones distintas", "icono": "medalla",
     "tipo_condicion": "lecciones_completadas", "valor_objetivo": 7, "recompensa_monedas": 40},
    {"codigo": "curso_completo", "nombre": "Curso completo",
     "descripcion": "Completa las 14 lecciones del curso", "icono": "trofeo",
     "tipo_condicion": "lecciones_completadas", "valor_objetivo": 14, "recompensa_monedas": 80},
]


def asegurar_logros(bd: Session) -> None:
    """Se ejecuta al arrancar el servidor: crea los logros que falten y actualiza los demás.
    Se puede ejecutar muchas veces sin duplicar nada."""
    for datos in CATALOGO:
        logro = bd.query(modelos.Logro).filter(modelos.Logro.codigo == datos["codigo"]).first()
        if logro is None:
            bd.add(modelos.Logro(**datos))
        else:
            for campo, valor in datos.items():
                setattr(logro, campo, valor)
    bd.commit()
