// Página de inicio: muestra el nivel/XP del usuario y las lecciones del curso, agrupadas por unidad.

// Unidades del curso. Cada una empieza en la lección cuyo "orden" es "desde" y llega hasta
// la anterior a la siguiente unidad. Debe coincidir con backend/app/catalogo_lecciones.py.
const UNIDADES = [
  { desde: 1, titulo: "Unidad 1: Conceptos sobre minería de datos" },
  { desde: 9, titulo: "Unidad 2: Modelos y técnicas de la minería de datos" },
];

// Devuelve la unidad a la que pertenece una lección según su orden
function unidadDe(orden) {
  let actual = null;
  for (const unidad of UNIDADES) {
    if (orden >= unidad.desde) actual = unidad;
  }
  return actual;
}

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

    // Cuántas lecciones tiene cada unidad y cuántas lleva completadas el usuario
    const conteo = new Map();
    for (const leccion of curso.lecciones) {
      const unidad = unidadDe(leccion.orden);
      if (!unidad) continue;
      if (!conteo.has(unidad)) conteo.set(unidad, { total: 0, hechas: 0 });
      const c = conteo.get(unidad);
      c.total++;
      if (progresoPorLeccion[leccion.id]) c.hechas++;
    }

    // textContent escribe texto plano (más seguro que innerHTML)
    document.getElementById("titulo-curso").textContent = curso.titulo;
    document.getElementById("descripcion-curso").textContent = curso.descripcion;

    contenedor.innerHTML = "";
    let unidadAnterior = null;
    for (const leccion of curso.lecciones) {
      // Al empezar una unidad nueva se dibuja su banner
      const unidad = unidadDe(leccion.orden);
      if (unidad && unidad !== unidadAnterior) {
        const banner = document.createElement("div");
        banner.className = "banner-unidad" + (UNIDADES.indexOf(unidad) % 2 === 1 ? " alterna" : "");
        const nombre = document.createElement("strong");
        nombre.textContent = unidad.titulo;
        const avance = document.createElement("small");
        const c = conteo.get(unidad);
        avance.textContent = c.hechas + " de " + c.total + " completadas";
        banner.appendChild(nombre);
        banner.appendChild(avance);
        contenedor.appendChild(banner);
        unidadAnterior = unidad;
      }

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
