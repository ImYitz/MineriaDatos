// Modo libre: subir un PDF, responder las preguntas generadas y ver el resultado.

const TAMANO_MAXIMO = 10 * 1024 * 1024;

let sesion = null;           // práctica abierta
const respuestas = {};       // pregunta_id -> texto elegido
const bloques = {};          // pregunta_id -> { botones, nota }
let terminado = false;

const elArchivo = document.getElementById("archivo");
const elCantidad = document.getElementById("cantidad");
const elBotonGenerar = document.getElementById("boton-generar");
const elEstado = document.getElementById("estado-subida");
const elErrorSubida = document.getElementById("error-subida");
const elBotonTerminar = document.getElementById("boton-terminar");
const elErrorPreguntas = document.getElementById("error-preguntas");

// ---------- Subida ----------

elArchivo.addEventListener("change", () => {
  elErrorSubida.textContent = "";
  const f = elArchivo.files[0];
  if (f && f.size > TAMANO_MAXIMO) {
    elErrorSubida.textContent = "El PDF pesa más de 10 MB.";
    elBotonGenerar.disabled = true;
    return;
  }
  elBotonGenerar.disabled = !f;
});

elBotonGenerar.addEventListener("click", async () => {
  const f = elArchivo.files[0];
  if (!f) return;
  elErrorSubida.textContent = "";
  elBotonGenerar.disabled = true;
  elBotonGenerar.textContent = "Generando preguntas…";
  elEstado.textContent = "Leyendo el PDF y creando las preguntas. Con IA puede tardar hasta un minuto.";

  const datos = new FormData();
  datos.append("archivo", f);
  datos.append("cantidad", elCantidad.value);
  try {
    const detalle = await pedirApi("/api/libre/generar", { method: "POST", body: datos });
    mostrarPractica(detalle);
  } catch (error) {
    elErrorSubida.textContent = error.message;
    elEstado.textContent = "";
    elBotonGenerar.disabled = false;
    elBotonGenerar.textContent = "Generar preguntas";
  }
});

// ---------- Historial ----------

function fechaCorta(iso) {
  return new Date(iso).toLocaleDateString("es-CO", { year: "numeric", month: "short", day: "numeric" });
}

async function cargarHistorial() {
  const contenedor = document.getElementById("lista-historial");
  try {
    const lista = await pedirApi("/api/libre");
    contenedor.textContent = "";
    if (lista.length === 0) {
      contenedor.appendChild(Object.assign(document.createElement("p"), {
        className: "texto-suave", textContent: "Todavía no has practicado con ningún PDF.",
      }));
      return;
    }
    for (const s of lista) {
      const fila = document.createElement("div");
      fila.className = "fila-historial" + (s.completada ? " hecha" : "");
      const texto = document.createElement("div");
      const titulo = document.createElement("span");
      titulo.className = "titulo-hist";
      titulo.textContent = s.titulo;
      const detalle = document.createElement("small");
      detalle.textContent = fechaCorta(s.fecha_creada) + " · " + (s.metodo === "ia" ? "con IA" : "generador local");
      texto.appendChild(titulo);
      texto.appendChild(detalle);
      fila.appendChild(texto);
      if (s.completada) {
        const marca = document.createElement("span");
        marca.className = "etiqueta-hecha";
        marca.textContent = "✓ " + s.puntaje + "%";
        fila.appendChild(marca);
      } else {
        const boton = document.createElement("button");
        boton.type = "button";
        boton.textContent = "Continuar";
        boton.addEventListener("click", async () => {
          try {
            mostrarPractica(await pedirApi("/api/libre/" + s.id));
          } catch (error) {
            elErrorSubida.textContent = error.message;
          }
        });
        fila.appendChild(boton);
      }
      contenedor.appendChild(fila);
    }
  } catch (error) {
    contenedor.textContent = "No se pudo cargar el historial.";
  }
}

// ---------- Preguntas ----------

function mostrarPractica(detalle) {
  sesion = detalle;
  document.getElementById("zona-subida").classList.add("oculto");
  document.getElementById("zona-preguntas").classList.remove("oculto");
  document.getElementById("titulo-practica").textContent = "📄 " + detalle.titulo;
  document.getElementById("info-practica").textContent =
    detalle.preguntas.length + " preguntas · " +
    (detalle.metodo === "ia"
      ? "redactadas con IA a partir de tu documento."
      : "generadas automáticamente del texto (sin IA): son más sencillas y pueden tener algún fallo.");
  const aviso = document.getElementById("aviso-recompensa");
  if (detalle.aviso_recompensa) {
    aviso.textContent = detalle.aviso_recompensa;
    aviso.classList.remove("oculto");
  }

  const lista = document.getElementById("lista-preguntas");
  lista.textContent = "";
  detalle.preguntas.forEach((pregunta, indice) => {
    const bloque = document.createElement("div");
    bloque.className = "pregunta-lab";
    const enunciado = document.createElement("h3");
    enunciado.textContent = (indice + 1) + ". " + pregunta.enunciado;
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
        elBotonTerminar.disabled = Object.keys(respuestas).length < detalle.preguntas.length;
      });
      botones.push(boton);
      bloque.appendChild(boton);
    }
    const nota = document.createElement("p");
    nota.className = "nota-pregunta";
    bloque.appendChild(nota);
    bloques[pregunta.id] = { botones, nota };
    lista.appendChild(bloque);
  });
  window.scrollTo({ top: 0 });
}

async function terminar() {
  elErrorPreguntas.textContent = "";
  elBotonTerminar.disabled = true;
  elBotonTerminar.textContent = "Guardando...";
  try {
    const resultado = await pedirApi("/api/libre/" + sesion.id + "/completar", {
      method: "POST",
      body: JSON.stringify({
        respuestas: sesion.preguntas.map((p) => ({ pregunta_id: p.id, respuesta: respuestas[p.id] })),
      }),
    });
    terminado = true;
    mostrarResultado(resultado);
  } catch (error) {
    elErrorPreguntas.textContent = error.message || "No se pudo guardar tu progreso. Intenta de nuevo.";
    elBotonTerminar.disabled = false;
    elBotonTerminar.textContent = "Terminar práctica";
  }
}

function mostrarResultado(r) {
  for (const rev of r.revision) {
    const bloque = bloques[rev.pregunta_id];
    for (const boton of bloque.botones) {
      boton.disabled = true;
      if (boton.textContent === rev.respuesta_correcta) {
        boton.classList.add("correcta");
      } else if (boton.classList.contains("elegida")) {
        boton.classList.add("incorrecta");
      }
    }
    bloque.nota.textContent = (rev.correcta ? "✓ " : "✗ ") + rev.explicacion;
    bloque.nota.className = "nota-pregunta " + (rev.correcta ? "bien" : "mal");
  }

  elBotonTerminar.classList.add("oculto");
  document.getElementById("zona-final").classList.remove("oculto");
  document.getElementById("resumen-final").textContent =
    "Acertaste " + r.aciertos + " de " + r.total + " preguntas (" + r.puntaje + "%).";
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
  document.getElementById("zona-final").scrollIntoView({ behavior: "smooth", block: "start" });
}

elBotonTerminar.addEventListener("click", terminar);

if (exigirSesion()) {
  cargarHistorial();
}
