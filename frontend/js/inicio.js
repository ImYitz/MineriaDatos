// Página de inicio: muestra el nivel/XP del usuario y las lecciones del curso.

async function cargarPerfil() {
  const perfil = await pedirApi("/api/usuario/actual");
  document.getElementById("nombre-usuario").textContent = perfil.nombre_usuario;
  document.getElementById("nivel").textContent = perfil.nivel;
  document.getElementById("texto-xp").textContent =
    perfil.xp_en_nivel + " / " + perfil.xp_por_nivel + " XP para el siguiente nivel  ·  " +
    perfil.xp_total + " XP en total";
  const porcentaje = (perfil.xp_en_nivel / perfil.xp_por_nivel) * 100;
  document.getElementById("barra-xp").style.width = porcentaje + "%";

  document.getElementById("ficha-racha").textContent =
    "🔥 Racha: " + perfil.racha_actual + (perfil.racha_actual === 1 ? " día" : " días");
  document.getElementById("ficha-monedas").textContent =
    "🪙 " + perfil.monedas + (perfil.monedas === 1 ? " moneda" : " monedas");
}

async function cargarAvatar() {
  const config = await pedirApi("/api/avatar");
  dibujarAvatar(document.getElementById("avatar-mini"), config);
}

async function cargarCurso() {
  const contenedor = document.getElementById("lista-lecciones");
  try {
    const cursos = await pedirApi("/api/cursos");
    const curso = await pedirApi("/api/cursos/" + cursos[0].id);
    const progreso = await pedirApi("/api/progreso");

    // Convertimos la lista de progreso en un "diccionario" para buscar por id de lección
    const progresoPorLeccion = {};
    for (const p of progreso) {
      progresoPorLeccion[p.leccion_id] = p;
    }

    // textContent escribe texto plano (más seguro que innerHTML)
    document.getElementById("titulo-curso").textContent = curso.titulo;
    document.getElementById("descripcion-curso").textContent = curso.descripcion;

    contenedor.innerHTML = "";
    for (const leccion of curso.lecciones) {
      const tarjeta = document.createElement("a");
      tarjeta.className = "tarjeta-leccion";
      tarjeta.href = "leccion.html?id=" + leccion.id;

      const titulo = document.createElement("h3");
      titulo.textContent = leccion.orden + ". " + leccion.titulo;
      const descripcion = document.createElement("p");
      descripcion.textContent = leccion.descripcion;

      tarjeta.appendChild(titulo);
      tarjeta.appendChild(descripcion);

      // Si ya la completó, la marcamos y mostramos su mejor puntaje
      const avance = progresoPorLeccion[leccion.id];
      if (avance) {
        tarjeta.classList.add("completada");
        const estado = document.createElement("p");
        estado.className = "estado";
        estado.textContent =
          "✓ Completada · mejor puntaje " + avance.mejor_puntaje + "% · " +
          avance.veces_completada + (avance.veces_completada === 1 ? " vez" : " veces");
        tarjeta.appendChild(estado);
      }
      contenedor.appendChild(tarjeta);
    }
  } catch (error) {
    contenedor.textContent =
      "No se pudo cargar el curso. ¿Está corriendo el servidor y sembraste los datos?";
  }
}

document.getElementById("boton-salir").addEventListener("click", cerrarSesion);

// Esta página es privada: sin sesión se redirige a login.html
if (exigirSesion()) {
  // El perfil y el curso se cargan por separado: si uno falla, el otro igual se muestra
  cargarPerfil().catch(() => {
    document.getElementById("texto-xp").textContent = "No se pudo cargar tu progreso.";
  });
  cargarAvatar().catch(() => { /* si falla, simplemente no se muestra el avatar */ });
  cargarCurso();
}
