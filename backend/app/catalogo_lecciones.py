# Catálogo de lecciones del curso "Minería de datos".
#
# Se ejecuta al arrancar el servidor (igual que los logros y la tienda): crea las lecciones y
# ejercicios que falten y actualiza los demás, SIN borrar usuarios ni progreso. Se puede ejecutar
# muchas veces sin duplicar nada. Las lecciones se reconocen por su título.
#
# Para añadir una lección: agrega una entrada a LECCIONES y reinicia el servidor.
# Para cambiar un ejercicio: edítalo aquí y reinicia (se actualiza solo).
#
# Las 3 primeras lecciones ya existen (vienen de sembrar_datos.py): aquí solo se les cambia el
# "orden" para que queden bien colocadas entre las nuevas. No tienen "ejercicios" en este archivo,
# así que sus preguntas no se tocan.
#
# Unidades (la pantalla principal las dibuja con frontend/js/inicio.js, lista UNIDADES):
#   Unidad 1: lecciones 1 a 8   ·   Unidad 2: lecciones 9 a 14
#
# Cada ejercicio: (enunciado, opciones, respuesta_correcta, explicacion)
# Escribe la respuesta correcta EXACTAMENTE igual que en la lista de opciones. Las opciones se
# mezclan solas (siempre en el mismo orden para cada ejercicio), así que no importa en qué
# posición las escribas.
import random
from sqlalchemy.orm import Session
from . import modelos

XP_LECCION = 10

