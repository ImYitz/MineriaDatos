// Pantalla de perfil del usuario.

async function cargarPerfil() {
  try {
    const perfil = await pedirApi("/api/usuario/actual");
    const progreso = await pedirApi("/api/progreso");

    document.getElementById("nombre-usuario").textContent = perfil.nombre_usuario;
    document.getElementById("nivel").textContent = perfil.nivel;
    document.getElementById("texto-xp").textContent =
      perfil.xp_en_nivel + " / " + perfil.xp_por_nivel + " XP para el siguiente nivel";
    document.getElementById("barra-xp").style.width =
      (perfil.xp_en_nivel / perfil.xp_por_nivel) * 100 + "%";

    document.getElementById("dato-correo").textContent = perfil.correo || "-";
    document.getElementById("dato-fecha").textContent =
      new Date(perfil.fecha_registro).toLocaleDateString("es-CO", {
        year: "numeric", month: "long", day: "numeric",
      });
    document.getElementById("dato-lecciones").textContent = progreso.length;
    document.getElementById("dato-xp").textContent = perfil.xp_total;
    document.getElementById("dato-monedas").textContent = perfil.monedas;
    document.getElementById("dato-racha").textContent = perfil.racha_actual + " días";
    document.getElementById("dato-racha-maxima").textContent = perfil.racha_maxima + " días";

    const avatar = await pedirApi("/api/avatar");
    dibujarAvatar(document.getElementById("avatar-mini"), avatar);

    const logros = await pedirApi("/api/logros");
    const obtenidos = logros.filter((l) => l.obtenido).length;
    document.getElementById("dato-logros").textContent = obtenidos + " de " + logros.length;
  } catch (error) {
    document.getElementById("mensaje-error").textContent = "No se pudo cargar tu perfil.";
  }
}

document.getElementById("boton-salir").addEventListener("click", cerrarSesion);

if (exigirSesion()) {
  cargarPerfil();
}
