# Reglas del juego (XP, niveles, monedas, rachas y corrección de respuestas).
# Se dejan en un archivo aparte para que sea fácil cambiarlas en un solo lugar.
from datetime import date, timedelta

XP_POR_NIVEL = 20             # cada 20 XP se sube de nivel
PORCENTAJE_REPETICION = 0.30  # al repetir una lección se gana el 30% de la XP y de las monedas
MONEDAS_POR_ACIERTO = 2       # monedas por cada respuesta correcta (la primera vez)


def calcular_nivel(xp_total: int) -> int:
    """Nivel 1 con 0-19 XP, nivel 2 con 20-39 XP, y así sucesivamente."""
    return xp_total // XP_POR_NIVEL + 1


def calcular_xp_ganada(xp_recompensa: int, es_primera_vez: bool) -> int:
    """Primera vez: XP completa. Repeticiones: 30% (redondeado)."""
    if es_primera_vez:
        return xp_recompensa
    return int(xp_recompensa * PORCENTAJE_REPETICION + 0.5)


def calcular_monedas(aciertos: int, es_primera_vez: bool) -> int:
    """2 monedas por acierto la primera vez; en repeticiones, el 30% (así no se 'cultivan')."""
    base = aciertos * MONEDAS_POR_ACIERTO
    if es_primera_vez:
        return base
    return int(base * PORCENTAJE_REPETICION + 0.5)


def es_respuesta_correcta(enviada: str, correcta: str) -> bool:
    """Compara sin importar mayúsculas ni espacios sobrantes."""
    return enviada.strip().lower() == correcta.strip().lower()


# ---------- Racha diaria ----------

def fecha_hoy() -> date:
    """La fecha de hoy según el reloj de la computadora donde corre el servidor.
    Está en una función aparte para poder simular otras fechas en las pruebas."""
    return date.today()


def actualizar_racha(usuario, hoy: date) -> None:
    """Se llama cada vez que el usuario completa una lección.

    - Ya estudió hoy             -> la racha no cambia
    - Estudió ayer               -> la racha sube en 1
    - Antes de ayer (o nunca)    -> la racha empieza de nuevo en 1
    """
    ultima = usuario.ultima_fecha_estudio
    if ultima == hoy:
        return
    if ultima == hoy - timedelta(days=1):
        usuario.racha_actual += 1
    else:
        usuario.racha_actual = 1
    usuario.ultima_fecha_estudio = hoy
    usuario.racha_maxima = max(usuario.racha_maxima, usuario.racha_actual)


def racha_vigente(usuario, hoy: date) -> int:
    """La racha que se muestra. Si pasó más de un día sin estudiar, la racha ya se rompió
    (aunque en la base siga el número viejo hasta que vuelva a estudiar)."""
    ultima = usuario.ultima_fecha_estudio
    if ultima is None or ultima < hoy - timedelta(days=1):
        return 0
    return usuario.racha_actual
