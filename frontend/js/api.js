// Funciones comunes para hablar con la API y manejar la sesión.

const CLAVE_TOKEN = "token_aprendizaje";   // nombre con el que se guarda el token en el navegador

// ---------- Sesión (el token se guarda en localStorage del navegador) ----------

function obtenerToken() {
  try { return localStorage.getItem(CLAVE_TOKEN); } catch (e) { return null; }
}

function guardarToken(token) {
  localStorage.setItem(CLAVE_TOKEN, token);
}

function cerrarSesion() {
  try { localStorage.removeItem(CLAVE_TOKEN); } catch (e) { /* nada */ }
  window.location.href = "login.html";
}

// Se llama al inicio de las páginas privadas. Devuelve false si no hay sesión.
function exigirSesion() {
  if (!obtenerToken()) {
    window.location.href = "login.html";
    return false;
  }
  return true;
}

// ---------- Llamadas a la API ----------

// "async/await" permite esperar la respuesta del servidor sin congelar la página.
// Si hay token, se envía en la cabecera Authorization para que el servidor sepa quién eres.
async function pedirApi(ruta, opciones = {}, redirigirSiNoAutorizado = true) {
  const cabeceras = { "Content-Type": "application/json" };
  const token = obtenerToken();
  if (token) {
    cabeceras["Authorization"] = "Bearer " + token;
  }

  const respuesta = await fetch(ruta, { ...opciones, headers: cabeceras });

  // 401 = no hay sesión o el token venció: volvemos a la pantalla de login
  if (respuesta.status === 401 && redirigirSiNoAutorizado) {
    cerrarSesion();
    throw new Error("Sesión vencida");
  }

  if (!respuesta.ok) {
    // Intentamos mostrar el mensaje en español que envía el servidor
    let mensaje = "Error " + respuesta.status;
    try {
      const datos = await respuesta.json();
      if (typeof datos.detail === "string") {
        mensaje = datos.detail;
      } else if (Array.isArray(datos.detail) && datos.detail.length > 0) {
        mensaje = String(datos.detail[0].msg).replace("Value error, ", "");
      }
    } catch (e) { /* si no es JSON, dejamos el mensaje genérico */ }
    throw new Error(mensaje);
  }
  return await respuesta.json();   // convierte el texto JSON en un objeto
}

// ---------- Iconos de logros ----------
// La base de datos guarda solo el nombre del icono; aquí se convierte en emoji.
const ICONOS_LOGRO = {
  estrella: "⭐",
  diana: "🎯",
  medalla: "🥇",
  trofeo: "🏆",
  fuego: "🔥",
  calendario: "📅",
};

function iconoLogro(nombre) {
  return ICONOS_LOGRO[nombre] || "🏅";
}
