// Pantalla de una lección de R: teoría con ejemplos ejecutables y práctica final.
//
// El código R se ejecuta en el navegador (ver js/r_motor.js). Al comprobar la práctica, el
// navegador envía al servidor solo los resultados; el servidor los corrige y reparte las recompensas.

// El código de la lección viene en la dirección: leccion_r.html?id=r_basico
const codigoR = new URLSearchParams(window.location.search).get("id");

let leccion = null;
const editores = {};    // id de tarea -> <textarea>
const salidas = {};     // id de tarea -> <pre> con la salida de R
const tarjetas = {};    // id de tarea -> tarjeta de la tarea
const marcas = {};      // "tarea-comprobacion" -> <li> de la comprobación
let aprobada = false;

const elBoton = document.getElementById("boton-comprobar");
const elError = document.getElementById("mensaje-error");
const elMensaje = document.getElementById("mensaje-practica");
const elEstado = document.getElementById("estado-r");

// ---------- Estado del motor de R ----------

function iniciarR() {
  RMotor.iniciar().catch(() => { /* el estado "error" ya se muestra en pantalla */ });
}

function pintarEstado(estado) {
  elEstado.className = "estado-r" + (estado === "listo" ? " listo" : estado === "error" ? " error" : "");
  elEstado.textContent = "";
  const texto = document.createElement("span");
  if (estado === "listo") {
    texto.textContent = "✅ R está listo. Puedes ejecutar el código.";
  } else if (estado === "error") {
    texto.textContent = "⚠️ No se pudo cargar R. Necesitas conexión a internet.";
  } else {
    texto.textContent = "⏳ Cargando R en tu navegador… la primera vez puede tardar unos segundos.";
  }
  elEstado.appendChild(texto);
  if (estado === "error") {
    const reintentar = document.createElement("button");
    reintentar.type = "button";
    reintentar.textContent = "Reintentar";
    reintentar.addEventListener("click", iniciarR);
    elEstado.appendChild(reintentar);
  }
}

// ---------- Utilidades de pantalla ----------

// Escribe texto en párrafos (separados por una línea en blanco) y convierte `código` en <code>
function escribirTexto(contenedor, texto) {
  for (const parrafo of texto.split("\n\n")) {
    const p = document.createElement("p");
    parrafo.split("`").forEach((trozo, i) => {
      if (i % 2 === 1) {
        const codigo = document.createElement("code");
        codigo.textContent = trozo;
        p.appendChild(codigo);
      } else {
        p.appendChild(document.createTextNode(trozo));
      }
    });
    contenedor.appendChild(p);
  }
}

function crearEditor(valor) {
  const area = document.createElement("textarea");
  area.className = "editor-r";
  area.value = valor;
  area.rows = Math.min(16, Math.max(4, valor.split("\n").length + 1));
  area.spellcheck = false;
  area.setAttribute("autocapitalize", "off");
  area.setAttribute("autocomplete", "off");
  area.setAttribute("aria-label", "Código de R");
  return area;
}

// Muestra en un <pre> lo que devolvió R: salida, avisos y error
function mostrarSalida(pre, r) {
  pre.textContent = "";
  if (r.salida) pre.appendChild(document.createTextNode(r.salida + "\n"));
  for (const aviso of r.avisos) {
    const linea = document.createElement("span");
    linea.className = "aviso-r";
    linea.textContent = aviso + "\n";
    pre.appendChild(linea);
  }
  if (r.error) {
    const linea = document.createElement("span");
    linea.className = "error-r";
    linea.textContent = "Error: " + r.error;
    pre.appendChild(linea);
  }
  if (!r.salida && r.avisos.length === 0 && !r.error) {
    pre.textContent = "(el código se ejecutó sin mostrar nada)";
  }
}

function mostrarFalloDeR(pre, error) {
  pre.textContent = "";
  const linea = document.createElement("span");
  linea.className = "error-r";
  linea.textContent = "No se pudo ejecutar R: " + (error && error.message ? error.message : "error desconocido");
  pre.appendChild(linea);
}

