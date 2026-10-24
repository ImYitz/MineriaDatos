# Llena la base de datos con el curso de Minería de datos.
# Uso:   python sembrar_datos.py              (solo si la BD está vacía)
#        python sembrar_datos.py --reiniciar  (borra todo y vuelve a crear)
import sys
from app.base_datos import Base, motor, SesionLocal
from app import modelos

# Cada ejercicio: (enunciado, opciones, respuesta_correcta, explicacion)
LECCION_1 = [
    ("¿Cuál es el objetivo principal de la minería de datos?",
     ["Descubrir patrones útiles en grandes volúmenes de datos",
      "Almacenar datos en servidores",
      "Diseñar interfaces web",
      "Borrar datos antiguos"],
     "Descubrir patrones útiles en grandes volúmenes de datos",
     "Se trata de extraer conocimiento que no es evidente a simple vista."),
    ("¿Qué significan las siglas KDD?",
     ["Key Data Design", "Knowledge Discovery in Databases",
      "Kernel Data Driver", "Known Database Dictionary"],
     "Knowledge Discovery in Databases",
     "KDD es el proceso completo de descubrir conocimiento; la minería de datos es uno de sus pasos."),
    ("¿Cuál es un ejemplo de minería de datos?",
     ["Recomendar productos según compras anteriores",
      "Formatear un disco duro",
      "Escribir un documento",
      "Imprimir una factura"],
     "Recomendar productos según compras anteriores",
     "Los sistemas de recomendación buscan patrones en el comportamiento de muchos usuarios."),
    ("¿Qué es un patrón en minería de datos?",
     ["Un error en la base de datos",
      "Una regularidad o relación que se repite en los datos",
      "Un tipo de gráfico",
      "Un lenguaje de programación"],
     "Una regularidad o relación que se repite en los datos",
     "Por ejemplo: los clientes que compran A suelen comprar también B."),
]

LECCION_2 = [
    ("¿Cómo se llama la metodología estándar de seis fases para proyectos de minería de datos?",
     ["CRISP-DM", "SQL-6", "AGILE-DB", "DATA-PLAN"],
     "CRISP-DM",
     "CRISP-DM significa Cross-Industry Standard Process for Data Mining."),
    ("¿Cuál es la primera fase de CRISP-DM?",
     ["Modelado", "Despliegue", "Comprensión del negocio", "Evaluación"],
     "Comprensión del negocio",
     "Antes de tocar los datos hay que entender qué problema se quiere resolver."),
    ("¿En qué consiste la limpieza de datos?",
     ["En comprimir los archivos",
      "En corregir o eliminar datos erróneos, duplicados o incompletos",
      "En cambiar el diseño del reporte",
      "En cifrar la base de datos"],
     "En corregir o eliminar datos erróneos, duplicados o incompletos",
     "Datos de mala calidad producen modelos de mala calidad."),
    ("¿Cómo se llama rellenar los valores faltantes con la media, la mediana u otro valor estimado?",
     ["Imputación", "Normalización", "Indexación", "Compilación"],
     "Imputación",
     "La imputación evita perder filas completas solo porque les falta un dato."),
]

LECCION_3 = [
    ("¿Qué técnica predice una categoría, como 'spam' o 'no spam'?",
     ["Clasificación", "Regresión", "Agrupamiento", "Reglas de asociación"],
     "Clasificación",
     "La clasificación aprende de ejemplos que ya tienen etiqueta."),
    ("¿Qué técnica agrupa elementos parecidos SIN categorías previas?",
     ["Clasificación", "Agrupamiento (clustering)", "Regresión", "Limpieza"],
     "Agrupamiento (clustering)",
     "Es aprendizaje no supervisado: el algoritmo descubre los grupos por sí solo."),
    ("'Quienes compran pan también compran leche' es un ejemplo de:",
     ["Regresión", "Reglas de asociación", "Imputación", "Normalización"],
     "Reglas de asociación",
     "Se usan mucho en el análisis de la canasta de compras."),
    ("¿Qué técnica sirve para predecir un valor numérico, como el precio de una casa?",
     ["Regresión", "Clasificación", "Agrupamiento", "Reglas de asociación"],
     "Regresión",
     "La regresión estima valores continuos a partir de otras variables."),
]

LECCIONES = [
    ("¿Qué es la minería de datos?", "Conceptos básicos y para qué sirve.", LECCION_1),
    ("El proceso y la preparación de datos", "CRISP-DM y limpieza de datos.", LECCION_2),
    ("Técnicas principales", "Clasificación, agrupamiento, regresión y asociación.", LECCION_3),
]


def sembrar():
    if "--reiniciar" in sys.argv:
        Base.metadata.drop_all(bind=motor)
    Base.metadata.create_all(bind=motor)

    bd = SesionLocal()
    if bd.query(modelos.Curso).count() > 0:
        print("La base de datos ya tiene contenido. Usa --reiniciar para empezar de cero.")
        bd.close()
        return

    curso = modelos.Curso(
        titulo="Minería de datos",
        descripcion="Aprende qué es la minería de datos, cómo se prepara la información y qué técnicas existen.",
    )
    bd.add(curso)
    bd.flush()   # asigna el id al curso sin cerrar la transacción

    for numero, (titulo, descripcion, ejercicios) in enumerate(LECCIONES, start=1):
        leccion = modelos.Leccion(
            curso_id=curso.id, titulo=titulo, descripcion=descripcion,
            orden=numero, xp_recompensa=10,
        )
        bd.add(leccion)
        bd.flush()
        for posicion, (enunciado, opciones, correcta, explicacion) in enumerate(ejercicios, start=1):
            bd.add(modelos.Ejercicio(
                leccion_id=leccion.id, tipo="opcion_multiple",
                enunciado=enunciado, opciones=opciones,
                respuesta_correcta=correcta, explicacion=explicacion,
                orden=posicion,
            ))

    bd.commit()
    bd.close()
    print("Listo: curso, 3 lecciones y 12 ejercicios creados.")


if __name__ == "__main__":
    sembrar()
