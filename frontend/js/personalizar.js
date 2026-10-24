// Pantalla "Mi avatar": ver el avatar, probarse objetos, comprarlos y guardar.

let perfil = null;     // datos del usuario (monedas y nivel)
let items = [];        // todos los objetos de la tienda, con su estado para este usuario
let categoriaActual = "color";

// Lo que el usuario lleva puesto EN LA VISTA PREVIA (id de objeto, o null).
// No se guarda en el servidor hasta pulsar "Guardar avatar".
let seleccion = { color: null, ropa: null, accesorio: null };

const elVista = document.getElementById("avatar-vista");
const elLista = document.getElementById("lista-items");
const elMensaje = document.getElementById("mensaje");

function itemPorId(id) {
  return items.find((i) => i.id === id) || null;
}

// Convierte la selección (ids) en lo que necesita dibujarAvatar
function configActual() {
  const color = itemPorId(seleccion.color);
  const ropa = itemPorId(seleccion.ropa);
  const accesorio = itemPorId(seleccion.accesorio);
  return {
    color: color ? color.valor : COLOR_POR_DEFECTO,
    ropa: ropa ? ropa.valor : null,
    accesorio: accesorio ? accesorio.valor : null,
  };
}

function mostrarMensaje(texto, esError) {
  elMensaje.textContent = texto;
  elMensaje.className = esError ? "mensaje-error" : "mensaje-ok";
}

function redibujar() {
  dibujarAvatar(elVista, configActual());
  document.getElementById("saldo-monedas").textContent = perfil.monedas;
  document.getElementById("saldo-nivel").textContent = perfil.nivel;
  dibujarLista();
}

// Crea un botón según el estado del objeto
function crearBoton(item) {
  const boton = document.createElement("button");
  boton.className = "boton-item";
  const puesto = seleccion[item.categoria] === item.id;

  if (item.estado === "poseido") {
    if (puesto && item.categoria === "color") {
      boton.textContent = "En uso";
      boton.disabled = true;     // el robot siempre necesita un color
    } else if (puesto) {
      boton.textContent = "Quitar";
      boton.classList.add("quitar");
      boton.addEventListener("click", () => {
        seleccion[item.categoria] = null;
        mostrarMensaje("", false);
        redibujar();
      });
    } else {
      boton.textContent = "Usar";
      boton.addEventListener("click", () => {
        seleccion[item.categoria] = item.id;
        mostrarMensaje("", false);
        redibujar();
      });
    }
  } else if (item.estado === "bloqueado_nivel") {
    boton.textContent = "🔒 Nivel " + item.nivel_requerido;
    boton.disabled = true;
  } else if (item.estado === "sin_monedas") {
    boton.textContent = "🪙 " + item.precio_monedas;
    boton.disabled = true;
  } else {
    boton.textContent = "Comprar 🪙" + item.precio_monedas;
    boton.classList.add("comprar");
    boton.addEventListener("click", () => comprar(item));
  }
  return boton;
}

function dibujarLista() {
  elLista.innerHTML = "";
  const rejilla = document.createElement("div");
  rejilla.className = "rejilla-items";

  for (const item of items.filter((i) => i.categoria === categoriaActual)) {
    const tarjeta = document.createElement("div");
    tarjeta.className = "tarjeta-item";
    if (seleccion[item.categoria] === item.id) {
      tarjeta.classList.add("equipado");
    }

    // Miniatura: el avatar actual pero con ESTE objeto puesto
    const miniatura = document.createElement("div");
    miniatura.className = "avatar-item";
    const config = configActual();
    config[item.categoria] = item.valor;
    dibujarAvatar(miniatura, config);

    const nombre = document.createElement("strong");
    nombre.textContent = item.nombre;

    const detalle = document.createElement("small");
    if (item.estado === "poseido") {
      detalle.textContent = "Es tuyo";
    } else if (item.precio_monedas === 0) {
      detalle.textContent = "Gratis desde el nivel " + item.nivel_requerido;
    } else if (item.nivel_requerido > 1) {
      detalle.textContent = "Desde el nivel " + item.nivel_requerido;
    }

    tarjeta.appendChild(miniatura);
    tarjeta.appendChild(nombre);
    tarjeta.appendChild(detalle);
    tarjeta.appendChild(crearBoton(item));
    rejilla.appendChild(tarjeta);
  }
  elLista.appendChild(rejilla);
}

async function comprar(item) {
  try {
    const resultado = await pedirApi("/api/tienda/comprar/" + item.id, { method: "POST" });
    // Recargamos la tienda y las monedas, y nos probamos lo que acabamos de comprar
    items = await pedirApi("/api/tienda");
    perfil = await pedirApi("/api/usuario/actual");
    seleccion[item.categoria] = item.id;
    redibujar();
    mostrarMensaje(
      "¡Compraste " + resultado.nombre + "! Pulsa \"Guardar avatar\" para conservarlo.",
      false
    );
  } catch (error) {
    mostrarMensaje(error.message, true);
  }
}

async function guardar() {
  try {
    await pedirApi("/api/avatar", {
      method: "PUT",
      body: JSON.stringify({
        color_item_id: seleccion.color,
        ropa_item_id: seleccion.ropa,
        accesorio_item_id: seleccion.accesorio,
      }),
    });
    mostrarMensaje("✓ Avatar guardado", false);
  } catch (error) {
    mostrarMensaje(error.message, true);
  }
}

async function iniciar() {
  try {
    perfil = await pedirApi("/api/usuario/actual");
    items = await pedirApi("/api/tienda");
    const guardado = await pedirApi("/api/avatar");

    seleccion.color = guardado.color_item_id;
    seleccion.ropa = guardado.ropa_item_id;
    seleccion.accesorio = guardado.accesorio_item_id;
    if (seleccion.color === null) {
      // Sin color elegido: se usa el verde, que es el gratuito
      const verde = items.find((i) => i.codigo === "color_verde");
      seleccion.color = verde ? verde.id : null;
    }
    redibujar();
  } catch (error) {
    mostrarMensaje("No se pudo cargar la tienda.", true);
  }
}

// Pestañas: Colores / Ropa / Accesorios
for (const pestana of document.querySelectorAll(".pestana")) {
  pestana.addEventListener("click", () => {
    categoriaActual = pestana.dataset.categoria;
    for (const otra of document.querySelectorAll(".pestana")) {
      otra.classList.toggle("activa", otra === pestana);
    }
    dibujarLista();
  });
}

document.getElementById("boton-guardar").addEventListener("click", guardar);

if (exigirSesion()) {
  iniciar();
}
