// Motor de R en el navegador (WebR: R compilado a WebAssembly).
//
// Uso desde las páginas:
//   await RMotor.iniciar();                              // carga R (la primera vez tarda unos segundos)
//   const r = await RMotor.ejecutar(codigo, expresiones); // ejecuta el código del estudiante
//   r.error      -> texto del error de R (o null)
//   r.salida     -> lo que R imprimiría en la consola
//   r.avisos     -> avisos y mensajes
//   r.valores    -> el resultado de cada expresión de comprobación, ya convertido a texto
//
// El código se ejecuta en un entorno nuevo cada vez, así que unas ejecuciones no afectan a otras.
// Los valores de las comprobaciones se envían al servidor, que es quien decide si son correctos.

const RMotor = (function () {
  const URL_WEBR = "https://webr.r-wasm.org/latest/webr.mjs";

  // Funciones de R que se cargan una sola vez al iniciar.
  const CODIGO_R = String.raw`
.mineria_js <- function(x) {
  x <- gsub("\\", "\\\\", x, fixed = TRUE)
  x <- gsub("\"", "\\\"", x, fixed = TRUE)
  x <- gsub("\n", "\\n", x, fixed = TRUE)
  x <- gsub("\t", "\\t", x, fixed = TRUE)
  x <- gsub("[[:cntrl:]]", " ", x)
  paste0("\"", x, "\"")
}

.mineria_formato <- function(v) {
  if (is.factor(v)) v <- as.character(v)
  if (is.list(v)) v <- unlist(v)
  if (is.numeric(v)) v <- round(v, 4)
  paste(as.character(v), collapse = ",")
}

.mineria_ejecutar <- function(codigo, expresiones = character(0)) {
  expresiones <- as.character(expresiones)
  env <- new.env(parent = globalenv())
  error <- NULL
  avisos <- character(0)

  salida <- utils::capture.output({
    tryCatch(
      withCallingHandlers({
        for (e in parse(text = codigo, keep.source = FALSE)) {
          r <- withVisible(eval(e, env))
          if (r$visible) print(r$value)
        }
      },
      warning = function(w) {
        avisos <<- c(avisos, paste0("Aviso: ", conditionMessage(w)))
        invokeRestart("muffleWarning")
      },
      message = function(m) {
        avisos <<- c(avisos, sub("\n$", "", conditionMessage(m)))
        invokeRestart("muffleMessage")
      }),
      error = function(e) error <<- conditionMessage(e)
    )
  })

  valores <- character(0)
  if (is.null(error)) {
    valores <- vapply(expresiones, function(ex) {
      tryCatch(.mineria_formato(eval(parse(text = ex)[[1]], env)),
               error = function(e) paste0("<error: ", conditionMessage(e), ">"))
    }, character(1), USE.NAMES = FALSE)
  }

  texto <- paste(salida, collapse = "\n")
  if (nchar(texto) > 20000) texto <- paste0(substr(texto, 1, 20000), "\n[... salida recortada ...]")

  paste0(
    "{\"error\":", if (is.null(error)) "null" else .mineria_js(error),
    ",\"salida\":", .mineria_js(texto),
    ",\"avisos\":[", paste(vapply(avisos, .mineria_js, character(1), USE.NAMES = FALSE), collapse = ","), "]",
    ",\"valores\":[", paste(vapply(valores, .mineria_js, character(1), USE.NAMES = FALSE), collapse = ","), "]}"
  )
}
`;

  let webR = null;
  let promesa = null;
  let estado = "sin_iniciar";   // sin_iniciar | cargando | listo | error
  const oyentes = [];

  function cambiarEstado(nuevo) {
    estado = nuevo;
    for (const f of oyentes) f(nuevo);
  }

  // Texto literal de R que admite comillas y saltos de línea sin escapar: r"------( ... )------"
  function literal(texto) {
    return 'r"------(' + texto + ')------"';
  }

  async function iniciar() {
    if (promesa) return promesa;
    cambiarEstado("cargando");
    promesa = (async () => {
      try {
        if (!webR) {
          const modulo = await import(URL_WEBR);
          // PostMessage funciona en cualquier servidor, sin cabeceras especiales
          const instancia = new modulo.WebR({ channelType: modulo.ChannelType.PostMessage });
          await instancia.init();
          webR = instancia;
        }
        await webR.evalRVoid(CODIGO_R);
        cambiarEstado("listo");
        return webR;
      } catch (error) {
        promesa = null;          // permite reintentar
        cambiarEstado("error");
        throw error;
      }
    })();
    return promesa;
  }

  async function ejecutar(codigo, expresiones) {
    await iniciar();
    const lista = (expresiones || []).map(literal).join(", ");
    const llamada = ".mineria_ejecutar(" + literal(codigo) + ", c(" + lista + "))";
    const texto = await webR.evalRString(llamada);
    return JSON.parse(texto);
  }

  return {
    iniciar,
    ejecutar,
    obtenerEstado: () => estado,
    alCambiarEstado: (f) => { oyentes.push(f); },
    // Solo para pruebas: usar una instancia de WebR ya creada
    _usar: (instancia) => { webR = instancia; },
  };
})();
