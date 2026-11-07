# Catálogo de laboratorios interactivos.
#
# Cada laboratorio tiene:
#   codigo          identificador estable; debe coincidir con LABS["codigo"] en frontend/js/labs/
#   xp_recompensa   XP al completarlo por primera vez (las repeticiones dan el 30%)
#   preguntas       preguntas de comprobación; el SERVIDOR las corrige (el navegador nunca
#                   recibe la respuesta correcta antes de enviar)
#
# Para añadir un laboratorio: agrega aquí su entrada y crea frontend/js/labs/<codigo>.js
# (y añade su <script> en frontend/laboratorio.html). No hace falta tocar la base de datos.
from typing import Optional

CATALOGO = [
    {
        "codigo": "normalizacion",
        "titulo": "Normalización de datos",
        "icono": "📏",
        "descripcion": "Min-Max y Z-score: cómo cambia la escala de los datos y por qué importa.",
        "xp_recompensa": 15,
        "instrucciones": (
            "Cada punto es una persona con dos variables: edad (años) y salario (miles de pesos). "
            "Cambia el método de normalización y observa cómo se transforman los valores, las "
            "estadísticas y cuánto pesa cada variable en la distancia entre los puntos A y B. "
            "Después añade un valor atípico y mira qué le pasa al resto de los datos."
        ),
        "preguntas": [
            {
                "enunciado": "Con Min-Max, ¿en qué rango quedan todos los valores de cada variable?",
                "opciones": ["Entre 0 y 1", "Entre -1 y 1", "Entre 0 y 100", "No cambian"],
                "respuesta_correcta": "Entre 0 y 1",
                "explicacion": "Min-Max lleva el mínimo a 0 y el máximo a 1: (x - mín) / (máx - mín).",
            },
            {
                "enunciado": "Sin normalizar, ¿qué variable domina la distancia entre A y B?",
                "opciones": [
                    "El salario, porque tiene una escala mucho mayor",
                    "La edad, porque es más importante",
                    "Las dos pesan lo mismo",
                    "Ninguna",
                ],
                "respuesta_correcta": "El salario, porque tiene una escala mucho mayor",
                "explicacion": "Las diferencias en miles de pesos son enormes frente a las de años; por eso hay que normalizar antes de usar distancias.",
            },
            {
                "enunciado": "Al añadir un valor atípico muy grande y usar Min-Max, ¿qué le pasa a la mayoría de los puntos?",
                "opciones": [
                    "Quedan comprimidos en un rango pequeño cerca de 0",
                    "Se alejan entre sí",
                    "Se eliminan automáticamente",
                    "No les pasa nada",
                ],
                "respuesta_correcta": "Quedan comprimidos en un rango pequeño cerca de 0",
                "explicacion": "Min-Max depende del máximo y del mínimo, así que un valor extremo aplasta al resto. Z-score lo sufre menos.",
            },
        ],
    },
    {
        "codigo": "imputacion",
        "titulo": "Valores faltantes",
        "icono": "🧩",
        "descripcion": "Eliminar filas o imputar con media, mediana o vecinos: compara el efecto.",
        "xp_recompensa": 15,
        "instrucciones": (
            "Cada punto es una vivienda: superficie (m²) y precio (millones). Se esconden algunos "
            "precios. Sube el porcentaje de faltantes y prueba cada método. Los puntos gris claro "
            "son el valor real que quedó oculto; los naranjas son el valor que el método inventó."
        ),
        "preguntas": [
            {
                "enunciado": "¿Qué efecto tiene imputar con la media sobre la desviación estándar del precio?",
                "opciones": [
                    "La reduce, porque muchos valores quedan iguales",
                    "La aumenta",
                    "No la cambia",
                    "La vuelve negativa",
                ],
                "respuesta_correcta": "La reduce, porque muchos valores quedan iguales",
                "explicacion": "Todos los faltantes reciben el mismo valor, así que los datos parecen menos dispersos de lo que realmente son.",
            },
            {
                "enunciado": "¿Cuál es el principal riesgo de eliminar las filas con datos faltantes?",
                "opciones": [
                    "Perder información y posiblemente sesgar el análisis",
                    "Que el modelo se vuelva más lento",
                    "Que cambie el tipo de dato",
                    "Ninguno, siempre es lo mejor",
                ],
                "respuesta_correcta": "Perder información y posiblemente sesgar el análisis",
                "explicacion": "Con muchos faltantes se pierde una parte grande de los datos, y las filas que quedan pueden no representar a todos.",
            },
            {
                "enunciado": "En este laboratorio, ¿qué método estima mejor los precios ocultos (menor error medio) cuando hay relación entre superficie y precio?",
                "opciones": [
                    "Vecinos más cercanos",
                    "Media",
                    "Mediana",
                    "Todos dan el mismo error",
                ],
                "respuesta_correcta": "Vecinos más cercanos",
                "explicacion": "Usa la superficie (otra variable) para estimar el precio, mientras que la media y la mediana ignoran esa relación.",
            },
        ],
    },
    {
        "codigo": "kmeans",
        "titulo": "Agrupamiento con K-means",
        "icono": "🎯",
        "descripcion": "Mira cómo se mueven los centroides y cómo se forman los grupos paso a paso.",
        "xp_recompensa": 20,
        "instrucciones": (
            "Los puntos no tienen etiqueta: K-means intenta descubrir grupos. Elige k y avanza paso "
            "a paso: primero se asigna cada punto al centroide más cercano y luego cada centroide se "
            "mueve al centro de su grupo. Puedes hacer clic en el gráfico para añadir puntos."
        ),
        "preguntas": [
            {
                "enunciado": "¿Qué hace K-means en cada iteración?",
                "opciones": [
                    "Asigna cada punto al centroide más cercano y recalcula los centroides",
                    "Elimina los puntos más alejados",
                    "Ordena los puntos de menor a mayor",
                    "Predice un valor numérico con una recta",
                ],
                "respuesta_correcta": "Asigna cada punto al centroide más cercano y recalcula los centroides",
                "explicacion": "Repite asignar y mover hasta que las asignaciones dejan de cambiar.",
            },
            {
                "enunciado": "Con k = 1, ¿dónde termina el único centroide?",
                "opciones": [
                    "En el centro (la media) de todos los puntos",
                    "En el punto más alejado",
                    "En una esquina del gráfico",
                    "No llega a ningún sitio",
                ],
                "respuesta_correcta": "En el centro (la media) de todos los puntos",
                "explicacion": "Un solo grupo contiene todos los puntos, y el centroide es la media de su grupo.",
            },
            {
                "enunciado": "En los datos iniciales hay 3 grupos naturales. Según la curva del codo, ¿qué valor de k marca el codo?",
                "opciones": ["3", "1", "6", "8"],
                "respuesta_correcta": "3",
                "explicacion": "Hasta k = 3 la inercia baja mucho; después casi no mejora. Ese cambio de pendiente es el codo.",
            },
        ],
    },
    {
        "codigo": "knn",
        "titulo": "Clasificación con k-NN",
        "icono": "🧭",
        "descripcion": "Coloca un punto nuevo y mira cómo votan sus vecinos más cercanos.",
        "xp_recompensa": 20,
        "instrucciones": (
            "Cada punto es un estudiante: nota del parcial y asistencia, con su resultado (aprueba "
            "o no aprueba). Haz clic o arrastra en el gráfico para colocar un estudiante nuevo y mira "
            "cómo k-NN predice su resultado según sus k vecinos. Cambia k y activa la frontera de decisión."
        ),
        "preguntas": [
            {
                "enunciado": "¿Cómo clasifica k-NN un punto nuevo?",
                "opciones": [
                    "Por votación de sus k vecinos más cercanos",
                    "Calculando una recta que pasa por todos los puntos",
                    "Agrupando los puntos sin etiquetas",
                    "Eligiendo siempre la clase más grande",
                ],
                "respuesta_correcta": "Por votación de sus k vecinos más cercanos",
                "explicacion": "Busca los k puntos etiquetados más cercanos y elige la clase que más se repite entre ellos.",
            },
            {
                "enunciado": "Con k = 1, ¿de qué depende la predicción?",
                "opciones": [
                    "Solo del vecino más cercano",
                    "De todos los puntos por igual",
                    "De la media de las clases",
                    "De ningún punto",
                ],
                "respuesta_correcta": "Solo del vecino más cercano",
                "explicacion": "Con k = 1 gana la clase del único vecino, por eso es sensible a puntos ruidosos.",
            },
            {
                "enunciado": "Si aumentas mucho k, ¿qué le pasa a la frontera de decisión?",
                "opciones": [
                    "Se vuelve más suave y simple",
                    "Se vuelve más irregular y compleja",
                    "Desaparece por completo",
                    "No cambia",
                ],
                "respuesta_correcta": "Se vuelve más suave y simple",
                "explicacion": "Con más vecinos votando, los puntos aislados pesan menos y la frontera deja de seguir cada detalle.",
            },
        ],
    },
]


def buscar_laboratorio(codigo: str) -> Optional[dict]:
    """Devuelve la entrada del catálogo con ese código, o None si no existe."""
    for lab in CATALOGO:
        if lab["codigo"] == codigo:
            return lab
    return None
