// Notificaciones de logros, estilo Minecraft: aparecen arriba a la derecha y se van solas.
//
// No hace falta tocar las pantallas: cuando una lección, laboratorio, práctica de R, modo libre
// o contrarreloj termina, su script añade una tarjeta ".logro-nuevo" dentro de #logros-nuevos.
// Aquí se vigila ese contenedor y por cada tarjeta nueva se muestra una notificación.
// Para usarla desde otro sitio:  mostrarNotificacionLogro({ icono, nombre, descripcion, monedas })
(function () {
  if (window.__notificacionesLogros) return;
  window.__notificacionesLogros = true;

  const SEGUNDOS_VISIBLE = 5.5;
  const PAUSA_ENTRE_LOGROS_MS = 700;

  const estilos = document.createElement("link");
  estilos.rel = "stylesheet";
  estilos.href = "css/notificaciones.css?v=1";
  document.head.appendChild(estilos);

  let caja = null;
  let cola = Promise.resolve();
  let descripciones = null;     // { nombre del logro: descripción }, se pide una sola vez

  const pausa = (ms) => new Promise((resolver) => setTimeout(resolver, ms));

  function contenedor() {
    if (!caja) {
      caja = document.createElement("div");
      caja.className = "notificaciones-logros";
      caja.setAttribute("role", "status");
      caja.setAttribute("aria-live", "polite");
      document.body.appendChild(caja);
    }
    return caja;
  }

  async function buscarDescripcion(nombre) {
    if (descripciones === null) {
      descripciones = {};
      try {
        const logros = await pedirApi("/api/logros");
        for (const l of logros) descripciones[l.nombre] = l.descripcion;
      } catch (error) { /* sin descripción: la notificación sale igual */ }
    }
    return descripciones[nombre] || "";
  }

  function mostrar(datos) {
    const tarjeta = document.createElement("div");
    tarjeta.className = "toast-logro";

    const icono = document.createElement("div");
    icono.className = "toast-icono";
    icono.textContent = datos.icono || "🏅";

    const texto = document.createElement("div");
    texto.className = "toast-texto";
    const titulo = document.createElement("span");
    titulo.className = "toast-titulo";
    titulo.textContent = "¡Logro desbloqueado!";
    const nombre = document.createElement("strong");
    nombre.className = "toast-nombre";
    nombre.textContent = datos.nombre;
    texto.appendChild(titulo);
    texto.appendChild(nombre);
    if (datos.descripcion) {
      const detalle = document.createElement("span");
      detalle.className = "toast-detalle";
      detalle.textContent = datos.descripcion;
      texto.appendChild(detalle);
    }
    if (datos.monedas) {
      const monedas = document.createElement("span");
      monedas.className = "toast-monedas";
      monedas.textContent = "+" + datos.monedas + " 🪙";
      texto.appendChild(monedas);
    }

    tarjeta.appendChild(icono);
    tarjeta.appendChild(texto);
    contenedor().appendChild(tarjeta);

    function cerrar() {
      if (tarjeta.classList.contains("saliendo")) return;
      tarjeta.classList.add("saliendo");
      setTimeout(() => tarjeta.remove(), 450);
    }
    tarjeta.addEventListener("click", cerrar);
    setTimeout(cerrar, SEGUNDOS_VISIBLE * 1000);
  }

  function mostrarNotificacionLogro(datos) {
    cola = cola.then(async () => {
      if (!datos.descripcion) datos.descripcion = await buscarDescripcion(datos.nombre);
      mostrar(datos);
      await pausa(PAUSA_ENTRE_LOGROS_MS);
    });
  }
  window.mostrarNotificacionLogro = mostrarNotificacionLogro;

  // Texto de la tarjeta: "⭐ ¡Logro desbloqueado: Nombre! (+10 🪙)"
  function leerTarjeta(texto) {
    const m = texto.match(/^(\S+)\s+¡Logro desbloqueado:\s*(.+?)!\s*\(\+(\d+)/);
    if (!m) return { icono: "🏅", nombre: texto.replace(/^\S+\s+/, ""), monedas: 0 };
    return { icono: m[1], nombre: m[2], monedas: Number(m[3]) };
  }

  function vigilar() {
    const zona = document.getElementById("logros-nuevos");
    if (!zona) return;
    new MutationObserver((cambios) => {
      for (const cambio of cambios) {
        for (const nodo of cambio.addedNodes) {
          if (nodo.nodeType === 1 && nodo.classList.contains("logro-nuevo")) {
            mostrarNotificacionLogro(leerTarjeta(nodo.textContent));
          }
        }
      }
    }).observe(zona, { childList: true });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", vigilar);
  } else {
    vigilar();
  }
})();
