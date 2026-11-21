// Repaso de errores: repasa las preguntas que se fallaron en las lecciones (repetición espaciada).
// El servidor decide qué toca, corrige cada respuesta y reprograma la siguiente revisión.

const elResumen = document.getElementById("zona-resumen");
const elJuego = document.getElementById("zona-juego");
const elFinal = document.getElementById("zona-final");
const elComenzar = document.getElementById("rp-comenzar");
const elError = document.getElementById("rp-error");
const elMensaje = document.getElementById("rp-mensaje");
const elEnunciado = document.getElementById("enunciado");
const elOpciones = document.getElementById("opciones");
const elRetro = document.getElementById("retroalimentacion");
const elBoton = document.getElementById("boton-principal");
const elBarra = document.getElementById("rp-barra");

let preguntas = [];
let indice = 0;
let opcionElegida = null;
let yaComprobado = false;
let aciertos = 0;
let dominadasNuevas = 0;

async function cargar() {
  try {
    const estado = await pedirApi("/api/repaso");
    document.getElementById("rp-pendientes").textContent = estado.pendientes;
    document.getElementById("rp-en-repaso").textContent = estado.en_repaso;
    document.getElementById("rp-dominados").textContent = estado.dominados;
    preguntas = estado.ejercicios;

    if (estado.pendientes === 0) {
      let texto;
      if (estado.en_repaso === 0) {
        texto = estado.dominados > 0
          ? "¡Todo dominado! No tienes preguntas por repasar."
          : "Todavía no tienes preguntas en repaso. Las que falles en las lecciones aparecerán aquí.";
      } else {
        const cuando = new Date(estado.proxima_revision).toLocaleDateString("es-CO", {
          weekday: "long", day: "numeric", month: "long",
        });
        texto = "Por hoy no queda nada. La próxima revisión toca el " + cuando + ".";
      }
      elMensaje.textContent = texto;
      elMensaje.classList.remove("oculto");
    } else {
      elComenzar.textContent = "Empezar el repaso (" + preguntas.length + " preguntas)";
      elComenzar.disabled = false;
    }
  } catch (error) {
    elError.textContent = "No se pudo cargar el repaso. ¿Reiniciaste el servidor?";
  }
}

elComenzar.addEventListener("click", () => {
  elResumen.classList.add("oculto");
  elJuego.classList.remove("oculto");
  indice = 0;
  aciertos = 0;
  dominadasNuevas = 0;
  mostrarPregunta();
});

function mostrarPregunta() {
  const pregunta = preguntas[indice];
  opcionElegida = null;
  yaComprobado = false;
  elEnunciado.textContent = pregunta.enunciado;
  elRetro.textContent = "";
  elRetro.className = "retroalimentacion";
  elBoton.textContent = "Comprobar";
  elBoton.disabled = true;
  elBarra.style.width = (indice / preguntas.length) * 100 + "%";

  elOpciones.textContent = "";
  for (const texto of pregunta.opciones) {
    const boton = document.createElement("button");
    boton.type = "button";
    boton.className = "opcion";
    boton.textContent = texto;
    boton.addEventListener("click", () => {
      if (yaComprobado) return;
      opcionElegida = texto;
      for (const otro of elOpciones.children) otro.classList.remove("elegida");
      boton.classList.add("elegida");
      elBoton.disabled = false;
    });
    elOpciones.appendChild(boton);
  }
}

async function comprobar() {
  const pregunta = preguntas[indice];
  elBoton.disabled = true;
  try {
    const r = await pedirApi("/api/repaso/responder", {
      method: "POST",
      body: JSON.stringify({ ejercicio_id: pregunta.id, respuesta: opcionElegida }),
    });
    yaComprobado = true;

    let texto;
    if (r.correcto) {
      aciertos++;
      texto = "¡Correcto!";
      if (r.dominado) {
        dominadasNuevas++;
        texto += " ¡Pregunta dominada!";
      } else if (r.proxima_en_dias) {
        texto += " La volverás a ver en " + r.proxima_en_dias + (r.proxima_en_dias === 1 ? " día." : " días.");
      }
      elRetro.className = "retroalimentacion bien";
    } else {
      texto = "Incorrecto. La respuesta era: " + r.respuesta_correcta;
      elRetro.className = "retroalimentacion mal";
    }
    if (r.explicacion) texto += " — " + r.explicacion;
    elRetro.textContent = texto;

    for (const b of elOpciones.children) {
      if (b.textContent === r.respuesta_correcta) {
        b.classList.add("correcta");
      } else if (b.classList.contains("elegida")) {
        b.classList.add("incorrecta");
      }
    }
    elBoton.textContent = indice === preguntas.length - 1 ? "Terminar" : "Continuar";
    elBoton.disabled = false;
  } catch (error) {
    elRetro.textContent = error.message || "Error al comprobar la respuesta. Intenta de nuevo.";
    elRetro.className = "retroalimentacion mal";
    elBoton.disabled = false;
  }
}

elBoton.addEventListener("click", () => {
  if (!yaComprobado) {
    comprobar();
    return;
  }
  indice++;
  if (indice >= preguntas.length) {
    terminar();
  } else {
    mostrarPregunta();
  }
});

function terminar() {
  elJuego.classList.add("oculto");
  elFinal.classList.remove("oculto");
  document.getElementById("rp-resultado").textContent =
    "Acertaste " + aciertos + " de " + preguntas.length + " preguntas. Las que fallaste volverán a aparecer.";
  document.getElementById("rp-dominadas-nuevas").textContent =
    dominadasNuevas > 0 ? "🏅 Preguntas dominadas en esta sesión: " + dominadasNuevas : "";
}

if (exigirSesion()) {
  cargar();
}
