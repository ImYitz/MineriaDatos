// Pantalla de logros: muestra cuáles tienes y cuánto te falta para los demás.

async function cargarLogros() {
  const contenedor = document.getElementById("lista-logros");
  try {
    const logros = await pedirApi("/api/logros");

    const obtenidos = logros.filter((l) => l.obtenido).length;
    document.getElementById("resumen-logros").textContent =
      "Has desbloqueado " + obtenidos + " de " + logros.length + " logros.";

    contenedor.innerHTML = "";
    for (const logro of logros) {
      const tarjeta = document.createElement("div");
      tarjeta.className = "tarjeta-logro" + (logro.obtenido ? " obtenido" : " bloqueado");

      const icono = document.createElement("div");
      icono.className = "icono-logro";
      icono.textContent = iconoLogro(logro.icono);

      const texto = document.createElement("div");
      texto.className = "texto-logro";

      const nombre = document.createElement("strong");
      nombre.textContent = logro.nombre;
      const descripcion = document.createElement("p");
      descripcion.textContent = logro.descripcion;
      texto.appendChild(nombre);
      texto.appendChild(descripcion);

      const estado = document.createElement("small");
      if (logro.obtenido) {
        const fecha = new Date(logro.fecha_obtenido).toLocaleDateString("es-CO", {
          year: "numeric", month: "long", day: "numeric",
        });
        estado.textContent = "Obtenido el " + fecha + " · +" + logro.recompensa_monedas + " 🪙";
      } else {
        // Barra con el avance hacia el objetivo
        const barra = document.createElement("div");
        barra.className = "barra barra-logro";
        const relleno = document.createElement("div");
        relleno.className = "barra-relleno";
        relleno.style.width = (logro.progreso_actual / logro.valor_objetivo) * 100 + "%";
        barra.appendChild(relleno);
        texto.appendChild(barra);
        estado.textContent =
          logro.progreso_actual + " / " + logro.valor_objetivo +
          " · Recompensa: " + logro.recompensa_monedas + " 🪙";
      }
      texto.appendChild(estado);

      tarjeta.appendChild(icono);
      tarjeta.appendChild(texto);
      contenedor.appendChild(tarjeta);
    }
  } catch (error) {
    document.getElementById("mensaje-error").textContent = "No se pudieron cargar los logros.";
  }
}

if (exigirSesion()) {
  cargarLogros();
}
