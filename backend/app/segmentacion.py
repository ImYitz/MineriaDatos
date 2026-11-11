# Segmentación de estudiantes con K-means (Etapa 9): agrupa a los estudiantes según CÓMO estudian,
# sin etiquetas previas (aprendizaje no supervisado). Escrito a mano, sin librerías externas.
#
# Pasos: 1) variables de cada estudiante, 2) estandarizar, 3) probar varios k y quedarse con el de
# mejor "silueta" (qué tan separados quedan los grupos), 4) ponerle nombre a cada grupo según su
# centroide y 5) ubicar al usuario en el grupo cuyo centroide le queda más cerca.
import math
import random
import time
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from . import esquemas_estudio as esq
from .datos_estudio import perfiles_actuales

VARIABLES = ["actividad_14", "dias_sin_estudiar", "puntaje_medio", "variedad"]
MINIMO_ESTUDIANTES = 20
K_MIN, K_MAX = 3, 5
REINICIOS = 6                # K-means depende del azar inicial: se repite y se queda el mejor resultado
MAXIMO_PUNTOS = 400          # puntos que se envían al navegador para el gráfico
SEGUNDOS_EN_MEMORIA = 300
SEMILLA = 7

_memoria: Dict = {"datos": None, "hasta": 0.0}

DESCRIPCIONES = {
    "Constantes": "Estudian casi todos los días y mantienen buenos resultados.",
    "Perfeccionistas": "Estudian con menos frecuencia, pero sacan puntajes muy altos y prueban distintas actividades.",
    "Esporádicos": "Estudian de vez en cuando; su ritmo es irregular.",
    "En pausa": "Llevan varios días sin estudiar: son quienes están más cerca de abandonar.",
}


def _dist2(a: List[float], b: List[float]) -> float:
    return sum((x - y) ** 2 for x, y in zip(a, b))


def _kmeans(puntos: List[List[float]], k: int, azar: random.Random):
    """Un K-means completo con centroides iniciales elegidos con k-means++ (lejos unos de otros)."""
    centroides = [list(azar.choice(puntos))]
    while len(centroides) < k:
        d2 = [min(_dist2(p, c) for c in centroides) for p in puntos]
        total = sum(d2)
        if total == 0:
            centroides.append(list(azar.choice(puntos)))
            continue
        umbral, acumulado = azar.random() * total, 0.0
        for p, d in zip(puntos, d2):
            acumulado += d
            if acumulado >= umbral:
                centroides.append(list(p))
                break
    asign: List[int] = []
    for _ in range(60):
        nueva = [min(range(k), key=lambda j: _dist2(p, centroides[j])) for p in puntos]
        if nueva == asign:
            break
        asign = nueva
        for j in range(k):
            miembros = [p for p, a in zip(puntos, asign) if a == j]
            if miembros:     # un grupo vacío conserva su centroide
                centroides[j] = [sum(c) / len(miembros) for c in zip(*miembros)]
    inercia = sum(_dist2(p, centroides[a]) for p, a in zip(puntos, asign))
    return centroides, asign, inercia


def _mejor_kmeans(puntos: List[List[float]], k: int, azar: random.Random):
    mejor = None
    for _ in range(REINICIOS):
        resultado = _kmeans(puntos, k, azar)
        if mejor is None or resultado[2] < mejor[2]:
            mejor = resultado
    return mejor


def _silueta(puntos: List[List[float]], asign: List[int], k: int) -> float:
    """Silueta media: cerca de 1 = grupos bien separados; cerca de 0 = grupos mezclados."""
    n = len(puntos)
    total = 0.0
    for i in range(n):
        suma = [0.0] * k
        cuenta = [0] * k
        for j in range(n):
            if i != j:
                suma[asign[j]] += math.sqrt(_dist2(puntos[i], puntos[j]))
                cuenta[asign[j]] += 1
        propio = asign[i]
        if cuenta[propio] == 0:
            continue                      # grupo de un solo punto: silueta 0
        a = suma[propio] / cuenta[propio]
        b = min((suma[j] / cuenta[j] for j in range(k) if j != propio and cuenta[j] > 0), default=a)
        total += (b - a) / max(a, b) if max(a, b) > 0 else 0.0
    return total / n


def _nombre_del_grupo(actividad: float, dias_sin: float, puntaje: float) -> str:
    if dias_sin >= 10 or actividad < 0.12:
        return "En pausa"
    if actividad >= 0.45:
        return "Constantes"
    if puntaje >= 85:
        return "Perfeccionistas"
    return "Esporádicos"


