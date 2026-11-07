// Pantalla con la lista de laboratorios y el avance de cada uno.

async function cargarLaboratorios() {
  const contenedor = document.getElementById("lista-laboratorios");
  try {
    const laboratorios = await pedirApi("/api/laboratorios");
    contenedor.innerHTML = "";

    for (const lab of laboratorios) {
      const tarjeta = document.createElement("a");
      tarjeta.className = "tarjeta-leccion tarjeta-lab";
      tarjeta.href = "laboratorio.html?id=" + encodeURIComponent(lab.codigo);

      const icono = document.createElement("div");
      icono.className = "icono-lab";
      icono.textContent = lab.icono;

      const cuerpo = document.createElement("div");
      cuerpo.className = "cuerpo-lab";
      const titulo = document.createElement("h3");
      titulo.textContent = lab.titulo;
      const descripcion = document.createElement("p");
      descripcion.textContent = lab.descripcion;
      cuerpo.appendChild(titulo);
      cuerpo.appendChild(descripcion);

      const estado = document.createElement("p");
      estado.className = "estado";
      if (lab.veces_completado > 0) {
        tarjeta.classList.add("completada");
        estado.textContent =
          "✓ Completado · mejor puntaje " + lab.mejor_puntaje + "% · " +
          lab.veces_completado + (lab.veces_completado === 1 ? " vez" : " veces");
      } else {
        estado.textContent = "+" + lab.xp_recompensa + " XP la primera vez";
      }
      cuerpo.appendChild(estado);

      tarjeta.appendChild(icono);
      tarjeta.appendChild(cuerpo);
      contenedor.appendChild(tarjeta);
    }
  } catch (error) {
    document.getElementById("mensaje-error").textContent =
      "No se pudieron cargar los laboratorios. ¿Reiniciaste el servidor?";
  }
}

if (exigirSesion()) {
  cargarLaboratorios();
}
