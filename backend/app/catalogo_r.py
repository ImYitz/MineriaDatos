# Catálogo de lecciones de R aplicado a minería de datos.
#
# Cada lección tiene:
#   codigo, titulo, descripcion, icono, xp_recompensa
#   teoria      lista de secciones { titulo, texto, codigo }. El texto admite párrafos separados
#               por una línea en blanco y `trozos de código` entre acentos graves. El código de
#               ejemplo se puede editar y ejecutar en la página.
#   practica    lista de tareas { enunciado, plantilla, solucion, comprobaciones }
#
# Cómo se corrige una tarea (el código R se ejecuta en el NAVEGADOR con WebR):
#   1. El navegador ejecuta el código del estudiante y evalúa cada "expresion" de las
#      comprobaciones (por ejemplo  round(mean(x), 2)  o  length(edades) ).
#   2. El navegador envía al servidor SOLO el resultado de cada expresión, convertido a texto.
#   3. El servidor lo compara con "esperado" (con una pequeña tolerancia numérica). El navegador
#      nunca recibe los valores esperados ni la solución: solo la expresión y su descripción.
#      La "pista" se muestra únicamente cuando la comprobación falla.
#
# "solucion" es solo para quien mantiene el catálogo (el servidor nunca la envía). Los valores
# "esperado" se obtuvieron ejecutando esa solución en R.
#
# Para añadir una lección: agrega una entrada aquí y reinicia el servidor. No hace falta tocar la
# base de datos. Usa conjuntos de datos que vienen con R (mtcars, iris, airquality): así el
# navegador no necesita descargar paquetes.
from typing import Optional

PUNTAJE_MINIMO = 60    # % de comprobaciones correctas para aprobar la práctica y ganar recompensas

