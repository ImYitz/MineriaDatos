// Tarjeta "Recomendado para ti" de la pantalla de inicio.
// El servidor clasifica al usuario (riesgo de abandono con regresión logística y perfil con K-means)
// y decide qué recomendar; aquí solo se dibuja (GET /api/estudio/inicio).

const NOMBRES_RIESGO = { bajo: "Riesgo bajo", medio: "Riesgo medio", alto: "Riesgo alto" };

function escribirPerfil(contenedor, datos) {
  contenedor.textContent = "";
  if (datos.grupo) {
    contenedor.appendChild(document.createTextNode("Tu perfil de estudio: "));
    const nombre = document.createElement("strong");
    nombre.textContent = datos.grupo;
    contenedor.appendChild(nombre);
    if (datos.grupo_descripcion) {
      const detalle = document.createElement("small");
      detalle.textContent = " · " + datos.grupo_descripcion;
      contenedor.appendChild(detalle);
    }
  } else {
    contenedor.textContent = "Completa tu primera actividad para que podamos conocer tu perfil de estudio.";
  }
}

async function cargarRecomendacion() {
  const tarjeta = document.getElementById("tarjeta-reco");
  try {
    const datos = await pedirApi("/api/estudio/inicio");

    tarjeta.className = "tarjeta-reco riesgo-" + datos.riesgo_nivel;
    const chip = document.getElementById("reco-chip-riesgo");
    chip.className = "chip-riesgo riesgo-" + datos.riesgo_nivel;
    chip.textContent = datos.riesgo_nivel === "nuevo"
      ? "Estudiante nuevo"
      : (NOMBRES_RIESGO[datos.riesgo_nivel] || datos.riesgo_nivel) + " de abandono · " +
        datos.riesgo_porcentaje + " %" + (datos.datos_suficientes ? "" : " (preliminar)");

    escribirPerfil(document.getElementById("reco-perfil"), datos);
    document.getElementById("reco-consejo").textContent = datos.consejo;

    const reco = datos.recomendacion;
    document.getElementById("reco-titulo").textContent = reco.titulo;
    document.getElementById("reco-texto").textContent = reco.texto;
    const boton = document.getElementById("reco-boton");
    boton.href = reco.enlace;
    boton.textContent = reco.boton;

    const relacionada = document.getElementById("reco-relacionada");
    relacionada.textContent = "";
    if (reco.relacionada) {
      relacionada.appendChild(document.createTextNode("Para practicar este tema: "));
      const enlace = document.createElement("a");
      enlace.href = reco.relacionada.enlace;
      enlace.textContent = reco.relacionada.titulo;
      relacionada.appendChild(enlace);
      relacionada.classList.remove("oculto");
    } else {
      relacionada.classList.add("oculto");
    }

    const extra = document.getElementById("reco-extra");
    if (datos.extra) {
      document.getElementById("reco-extra-titulo").textContent = datos.extra.titulo;
      document.getElementById("reco-extra-texto").textContent = datos.extra.texto + " ";
      const enlaceExtra = document.getElementById("reco-extra-enlace");
      enlaceExtra.href = datos.extra.enlace;
      enlaceExtra.textContent = datos.extra.boton + " →";
      extra.classList.remove("oculto");
    } else {
      extra.classList.add("oculto");
    }

    tarjeta.classList.remove("oculto");
  } catch (error) {
    // Si falla, la pantalla de inicio sigue funcionando normalmente, solo sin la tarjeta
    tarjeta.classList.add("oculto");
  }
}

// inicio.js ya redirige al login si no hay sesión; aquí solo se carga si la hay
if (obtenerToken()) {
  cargarRecomendacion();
}