LECCIONES = [
    # ---------------- Unidad 1: Conceptos sobre minería de datos ----------------
    {"titulo": "¿Qué es la minería de datos?", "orden": 1},   # ya existe

    {
        "titulo": "El proceso KDD",
        "descripcion": "Las etapas para pasar de los datos al conocimiento.",
        "orden": 2,
        "ejercicios": [
            ("¿Cuál es el orden de las etapas del proceso KDD?",
             ["Selección, preprocesamiento, transformación, minería de datos e interpretación",
              "Minería de datos, selección, transformación, preprocesamiento e interpretación",
              "Transformación, interpretación, selección, minería de datos y preprocesamiento",
              "Interpretación, minería de datos, selección, preprocesamiento y transformación"],
             "Selección, preprocesamiento, transformación, minería de datos e interpretación",
             "Primero se eligen los datos, luego se limpian y transforman, después se minan y al final se interpretan los patrones."),
            ("¿Qué se hace en la etapa de preprocesamiento (limpieza)?",
             ["Se tratan los valores faltantes, el ruido y los datos duplicados",
              "Se eligen los objetivos del negocio",
              "Se publican los resultados para los usuarios",
              "Se aplican los algoritmos de aprendizaje"],
             "Se tratan los valores faltantes, el ruido y los datos duplicados",
             "Sin datos limpios, los patrones que se encuentren no serán confiables."),
            ("¿Qué ocurre en la etapa de transformación?",
             ["Los datos se convierten a una forma adecuada para minarlos, por ejemplo normalizando o reduciendo variables",
              "Se descartan todos los datos antiguos",
              "Se escribe el informe final",
              "Se instala el servidor de la base de datos"],
             "Los datos se convierten a una forma adecuada para minarlos, por ejemplo normalizando o reduciendo variables",
             "Aquí se normalizan valores, se discretizan variables o se reduce la dimensionalidad."),
            ("¿Qué se hace en la última etapa de KDD?",
             ["Interpretar y evaluar los patrones para convertirlos en conocimiento útil",
              "Recolectar los datos por primera vez",
              "Eliminar los datos con errores",
              "Crear la base de datos"],
             "Interpretar y evaluar los patrones para convertirlos en conocimiento útil",
             "No todos los patrones encontrados son útiles o nuevos: hay que revisarlos con criterio."),
        ],
    },

    {
        "titulo": "Metodología CRISP-DM",
        "descripcion": "Las seis fases, de la comprensión del negocio al despliegue.",
        "orden": 3,
        "ejercicios": [
            ("¿Cuál es el orden de las seis fases de CRISP-DM?",
             ["Comprensión del negocio, comprensión de los datos, preparación de los datos, modelado, evaluación y despliegue",
              "Comprensión de los datos, comprensión del negocio, modelado, preparación de los datos, despliegue y evaluación",
              "Preparación de los datos, modelado, evaluación, comprensión del negocio, comprensión de los datos y despliegue",
              "Modelado, evaluación, despliegue, comprensión del negocio, preparación de los datos y comprensión de los datos"],
             "Comprensión del negocio, comprensión de los datos, preparación de los datos, modelado, evaluación y despliegue",
             "El proyecto empieza por el problema del negocio y termina poniendo el modelo en uso."),
            ("¿En qué fase se exploran los datos y se revisa su calidad por primera vez?",
             ["Comprensión de los datos", "Despliegue", "Modelado", "Comprensión del negocio"],
             "Comprensión de los datos",
             "Se recolectan, se describen y se revisa si tienen errores o faltantes antes de prepararlos."),
            ("¿Qué se hace en la fase de evaluación?",
             ["Comprobar si el modelo cumple los objetivos del negocio antes de ponerlo en uso",
              "Recolectar los datos por primera vez",
              "Limpiar los valores faltantes",
              "Definir el problema que se quiere resolver"],
             "Comprobar si el modelo cumple los objetivos del negocio antes de ponerlo en uso",
             "No basta con que el modelo sea preciso: tiene que servir para el objetivo del negocio."),
            ("CRISP-DM es un proceso iterativo. ¿Qué significa?",
             ["Se puede volver a fases anteriores cuando los resultados lo exigen",
              "Cada fase se hace una sola vez y no se repite",
              "Solo se repite la fase de despliegue",
              "Todas las fases se hacen al mismo tiempo"],
             "Se puede volver a fases anteriores cuando los resultados lo exigen",
             "Por ejemplo, si el modelo no es bueno, se vuelve a preparar los datos o a entender mejor el negocio."),
        ],
    },

    {"titulo": "El proceso y la preparación de datos", "orden": 4},   # ya existe

    {
        "titulo": "¿Qué es un modelo?",
        "descripcion": "Qué es un modelo, cómo se entrena y cómo se evalúa.",
        "orden": 5,
        "ejercicios": [
            ("En minería de datos, ¿qué es un modelo?",
             ["Una representación de los patrones aprendidos de los datos, que sirve para describir o predecir",
              "Un tipo de base de datos",
              "Un formato de archivo",
              "Un informe en PDF"],
             "Una representación de los patrones aprendidos de los datos, que sirve para describir o predecir",
             "El algoritmo aprende de los datos y el resultado de ese aprendizaje es el modelo."),
            ("¿Para qué se separan los datos en conjunto de entrenamiento y de prueba?",
             ["Para evaluar el modelo con datos que no vio mientras aprendía",
              "Para tener el doble de datos",
              "Para eliminar los datos erróneos",
              "Para ordenar los datos por fecha"],
             "Para evaluar el modelo con datos que no vio mientras aprendía",
             "Evaluar con los mismos datos de entrenamiento daría una idea demasiado optimista."),
            ("Un modelo que acierta casi todo con los datos de entrenamiento pero falla con datos nuevos sufre de:",
             ["Sobreajuste (overfitting)", "Normalización", "Imputación", "Discretización"],
             "Sobreajuste (overfitting)",
             "Memorizó los ejemplos en lugar de aprender el patrón general."),
            ("¿Qué mide la exactitud (accuracy) de un modelo de clasificación?",
             ["El porcentaje de predicciones correctas sobre el total",
              "El tiempo que tarda en entrenar",
              "El número de variables que usa",
              "El tamaño del archivo del modelo"],
             "El porcentaje de predicciones correctas sobre el total",
             "Si acierta 90 de 100 casos, su exactitud es del 90 %."),
        ],
    },

    {
        "titulo": "El modelo híbrido",
        "descripcion": "Un proceso de seis pasos que combina el enfoque académico y el industrial.",
        "orden": 6,
        "ejercicios": [
            ("El modelo de proceso híbrido de seis pasos se llama así porque combina:",
             ["El enfoque académico (KDD) y el industrial (CRISP-DM)",
              "Bases de datos relacionales y no relacionales",
              "Redes neuronales y árboles de decisión",
              "Trabajo en la nube y trabajo local"],
             "El enfoque académico (KDD) y el industrial (CRISP-DM)",
             "Toma ideas de los dos mundos para ofrecer un proceso de seis pasos."),
            ("¿Cuál es el primer paso del modelo híbrido?",
             ["Comprender el dominio del problema",
              "Aplicar el algoritmo de minería",
              "Usar el conocimiento descubierto",
              "Preparar los datos"],
             "Comprender el dominio del problema",
             "Igual que en CRISP-DM, primero se entiende el problema y sus objetivos."),
            ("¿En qué consiste el último paso, el uso del conocimiento descubierto?",
             ["En aplicar lo aprendido en el problema real y documentarlo para otros casos",
              "En volver a recolectar los datos",
              "En limpiar otra vez los datos",
              "En borrar el modelo"],
             "En aplicar lo aprendido en el problema real y documentarlo para otros casos",
             "El resultado solo vale si se usa; además, lo aprendido puede servir en otros proyectos."),
            ("El modelo híbrido incluye ciclos de retroalimentación. ¿Qué permiten?",
             ["Volver a pasos anteriores para mejorar el resultado",
              "Saltarse la evaluación",
              "Eliminar el paso de preparación de datos",
              "Ejecutar el proceso una sola vez"],
             "Volver a pasos anteriores para mejorar el resultado",
             "Los resultados de un paso pueden obligar a revisar los anteriores."),
        ],
    },

    {
        "titulo": "Predicción",
        "descripcion": "Clasificación y regresión: estimar lo que todavía no se conoce.",
        "orden": 7,
        "ejercicios": [
            ("¿Qué es la predicción en minería de datos?",
             ["Estimar una categoría o un valor desconocido a partir de datos conocidos",
              "Borrar datos antiguos",
              "Agrupar elementos sin usar ninguna variable",
              "Guardar datos en un almacén"],
             "Estimar una categoría o un valor desconocido a partir de datos conocidos",
             "Se aprende de casos pasados para estimar casos nuevos."),
            ("¿Qué tipo de aprendizaje usa ejemplos con la respuesta ya conocida para predecir?",
             ["Supervisado", "No supervisado", "Por agrupamiento", "Ninguno"],
             "Supervisado",
             "En el aprendizaje supervisado cada ejemplo viene con su etiqueta o valor objetivo."),
            ("Predecir si un cliente abandonará el servicio (sí o no) es un problema de:",
             ["Clasificación", "Regresión", "Reglas de asociación", "Imputación"],
             "Clasificación",
             "La respuesta es una categoría: 'abandona' o 'no abandona'."),
            ("Predecir las ventas del próximo mes (un número) es un problema de:",
             ["Regresión", "Clasificación", "Agrupamiento", "Normalización"],
             "Regresión",
             "La regresión estima valores numéricos continuos."),
        ],
    },

    {
        "titulo": "Almacén de datos (Data Warehouse)",
        "descripcion": "Dónde se guardan los datos para poder analizarlos.",
        "orden": 8,
        "ejercicios": [
            ("¿Qué es un almacén de datos (data warehouse)?",
             ["Un repositorio central de datos históricos e integrados, pensado para el análisis",
              "Una copia de seguridad de un solo programa",
              "Una hoja de cálculo compartida",
              "Un servidor web"],
             "Un repositorio central de datos históricos e integrados, pensado para el análisis",
             "Reúne datos de varias fuentes para consultarlos y analizarlos."),
            ("¿Qué significan las siglas ETL?",
             ["Extracción, transformación y carga",
              "Evaluación, tabulación y lectura",
              "Entrada, texto y lista",
              "Edición, traducción y lenguaje"],
             "Extracción, transformación y carga",
             "Los datos se extraen de las fuentes, se limpian y transforman, y se cargan en el almacén."),
            ("¿Cuál es una característica clásica de un almacén de datos?",
             ["Es no volátil: los datos no se modifican con las operaciones del día a día",
              "Guarda solo los datos de hoy",
              "Registra cada venta en tiempo real como una caja registradora",
              "Cada aplicación guarda sus datos por separado"],
             "Es no volátil: los datos no se modifican con las operaciones del día a día",
             "Un almacén es orientado a temas, integrado, no volátil y guarda la historia en el tiempo."),
            ("¿Qué diferencia a OLAP de OLTP?",
             ["OLAP está pensado para analizar datos; OLTP, para registrar las transacciones del día a día",
              "OLAP registra las ventas y OLTP hace los análisis",
              "No hay ninguna diferencia",
              "OLAP solo funciona sin datos históricos"],
             "OLAP está pensado para analizar datos; OLTP, para registrar las transacciones del día a día",
             "Los sistemas OLTP alimentan al almacén; los análisis OLAP se hacen sobre el almacén."),
        ],
    },

    # ---------------- Unidad 2: Modelos y técnicas de la minería de datos ----------------
    {
        "titulo": "Modelos descriptivos y predictivos",
        "descripcion": "Los dos grandes tipos de modelos y el aprendizaje supervisado y no supervisado.",
        "orden": 9,
        "ejercicios": [
            ("¿Qué hace un modelo descriptivo?",
             ["Resume los datos y encuentra patrones en lo que ya existe",
              "Predice un valor futuro a partir de etiquetas",
              "Borra los datos duplicados",
              "Cifra los datos"],
             "Resume los datos y encuentra patrones en lo que ya existe",
             "Los modelos descriptivos explican cómo son los datos; los predictivos estiman lo que no se conoce."),
            ("¿Cuál de estas técnicas se usa para construir un modelo predictivo?",
             ["Clasificación", "Agrupamiento (clustering)", "Reglas de asociación", "Resumen estadístico"],
             "Clasificación",
             "La clasificación predice una categoría para casos nuevos."),
            ("El agrupamiento (clustering) pertenece al aprendizaje:",
             ["No supervisado", "Supervisado", "Siempre supervisado", "Ninguno de los dos"],
             "No supervisado",
             "No hay etiquetas: el algoritmo descubre los grupos por sí solo."),
            ("¿Qué diferencia a los datos etiquetados de los no etiquetados?",
             ["Los etiquetados traen la respuesta conocida (la clase o el valor objetivo)",
              "Los etiquetados están cifrados",
              "Los no etiquetados siempre están limpios",
              "No hay ninguna diferencia"],
             "Los etiquetados traen la respuesta conocida (la clase o el valor objetivo)",
             "Con etiquetas se hace aprendizaje supervisado; sin ellas, no supervisado."),
        ],
    },

    {"titulo": "Técnicas principales", "orden": 10},   # ya existe (los métodos de minería de datos)

    {
        "titulo": "Árboles de clasificación",
        "descripcion": "Decidir paso a paso con preguntas en forma de árbol.",
        "orden": 11,
        "ejercicios": [
            ("En un árbol de clasificación, ¿qué representan las hojas?",
             ["La clase que se predice para los casos que llegan hasta ellas",
              "Las variables de entrada",
              "El primer nodo del árbol",
              "Los datos eliminados"],
             "La clase que se predice para los casos que llegan hasta ellas",
             "Al final de cada camino hay una decisión: la clase predicha."),
            ("¿Qué representa cada nodo interno de un árbol?",
             ["Una pregunta sobre una variable que divide los datos en ramas",
              "Una clase final",
              "Un valor faltante",
              "Un error del modelo"],
             "Una pregunta sobre una variable que divide los datos en ramas",
             "Por ejemplo: ¿la edad es mayor que 30? Según la respuesta, el caso sigue una rama u otra."),
            ("¿Para qué sirven la entropía, la ganancia de información o el índice Gini?",
             ["Para elegir la mejor variable con la que dividir los datos en cada nodo",
              "Para limpiar los datos",
              "Para dibujar el árbol",
              "Para cifrar el modelo"],
             "Para elegir la mejor variable con la que dividir los datos en cada nodo",
             "Miden qué tan 'mezcladas' quedan las clases: se prefiere la división que las separa mejor."),
            ("Un árbol demasiado profundo que memoriza los datos de entrenamiento sufre sobreajuste. ¿Qué técnica ayuda a evitarlo?",
             ["La poda (recortar ramas)",
              "Añadir más niveles",
              "Eliminar el conjunto de prueba",
              "Duplicar los datos de entrenamiento"],
             "La poda (recortar ramas)",
             "Podar simplifica el árbol y lo hace generalizar mejor a datos nuevos."),
        ],
    },

    {
        "titulo": "Redes neuronales",
        "descripcion": "Neuronas artificiales que aprenden de los datos.",
        "orden": 12,
        "ejercicios": [
            ("¿Qué es una neurona artificial?",
             ["Una unidad que combina sus entradas con pesos y aplica una función de activación",
              "Un tipo de base de datos",
              "Un gráfico estadístico",
              "Un sensor físico"],
             "Una unidad que combina sus entradas con pesos y aplica una función de activación",
             "Suma las entradas multiplicadas por sus pesos y decide qué señal envía a la siguiente capa."),
            ("¿Qué se ajusta durante el entrenamiento de una red neuronal?",
             ["Los pesos de las conexiones",
              "Los nombres de las columnas",
              "El orden de las filas",
              "El formato del archivo"],
             "Los pesos de las conexiones",
             "El entrenamiento va corrigiendo los pesos para reducir el error de las predicciones."),
            ("¿Qué papel cumple la función de activación?",
             ["Introduce no linealidad para que la red pueda aprender relaciones complejas",
              "Guarda los datos en disco",
              "Normaliza el archivo de entrada",
              "Mide la exactitud del modelo"],
             "Introduce no linealidad para que la red pueda aprender relaciones complejas",
             "Sin ella, una red de varias capas se comportaría como una sola operación lineal."),
            ("Una red neuronal típica se organiza en capas. ¿Cuáles son?",
             ["Entrada, ocultas y salida",
              "Selección, limpieza y despliegue",
              "Raíz, ramas y hojas",
              "Centroides, grupos y puntos"],
             "Entrada, ocultas y salida",
             "Los datos entran por la capa de entrada, se procesan en las ocultas y salen por la de salida."),
        ],
    },

    {
        "titulo": "Aplicaciones de la minería de datos",
        "descripcion": "Dónde se usa en la vida real: bancos, comercio, marketing, agricultura...",
        "orden": 13,
        "ejercicios": [
            ("Detectar transacciones sospechosas con tarjeta de crédito es una aplicación típica en:",
             ["Banca y finanzas (detección de fraude)",
              "Diseño gráfico",
              "Construcción civil",
              "Edición de video"],
             "Banca y finanzas (detección de fraude)",
             "El modelo aprende cómo se ven las transacciones normales y señala las que se salen del patrón."),
            ("Descubrir qué productos se compran juntos para colocarlos cerca en la tienda usa:",
             ["Reglas de asociación", "Regresión", "Imputación", "Normalización"],
             "Reglas de asociación",
             "Es el análisis de la canasta de compras: 'quienes compran A también compran B'."),
            ("Dividir a los clientes en segmentos de comportamiento parecido para campañas de marketing usa:",
             ["Agrupamiento (clustering)",
              "Predicción de un número",
              "Limpieza de duplicados",
              "Cifrado de datos"],
             "Agrupamiento (clustering)",
             "Los segmentos no existen de antemano: el algoritmo los descubre."),
            ("Estimar el rendimiento de una cosecha a partir del clima, el suelo y datos históricos es un problema de:",
             ["Regresión", "Clasificación binaria", "Reglas de asociación", "Detección de duplicados"],
             "Regresión",
             "El resultado es un número (por ejemplo, toneladas por hectárea)."),
        ],
    },

    {
        "titulo": "Minería de datos en la educación",
        "descripcion": "Usar los datos de los estudiantes para mejorar el aprendizaje.",
        "orden": 14,
        "ejercicios": [
            ("¿Qué estudia la minería de datos educativa?",
             ["Los datos de entornos educativos para entender y mejorar el aprendizaje",
              "Solo las notas finales de un colegio",
              "La construcción de edificios escolares",
              "El diseño de pupitres"],
             "Los datos de entornos educativos para entender y mejorar el aprendizaje",
             "Usa datos como las notas, la asistencia y la actividad en plataformas virtuales."),
            ("¿Cuál es una aplicación típica de la minería de datos educativa?",
             ["Predecir qué estudiantes están en riesgo de abandonar o reprobar para apoyarlos a tiempo",
              "Cobrar las matrículas",
              "Imprimir los boletines",
              "Reservar las aulas"],
             "Predecir qué estudiantes están en riesgo de abandonar o reprobar para apoyarlos a tiempo",
             "Detectar el riesgo temprano permite intervenir antes de que el problema crezca."),
            ("Un sistema que recomienda ejercicios según el progreso de cada estudiante se basa en:",
             ["El análisis de los datos de aprendizaje para personalizar el contenido",
              "Sorteos al azar",
              "Dar siempre los mismos contenidos a todos",
              "Datos de otros países sin relación con el curso"],
             "El análisis de los datos de aprendizaje para personalizar el contenido",
             "Es la base de los tutores inteligentes y de las plataformas de aprendizaje adaptativo."),
            ("¿Qué hay que cuidar al analizar datos de estudiantes?",
             ["La privacidad y el uso ético de los datos personales",
              "Solo la velocidad del análisis",
              "Nada: los datos educativos son públicos",
              "Usar siempre los nombres completos"],
             "La privacidad y el uso ético de los datos personales",
             "Los datos de estudiantes son sensibles: hay que protegerlos y usarlos de forma responsable."),
        ],
    },
]


