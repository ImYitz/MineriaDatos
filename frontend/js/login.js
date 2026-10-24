// Pantalla de inicio de sesión.

// Si ya hay una sesión iniciada, vamos directo al inicio
if (obtenerToken()) {
  window.location.href = "index.html";
}

const formulario = document.getElementById("formulario");
const elError = document.getElementById("mensaje-error");
const elBoton = document.getElementById("boton-enviar");

formulario.addEventListener("submit", async (evento) => {
  evento.preventDefault();   // evita que el navegador recargue la página
  elError.textContent = "";
  elBoton.disabled = true;

  try {
    const datos = {
      usuario_o_correo: document.getElementById("usuario_o_correo").value,
      contrasena: document.getElementById("contrasena").value,
    };
    // El último "false" evita que un 401 (contraseña incorrecta) nos redirija
    const respuesta = await pedirApi(
      "/api/auth/login",
      { method: "POST", body: JSON.stringify(datos) },
      false
    );
    guardarToken(respuesta.access_token);
    window.location.href = "index.html";
  } catch (error) {
    elError.textContent = error.message;
    elBoton.disabled = false;
  }
});
