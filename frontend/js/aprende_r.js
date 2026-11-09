// Pantalla con la lista de lecciones de R y el avance de cada una.

async function cargarLeccionesR() {
  const contenedor = document.getElementById("lista-lecciones-r");
  try {
    const lecciones = await pedirApi("/api/r");
    contenedor.innerHTML = "";

    lecciones.forEach((leccion, indice) => {
      const tarjeta = document.createElement("a");
      tarjeta.className = "tarjeta-leccion tarjeta-r";
      tarjeta.href = "leccion_r.html?id=" + encodeURIComponent(leccion.codigo);

      const icono = document.createElement("div");
      icono.className = "icono-r";
      icono.textContent = leccion.icono;

      const cuerpo = document.createElement("div");
      cuerpo.className = "cuerpo-r";
      const titulo = document.createElement("h3");
      titulo.textContent = (indice + 1) + ". " + leccion.titulo;
      const descripcion = document.createElement("p");
      descripcion.textContent = leccion.descripcion;
      cuerpo.appendChild(titulo);
      cuerpo.appendChild(descripcion);

      const estado = document.createElement("p");
      estado.className = "estado";
      if (leccion.veces_completada > 0) {
        tarjeta.classList.add("completada");
        estado.textContent =
          "✓ Aprobada · mejor puntaje " + leccion.mejor_puntaje + "% · " +
          leccion.veces_completada + (leccion.veces_completada === 1 ? " vez" : " veces");
      } else {
        estado.textContent = "Teoría + práctica · +" + leccion.xp_recompensa + " XP la primera vez";
      }
      cuerpo.appendChild(estado);

      tarjeta.appendChild(icono);
      tarjeta.appendChild(cuerpo);
      contenedor.appendChild(tarjeta);
    });
  } catch (error) {
    document.getElementById("mensaje-error").textContent =
      "No se pudieron cargar las lecciones de R. ¿Reiniciaste el servidor?";
  }
}

if (exigirSesion()) {
  cargarLeccionesR();
}
