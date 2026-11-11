# Modelo de riesgo de abandono (Etapa 9): regresión logística escrita a mano, sin librerías externas.
#
# Idea: a partir de cómo estudia una persona (días sin estudiar, constancia, puntajes...) estimar la
# probabilidad de que NO vuelva a estudiar en los próximos 14 días. Es un problema de CLASIFICACIÓN.
#
# De dónde salen los datos de entrenamiento:
#   1. De la base de datos (datos_estudio.construir_dataset), si hay suficientes estudiantes.
#      Con sembrar_estudiantes.py se crean estudiantes SIMULADOS (sim_001, sim_002...) para tener
#      una base sólida con la que practicar.
#   2. Si hay pocos, se usan estudiantes simulados EN MEMORIA (generar_estudiantes), siempre iguales.
# En ambos casos, si los datos son simulados, el modelo demuestra el PROCESO de minería de datos,
# no es un diagnóstico real. El panel lo avisa.
#
# Proceso (mismo orden que CRISP-DM): datos -> preparación (estandarizar) -> modelo -> evaluación.
import math
import random
import time
from dataclasses import dataclass
from functools import lru_cache
from typing import Dict, List, Optional, Tuple

from . import logica
from .datos_estudio import CARACTERISTICAS, construir_dataset

CANTIDAD_ENTRENAMIENTO = 500     # estudiantes simulados en memoria (plan B)
CANTIDAD_PRUEBA = 200
SEMILLA = 2026
MINIMO_ESTUDIANTES = 40          # con menos estudiantes en la base, se usa el plan B
MINIMO_POR_CLASE = 5             # y debe haber al menos 5 que abandonaron y 5 que continuaron
SEGUNDOS_EN_MEMORIA = 300        # el modelo se vuelve a entrenar como máximo cada 5 minutos

_memoria: Dict = {"modelo": None, "hasta": 0.0}


def _limitar(valor: float, minimo: float, maximo: float) -> float:
    return max(minimo, min(maximo, valor))


def _sigmoide(z: float) -> float:
    z = _limitar(z, -35.0, 35.0)
    return 1.0 / (1.0 + math.exp(-z))


def generar_estudiantes(cantidad: int, azar: random.Random) -> List[Tuple[List[float], int]]:
    """Estudiantes simulados en memoria: (variables, abandona) con abandona = 1 si deja de estudiar.

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


def _entrenar_y_evaluar(entrenamiento: List[Tuple[List[float], int]], prueba: List[Tuple[List[float], int]],
                        origen: str, simulados: int) -> Modelo:
    """Prepara los datos, entrena el modelo y lo evalúa con estudiantes que no vio al entrenar."""
    k = len(CARACTERISTICAS)
    n = len(entrenamiento)
    medias = [sum(f[0][j] for f in entrenamiento) / n for j in range(k)]
    desvios = [math.sqrt(sum((f[0][j] - medias[j]) ** 2 for f in entrenamiento) / n) or 1.0 for j in range(k)]

    def estandar(x):
        return [(v - m) / d for v, m, d in zip(x, medias, desvios)]

    pesos, sesgo = _entrenar([estandar(f[0]) for f in entrenamiento], [f[1] for f in entrenamiento])
    modelo = Modelo(medias, desvios, pesos, sesgo, {})

    # Positivo = "abandona". matriz[real][predicho]: 0 = continúa, 1 = abandona
    matriz = [[0, 0], [0, 0]]
    for x, real in prueba:
        matriz[real][1 if modelo.probabilidad(x) >= 0.5 else 0] += 1
    vn, fp, fn, vp = matriz[0][0], matriz[0][1], matriz[1][0], matriz[1][1]
    total = len(prueba)
    modelo.metricas = {
        "algoritmo": "Regresión logística",
        "origen": origen,                      # "base_datos" o "memoria"
        "simulados": simulados,                # cuántos de los estudiantes usados son simulados
        "datos_entrenamiento": n,
        "datos_prueba": total,
        "exactitud": _porcentaje(vn + vp, total),
        "precision": _porcentaje(vp, vp + fp),
        "sensibilidad": _porcentaje(vp, vp + fn),
        "exactitud_base": _porcentaje(max(vn + fp, fn + vp), total),
        "matriz": matriz,
    }
    return modelo


@lru_cache(maxsize=1)
def _modelo_en_memoria() -> Modelo:
    azar = random.Random(SEMILLA)
    entrenamiento = generar_estudiantes(CANTIDAD_ENTRENAMIENTO, azar)
    prueba = generar_estudiantes(CANTIDAD_PRUEBA, azar)
    return _entrenar_y_evaluar(entrenamiento, prueba, "memoria", CANTIDAD_ENTRENAMIENTO + CANTIDAD_PRUEBA)


def _desde_base_datos(bd) -> Optional[Modelo]:
    filas = construir_dataset(bd, logica.fecha_hoy())
    abandonan = sum(f[1] for f in filas)
    if len(filas) < MINIMO_ESTUDIANTES or min(abandonan, len(filas) - abandonan) < MINIMO_POR_CLASE:
        return None
    random.Random(SEMILLA).shuffle(filas)
    corte = int(len(filas) * 0.7)       # 70 % para entrenar y 30 % para evaluar
    ejemplos = [(f[0], f[1]) for f in filas]
    return _entrenar_y_evaluar(ejemplos[:corte], ejemplos[corte:], "base_datos", sum(1 for f in filas if f[2]))


def obtener_modelo(bd=None) -> Modelo:
    """El modelo de riesgo. Si hay suficientes estudiantes en la base de datos se entrena con ellos;
    si no, con estudiantes simulados en memoria. Se guarda unos minutos para no reentrenar en cada visita."""
    if _memoria["modelo"] is not None and time.time() < _memoria["hasta"]:
        return _memoria["modelo"]
    modelo = _desde_base_datos(bd) if bd is not None else None
    if modelo is None:
        modelo = _modelo_en_memoria()
    _memoria["modelo"] = modelo
    _memoria["hasta"] = time.time() + SEGUNDOS_EN_MEMORIA
    return modelo