CATALOGO = [
    # ------------------------------------------------------------------------------------------
    {
        "codigo": "r_basico",
        "titulo": "Primeros pasos en R",
        "icono": "🔤",
        "descripcion": "Variables, vectores y funciones: la base para trabajar con datos en R.",
        "xp_recompensa": 20,
        "teoria": [
            {
                "titulo": "R como calculadora y variables",
                "texto": (
                    "R es un lenguaje diseñado para analizar datos. Se usa muchísimo en minería de datos "
                    "porque trae de fábrica estadística, modelos y manejo de tablas.\n\n"
                    "Puedes hacer cuentas directamente y guardar los resultados en variables con el "
                    "operador `<-`. R distingue mayúsculas de minúsculas: `total` y `Total` son variables "
                    "distintas. Para ver el valor de una variable basta con escribir su nombre."
                ),
                "codigo": "precio <- 12500\ncantidad <- 4\ntotal <- precio * cantidad\ntotal",
            },
            {
                "titulo": "Vectores",
                "texto": (
                    "Un vector es una secuencia de valores del mismo tipo. Se crea con `c()`. Las operaciones "
                    "se aplican a todos los elementos a la vez (esto se llama vectorización), y con corchetes "
                    "`[ ]` se seleccionan elementos por posición o por condición.\n\n"
                    "Funciones muy usadas: `length()`, `sum()`, `mean()`, `max()` y `min()`."
                ),
                "codigo": (
                    "ventas <- c(120, 95, 143, 80, 110)\n"
                    "length(ventas)\n"
                    "mean(ventas)\n"
                    "ventas * 2\n"
                    "ventas[3]\n"
                    "ventas[ventas > 100]"
                ),
            },
            {
                "titulo": "Tipos de datos",
                "texto": (
                    "Los tres tipos más comunes son `numeric` (números), `character` (texto, siempre entre "
                    "comillas) y `logical` (`TRUE` o `FALSE`). La función `class()` te dice de qué tipo es "
                    "un valor. Conocer el tipo importa en minería de datos: no se puede calcular una media "
                    "de texto."
                ),
                "codigo": (
                    "class(3.14)\n"
                    "class(\"hola\")\n"
                    "class(TRUE)\n"
                    "is.numeric(c(1, 2, 3))"
                ),
            },
            {
                "titulo": "Funciones propias",
                "texto": (
                    "Una función recibe argumentos y devuelve el valor de su última expresión. Crear tus "
                    "propias funciones evita repetir código y es la base de cualquier flujo de preparación "
                    "de datos."
                ),
                "codigo": "doble <- function(x) {\n  x * 2\n}\ndoble(21)\ndoble(c(1, 2, 3))",
            },
        ],
        "practica": [
            {
                "enunciado": (
                    "Crea un vector llamado `edades` con los valores 23, 35, 41, 29 y 52. Luego calcula su "
                    "promedio y guárdalo en una variable llamada `promedio`."
                ),
                "plantilla": "# 1. Crea el vector `edades`\n\n# 2. Calcula el promedio y guárdalo en `promedio`\n",
                "solucion": "edades <- c(23, 35, 41, 29, 52)\npromedio <- mean(edades)",
                "comprobaciones": [
                    {"expresion": "length(edades)", "esperado": "5",
                     "descripcion": "El vector `edades` tiene los 5 valores",
                     "pista": "Usa c() con los cinco valores separados por comas."},
                    {"expresion": "promedio", "esperado": "36",
                     "descripcion": "`promedio` es la media de `edades`",
                     "pista": "Usa mean(edades) y guarda el resultado con <-."},
                ],
            },
            {
                "enunciado": (
                    "Escribe una función `a_celsius` que reciba una temperatura en grados Fahrenheit y "
                    "devuelva su equivalente en Celsius con la fórmula (F - 32) * 5 / 9."
                ),
                "plantilla": "a_celsius <- function(f) {\n  # escribe aquí la fórmula\n}\n",
                "solucion": "a_celsius <- function(f) {\n  (f - 32) * 5 / 9\n}",
                "comprobaciones": [
                    {"expresion": "a_celsius(212)", "esperado": "100",
                     "descripcion": "Convierte 212 °F a Celsius",
                     "pista": "La función debe devolver el resultado de la fórmula (F - 32) * 5 / 9."},
                    {"expresion": "round(a_celsius(98.6), 1)", "esperado": "37",
                     "descripcion": "Convierte 98.6 °F a Celsius (con un decimal)",
                     "pista": "Revisa los paréntesis: primero se resta 32 y después se multiplica por 5 / 9."},
                ],
            },
        ],
    },
    # ------------------------------------------------------------------------------------------
    {
        "codigo": "r_dataframes",
        "titulo": "Data frames: la tabla de datos",
        "icono": "🗂️",
        "descripcion": "Crear, explorar y filtrar tablas, el formato habitual de los datos en minería.",
        "xp_recompensa": 20,
        "teoria": [
            {
                "titulo": "¿Qué es un data frame?",
                "texto": (
                    "Un data frame es una tabla: cada fila es una observación (un cliente, un auto, un "
                    "estudiante) y cada columna es una variable. Se crea con `data.frame()` y se accede a "
                    "una columna con el signo `$`."
                ),
                "codigo": (
                    "clientes <- data.frame(\n"
                    "  nombre = c(\"Ana\", \"Luis\", \"Marta\", \"Pedro\"),\n"
                    "  edad = c(28, 35, 42, 31),\n"
                    "  compras = c(5, 12, 8, 3)\n"
                    ")\n"
                    "clientes\n"
                    "clientes$edad"
                ),
            },
            {
                "titulo": "Explorar un data frame",
                "texto": (
                    "Antes de analizar, hay que mirar los datos. `head()` muestra las primeras filas, "
                    "`dim()` el número de filas y columnas, `str()` los tipos de cada variable y `summary()` "
                    "un resumen estadístico. R trae conjuntos de datos de práctica; aquí usamos `mtcars`, "
                    "con datos de 32 autos."
                ),
                "codigo": "head(mtcars)\ndim(mtcars)\nstr(mtcars)\nsummary(mtcars$mpg)",
            },
            {
                "titulo": "Filtrar filas y elegir columnas",
                "texto": (
                    "Con corchetes se escribe `datos[filas, columnas]`. Las filas se pueden elegir con una "
                    "condición, y si dejas vacía una de las dos posiciones se toman todas. No olvides la "
                    "coma: `datos[condicion, ]` filtra filas; `datos[condicion]` haría otra cosa."
                ),
                "codigo": (
                    "economicos <- mtcars[mtcars$mpg > 25, ]\n"
                    "economicos\n"
                    "nrow(economicos)\n"
                    "mtcars[mtcars$cyl == 4, c(\"mpg\", \"hp\")]"
                ),
            },
            {
                "titulo": "Nuevas columnas y resúmenes por grupo",
                "texto": (
                    "Crear una columna nueva es tan simple como asignarla con `$`. Para resumir por grupos "
                    "puedes usar `tapply()`, que aplica una función (por ejemplo `mean`) a cada grupo de "
                    "una variable."
                ),
                "codigo": (
                    "autos <- mtcars\n"
                    "autos$kpl <- autos$mpg * 0.425\n"
                    "head(autos[, c(\"mpg\", \"kpl\")])\n"
                    "tapply(autos$mpg, autos$cyl, mean)"
                ),
            },
        ],
        "practica": [
            {
                "enunciado": (
                    "La base `mtcars` ya está disponible. Crea un data frame llamado `potentes` con los "
                    "autos que tengan más de 200 hp (caballos de fuerza)."
                ),
                "plantilla": "# Filtra las filas de mtcars donde hp sea mayor que 200\n",
                "solucion": "potentes <- mtcars[mtcars$hp > 200, ]",
                "comprobaciones": [
                    {"expresion": "nrow(potentes)", "esperado": "7",
                     "descripcion": "Número de autos en `potentes`",
                     "pista": "Usa mtcars[condicion, ] y no olvides la coma al final."},
                    {"expresion": "round(mean(potentes$mpg), 2)", "esperado": "13.41",
                     "descripcion": "Consumo medio (mpg) de los autos de `potentes`",
                     "pista": "La condición debe ser hp > 200 (estrictamente mayor)."},
                ],
            },
            {
                "enunciado": (
                    "Calcula el consumo medio (`mpg`) de los autos de 6 cilindros y guárdalo en `mpg_6`. "
                    "Después guarda en `n_cuatro` cuántos autos tienen 4 cilindros."
                ),
                "plantilla": "# 1. Media de mpg de los autos con cyl igual a 6 -> mpg_6\n\n# 2. Número de autos con 4 cilindros -> n_cuatro\n",
                "solucion": "mpg_6 <- mean(mtcars$mpg[mtcars$cyl == 6])\nn_cuatro <- sum(mtcars$cyl == 4)",
                "comprobaciones": [
                    {"expresion": "round(mpg_6, 2)", "esperado": "19.74",
                     "descripcion": "Consumo medio de los autos de 6 cilindros",
                     "pista": "Selecciona mpg solo donde cyl == 6 (con dos signos igual) y aplica mean()."},
                    {"expresion": "n_cuatro", "esperado": "11",
                     "descripcion": "Cantidad de autos de 4 cilindros",
                     "pista": "sum() sobre una condición cuenta cuántos valores la cumplen."},
                ],
            },
        ],
    },
    # ------------------------------------------------------------------------------------------
    {
        "codigo": "r_faltantes",
        "titulo": "Valores faltantes en R",
        "icono": "🕳️",
        "descripcion": "Detectar NA, calcular ignorándolos, eliminar filas e imputar valores.",
        "xp_recompensa": 20,
        "teoria": [
            {
                "titulo": "Detectar los NA",
                "texto": (
                    "En R, un dato que falta se representa con `NA`. La función `is.na()` devuelve `TRUE` "
                    "donde hay un valor faltante, y como `TRUE` vale 1, `sum(is.na(x))` cuenta cuántos hay. "
                    "`colSums(is.na(datos))` lo hace para todas las columnas de un data frame. Usaremos "
                    "`airquality`, mediciones de calidad del aire que traen datos faltantes."
                ),
                "codigo": "head(airquality)\nsum(is.na(airquality$Ozone))\ncolSums(is.na(airquality))",
            },
            {
                "titulo": "Los NA contagian los cálculos",
                "texto": (
                    "Si un vector tiene aunque sea un `NA`, funciones como `mean()` o `sum()` devuelven "
                    "`NA`. Para ignorarlos se usa el argumento `na.rm = TRUE`. Ojo: ignorar los NA es una "
                    "decisión de análisis, no un detalle técnico."
                ),
                "codigo": (
                    "mean(airquality$Ozone)\n"
                    "mean(airquality$Ozone, na.rm = TRUE)\n"
                    "median(airquality$Ozone, na.rm = TRUE)"
                ),
            },
            {
                "titulo": "Eliminar filas incompletas",
                "texto": (
                    "`complete.cases()` marca las filas que no tienen ningún NA. Es la forma más simple de "
                    "tratarlos, pero se pierde información: compara cuántas filas quedan."
                ),
                "codigo": (
                    "completos <- airquality[complete.cases(airquality), ]\n"
                    "nrow(airquality)\n"
                    "nrow(completos)"
                ),
            },
            {
                "titulo": "Imputar con la media o la mediana",
                "texto": (
                    "Imputar es reemplazar los NA por un valor estimado. Se selecciona con "
                    "`is.na()` dentro de los corchetes y se asigna el nuevo valor. Trabaja sobre una copia "
                    "para no perder los datos originales. La mediana es más robusta que la media cuando "
                    "hay valores extremos."
                ),
                "codigo": (
                    "aire <- airquality\n"
                    "media_ozono <- mean(aire$Ozone, na.rm = TRUE)\n"
                    "aire$Ozone[is.na(aire$Ozone)] <- media_ozono\n"
                    "sum(is.na(aire$Ozone))"
                ),
            },
        ],
        "practica": [
            {
                "enunciado": (
                    "En `airquality`, cuenta los valores faltantes de la columna `Solar.R` y guárdalos en "
                    "`faltantes_solar`. Calcula también la media de esa columna ignorando los NA y guárdala "
                    "en `media_solar`."
                ),
                "plantilla": "# 1. Cuenta los NA de Solar.R -> faltantes_solar\n\n# 2. Media de Solar.R sin contar los NA -> media_solar\n",
                "solucion": (
                    "faltantes_solar <- sum(is.na(airquality$Solar.R))\n"
                    "media_solar <- mean(airquality$Solar.R, na.rm = TRUE)"
                ),
                "comprobaciones": [
                    {"expresion": "faltantes_solar", "esperado": "7",
                     "descripcion": "Cantidad de valores faltantes en `Solar.R`",
                     "pista": "Combina sum() con is.na() sobre airquality$Solar.R."},
                    {"expresion": "round(media_solar, 2)", "esperado": "185.93",
                     "descripcion": "Media de `Solar.R` ignorando los NA",
                     "pista": "Añade na.rm = TRUE dentro de mean()."},
                ],
            },
            {
                "enunciado": (
                    "Se hizo una copia de `airquality` llamada `aire2`. Imputa los NA de la columna `Ozone` "
                    "con la mediana de esa columna (calculada sin los NA)."
                ),
                "plantilla": "aire2 <- airquality\n\n# Reemplaza los NA de Ozone con la mediana\n",
                "solucion": (
                    "aire2 <- airquality\n"
                    "aire2$Ozone[is.na(aire2$Ozone)] <- median(aire2$Ozone, na.rm = TRUE)"
                ),
                "comprobaciones": [
                    {"expresion": "sum(is.na(aire2$Ozone))", "esperado": "0",
                     "descripcion": "Ya no quedan NA en `aire2$Ozone`",
                     "pista": "Selecciona con aire2$Ozone[is.na(aire2$Ozone)] y asígnale un valor."},
                    {"expresion": "round(mean(aire2$Ozone), 3)", "esperado": "39.559",
                     "descripcion": "Media de `Ozone` después de imputar",
                     "pista": "Imputa con median(..., na.rm = TRUE), no con la media."},
                ],
            },
        ],
    },
    # ------------------------------------------------------------------------------------------
    {
        "codigo": "r_estadistica",
        "titulo": "Estadística descriptiva y correlación",
        "icono": "📊",
        "descripcion": "Medidas de resumen, tablas de frecuencia, correlación y valores atípicos.",
        "xp_recompensa": 20,
        "teoria": [
            {
                "titulo": "Tendencia central y dispersión",
                "texto": (
                    "Para entender una variable numérica se miran su centro y su dispersión: `mean()` "
                    "(media), `median()` (mediana), `sd()` (desviación estándar), `var()` (varianza) y "
                    "`range()` (mínimo y máximo). `summary()` reúne varias de ellas. Probamos con el "
                    "conjunto `iris`, medidas de 150 flores."
                ),
                "codigo": (
                    "x <- iris$Sepal.Length\n"
                    "mean(x)\n"
                    "median(x)\n"
                    "sd(x)\n"
                    "range(x)\n"
                    "summary(x)"
                ),
            },
            {
                "titulo": "Tablas de frecuencia",
                "texto": (
                    "`table()` cuenta cuántas veces aparece cada valor de una variable categórica, y "
                    "`prop.table()` convierte esos conteos en proporciones."
                ),
                "codigo": (
                    "table(iris$Species)\n"
                    "table(mtcars$cyl)\n"
                    "prop.table(table(mtcars$cyl))"
                ),
            },
            {
                "titulo": "Correlación",
                "texto": (
                    "La correlación (`cor()`) mide qué tan relacionadas están dos variables numéricas. Va "
                    "de -1 a 1: cerca de 1, suben juntas; cerca de -1, una sube cuando la otra baja; cerca "
                    "de 0, no hay relación lineal. Una correlación alta no prueba que una variable cause "
                    "la otra."
                ),
                "codigo": (
                    "cor(mtcars$mpg, mtcars$wt)\n"
                    "cor(mtcars[, c(\"mpg\", \"wt\", \"hp\")])"
                ),
            },
            {
                "titulo": "Valores atípicos con la regla del IQR",
                "texto": (
                    "Un valor atípico (outlier) está muy lejos del resto. Una regla común: se considera "
                    "atípico lo que queda por encima de Q3 + 1.5 × IQR o por debajo de Q1 - 1.5 × IQR, donde "
                    "IQR es el rango intercuartílico (`IQR()`). Los atípicos pueden ser errores o casos "
                    "reales interesantes: hay que revisarlos antes de eliminarlos."
                ),
                "codigo": (
                    "x <- mtcars$hp\n"
                    "q3 <- quantile(x, 0.75)\n"
                    "limite <- q3 + 1.5 * IQR(x)\n"
                    "limite\n"
                    "x[x > limite]"
                ),
            },
        ],
        "practica": [
            {
                "enunciado": (
                    "Calcula la media y la desviación estándar de la columna `Sepal.Length` del conjunto "
                    "`iris`. Guárdalas en `media_sepalo` y `desv_sepalo`."
                ),
                "plantilla": "# Media -> media_sepalo\n\n# Desviación estándar -> desv_sepalo\n",
                "solucion": "media_sepalo <- mean(iris$Sepal.Length)\ndesv_sepalo <- sd(iris$Sepal.Length)",
                "comprobaciones": [
                    {"expresion": "round(media_sepalo, 2)", "esperado": "5.84",
                     "descripcion": "Media de `Sepal.Length`",
                     "pista": "Usa mean(iris$Sepal.Length)."},
                    {"expresion": "round(desv_sepalo, 2)", "esperado": "0.83",
                     "descripcion": "Desviación estándar de `Sepal.Length`",
                     "pista": "La función de R para la desviación estándar es sd()."},
                ],
            },
            {
                "enunciado": (
                    "Calcula la correlación entre `mpg` y `wt` de `mtcars` y guárdala en `correlacion`. "
                    "Luego usa la regla del IQR (Q3 + 1.5 × IQR) para contar cuántos autos tienen un `hp` "
                    "atípicamente alto y guarda ese número en `n_atipicos`."
                ),
                "plantilla": "# 1. Correlación entre mpg y wt -> correlacion\n\n# 2. Límite superior: Q3 + 1.5 * IQR de hp\n\n# 3. Cuántos autos superan ese límite -> n_atipicos\n",
                "solucion": (
                    "correlacion <- cor(mtcars$mpg, mtcars$wt)\n"
                    "q3 <- quantile(mtcars$hp, 0.75)\n"
                    "limite <- q3 + 1.5 * IQR(mtcars$hp)\n"
                    "n_atipicos <- sum(mtcars$hp > limite)"
                ),
                "comprobaciones": [
                    {"expresion": "round(correlacion, 3)", "esperado": "-0.868",
                     "descripcion": "Correlación entre `mpg` y `wt`",
                     "pista": "cor(x, y) recibe las dos columnas: mtcars$mpg y mtcars$wt."},
                    {"expresion": "n_atipicos", "esperado": "1",
                     "descripcion": "Autos con `hp` por encima del límite superior",
                     "pista": "El límite es quantile(hp, 0.75) + 1.5 * IQR(hp); cuenta con sum(hp > limite)."},
                ],
            },
        ],
    },
    # ------------------------------------------------------------------------------------------
    {
        "codigo": "r_kmeans",
        "titulo": "Normalización y K-means en R",
        "icono": "🧪",
        "descripcion": "Escalar variables y agrupar datos con K-means, igual que en el laboratorio.",
        "xp_recompensa": 20,
        "teoria": [
            {
                "titulo": "Escalar variables",
                "texto": (
                    "Las variables con escalas muy distintas dominan las distancias. Hay dos formas "
                    "comunes de escalar: Min-Max lleva los valores al rango [0, 1] y Z-score los centra "
                    "en 0 con desviación 1. En R, Z-score es `scale()`; Min-Max se escribe a mano con una "
                    "función."
                ),
                "codigo": (
                    "min_max <- function(x) {\n"
                    "  (x - min(x)) / (max(x) - min(x))\n"
                    "}\n"
                    "x <- c(10, 20, 30, 50)\n"
                    "min_max(x)\n"
                    "as.numeric(scale(x))"
                ),
            },
            {
                "titulo": "Distancias",
                "texto": (
                    "K-means y k-NN se basan en distancias. `dist()` calcula la distancia euclidiana entre "
                    "todas las filas de una tabla. Compara la distancia entre los tres primeros autos con "
                    "los datos originales y con los datos escalados."
                ),
                "codigo": (
                    "datos <- mtcars[1:3, c(\"mpg\", \"hp\", \"wt\")]\n"
                    "dist(datos)\n"
                    "dist(scale(mtcars[, c(\"mpg\", \"hp\", \"wt\")]))[1:3]"
                ),
            },
            {
                "titulo": "K-means con kmeans()",
                "texto": (
                    "`kmeans(datos, centers = 3)` agrupa las filas en 3 grupos. Como arranca con "
                    "centroides al azar, conviene fijar una semilla con `set.seed()` para obtener siempre "
                    "el mismo resultado y usar `nstart` para probar varios arranques y quedarse con el "
                    "mejor. El resultado trae `cluster` (grupo de cada fila), `centers` y `size`."
                ),
                "codigo": (
                    "datos <- scale(iris[, 1:4])\n"
                    "set.seed(123)\n"
                    "modelo <- kmeans(datos, centers = 3, nstart = 25)\n"
                    "modelo$size\n"
                    "table(modelo$cluster, iris$Species)"
                ),
            },
            {
                "titulo": "Elegir k: el método del codo",
                "texto": (
                    "`tot.withinss` es la inercia: la suma de distancias al cuadrado de cada punto a su "
                    "centroide. Siempre baja al aumentar k, pero el punto donde deja de bajar con fuerza "
                    "(el codo) sugiere un buen valor de k."
                ),
                "codigo": (
                    "datos <- scale(iris[, 1:4])\n"
                    "set.seed(123)\n"
                    "inercia <- sapply(1:6, function(k) kmeans(datos, centers = k, nstart = 25)$tot.withinss)\n"
                    "round(inercia, 1)"
                ),
            },
        ],
        "practica": [
            {
                "enunciado": (
                    "Aplica la normalización Min-Max a la columna `mpg` de `mtcars` y guarda el resultado "
                    "en `mpg_norm`. Todos los valores deben quedar entre 0 y 1."
                ),
                "plantilla": "x <- mtcars$mpg\n\n# Escribe (x - mínimo) / (máximo - mínimo) y guárdalo en mpg_norm\n",
                "solucion": "x <- mtcars$mpg\nmpg_norm <- (x - min(x)) / (max(x) - min(x))",
                "comprobaciones": [
                    {"expresion": "round(range(mpg_norm), 2)", "esperado": "0,1",
                     "descripcion": "El mínimo y el máximo de `mpg_norm`",
                     "pista": "Resta el mínimo y divide entre (máximo - mínimo)."},
                    {"expresion": "round(mean(mpg_norm), 3)", "esperado": "0.412",
                     "descripcion": "Media de `mpg_norm`",
                     "pista": "Revisa los paréntesis: (x - min(x)) / (max(x) - min(x))."},
                ],
            },
            {
                "enunciado": (
                    "Escala las cuatro primeras columnas de `iris` con `scale()` (guárdalas en `datos`) y "
                    "ejecuta K-means con 3 grupos y `nstart = 25`. Guarda el modelo en `modelo`. La semilla "
                    "ya está fijada para que el resultado sea reproducible."
                ),
                "plantilla": "set.seed(123)\n\n# 1. Escala las columnas 1 a 4 de iris -> datos\n\n# 2. Ejecuta kmeans con 3 grupos y nstart = 25 -> modelo\n",
                "solucion": (
                    "set.seed(123)\n"
                    "datos <- scale(iris[, 1:4])\n"
                    "modelo <- kmeans(datos, centers = 3, nstart = 25)"
                ),
                "comprobaciones": [
                    {"expresion": "length(modelo$size)", "esperado": "3",
                     "descripcion": "El modelo tiene 3 grupos",
                     "pista": "Usa centers = 3 en kmeans()."},
                    {"expresion": "sort(modelo$size)", "esperado": "47,50,53",
                     "descripcion": "Tamaño de los grupos (ordenados de menor a mayor)",
                     "pista": "Escala los datos con scale(iris[, 1:4]) antes de ejecutar kmeans() y usa nstart = 25."},
                ],
            },
        ],
    },
    # ------------------------------------------------------------------------------------------
    {
        "codigo": "r_regresion",
        "titulo": "Regresión lineal y evaluación",
        "icono": "📈",
        "descripcion": "Ajustar un modelo con lm(), predecir, separar entrenamiento y prueba y medir el error.",
        "xp_recompensa": 20,
        "teoria": [
            {
                "titulo": "Regresión lineal simple con lm()",
                "texto": (
                    "La regresión lineal predice una variable numérica a partir de otra con una recta. En R se "
                    "escribe con una fórmula: `lm(y ~ x, data = datos)` significa \"y en función de x\". "
                    "`coef()` devuelve la ordenada y la pendiente, y `summary()` trae medidas de ajuste como "
                    "el R² (qué proporción de la variación explica el modelo)."
                ),
                "codigo": (
                    "modelo <- lm(mpg ~ wt, data = mtcars)\n"
                    "coef(modelo)\n"
                    "summary(modelo)$r.squared"
                ),
            },
            {
                "titulo": "Predecir con el modelo",
                "texto": (
                    "`predict()` aplica el modelo a datos nuevos. Los datos nuevos deben ser un data frame "
                    "con columnas del mismo nombre que las variables del modelo."
                ),
                "codigo": (
                    "modelo <- lm(mpg ~ wt, data = mtcars)\n"
                    "nuevos <- data.frame(wt = c(2.5, 3, 4))\n"
                    "predict(modelo, newdata = nuevos)"
                ),
            },
            {
                "titulo": "Entrenamiento y prueba",
                "texto": (
                    "Para saber si un modelo generaliza, se entrena con una parte de los datos y se evalúa "
                    "con otra que no vio. `sample()` elige filas al azar; el signo menos en `[-indices, ]` "
                    "selecciona todas las demás. Fijar la semilla hace que la separación sea repetible."
                ),
                "codigo": (
                    "set.seed(42)\n"
                    "n <- nrow(mtcars)\n"
                    "indices <- sample(1:n, size = round(0.7 * n))\n"
                    "entrenamiento <- mtcars[indices, ]\n"
                    "prueba <- mtcars[-indices, ]\n"
                    "c(nrow(entrenamiento), nrow(prueba))"
                ),
            },
            {
                "titulo": "Medir el error: RMSE",
                "texto": (
                    "El RMSE (raíz del error cuadrático medio) resume cuánto se equivoca el modelo, en las "
                    "mismas unidades de la variable que se predice. Se calcula como la raíz de la media de "
                    "los errores al cuadrado. Entre dos modelos, es mejor el de menor RMSE sobre datos de prueba."
                ),
                "codigo": (
                    "set.seed(42)\n"
                    "indices <- sample(1:nrow(mtcars), size = 22)\n"
                    "modelo <- lm(mpg ~ wt, data = mtcars[indices, ])\n"
                    "prueba <- mtcars[-indices, ]\n"
                    "predicho <- predict(modelo, newdata = prueba)\n"
                    "sqrt(mean((prueba$mpg - predicho)^2))"
                ),
            },
        ],
        "practica": [
            {
                "enunciado": (
                    "Ajusta una regresión lineal que prediga `mpg` a partir de `hp` usando `mtcars` y "
                    "guarda el modelo en `modelo_hp`."
                ),
                "plantilla": "# Ajusta el modelo con lm() y guárdalo en modelo_hp\n",
                "solucion": "modelo_hp <- lm(mpg ~ hp, data = mtcars)",
                "comprobaciones": [
                    {"expresion": "round(coef(modelo_hp)[2], 4)", "esperado": "-0.0682",
                     "descripcion": "Pendiente del modelo (coeficiente de `hp`)",
                     "pista": "La fórmula es mpg ~ hp: la variable a predecir va a la izquierda de ~."},
                    {"expresion": "round(summary(modelo_hp)$r.squared, 3)", "esperado": "0.602",
                     "descripcion": "R² del modelo",
                     "pista": "Usa data = mtcars y la fórmula mpg ~ hp."},
                ],
            },
            {
                "enunciado": (
                    "Usando el modelo ya ajustado, predice el `mpg` de un auto de 150 hp y guárdalo en "
                    "`prediccion`. Calcula también el RMSE del modelo sobre los propios datos de `mtcars` "
                    "y guárdalo en `rmse`."
                ),
                "plantilla": "modelo_hp <- lm(mpg ~ hp, data = mtcars)\n\n# 1. Predicción para hp = 150 -> prediccion\n\n# 2. RMSE sobre mtcars -> rmse\n",
                "solucion": (
                    "modelo_hp <- lm(mpg ~ hp, data = mtcars)\n"
                    "prediccion <- predict(modelo_hp, newdata = data.frame(hp = 150))\n"
                    "rmse <- sqrt(mean((mtcars$mpg - predict(modelo_hp))^2))"
                ),
                "comprobaciones": [
                    {"expresion": "round(prediccion, 2)", "esperado": "19.86",
                     "descripcion": "Predicción de `mpg` para un auto de 150 hp",
                     "pista": "predict() necesita newdata = data.frame(hp = 150)."},
                    {"expresion": "round(rmse, 3)", "esperado": "3.74",
                     "descripcion": "RMSE del modelo sobre `mtcars`",
                     "pista": "sqrt(mean((reales - predichos)^2)), con predict(modelo_hp) como predichos."},
                ],
            },
        ],
    },
]


def buscar_leccion_r(codigo: str) -> Optional[dict]:
    """Devuelve la lección de R con ese código, o None si no existe."""
    for leccion in CATALOGO:
        if leccion["codigo"] == codigo:
            return leccion
    return None
