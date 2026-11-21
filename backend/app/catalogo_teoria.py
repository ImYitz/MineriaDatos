# Teoría breve que se muestra ANTES de los ejercicios de cada lección del curso.
#
# Las lecciones se reconocen por su título (el mismo de catalogo_lecciones.py). Cada una tiene una
# lista de secciones (titulo, texto). Para cambiar un texto basta con editarlo aquí; no hace falta
# tocar la base de datos. Una lección sin entrada aquí simplemente empieza por los ejercicios.
from typing import List, Tuple

TEORIA = {
    "¿Qué es la minería de datos?": [
        ("La idea", "La minería de datos es el proceso de descubrir patrones útiles y no evidentes en grandes volúmenes de datos. No se trata de guardar datos, sino de extraer conocimiento de ellos."),
        ("Patrones", "Un patrón es una regularidad o relación que se repite, por ejemplo: «los clientes que compran A suelen comprar también B». Los sistemas de recomendación son un ejemplo cotidiano."),
        ("KDD", "KDD (Knowledge Discovery in Databases) es el proceso completo de descubrir conocimiento. La minería de datos es uno de sus pasos, el que aplica los algoritmos."),
    ],
    "El proceso KDD": [
        ("Cinco etapas", "KDD sigue un orden: selección de los datos, preprocesamiento (limpieza), transformación, minería de datos e interpretación/evaluación de los patrones."),
        ("Preprocesamiento y transformación", "El preprocesamiento trata valores faltantes, ruido y duplicados. La transformación deja los datos en una forma adecuada para minarlos: normalizar, discretizar o reducir variables."),
        ("Interpretación", "No todos los patrones encontrados son nuevos o útiles. La última etapa los revisa con criterio para convertirlos en conocimiento."),
    ],
    "Metodología CRISP-DM": [
        ("Seis fases", "CRISP-DM es la metodología estándar de la industria: comprensión del negocio, comprensión de los datos, preparación de los datos, modelado, evaluación y despliegue."),
        ("Empieza por el negocio", "Antes de tocar los datos se define el problema y el objetivo. En la evaluación se comprueba que el modelo sirva a ese objetivo, no solo que sea preciso."),
        ("Iterativo", "Las fases no son una línea recta: si los resultados no son buenos, se vuelve a fases anteriores, por ejemplo a preparar mejor los datos."),
    ],
    "El proceso y la preparación de datos": [
        ("Limpieza", "Limpiar es corregir o eliminar datos erróneos, duplicados o incompletos. Datos de mala calidad producen modelos de mala calidad."),
        ("Valores faltantes", "Se pueden eliminar las filas incompletas (se pierde información) o imputar: rellenar con la media, la mediana u otro valor estimado."),
        ("Normalización", "Cuando las variables tienen escalas muy distintas, la de mayor escala domina las distancias. Escalar (Min-Max o Z-score) evita ese problema."),
    ],
    "¿Qué es un modelo?": [
        ("Modelo", "Un modelo es la representación de los patrones que un algoritmo aprendió de los datos. Sirve para describir o para predecir."),
        ("Entrenamiento y prueba", "Los datos se separan: con una parte se entrena el modelo y con otra, que no vio, se evalúa. Evaluar con los mismos datos de entrenamiento da una idea demasiado optimista."),
        ("Sobreajuste", "Si un modelo acierta casi todo en el entrenamiento pero falla con datos nuevos, memorizó en lugar de aprender: es el sobreajuste (overfitting). La exactitud (accuracy) es el porcentaje de predicciones correctas."),
    ],
    "El modelo híbrido": [
        ("Qué combina", "El modelo de proceso híbrido de seis pasos mezcla el enfoque académico (KDD) y el industrial (CRISP-DM)."),
        ("Los pasos", "Empieza por comprender el dominio del problema y termina con el uso del conocimiento descubierto: aplicarlo en el problema real y documentarlo para otros casos."),
        ("Retroalimentación", "Incluye ciclos para volver a pasos anteriores cuando los resultados de un paso obligan a revisar los previos."),
    ],
    "Predicción": [
        ("Qué es predecir", "Predecir es estimar una categoría o un valor desconocido a partir de casos pasados cuyo resultado ya se conoce."),
        ("Aprendizaje supervisado", "Cuando cada ejemplo trae su respuesta (etiqueta o valor objetivo), el aprendizaje es supervisado."),
        ("Clasificación y regresión", "Si lo que se predice es una categoría (¿abandona sí o no?), es clasificación. Si es un número continuo (las ventas del próximo mes), es regresión."),
    ],
    "Almacén de datos (Data Warehouse)": [
        ("Qué es", "Un almacén de datos es un repositorio central de datos históricos e integrados de varias fuentes, pensado para el análisis."),
        ("ETL", "Los datos llegan mediante ETL: se extraen de las fuentes, se transforman (limpieza y unificación) y se cargan en el almacén."),
        ("OLTP y OLAP", "Los sistemas OLTP registran las transacciones del día a día. Los análisis OLAP se hacen sobre el almacén. Un almacén es orientado a temas, integrado, no volátil y guarda la historia en el tiempo."),
    ],
    "Modelos descriptivos y predictivos": [
        ("Dos tipos de modelos", "Un modelo descriptivo resume los datos y encuentra patrones en lo que ya existe. Un modelo predictivo estima lo que todavía no se conoce."),
        ("Supervisado y no supervisado", "Con datos etiquetados se hace aprendizaje supervisado (clasificación, regresión). Sin etiquetas, no supervisado: el agrupamiento (clustering) descubre grupos por sí solo."),
    ],
    "Técnicas principales": [
        ("Clasificación y regresión", "La clasificación predice una categoría («spam» o «no spam»). La regresión predice un valor numérico, como el precio de una casa."),
        ("Agrupamiento", "Agrupa elementos parecidos sin categorías previas: es aprendizaje no supervisado."),
        ("Reglas de asociación", "Encuentran elementos que ocurren juntos: «quienes compran pan también compran leche». Se usan mucho en el análisis de la canasta de compras."),
    ],
    "Árboles de clasificación": [
        ("Cómo es un árbol", "Cada nodo interno hace una pregunta sobre una variable y divide los datos en ramas. Las hojas contienen la clase que se predice."),
        ("Elegir la división", "En cada nodo se elige la variable que mejor separa las clases, medido con la entropía, la ganancia de información o el índice Gini: se prefiere la división que deja las clases menos mezcladas."),
        ("Poda", "Un árbol muy profundo puede memorizar los datos de entrenamiento (sobreajuste). La poda recorta ramas para que generalice mejor. Pruébalo en el laboratorio de árboles."),
    ],
    "Redes neuronales": [
        ("La neurona artificial", "Una neurona suma sus entradas multiplicadas por pesos y aplica una función de activación para decidir qué señal envía a la siguiente capa."),
        ("Capas", "Una red se organiza en capa de entrada, capas ocultas y capa de salida."),
        ("Entrenamiento", "Entrenar es ajustar los pesos de las conexiones para reducir el error. La función de activación introduce no linealidad, lo que permite aprender relaciones complejas."),
    ],
    "Aplicaciones de la minería de datos": [
        ("En la vida real", "Banca y finanzas (detección de fraude), comercio (qué productos se compran juntos), marketing (segmentación de clientes) y agricultura (estimar el rendimiento de una cosecha)."),
        ("Cada problema, su técnica", "Detectar lo que se sale del patrón, asociar productos, agrupar clientes o estimar un número usan técnicas distintas: asociación, agrupamiento, regresión o clasificación."),
    ],
    "Minería de datos en la educación": [
        ("Minería de datos educativa", "Estudia los datos de entornos educativos (notas, asistencia, actividad en plataformas) para entender y mejorar el aprendizaje."),
        ("Usos típicos", "Predecir qué estudiantes están en riesgo de abandonar para apoyarlos a tiempo, y personalizar los contenidos según el progreso de cada uno (aprendizaje adaptativo)."),
        ("Ética y privacidad", "Los datos de estudiantes son sensibles: hay que protegerlos y usarlos de forma responsable."),
    ],
}


def obtener_teoria(titulo: str) -> List[Tuple[str, str]]:
    """Las secciones de teoría de una lección (lista vacía si no tiene)."""
    return TEORIA.get(titulo, [])
