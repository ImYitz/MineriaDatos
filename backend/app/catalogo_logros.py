# Catálogo de logros del juego.
#
# Para agregar un logro nuevo basta con añadir una línea a esta lista y reiniciar
# el servidor. Los tipos de condición que existen hoy son:
#   "lecciones_completadas"    -> cuántas lecciones DISTINTAS ha completado
#   "leccion_perfecta"         -> cuántas veces ha terminado una lección sin errores
#   "laboratorios_completados" -> cuántos laboratorios DISTINTOS ha completado
#   "laboratorio_perfecto"     -> cuántas veces ha respondido bien todo un laboratorio
#   "lecciones_r_completadas"  -> cuántas lecciones de R DISTINTAS ha aprobado
#   "practica_r_perfecta"      -> cuántas veces ha aprobado una práctica de R sin fallos
#   "libre_completadas"        -> cuántas prácticas del modo libre ha completado
#   "contrarreloj_partidas"    -> cuántas partidas de contrarreloj ha jugado (con alguna respuesta)
#   "contrarreloj_mejor"       -> su mejor marca de aciertos en una partida de contrarreloj
#   "contrarreloj_completo"    -> cuántas partidas de contrarreloj ha terminado respondiendo TODAS las preguntas
#   "actividades_totales"      -> cuántas actividades ha terminado (de cualquier tipo)
#   "tipos_actividad"          -> cuántos tipos de actividad distintos ha usado (máximo 4)
#   "dias_activos"             -> en cuántos días distintos ha estudiado
#   "dias_fin_de_semana"       -> en cuántos sábados o domingos distintos ha estudiado
#   "madrugador"               -> cuántas actividades ha terminado antes de las 7:00
#   "noctambulo"               -> cuántas actividades ha terminado después de las 22:00
#   "racha"                    -> días seguidos estudiando
#   "nivel"                    -> nivel alcanzado
# (Si quieres un tipo nuevo, hay que añadirlo también en servicio_logros.py)
#
# Los iconos están definidos en ICONOS_LOGRO en frontend/js/api.js
# (si un icono no está allí, se muestra el icono por defecto 🏅).
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
     "descripcion": "Completa los 5 laboratorios distintos", "icono": "trofeo",
     "tipo_condicion": "laboratorios_completados", "valor_objetivo": 5, "recompensa_monedas": 50},
    # ---- Avance en el curso ----
    {"codigo": "siete_lecciones", "nombre": "Mitad del camino",
     "descripcion": "Completa 7 lecciones distintas", "icono": "medalla",
     "tipo_condicion": "lecciones_completadas", "valor_objetivo": 7, "recompensa_monedas": 40},
    {"codigo": "curso_completo", "nombre": "Curso completo",
     "descripcion": "Completa las 14 lecciones del curso", "icono": "trofeo",
     "tipo_condicion": "lecciones_completadas", "valor_objetivo": 14, "recompensa_monedas": 80},
    # ---- Aprende R (Etapa 7) ----
    {"codigo": "primera_practica_r", "nombre": "Primer script",
     "descripcion": "Aprueba tu primera práctica de R", "icono": "codigo",
     "tipo_condicion": "lecciones_r_completadas", "valor_objetivo": 1, "recompensa_monedas": 15},
    {"codigo": "practica_r_perfecta", "nombre": "Código sin fallos",
     "descripcion": "Aprueba una práctica de R con todas las comprobaciones correctas", "icono": "diana",
     "tipo_condicion": "practica_r_perfecta", "valor_objetivo": 1, "recompensa_monedas": 20},
    {"codigo": "todas_practicas_r", "nombre": "Programador de datos",
     "descripcion": "Aprueba las 6 prácticas de R", "icono": "codigo",
     "tipo_condicion": "lecciones_r_completadas", "valor_objetivo": 6, "recompensa_monedas": 60},
    # ======== Logros nuevos ========
    # ---- Avance en el curso (más) ----
    {"codigo": "cinco_lecciones", "nombre": "Calentando motores",
     "descripcion": "Completa 5 lecciones distintas", "icono": "cohete",
     "tipo_condicion": "lecciones_completadas", "valor_objetivo": 5, "recompensa_monedas": 20},
    {"codigo": "diez_lecciones", "nombre": "Imparable",
     "descripcion": "Completa 10 lecciones distintas", "icono": "rayo",
     "tipo_condicion": "lecciones_completadas", "valor_objetivo": 10, "recompensa_monedas": 50},
    # ---- Perfección ----
    {"codigo": "perfecta_3", "nombre": "Perfeccionista",
     "descripcion": "Termina 3 lecciones sin ningún error", "icono": "gema",
     "tipo_condicion": "leccion_perfecta", "valor_objetivo": 3, "recompensa_monedas": 30},
    {"codigo": "perfecta_10", "nombre": "Impecable",
     "descripcion": "Termina 10 lecciones sin ningún error", "icono": "corona",
     "tipo_condicion": "leccion_perfecta", "valor_objetivo": 10, "recompensa_monedas": 70},
    # ---- Laboratorios y R (más) ----
    {"codigo": "tres_laboratorios", "nombre": "Investigador",
     "descripcion": "Completa 3 laboratorios distintos", "icono": "lupa",
     "tipo_condicion": "laboratorios_completados", "valor_objetivo": 3, "recompensa_monedas": 25},
    {"codigo": "laboratorio_perfecto_3", "nombre": "Mente de laboratorio",
     "descripcion": "Responde bien todo un laboratorio en 3 ocasiones", "icono": "cerebro",
     "tipo_condicion": "laboratorio_perfecto", "valor_objetivo": 3, "recompensa_monedas": 40},
    {"codigo": "tres_practicas_r", "nombre": "Analista en formación",
     "descripcion": "Aprueba 3 lecciones de R distintas", "icono": "codigo",
     "tipo_condicion": "lecciones_r_completadas", "valor_objetivo": 3, "recompensa_monedas": 30},
    {"codigo": "practica_r_perfecta_3", "nombre": "Código limpio",
     "descripcion": "Aprueba 3 prácticas de R sin ningún fallo", "icono": "codigo",
     "tipo_condicion": "practica_r_perfecta", "valor_objetivo": 3, "recompensa_monedas": 40},
    # ---- Modo libre ----
    {"codigo": "primer_libre", "nombre": "Autodidacta",
     "descripcion": "Completa tu primera práctica del modo libre", "icono": "libro",
     "tipo_condicion": "libre_completadas", "valor_objetivo": 1, "recompensa_monedas": 15},
    {"codigo": "cinco_libres", "nombre": "Biblioteca personal",
     "descripcion": "Completa 5 prácticas del modo libre", "icono": "libro",
     "tipo_condicion": "libre_completadas", "valor_objetivo": 5, "recompensa_monedas": 40},
    # ---- Constancia ----
    {"codigo": "racha_14", "nombre": "Dos semanas",
     "descripcion": "Estudia 14 días seguidos", "icono": "fuego",
     "tipo_condicion": "racha", "valor_objetivo": 14, "recompensa_monedas": 60},
    {"codigo": "racha_30", "nombre": "Hábito de hierro",
     "descripcion": "Estudia 30 días seguidos", "icono": "corona",
     "tipo_condicion": "racha", "valor_objetivo": 30, "recompensa_monedas": 120},
    {"codigo": "dias_10", "nombre": "Presente",
     "descripcion": "Estudia en 10 días distintos", "icono": "calendario",
     "tipo_condicion": "dias_activos", "valor_objetivo": 10, "recompensa_monedas": 30},
    {"codigo": "dias_30", "nombre": "Veterano",
     "descripcion": "Estudia en 30 días distintos", "icono": "medalla",
     "tipo_condicion": "dias_activos", "valor_objetivo": 30, "recompensa_monedas": 80},
    # ---- Horarios ----
    {"codigo": "madrugador", "nombre": "Madrugador",
     "descripcion": "Completa una actividad antes de las 7:00 a. m.", "icono": "sol",
     "tipo_condicion": "madrugador", "valor_objetivo": 1, "recompensa_monedas": 20},
    {"codigo": "noctambulo", "nombre": "Noctámbulo",
     "descripcion": "Completa una actividad después de las 10:00 p. m.", "icono": "luna",
     "tipo_condicion": "noctambulo", "valor_objetivo": 1, "recompensa_monedas": 20},
    {"codigo": "fin_de_semana", "nombre": "Sin descanso",
     "descripcion": "Estudia en 4 días de fin de semana distintos", "icono": "confeti",
     "tipo_condicion": "dias_fin_de_semana", "valor_objetivo": 4, "recompensa_monedas": 35},
    # ---- Niveles ----
    {"codigo": "nivel_5", "nombre": "Estudiante avanzado",
     "descripcion": "Alcanza el nivel 5", "icono": "medalla",
     "tipo_condicion": "nivel", "valor_objetivo": 5, "recompensa_monedas": 30},
    {"codigo": "nivel_10", "nombre": "Experto",
     "descripcion": "Alcanza el nivel 10", "icono": "trofeo",
     "tipo_condicion": "nivel", "valor_objetivo": 10, "recompensa_monedas": 70},
    {"codigo": "nivel_15", "nombre": "Maestro de datos",
     "descripcion": "Alcanza el nivel 15", "icono": "corona",
     "tipo_condicion": "nivel", "valor_objetivo": 15, "recompensa_monedas": 120},
    # ---- Variedad y volumen ----
    {"codigo": "explorador", "nombre": "Explorador",
     "descripcion": "Usa los 4 tipos de actividad: lecciones, laboratorios, R y modo libre", "icono": "brujula",
     "tipo_condicion": "tipos_actividad", "valor_objetivo": 4, "recompensa_monedas": 30},
    {"codigo": "actividades_10", "nombre": "Dedicación",
     "descripcion": "Termina 10 actividades", "icono": "rayo",
     "tipo_condicion": "actividades_totales", "valor_objetivo": 10, "recompensa_monedas": 25},
    {"codigo": "actividades_25", "nombre": "Incansable",
     "descripcion": "Termina 25 actividades", "icono": "cohete",
     "tipo_condicion": "actividades_totales", "valor_objetivo": 25, "recompensa_monedas": 50},
    {"codigo": "actividades_50", "nombre": "Máquina de estudiar",
     "descripcion": "Termina 50 actividades", "icono": "robot",
     "tipo_condicion": "actividades_totales", "valor_objetivo": 50, "recompensa_monedas": 100},
    # ---- Contrarreloj (Etapa 11) ----
    {"codigo": "primera_contrarreloj", "nombre": "Contra el reloj",
     "descripcion": "Juega tu primera partida de contrarreloj", "icono": "rayo",
     "tipo_condicion": "contrarreloj_partidas", "valor_objetivo": 1, "recompensa_monedas": 15},
    {"codigo": "contrarreloj_10", "nombre": "Rápido y certero",
     "descripcion": "Acierta 10 preguntas en una sola partida de contrarreloj", "icono": "cohete",
     "tipo_condicion": "contrarreloj_mejor", "valor_objetivo": 10, "recompensa_monedas": 40},
    {"codigo": "contrarreloj_completo", "nombre": "Maestro del tiempo",
     "descripcion": "Responde todas las preguntas de una partida de contrarreloj antes de que se acabe el tiempo",
     "icono": "trofeo",
     "tipo_condicion": "contrarreloj_completo", "valor_objetivo": 1, "recompensa_monedas": 60},
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
