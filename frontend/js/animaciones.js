// Animaciones con JavaScript: onda al hacer clic, confeti al terminar, contadores y avatar.
// Los demás efectos (sacudidas, rebotes, entradas...) están en css/animaciones.css y se activan
// solos cuando los otros scripts añaden clases. Se carga automáticamente desde api.js.
(function () {
  if (window.__animacionesIniciadas) return;
  window.__animacionesIniciadas = true;

  const reducir = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const COLORES = ["#58cc02", "#1cb0f6", "#ff9600", "#a560e8", "#ff4b4b", "#ffc800"];

  // ---------- 1) Onda al hacer clic ----------
  const SELECTOR_ONDA =
    ".boton, .opcion, .pestana, .boton-item, .boton-r, .lab-boton, .tarjeta-leccion, " +
    ".menu-lateral a, .fila-historial button, .enlace-boton";

  document.addEventListener("pointerdown", (evento) => {
    if (reducir) return;
    const objetivo = evento.target.closest && evento.target.closest(SELECTOR_ONDA);
    if (!objetivo || objetivo.disabled) return;
    const caja = objetivo.getBoundingClientRect();
    const tamano = Math.max(caja.width, caja.height) * 2;
    const onda = document.createElement("span");
    onda.className = "onda-clic";
    onda.style.width = onda.style.height = tamano + "px";
    onda.style.left = evento.clientX - caja.left - tamano / 2 + "px";
    onda.style.top = evento.clientY - caja.top - tamano / 2 + "px";
    objetivo.appendChild(onda);
    onda.addEventListener("animationend", () => onda.remove());
    setTimeout(() => onda.remove(), 900);
  });

  // ---------- 2) Confeti ----------
  function confeti(cantidad, origenX, origenY) {
    if (reducir) return;
    const x0 = origenX !== undefined ? origenX : window.innerWidth / 2;
    const y0 = origenY !== undefined ? origenY : window.innerHeight * 0.35;
    for (let i = 0; i < cantidad; i++) {
      const trozo = document.createElement("span");
      trozo.className = "confeti";
      const ancho = 6 + Math.random() * 6;
      trozo.style.width = ancho + "px";
      trozo.style.height = ancho * (0.5 + Math.random() * 0.9) + "px";
      trozo.style.background = COLORES[i % COLORES.length];
      trozo.style.borderRadius = Math.random() < 0.3 ? "50%" : "2px";
      document.body.appendChild(trozo);

      const angulo = Math.random() * Math.PI * 2;
      const fuerza = 120 + Math.random() * 260;
      const dx = Math.cos(angulo) * fuerza;
      const dy = Math.sin(angulo) * fuerza - 120;
      const caida = 260 + Math.random() * 360;
      const giro = (Math.random() - 0.5) * 1080;
      const duracion = 1300 + Math.random() * 1100;
      const animacion = trozo.animate(
        [
          { transform: "translate(" + x0 + "px," + y0 + "px) rotate(0deg)", opacity: 1 },
          { transform: "translate(" + (x0 + dx) + "px," + (y0 + dy) + "px) rotate(" + giro / 2 + "deg)", opacity: 1, offset: 0.45 },
          { transform: "translate(" + (x0 + dx * 1.15) + "px," + (y0 + dy + caida) + "px) rotate(" + giro + "deg)", opacity: 0 },
        ],
        { duration: duracion, easing: "cubic-bezier(0.2, 0.7, 0.4, 1)", fill: "forwards" }
      );
      animacion.onfinish = () => trozo.remove();
    }
  }
  window.lanzarConfeti = confeti;

  // ---------- 3) Contador animado (0 -> valor) ----------
  const escrito = new WeakMap();   // elemento -> último texto que escribimos nosotros

  function contar(el) {
    if (reducir) return;
    const texto = el.textContent;
    if (escrito.get(el) === texto) return;          // es un cambio nuestro
    const m = texto.match(/\d+/);
    if (!m) return;
    const final = parseInt(m[0], 10);
    if (final === 0 || final > 100000) return;
    const antes = texto.slice(0, m.index);
    const despues = texto.slice(m.index + m[0].length);
    const inicio = performance.now();
    const duracion = 900;
    function cuadro(ahora) {
      const t = Math.min(1, (ahora - inicio) / duracion);
      const valor = Math.round(final * (1 - Math.pow(1 - t, 3)));
      const nuevo = antes + valor + despues;
      escrito.set(el, nuevo);
      el.textContent = nuevo;
      if (t < 1) requestAnimationFrame(cuadro);
    }
    requestAnimationFrame(cuadro);
  }

  function observarContador(id) {
    const el = document.getElementById(id);
    if (!el) return;
    new MutationObserver(() => contar(el)).observe(el, { childList: true, characterData: true, subtree: true });
  }

  // ---------- 4) Pantalla de resultado ----------
  function iniciarResultado() {
    const zona = document.getElementById("zona-final");
    if (zona) {
      new MutationObserver(() => {
        if (zona.classList.contains("oculto")) return;
        const resumen = (document.getElementById("resumen-final") || {}).textContent || "";
        const perfecto = /\(100\s?%/.test(resumen);
        confeti(perfecto ? 120 : 70);
        const nivel = document.getElementById("mensaje-nivel");
        if (nivel && nivel.textContent.trim()) setTimeout(() => confeti(90), 500);
      }).observe(zona, { attributes: true, attributeFilter: ["class"] });
    }

    const logros = document.getElementById("logros-nuevos");
    if (logros) {
      new MutationObserver(() => {
        if (logros.children.length === 0) return;
        const caja = logros.getBoundingClientRect();
        setTimeout(() => confeti(50, caja.left + caja.width / 2, Math.max(60, caja.top)), 400);
      }).observe(logros, { childList: true });
    }

    observarContador("resumen-xp");
    observarContador("resumen-monedas");
  }

  // ---------- 5) Cada ejercicio nuevo entra con animación ----------
  function iniciarEnunciado() {
    const enunciado = document.getElementById("enunciado");
    if (!enunciado) return;
    new MutationObserver(() => {
      enunciado.classList.remove("enunciado-animado");
      void enunciado.offsetWidth;            // reinicia la animación
      enunciado.classList.add("enunciado-animado");
    }).observe(enunciado, { childList: true });
  }

  // ---------- 6) El avatar rebota al cambiar de ropa o de color ----------
  function iniciarAvatar() {
    const vista = document.getElementById("avatar-vista");
    if (!vista) return;
    let primera = true;
    new MutationObserver(() => {
      if (primera) { primera = false; return; }   // el dibujo inicial no cuenta
      vista.classList.remove("cambio");
      void vista.offsetWidth;
      vista.classList.add("cambio");
    }).observe(vista, { childList: true });
  }

  function iniciar() {
    iniciarResultado();
    iniciarEnunciado();
    iniciarAvatar();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", iniciar);
  } else {
    iniciar();
  }
})();
