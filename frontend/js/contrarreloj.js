// Modo contrarreloj: 60 segundos para responder las preguntas del curso que se pueda.
// El servidor controla el tiempo y corrige cada respuesta; aquí solo se dibuja y se lleva el cronómetro.

const elInicio = document.getElementById("zona-inicio");
const elJuego = document.getElementById("zona-juego");
const elFinal = document.getElementById("zona-final");
const elComenzar = document.getElementById("boton-comenzar");
const elErrorInicio = document.getElementById("error-cr");
const elErrorJuego = document.getElementById("error-juego");
const elEnunciado = document.getElementById("enunciado");
const elOpciones = document.getElementById("opciones");
const elRetro = document.getElementById("retroalimentacion");
const elTiempo = document.getElementById("cr-tiempo");
const elBarra = document.getElementById("cr-barra");
const elAciertos = document.getElementById("cr-aciertos");
const elProgreso = document.getElementById("cr-progreso");

let partida = null;
let indice = 0;
let aciertos = 0;
let bloqueado = false;
let terminado = false;
let inicioLocal = 0;
let temporizador = null;

const pausa = (ms) => new Promise((resolver) => setTimeout(resolver, ms));

// ---------- Pantalla de inicio ----------

function fechaCorta(iso) {
  return new Date(iso).toLocaleDateString("es-CO", { day: "numeric", month: "short" }) +
    ", " + new Date(iso).toLocaleTimeString("es-CO", { hour: "2-digit", minute: "2-digit" });
}

async function cargarEstado() {
  try {
    const estado = await pedirApi("/api/contrarreloj");
    document.getElementById("descripcion-cr").textContent =
      "Responde todas las preguntas del curso que puedas en " + estado.duracion + " segundos. " +
      "Cada partida tiene " + estado.preguntas_por_partida + " preguntas: si las respondes todas antes de que " +
      "se acabe el tiempo, desbloqueas un logro.";
    document.getElementById("cr-record").textContent = estado.mejor_aciertos;
    document.getElementById("cr-hoy").textContent = estado.recompensas_hoy + " / " + estado.limite_recompensas;

    const aviso = document.getElementById("aviso-cr");
    if (estado.aviso_recompensa) {
      aviso.textContent = estado.aviso_recompensa;
      aviso.classList.remove("oculto");
    }

    const lista = document.getElementById("lista-historial");
    lista.textContent = "";
    if (estado.recientes.length === 0) {
      const vacio = document.createElement("p");
      vacio.className = "texto-suave";
      vacio.textContent = "Todavía no has jugado ninguna partida.";
      lista.appendChild(vacio);
    }
    for (const p of estado.recientes) {
      const fila = document.createElement("div");
      fila.className = "cr-fila" + (p.termino_todas ? " completa" : "");
      const texto = document.createElement("div");
      const titulo = document.createElement("strong");
      titulo.textContent = p.aciertos + " aciertos de " + p.respondidas + " respondidas";
      const detalle = document.createElement("small");
      detalle.textContent = fechaCorta(p.fecha);
      texto.appendChild(titulo);
      texto.appendChild(detalle);
      fila.appendChild(texto);
      if (p.termino_todas) {
        const marca = document.createElement("span");
        marca.textContent = "🏁 Las respondió todas";
        fila.appendChild(marca);
      }
      lista.appendChild(fila);
    }
    elComenzar.disabled = false;
  } catch (error) {
    elErrorInicio.textContent = "No se pudo cargar el modo contrarreloj. ¿Reiniciaste el servidor?";
  }
}

elComenzar.addEventListener("click", async () => {
  elErrorInicio.textContent = "";
  elComenzar.disabled = true;
  try {
    partida = await pedirApi("/api/contrarreloj/iniciar", { method: "POST" });
  } catch (error) {
    elErrorInicio.textContent = error.message;
    elComenzar.disabled = false;
    return;
  }
  empezar();
});

// ---------- Partida ----------

function empezar() {
  indice = 0;
  aciertos = 0;
  bloqueado = false;
  terminado = false;
  elInicio.classList.add("oculto");
  elJuego.classList.remove("oculto");
  elAciertos.textContent = "✓ 0";
  mostrarPregunta();
  inicioLocal = performance.now();
  temporizador = setInterval(tick, 100);
  tick();
}

function tick() {
  const restante = partida.duracion - (performance.now() - inicioLocal) / 1000;
  if (restante <= 0) {
    elTiempo.textContent = "0";
    elBarra.style.width = "0%";
    terminar();
    return;
  }
  elTiempo.textContent = String(Math.ceil(restante));
  elBarra.style.width = (restante / partida.duracion) * 100 + "%";
  const clase = restante <= 10 ? "urgente" : restante <= 20 ? "poco" : "";
  elTiempo.parentElement.className = "cr-tiempo " + clase;
  elBarra.className = "barra-relleno cr-barra " + clase;
}

