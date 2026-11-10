# Modelo de riesgo de abandono (Etapa 9): regresión logística escrita a mano, sin librerías externas.
#
# Idea: a partir de cómo estudia una persona (días sin estudiar, constancia, puntajes...) estimar la
# probabilidad de que deje de estudiar. Es un problema de CLASIFICACIÓN (abandona / continúa).
#
# IMPORTANTE (honestidad de los datos): con pocos usuarios reales no hay datos suficientes para
# entrenar un modelo de verdad. Por eso el modelo se entrena con estudiantes SIMULADOS, generados
# con una semilla fija (siempre salen los mismos). Es una demostración del proceso de minería de
# datos, no un diagnóstico real. Cuando haya muchos usuarios reales, basta con reemplazar
# generar_estudiantes() por una consulta a la base de datos con el mismo formato.
#
# Proceso (mismo orden que CRISP-DM): datos -> preparación (estandarizar) -> modelo -> evaluación.
import math
import random
from dataclasses import dataclass
from functools import lru_cache
from typing import Dict, List, Tuple

# Variables que usa el modelo (el orden importa; coincide con servicio_estudio.py)
CARACTERISTICAS = [
    "dias_sin_estudiar",   # días desde la última actividad (0 a 30)
    "actividad_14",        # fracción de los últimos 14 días en que estudió (0 a 1)
    "puntaje_medio",       # promedio de los últimos resultados (0 a 100)
    "tendencia",           # últimos resultados menos los anteriores (-50 a 50)
    "variedad",            # tipos de actividad distintos usados (0 a 4)
    "racha",               # días seguidos estudiando (0 a 14)
]

CANTIDAD_ENTRENAMIENTO = 500
CANTIDAD_PRUEBA = 200
SEMILLA = 2026


def _limitar(valor: float, minimo: float, maximo: float) -> float:
    return max(minimo, min(maximo, valor))


def _sigmoide(z: float) -> float:
    z = _limitar(z, -35.0, 35.0)
    return 1.0 / (1.0 + math.exp(-z))


def generar_estudiantes(cantidad: int, azar: random.Random) -> List[Tuple[List[float], int]]:
    """Estudiantes simulados: (variables, abandona) con abandona = 1 si deja de estudiar.

    Cada estudiante tiene un "compromiso" oculto g (positivo = muy comprometido). Las variables son
    observaciones ruidosas de g, y el abandono depende de g más algo de azar. Así el modelo tiene
    que aprender la relación a partir del ruido, como pasaría con datos reales."""
    filas = []
    for _ in range(cantidad):
        g = azar.gauss(0, 1)
        dias = _limitar(round(math.exp(1.2 - 0.9 * g + 0.5 * azar.gauss(0, 1))), 0, 30)
        actividad = _limitar(0.35 + 0.2 * g + 0.08 * azar.gauss(0, 1), 0, 1)
        puntaje = _limitar(65 + 10 * g + 12 * azar.gauss(0, 1), 0, 100)
        tendencia = _limitar(4 * g + 10 * azar.gauss(0, 1), -50, 50)
        variedad = _limitar(round(2 + 0.8 * g + 0.7 * azar.gauss(0, 1)), 0, 4)
        racha = _limitar(round(2 + 1.5 * g + azar.gauss(0, 1)), 0, 14)
        abandona = 1 if (-1.5 * g + 0.9 * azar.gauss(0, 1)) > 0.4 else 0
        filas.append(([float(dias), actividad, puntaje, tendencia, float(variedad), float(racha)], abandona))
    return filas


@dataclass
class Modelo:
    medias: List[float]
    desvios: List[float]
    pesos: List[float]
    sesgo: float
    metricas: Dict

    def estandarizar(self, x: List[float]) -> List[float]:
        return [(v - m) / d for v, m, d in zip(x, self.medias, self.desvios)]

    def probabilidad(self, x: List[float]) -> float:
        z = self.estandarizar(x)
        return _sigmoide(sum(w * v for w, v in zip(self.pesos, z)) + self.sesgo)

    def contribuciones(self, x: List[float]) -> List[float]:
        """Cuánto empuja cada variable hacia "abandona" (+) o hacia "continúa" (-)."""
        z = self.estandarizar(x)
        return [w * v for w, v in zip(self.pesos, z)]


def _entrenar(X: List[List[float]], y: List[int], epocas: int = 400, tasa: float = 0.3, l2: float = 0.01):
    """Descenso de gradiente para la regresión logística (con una pequeña penalización L2)."""
    n, k = len(X), len(X[0])
    pesos, sesgo = [0.0] * k, 0.0
    for _ in range(epocas):
        grad = [0.0] * k
        grad_sesgo = 0.0
        for xi, yi in zip(X, y):
            error = _sigmoide(sum(pesos[j] * xi[j] for j in range(k)) + sesgo) - yi
            for j in range(k):
                grad[j] += error * xi[j]
            grad_sesgo += error
        for j in range(k):
            pesos[j] -= tasa * (grad[j] / n + l2 * pesos[j])
        sesgo -= tasa * grad_sesgo / n
    return pesos, sesgo


def _porcentaje(parte: int, total: int) -> int:
    return int(round(100 * parte / total)) if total else 0


@lru_cache(maxsize=1)
def obtener_modelo() -> Modelo:
    """Entrena el modelo la primera vez que se pide (tarda menos de un segundo) y lo guarda en memoria."""
    azar = random.Random(SEMILLA)
    entrenamiento = generar_estudiantes(CANTIDAD_ENTRENAMIENTO, azar)
    prueba = generar_estudiantes(CANTIDAD_PRUEBA, azar)

    k = len(CARACTERISTICAS)
    medias = [sum(f[0][j] for f in entrenamiento) / len(entrenamiento) for j in range(k)]
    desvios = [
        math.sqrt(sum((f[0][j] - medias[j]) ** 2 for f in entrenamiento) / len(entrenamiento)) or 1.0
        for j in range(k)
    ]

    def estandar(x):
        return [(v - m) / d for v, m, d in zip(x, medias, desvios)]

    pesos, sesgo = _entrenar([estandar(f[0]) for f in entrenamiento], [f[1] for f in entrenamiento])
    modelo = Modelo(medias, desvios, pesos, sesgo, {})

    # Evaluación con estudiantes que el modelo nunca vio. Positivo = "abandona".
    matriz = [[0, 0], [0, 0]]    # matriz[real][predicho]: 0 = continúa, 1 = abandona
    for x, real in prueba:
        predicho = 1 if modelo.probabilidad(x) >= 0.5 else 0
        matriz[real][predicho] += 1
    vn, fp, fn, vp = matriz[0][0], matriz[0][1], matriz[1][0], matriz[1][1]
    total = len(prueba)
    mayoritaria = max(vn + fp, fn + vp)
    modelo.metricas = {
        "algoritmo": "Regresión logística",
        "datos_entrenamiento": len(entrenamiento),
        "datos_prueba": total,
        "exactitud": _porcentaje(vn + vp, total),
        "precision": _porcentaje(vp, vp + fp),
        "sensibilidad": _porcentaje(vp, vp + fn),
        "exactitud_base": _porcentaje(mayoritaria, total),
        "matriz": matriz,
    }
    return modelo
