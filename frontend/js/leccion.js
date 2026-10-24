// Lógica de la pantalla de ejercicios.

// El id de la lección viene en la dirección: leccion.html?id=1
const parametros = new URLSearchParams(window.location.search);
const idLeccion = parametros.get("id");

// Estado actual de la lección
let leccion = null;        // datos de la lección
let indiceActual = 0;      // en qué ejercicio vamos
let aciertos = 0;          // cuántos ha acertado (solo para mostrar mientras juega)
let opcionElegida = null;  // texto de la opción seleccionada
let yaComprobado = false;  // true cuando ya vio si acertó
let respuestasDadas = [];  // lista de {ejercicio_id, respuesta} para enviar al terminar

// Elementos de la página
const elTitulo = document.getElementById("titulo-leccion");
const elEnunciado = document.getElementById("enunciado");
const elOpciones = document.getElementById("opciones");
const elRetro = document.getElementById("retroalimentacion");
const elBoton = document.getElementById("boton-principal");
const elBarra = document.getElementById("barra-progreso");

async function iniciar() {
  try {
    leccion = await pedirApi("/api/lecciones/" + idLeccion);
    elTitulo.textContent = leccion.titulo;
    mostrarEjercicio();
  } catch (error) {
    elEnunciado.textContent = "No se pudo cargar la lección.";
  }
}

function mostrarEjercicio() {
  const ejercicio = leccion.ejercicios[indiceActual];
  opcionElegida = null;
  yaComprobado = false;

  elEnunciado.textContent = ejercicio.enunciado;
  elRetro.textContent = "";
  elRetro.className = "retroalimentacion";
  elBoton.textContent = "Comprobar";
  elBoton.disabled = true;   // se activa al elegir una opción

  // La barra avanza según los ejercicios ya completados
  const porcentaje = (indiceActual / leccion.ejercicios.length) * 100;
  elBarra.style.width = porcentaje + "%";

  // Crear un botón por cada opción
  elOpciones.innerHTML = "";
  for (const texto of ejercicio.opciones) {
    const boton = document.createElement("button");
    boton.className = "opcion";
    boton.textContent = texto;
    boton.addEventListener("click", () => elegirOpcion(texto, boton));
    elOpciones.appendChild(boton);
  }
}

function elegirOpcion(texto, boton) {
  if (yaComprobado) return;   // no se puede cambiar después de comprobar
  opcionElegida = texto;
  for (const otro of elOpciones.children) {
    otro.classList.remove("elegida");
  }
  boton.classList.add("elegida");
  elBoton.disabled = false;
}

async function comprobar() {
  const ejercicio = leccion.ejercicios[indiceActual];
  try {
    // Enviamos la respuesta al servidor, que es quien la corrige
    const resultado = await pedirApi(
      "/api/ejercicios/" + ejercicio.id + "/responder",
      { method: "POST", body: JSON.stringify({ respuesta: opcionElegida }) }
    );
    yaComprobado = true;

    // Guardamos la respuesta; al terminar la lección se enviarán todas juntas
    respuestasDadas.push({ ejercicio_id: ejercicio.id, respuesta: opcionElegida });

    if (resultado.correcto) {
      aciertos++;
      elRetro.textContent = "¡Correcto!";
      elRetro.className = "retroalimentacion bien";
    } else {
      elRetro.textContent = "Incorrecto. La respuesta era: " + resultado.respuesta_correcta;
      elRetro.className = "retroalimentacion mal";
    }
    if (resultado.explicacion) {
      elRetro.textContent += " — " + resultado.explicacion;
    }

    // Pintar la opción correcta en verde y la elegida (si falló) en rojo
    for (const boton of elOpciones.children) {
      if (boton.textContent === resultado.respuesta_correcta) {
        boton.classList.add("correcta");
      } else if (boton.classList.contains("elegida")) {
        boton.classList.add("incorrecta");
      }
    }

    const esUltimo = indiceActual === leccion.ejercicios.length - 1;
    elBoton.textContent = esUltimo ? "Terminar" : "Continuar";
  } catch (error) {
    elRetro.textContent = "Error al comprobar la respuesta. Intenta de nuevo.";
    elRetro.className = "retroalimentacion mal";
  }
}

function continuar() {
  indiceActual++;
  if (indiceActual >= leccion.ejercicios.length) {
    terminarLeccion();
  } else {
    mostrarEjercicio();
  }
}

// Envía todas las respuestas al servidor, que calcula el puntaje y la XP y la guarda
async function terminarLeccion() {
  elBoton.disabled = true;
  elBoton.textContent = "Guardando...";
  try {
    const resultado = await pedirApi(
      "/api/lecciones/" + idLeccion + "/completar",
      { method: "POST", body: JSON.stringify({ respuestas: respuestasDadas }) }
    );
    mostrarResultadoFinal(resultado);
  } catch (error) {
    // Si falla, dejamos el botón para reintentar sin perder las respuestas
    elRetro.textContent = "No se pudo guardar tu progreso. Pulsa el botón para reintentar.";
    elRetro.className = "retroalimentacion mal";
    elBoton.disabled = false;
    elBoton.textContent = "Reintentar";
    indiceActual = leccion.ejercicios.length - 1;   // seguimos en el último ejercicio
  }
}

function mostrarResultadoFinal(resultado) {
  document.getElementById("zona-ejercicio").classList.add("oculto");
  document.getElementById("zona-final").classList.remove("oculto");

  document.getElementById("resumen-final").textContent =
    "Acertaste " + resultado.aciertos + " de " + resultado.total +
    " ejercicios (" + resultado.puntaje + "%).";

  let textoXp = "+" + resultado.xp_ganada + " XP";
  if (!resultado.es_primera_vez) {
    textoXp += " (repetición: 30% de la XP)";
  }
  document.getElementById("resumen-xp").textContent = textoXp;

  if (resultado.subio_de_nivel) {
    document.getElementById("mensaje-nivel").textContent =
      "🎉 ¡Subiste al nivel " + resultado.nivel + "!";
  }

  // Monedas y racha
  document.getElementById("resumen-monedas").textContent =
    "+" + resultado.monedas_ganadas + " 🪙 monedas (tienes " + resultado.monedas_total + ")";
  document.getElementById("resumen-racha").textContent =
    "🔥 Racha: " + resultado.racha_actual + (resultado.racha_actual === 1 ? " día" : " días");

  // Logros desbloqueados con esta lección
  const contenedorLogros = document.getElementById("logros-nuevos");
  contenedorLogros.innerHTML = "";
  for (const logro of resultado.logros_nuevos) {
    const tarjeta = document.createElement("div");
    tarjeta.className = "logro-nuevo";
    tarjeta.textContent =
      iconoLogro(logro.icono) + " ¡Logro desbloqueado: " + logro.nombre +
      "! (+" + logro.recompensa_monedas + " 🪙)";
    contenedorLogros.appendChild(tarjeta);
  }
}

// El botón principal hace dos cosas según el momento
elBoton.addEventListener("click", () => {
  if (yaComprobado) {
    continuar();
  } else {
    comprobar();
  }
});

// Esta página es privada: sin sesión se redirige a login.html
if (exigirSesion()) {
  iniciar();
}