function mostrarPregunta() {
  const pregunta = partida.preguntas[indice];
  elEnunciado.textContent = pregunta.enunciado;
  elRetro.textContent = "";
  elRetro.className = "retroalimentacion";
  elProgreso.textContent = "Pregunta " + (indice + 1) + " de " + partida.preguntas.length;
  elOpciones.textContent = "";
  for (const texto of pregunta.opciones) {
    const boton = document.createElement("button");
    boton.type = "button";
    boton.className = "opcion";
    boton.textContent = texto;
    boton.addEventListener("click", () => elegir(texto, boton));
    elOpciones.appendChild(boton);
  }
}

async function elegir(texto, boton) {
  if (bloqueado || terminado) return;
  bloqueado = true;
  boton.classList.add("elegida");
  const pregunta = partida.preguntas[indice];
  try {
    const r = await pedirApi("/api/contrarreloj/" + partida.id + "/responder", {
      method: "POST",
      body: JSON.stringify({ pregunta_id: pregunta.id, respuesta: texto }),
    });
    if (terminado) return;

    if (r.correcto) {
      aciertos++;
      elAciertos.textContent = "✓ " + aciertos;
      elRetro.textContent = "¡Correcto!";
      elRetro.className = "retroalimentacion bien";
    } else {
      elRetro.textContent = "Incorrecto. La respuesta era: " + r.respuesta_correcta;
      elRetro.className = "retroalimentacion mal";
    }
    for (const b of elOpciones.children) {
      if (b.textContent === r.respuesta_correcta) {
        b.classList.add("correcta");
      } else if (b.classList.contains("elegida")) {
        b.classList.add("incorrecta");
      }
    }

    // Una pausa corta para ver el resultado (más larga si falló, para que se lea la correcta)
    await pausa(r.correcto ? 300 : 1100);
    if (terminado) return;
    indice++;
    if (indice >= partida.preguntas.length) {
      terminar();           // respondió todas dentro del tiempo
    } else {
      bloqueado = false;
      mostrarPregunta();
    }
  } catch (error) {
    // Normalmente "Se acabó el tiempo": el servidor ya no acepta más respuestas
    terminar();
  }
}

async function terminar() {
  if (terminado) return;
  terminado = true;
  clearInterval(temporizador);
  elErrorJuego.textContent = "";
  try {
    const resultado = await pedirApi("/api/contrarreloj/" + partida.id + "/terminar", { method: "POST" });
    mostrarResultado(resultado);
  } catch (error) {
    elErrorJuego.textContent =
      "No se pudo guardar la partida: " + (error && error.message ? error.message : "error desconocido") +
      ". Recarga la página para volver a empezar.";
  }
}

// ---------- Resultado ----------

function mostrarResultado(r) {
  elJuego.classList.add("oculto");
  elFinal.classList.remove("oculto");

  document.getElementById("titulo-final").textContent =
    r.termino_todas ? "🏁 ¡Las respondiste todas!" : "⏱️ ¡Se acabó el tiempo!";
  document.getElementById("resumen-final").textContent =
    "Acertaste " + r.aciertos + " de " + r.respondidas + " respondidas (" + r.puntaje + " % de precisión).";
  document.getElementById("cr-puntos").textContent = r.puntos + " puntos";

  const mensaje = document.getElementById("cr-mensaje");
  if (r.es_record && r.aciertos > 0) {
    mensaje.textContent = "🎉 ¡Nuevo récord! Tu marca anterior era " + r.mejor_anterior + ".";
  } else {
    mensaje.textContent = "Tu récord es " + Math.max(r.mejor_anterior, r.aciertos) + " aciertos.";
  }

  document.getElementById("resumen-xp").textContent = "+" + r.xp_ganada + " XP";
  if (r.subio_de_nivel) {
    document.getElementById("mensaje-nivel").textContent = "🎉 ¡Subiste al nivel " + r.nivel + "!";
  }
  document.getElementById("resumen-monedas").textContent =
    "+" + r.monedas_ganadas + " 🪙 monedas (tienes " + r.monedas_total + ")";
  document.getElementById("resumen-racha").textContent =
    "🔥 Racha: " + r.racha_actual + (r.racha_actual === 1 ? " día" : " días");
  if (r.motivo_sin_recompensa) {
    const aviso = document.getElementById("motivo-sin-recompensa");
    aviso.textContent = r.motivo_sin_recompensa;
    aviso.classList.remove("oculto");
  }

  const contenedor = document.getElementById("logros-nuevos");
  contenedor.textContent = "";
  for (const logro of r.logros_nuevos) {
    const tarjeta = document.createElement("div");
    tarjeta.className = "logro-nuevo";
    tarjeta.textContent =
      iconoLogro(logro.icono) + " ¡Logro desbloqueado: " + logro.nombre +
      "! (+" + logro.recompensa_monedas + " 🪙)";
    contenedor.appendChild(tarjeta);
  }
  elFinal.scrollIntoView({ behavior: "smooth", block: "start" });
}

if (exigirSesion()) {
  cargarEstado();
}