// Editor + botones Ejecutar / Restaurar + salida. Sirve para los ejemplos y para las tareas.
function crearBloqueEjecutable(codigoInicial) {
  const caja = document.createElement("div");
  const editor = crearEditor(codigoInicial);
  const salida = document.createElement("pre");
  salida.className = "salida-r";
  salida.setAttribute("aria-live", "polite");

  const controles = document.createElement("div");
  controles.className = "controles-r";
  const botonEjecutar = document.createElement("button");
  botonEjecutar.type = "button";
  botonEjecutar.className = "boton-r ejecutar";
  botonEjecutar.textContent = "▶ Ejecutar";
  const botonRestaurar = document.createElement("button");
  botonRestaurar.type = "button";
  botonRestaurar.className = "boton-r";
  botonRestaurar.textContent = "↺ Restaurar código";
  controles.appendChild(botonEjecutar);
  controles.appendChild(botonRestaurar);

  async function ejecutar() {
    botonEjecutar.disabled = true;
    botonEjecutar.textContent = "Ejecutando…";
    salida.textContent = "";
    try {
      mostrarSalida(salida, await RMotor.ejecutar(editor.value, []));
    } catch (error) {
      mostrarFalloDeR(salida, error);
    }
    botonEjecutar.disabled = false;
    botonEjecutar.textContent = "▶ Ejecutar";
  }

  botonEjecutar.addEventListener("click", ejecutar);
  botonRestaurar.addEventListener("click", () => { editor.value = codigoInicial; salida.textContent = ""; });
  editor.addEventListener("keydown", (evento) => {
    if ((evento.ctrlKey || evento.metaKey) && evento.key === "Enter") {
      evento.preventDefault();
      ejecutar();
    }
  });

  caja.appendChild(editor);
  caja.appendChild(controles);
  caja.appendChild(salida);
  return { caja, editor, salida };
}

// ---------- Teoría ----------

function dibujarTeoria() {
  const zona = document.getElementById("zona-teoria");
  zona.textContent = "";
  leccion.teoria.forEach((seccion, indice) => {
    const tarjeta = document.createElement("div");
    tarjeta.className = "tarjeta-teoria";
    const titulo = document.createElement("h3");
    titulo.textContent = (indice + 1) + ". " + seccion.titulo;
    tarjeta.appendChild(titulo);
    escribirTexto(tarjeta, seccion.texto);
    if (seccion.codigo) {
      const ayuda = document.createElement("p");
      ayuda.className = "texto-suave";
      ayuda.textContent = "Prueba el ejemplo: puedes cambiar el código y ejecutarlo (Ctrl + Enter).";
      tarjeta.appendChild(ayuda);
      tarjeta.appendChild(crearBloqueEjecutable(seccion.codigo).caja);
    }
    zona.appendChild(tarjeta);
  });
}

// ---------- Práctica ----------

function dibujarPractica() {
  document.getElementById("zona-practica").classList.remove("oculto");
  document.getElementById("intro-practica").textContent =
    "Escribe tu código en cada tarea. Con «Ejecutar» ves el resultado; con «Comprobar mi práctica» " +
    "se ejecuta todo y el servidor lo corrige. Necesitas al menos " + leccion.puntaje_minimo +
    " % de comprobaciones correctas para aprobar y ganar XP.";

  const lista = document.getElementById("lista-tareas");
  lista.textContent = "";
  for (const tarea of leccion.practica) {
    const tarjeta = document.createElement("div");
    tarjeta.className = "tarjeta-tarea";
    const titulo = document.createElement("h3");
    titulo.textContent = "Tarea " + (tarea.id + 1);
    tarjeta.appendChild(titulo);
    escribirTexto(tarjeta, tarea.enunciado);

    const bloque = crearBloqueEjecutable(tarea.plantilla);
    editores[tarea.id] = bloque.editor;
    salidas[tarea.id] = bloque.salida;
    tarjeta.appendChild(bloque.caja);

    const checks = document.createElement("ul");
    checks.className = "checks-r";
    for (const c of tarea.comprobaciones) {
      const li = document.createElement("li");
      const marca = document.createElement("span");
      marca.className = "marca";
      marca.textContent = "○";
      const texto = document.createElement("span");
      texto.textContent = c.descripcion;
      li.appendChild(marca);
      li.appendChild(texto);
      checks.appendChild(li);
      marcas[tarea.id + "-" + c.id] = li;
    }
    tarjeta.appendChild(checks);

    tarjetas[tarea.id] = tarjeta;
    lista.appendChild(tarjeta);
  }
}