def _validar() -> None:
    """Se ejecuta al importar: avisa enseguida si algún ejercicio está mal escrito."""
    for leccion in LECCIONES:
        for numero, (enunciado, opciones, correcta, _explicacion) in enumerate(leccion.get("ejercicios", []), start=1):
            lugar = leccion["titulo"] + ", ejercicio " + str(numero)
            if correcta not in opciones:
                raise ValueError("La respuesta correcta no está entre las opciones: " + lugar)
            if len(set(opciones)) != len(opciones):
                raise ValueError("Hay opciones repetidas: " + lugar)


_validar()


def _mezclar(opciones, semilla: str):
    """Mezcla las opciones, pero siempre igual para el mismo ejercicio (así no cambian al reiniciar)."""
    copia = list(opciones)
    random.Random(semilla).shuffle(copia)
    return copia


def asegurar_lecciones(bd: Session) -> None:
    """Se ejecuta al arrancar el servidor: crea las lecciones y ejercicios que falten y actualiza
    los demás. No borra nada. Si todavía no existe el curso (no se ha ejecutado sembrar_datos.py),
    no hace nada."""
    curso = bd.query(modelos.Curso).order_by(modelos.Curso.id).first()
    if curso is None:
        return

    for datos in LECCIONES:
        leccion = (
            bd.query(modelos.Leccion)
            .filter(modelos.Leccion.curso_id == curso.id, modelos.Leccion.titulo == datos["titulo"])
            .first()
        )
        tiene_ejercicios = "ejercicios" in datos

        if leccion is None:
            if not tiene_ejercicios:
                continue   # lección antigua que no está en la BD: no se inventa
            leccion = modelos.Leccion(
                curso_id=curso.id,
                titulo=datos["titulo"],
                descripcion=datos["descripcion"],
                orden=datos["orden"],
                xp_recompensa=XP_LECCION,
            )
            bd.add(leccion)
            bd.flush()   # asigna el id de la lección
        else:
            leccion.orden = datos["orden"]
            if tiene_ejercicios:
                leccion.descripcion = datos["descripcion"]
                leccion.xp_recompensa = XP_LECCION

        for posicion, (enunciado, opciones, correcta, explicacion) in enumerate(
            datos.get("ejercicios", []), start=1
        ):
            ejercicio = (
                bd.query(modelos.Ejercicio)
                .filter(modelos.Ejercicio.leccion_id == leccion.id, modelos.Ejercicio.orden == posicion)
                .first()
            )
            if ejercicio is None:
                ejercicio = modelos.Ejercicio(leccion_id=leccion.id, orden=posicion)
                bd.add(ejercicio)
            ejercicio.tipo = "opcion_multiple"
            ejercicio.enunciado = enunciado
            ejercicio.opciones = _mezclar(opciones, datos["titulo"] + "|" + str(posicion))
            ejercicio.respuesta_correcta = correcta
            ejercicio.explicacion = explicacion
    bd.commit()
