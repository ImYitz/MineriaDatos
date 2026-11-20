// Menú lateral compartido: se inyecta en todas las páginas privadas para que siempre esté visible.
// Hay que cargarlo DESPUÉS de api.js (usa cerrarSesion) y ANTES del script propio de cada página.
(function () {
  const ITEMS = [
    { archivo: "index.html", icono: "🏠", texto: "Inicio", tambien: ["leccion.html"] },
    { archivo: "perfil.html", icono: "👤", texto: "Mi perfil" },
    { archivo: "estudio.html", icono: "📊", texto: "Mis datos" },
    { archivo: "informes.html", icono: "📥", texto: "Informes PDF" },
    { archivo: "laboratorios.html", icono: "🧪", texto: "Laboratorios", tambien: ["laboratorio.html"] },
    { archivo: "aprende_r.html", icono: "💻", texto: "Aprende R", tambien: ["leccion_r.html"] },
    { archivo: "libre.html", icono: "📄", texto: "Modo libre" },
    { archivo: "contrarreloj.html", icono: "⏱️", texto: "Contrarreloj" },
    { archivo: "logros.html", icono: "🏆", texto: "Logros" },
    { archivo: "avatar.html", icono: "🤖", texto: "Avatar" },
  ];

  const principal = document.querySelector("main");
  if (!principal) return;

  const actual = window.location.pathname.split("/").pop() || "index.html";

  const nav = document.createElement("nav");
  nav.className = "menu-lateral";
  nav.setAttribute("aria-label", "Menú principal");

  function fila(icono, texto) {
    const i = document.createElement("span");
    i.className = "icono-menu";
    i.textContent = icono;
    return [i, document.createTextNode(texto)];
  }

  for (const item of ITEMS) {
    const a = document.createElement("a");
    a.href = item.archivo;
    for (const n of fila(item.icono, item.texto)) a.appendChild(n);
    if (actual === item.archivo || (item.tambien || []).includes(actual)) {
      a.classList.add("activo");
      a.setAttribute("aria-current", "page");
    }
    nav.appendChild(a);
  }

  const separador = document.createElement("div");
  separador.className = "separador";
  nav.appendChild(separador);

  const salir = document.createElement("button");
  salir.type = "button";
  salir.className = "enlace-boton";
  for (const n of fila("🚪", "Cerrar sesión")) salir.appendChild(n);
  if (document.getElementById("boton-salir")) {
    // La página ya tiene su propio botón (perfil): este usa otro id y su propio listener
    salir.id = "menu-salir";
    salir.addEventListener("click", cerrarSesion);
  } else {
    // inicio.js busca "boton-salir" y le añade el listener
    salir.id = "boton-salir";
  }
  nav.appendChild(salir);

  const aside = document.createElement("aside");
  aside.appendChild(nav);

  const layout = document.createElement("div");
  layout.className = "app-layout";
  principal.parentNode.insertBefore(layout, principal);
  layout.appendChild(aside);
  layout.appendChild(principal);
  document.body.classList.add("con-menu");
})();