def _calcular(bd: Session, hoy) -> Optional[Dict]:
    perfiles = perfiles_actuales(bd, hoy)
    if len(perfiles) < MINIMO_ESTUDIANTES:
        return None

    crudos = [[p[1][v] for v in VARIABLES] for p in perfiles]
    n, m = len(crudos), len(VARIABLES)
    medias = [sum(f[j] for f in crudos) / n for j in range(m)]
    desvios = [math.sqrt(sum((f[j] - medias[j]) ** 2 for f in crudos) / n) or 1.0 for j in range(m)]
    puntos = [[(f[j] - medias[j]) / desvios[j] for j in range(m)] for f in crudos]

    # Probar varios k y quedarse con el de mejor silueta
    azar = random.Random(SEMILLA)
    siluetas, mejor = [], None
    for k in range(K_MIN, min(K_MAX, n - 1) + 1):
        centroides, asign, _ = _mejor_kmeans(puntos, k, azar)
        s = _silueta(puntos, asign, k)
        siluetas.append(esq.SiluetaK(k=k, silueta=round(s, 2)))
        if mejor is None or s > mejor[0]:
            mejor = (s, k, centroides, asign)
    silueta, k, centroides, asign = mejor

    # Resumen de cada grupo en las unidades originales
    grupos = []
    for j in range(k):
        miembros = [crudos[i] for i in range(n) if asign[i] == j]
        if not miembros:
            continue
        medias_g = [sum(f[c] for f in miembros) / len(miembros) for c in range(m)]
        grupos.append({"j": j, "tamano": len(miembros), "medias": medias_g,
                       "nombre": _nombre_del_grupo(medias_g[0], medias_g[1], medias_g[2])})
    grupos.sort(key=lambda g: -g["medias"][0])      # el más activo primero
    repetidos: Dict[str, int] = {}
    for g in grupos:
        base = g["nombre"]
        repetidos[base] = repetidos.get(base, 0) + 1
        g["etiqueta"] = base if repetidos[base] == 1 else base + " (" + str(repetidos[base]) + ")"
    nuevo_id = {g["j"]: i for i, g in enumerate(grupos)}

    resumen = [
        esq.GrupoEstudio(
            id=i, nombre=g["etiqueta"], descripcion=DESCRIPCIONES.get(g["nombre"], ""),
            tamano=g["tamano"], porcentaje=int(round(100 * g["tamano"] / n)),
            dias_activos_14=round(g["medias"][0] * 14, 1), dias_sin_estudiar=round(g["medias"][1], 1),
            puntaje_medio=int(round(g["medias"][2])), variedad=round(g["medias"][3], 1))
        for i, g in enumerate(grupos)
    ]
    indices = list(range(n))
    if n > MAXIMO_PUNTOS:
        indices = random.Random(SEMILLA).sample(indices, MAXIMO_PUNTOS)
    puntos_grafico = [
        esq.PuntoGrupo(x=round(crudos[i][0] * 14, 2), y=round(crudos[i][2], 1), grupo=nuevo_id[asign[i]])
        for i in indices
    ]
    return {
        "medias": medias, "desvios": desvios, "centroides": centroides, "nuevo_id": nuevo_id,
        "k": k, "silueta": round(silueta, 2), "siluetas": siluetas, "grupos": resumen,
        "puntos": puntos_grafico, "total": n, "simulados": sum(1 for p in perfiles if p[2]),
    }


def _obtener(bd: Session, hoy) -> Optional[Dict]:
    if _memoria["datos"] is not None and time.time() < _memoria["hasta"]:
        return _memoria["datos"]
    datos = _calcular(bd, hoy)
    _memoria["datos"] = datos
    _memoria["hasta"] = time.time() + SEGUNDOS_EN_MEMORIA
    return datos


def resumen_segmentos(bd: Session, hoy, caracteristicas: Dict[str, float],
                      n_eventos: int) -> Optional[esq.Segmentacion]:
    """La segmentación de todos los estudiantes y el grupo del usuario (None si hay pocos estudiantes)."""
    datos = _obtener(bd, hoy)
    if datos is None:
        return None
    mi_grupo, mi_punto = None, None
    if n_eventos > 0:    # sin actividad no hay con qué ubicarlo
        x = [(caracteristicas[v] - datos["medias"][j]) / datos["desvios"][j] for j, v in enumerate(VARIABLES)]
        cercano = min(range(len(datos["centroides"])), key=lambda c: _dist2(x, datos["centroides"][c]))
        mi_grupo = datos["nuevo_id"].get(cercano, 0)
        mi_punto = esq.PuntoGrupo(
            x=round(caracteristicas["actividad_14"] * 14, 2), y=round(caracteristicas["puntaje_medio"], 1),
            grupo=mi_grupo)
    return esq.Segmentacion(
        k=datos["k"], silueta=datos["silueta"], siluetas=datos["siluetas"], grupos=datos["grupos"],
        puntos=datos["puntos"], total=datos["total"], simulados=datos["simulados"],
        mi_grupo=mi_grupo, mi_punto=mi_punto)
