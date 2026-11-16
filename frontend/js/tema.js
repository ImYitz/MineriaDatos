// Botón "Tema de color": deja elegir la paleta de toda la aplicación.
// El tema se guarda en el navegador, por usuario (ver leerTema / guardarTema en api.js), y se
// aplica con <html data-tema="...">. Los colores de cada tema están en css/temas.css.
(function () {
  if (window.__temaIniciado) return;
  window.__temaIniciado = true;

  // muestra = fondo del círculo de color. Para un tema nuevo, añade aquí su fila y su bloque en temas.css
  const TEMAS = [
    { id: "clasico",   nombre: "Clásico",   muestra: "linear-gradient(135deg, #58cc02 50%, #1cb0f6 50%)" },
    { id: "oceano",    nombre: "Océano",    muestra: "linear-gradient(135deg, #1c9be6 50%, #dcefff 50%)" },
    { id: "violeta",   nombre: "Violeta",   muestra: "linear-gradient(135deg, #a560e8 50%, #efe0ff 50%)" },
    { id: "atardecer", nombre: "Atardecer", muestra: "linear-gradient(135deg, #ff8a1f 50%, #ffe8cc 50%)" },
    { id: "rosa",      nombre: "Rosa",      muestra: "linear-gradient(135deg, #ff5fa2 50%, #ffdcec 50%)" },
    { id: "menta",     nombre: "Menta",     muestra: "linear-gradient(135deg, #14b8a6 50%, #d3f5f0 50%)" },
    { id: "grafito",   nombre: "Grafito",   muestra: "linear-gradient(135deg, #5b6b8a 50%, #e1e6f0 50%)" },
  ];

  let boton = null;
  let panel = null;

  function temaActual() {
    return document.documentElement.getAttribute("data-tema") || "clasico";
  }

  function marcarActivo() {
    if (!panel) return;
    for (const b of panel.querySelectorAll(".opcion-tema")) {
      b.setAttribute("aria-pressed", String(b.dataset.tema === temaActual()));
    }
  }

  function elegir(id) {
    const raiz = document.documentElement;
    raiz.classList.add("cambiando-tema");
    guardarTema(id);
    marcarActivo();
    setTimeout(() => raiz.classList.remove("cambiando-tema"), 450);
  }

  function cerrar(devolverFoco) {
    if (!panel) return;
    panel.remove();
    panel = null;
    boton.setAttribute("aria-expanded", "false");
    if (devolverFoco) boton.focus();
  }

  function abrir() {
    panel = document.createElement("div");
    panel.className = "panel-tema";
    panel.setAttribute("role", "dialog");
    panel.setAttribute("aria-label", "Elegir tema de color");

    const titulo = document.createElement("strong");
    titulo.textContent = "🎨 Tema de color";
    panel.appendChild(titulo);

    const rejilla = document.createElement("div");
    rejilla.className = "rejilla-temas";
    for (const t of TEMAS) {
      const b = document.createElement("button");
      b.type = "button";
      b.className = "opcion-tema";
      b.dataset.tema = t.id;
      const muestra = document.createElement("span");
      muestra.className = "muestra";
      muestra.style.background = t.muestra;
      b.appendChild(muestra);
      b.appendChild(document.createTextNode(t.nombre));
      b.addEventListener("click", () => elegir(t.id));
      rejilla.appendChild(b);
    }
    panel.appendChild(rejilla);
    document.body.appendChild(panel);
    marcarActivo();

    // Posición: junto al botón (o como hoja inferior en pantallas pequeñas)
    if (window.innerWidth <= 760) {
      panel.classList.add("movil");
    } else {
      const caja = boton.getBoundingClientRect();
      const ancho = panel.offsetWidth, alto = panel.offsetHeight;
      let izquierda = boton.classList.contains("boton-tema-flotante") ? caja.right - ancho : caja.right + 10;
      let arriba = boton.classList.contains("boton-tema-flotante") ? caja.bottom + 8 : caja.top;
      izquierda = Math.max(8, Math.min(izquierda, window.innerWidth - ancho - 8));
      arriba = Math.max(8, Math.min(arriba, window.innerHeight - alto - 8));
      panel.style.left = izquierda + "px";
      panel.style.top = arriba + "px";
    }
    boton.setAttribute("aria-expanded", "true");
    const activo = panel.querySelector('.opcion-tema[aria-pressed="true"]');
    if (activo) activo.focus();
  }

  function alternar() {
    if (panel) cerrar(false); else abrir();
  }

  function iniciar() {
    const menu = document.querySelector(".menu-lateral");
    boton = document.createElement("button");
    boton.type = "button";
    boton.setAttribute("aria-haspopup", "dialog");
    boton.setAttribute("aria-expanded", "false");

    if (menu) {
      boton.className = "enlace-boton";
      const icono = document.createElement("span");
      icono.className = "icono-menu";
      icono.textContent = "🎨";
      boton.appendChild(icono);
      boton.appendChild(document.createTextNode("Tema de color"));
      menu.insertBefore(boton, menu.querySelector(".separador"));
    } else {
      // Páginas sin menú (login y registro): botón flotante
      boton.className = "boton-tema-flotante";
      boton.textContent = "🎨";
      boton.title = "Tema de color";
      boton.setAttribute("aria-label", "Tema de color");
      document.body.appendChild(boton);
    }
    boton.addEventListener("click", alternar);

    document.addEventListener("pointerdown", (e) => {
      if (panel && !panel.contains(e.target) && !boton.contains(e.target)) cerrar(false);
    });
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && panel) cerrar(true);
    });
    window.addEventListener("resize", () => cerrar(false));
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", iniciar);
  } else {
    iniciar();
  }
})();
