// Pantalla de un laboratorio: monta el gráfico interactivo y las preguntas de comprobación.

// El código del laboratorio viene en la dirección: laboratorio.html?id=kmeans
const codigoLab = new URLSearchParams(window.location.search).get("id");

let laboratorio = null;
const respuestas = {};      // pregunta_id -> texto de la opción elegida
const bloques = {};         // pregunta_id -> { botones, nota } para pintar la corrección
let terminado = false;

const elBoton = document.getElementById("boton-terminar");
const elError = document.getElementById("mensaje-error");

async function iniciar() {
  try {
    laboratorio = await pedirApi("/api/laboratorios/" + encodeURIComponent(codigoLab));
  } catch (error) {
    document.getElementById("titulo-lab").textContent = "No se pudo cargar el laboratorio";
    document.getElementById("zona-preguntas").classList.add("oculto");
    return;
  }

  document.title = laboratorio.titulo;
  document.getElementById("titulo-lab").textContent = laboratorio.icono + " " + laboratorio.titulo;
  document.getElementById("instrucciones-lab").textContent = laboratorio.instrucciones;

  // Cada laboratorio se registra en LABS (ver js/labs/)
  const modulo = LABS[laboratorio.codigo];
  const zona = document.getElementById("zona-lab");
  if (modulo) {
    modulo.montar(zona);
  } else {
    zona.textContent = "Este laboratorio todavía no tiene su parte interactiva.";
  }

  dibujarPreguntas();
}

function dibujarPreguntas() {
  const lista = document.getElementById("lista-preguntas");
  lista.innerHTML = "";

  for (const pregunta of laboratorio.preguntas) {
    const bloque = document.createElement("div");
    bloque.className = "pregunta-lab";

    const enunciado = document.createElement("h3");
    enunciado.textContent = pregunta.enunciado;
    bloque.appendChild(enunciado);

    const botones = [];
    for (const texto of pregunta.opciones) {
      const boton = document.createElement("button");
      boton.type = "button";
      boton.className = "opcion";
      boton.textContent = texto;
      boton.addEventListener("click", () => {
        if (terminado) return;
        respuestas[pregunta.id] = texto;
        for (const otro of botones) otro.classList.remove("elegida");
        boton.classList.add("elegida");
        elBoton.disabled = Object.keys(respuestas).length < laboratorio.preguntas.length;
      });
      botones.push(boton);
      bloque.appendChild(boton);
    }

    const nota = document.createElement("p");
    nota.className = "nota-pregunta";
    bloque.appendChild(nota);

    bloques[pregunta.id] = { botones, nota };
    lista.appendChild(bloque);
  }
}

async function terminar() {
  elError.textContent = "";
  elBoton.disabled = true;
  elBoton.textContent = "Guardando...";
  try {
    const resultado = await pedirApi(
      "/api/laboratorios/" + encodeURIComponent(laboratorio.codigo) + "/completar",
      {
        method: "POST",
        body: JSON.stringify({
          respuestas: laboratorio.preguntas.map((p) => ({
            pregunta_id: p.id,
            respuesta: respuestas[p.id],
          })),
        }),
      }
    );
    terminado = true;
    mostrarResultado(resultado);
  } catch (error) {
    elError.textContent = "No se pudo guardar tu progreso. Intenta de nuevo.";
    elBoton.disabled = false;
    elBoton.textContent = "Terminar laboratorio";
  }
}

function mostrarResultado(resultado) {
  // Corrección de cada pregunta
  for (const r of resultado.revision) {
    const bloque = bloques[r.pregunta_id];
    for (const boton of bloque.botones) {
      boton.disabled = true;
      if (boton.textContent === r.respuesta_correcta) {
        boton.classList.add("correcta");
      } else if (boton.classList.contains("elegida")) {
        boton.classList.add("incorrecta");
      }
    }
    bloque.nota.textContent = (r.correcta ? "✓ " : "✗ ") + r.explicacion;
    bloque.nota.className = "nota-pregunta " + (r.correcta ? "bien" : "mal");
  }

  elBoton.classList.add("oculto");
  document.getElementById("zona-final").classList.remove("oculto");

  document.getElementById("resumen-final").textContent =
    "Acertaste " + resultado.aciertos + " de " + resultado.total +
    " preguntas (" + resultado.puntaje + "%).";

  let textoXp = "+" + resultado.xp_ganada + " XP";
  if (!resultado.es_primera_vez) {
    textoXp += " (repetición: 30% de la XP)";
  }
  document.getElementById("resumen-xp").textContent = textoXp;

  if (resultado.subio_de_nivel) {
    document.getElementById("mensaje-nivel").textContent =
      "🎉 ¡Subiste al nivel " + resultado.nivel + "!";
  }

  document.getElementById("resumen-monedas").textContent =
    "+" + resultado.monedas_ganadas + " 🪙 monedas (tienes " + resultado.monedas_total + ")";
  document.getElementById("resumen-racha").textContent =
    "🔥 Racha: " + resultado.racha_actual + (resultado.racha_actual === 1 ? " día" : " días");

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

  document.getElementById("zona-final").scrollIntoView({ behavior: "smooth", block: "start" });
}

elBoton.addEventListener("click", terminar);

if (exigirSesion()) {
  iniciar();
}