async function comprobar() {
  elError.textContent = "";
  elMensaje.textContent = "";
  elMensaje.className = "mensaje-practica";
  elBoton.disabled = true;
  elBoton.textContent = "Ejecutando y comprobando…";

  try {
    // 1) El navegador ejecuta el código de cada tarea y evalúa las comprobaciones
    const tareas = [];
    for (const tarea of leccion.practica) {
      const expresiones = tarea.comprobaciones.map((c) => c.expresion);
      const r = await RMotor.ejecutar(editores[tarea.id].value, expresiones);
      mostrarSalida(salidas[tarea.id], r);
      tareas.push({ tarea_id: tarea.id, error: r.error, valores: r.valores });
    }
    // 2) El servidor compara con los valores esperados y reparte las recompensas
    const resultado = await pedirApi(
      "/api/r/" + encodeURIComponent(leccion.codigo) + "/evaluar",
      { method: "POST", body: JSON.stringify({ tareas }) }
    );
    mostrarResultado(resultado);
  } catch (error) {
    elError.textContent =
      "No se pudo comprobar tu práctica: " + (error && error.message ? error.message : "error desconocido");
  }

  if (!aprobada) {
    elBoton.disabled = false;
    elBoton.textContent = "Comprobar mi práctica";
  }
}

function mostrarResultado(res) {
  // Marca cada comprobación y muestra la pista de las que fallaron
  const tareaCorrecta = {};
  for (const r of res.revision) {
    const li = marcas[r.tarea_id + "-" + r.comprobacion_id];
    if (!li) continue;
    li.className = r.correcta ? "ok" : "mal";
    li.querySelector(".marca").textContent = r.correcta ? "✓" : "✗";
    const anterior = li.querySelector(".pista-r");
    if (anterior) anterior.remove();
    if (!r.correcta && r.pista) {
      const pista = document.createElement("span");
      pista.className = "pista-r";
      pista.textContent = "Pista: " + r.pista;
      li.appendChild(pista);
    }
    tareaCorrecta[r.tarea_id] = tareaCorrecta[r.tarea_id] !== false && r.correcta;
  }
  for (const id in tareaCorrecta) {
    tarjetas[id].classList.toggle("hecha", tareaCorrecta[id]);
    tarjetas[id].classList.toggle("fallida", !tareaCorrecta[id]);
  }

  if (!res.aprobado) {
    elMensaje.className = "mensaje-practica mal";
    elMensaje.textContent =
      "Acertaste " + res.aciertos + " de " + res.total + " comprobaciones (" + res.puntaje + " %). " +
      "Necesitas al menos " + res.puntaje_minimo + " % para aprobar. Revisa las pistas y vuelve a comprobar.";
    return;
  }

  // Práctica aprobada: se muestran las recompensas
  aprobada = true;
  elBoton.classList.add("oculto");
  document.getElementById("zona-final").classList.remove("oculto");

  document.getElementById("resumen-final").textContent =
    "Acertaste " + res.aciertos + " de " + res.total + " comprobaciones (" + res.puntaje + " %).";

  let textoXp = "+" + res.xp_ganada + " XP";
  if (!res.es_primera_vez) {
    textoXp += " (repetición: 30% de la XP)";
  }
  document.getElementById("resumen-xp").textContent = textoXp;

  if (res.subio_de_nivel) {
    document.getElementById("mensaje-nivel").textContent = "🎉 ¡Subiste al nivel " + res.nivel + "!";
  }
  document.getElementById("resumen-monedas").textContent =
    "+" + res.monedas_ganadas + " 🪙 monedas (tienes " + res.monedas_total + ")";
  document.getElementById("resumen-racha").textContent =
    "🔥 Racha: " + res.racha_actual + (res.racha_actual === 1 ? " día" : " días");

  const contenedorLogros = document.getElementById("logros-nuevos");
  contenedorLogros.textContent = "";
  for (const logro of res.logros_nuevos) {
    const tarjeta = document.createElement("div");
    tarjeta.className = "logro-nuevo";
    tarjeta.textContent =
      iconoLogro(logro.icono) + " ¡Logro desbloqueado: " + logro.nombre +
      "! (+" + logro.recompensa_monedas + " 🪙)";
    contenedorLogros.appendChild(tarjeta);
  }
  document.getElementById("zona-final").scrollIntoView({ behavior: "smooth", block: "start" });
}

// ---------- Inicio ----------

async function iniciar() {
  // R empieza a cargar enseguida, mientras se lee la lección
  RMotor.alCambiarEstado(pintarEstado);
  pintarEstado(RMotor.obtenerEstado());
  iniciarR();

  try {
    leccion = await pedirApi("/api/r/" + encodeURIComponent(codigoR));
  } catch (error) {
    document.getElementById("titulo-r").textContent = "No se pudo cargar la lección";
    elEstado.classList.add("oculto");
    return;
  }

  document.title = leccion.titulo;
  document.getElementById("titulo-r").textContent = leccion.icono + " " + leccion.titulo;
  document.getElementById("descripcion-r").textContent = leccion.descripcion;
  dibujarTeoria();
  dibujarPractica();
}

elBoton.addEventListener("click", comprobar);

if (exigirSesion()) {
  iniciar();
}
