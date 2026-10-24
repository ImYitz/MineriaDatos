// Pantalla de registro.

if (obtenerToken()) {
  window.location.href = "index.html";
}

const formulario = document.getElementById("formulario");
const elError = document.getElementById("mensaje-error");
const elBoton = document.getElementById("boton-enviar");

formulario.addEventListener("submit", async (evento) => {
  evento.preventDefault();
  elError.textContent = "";

  const contrasena = document.getElementById("contrasena").value;
  const contrasena2 = document.getElementById("contrasena2").value;
  if (contrasena !== contrasena2) {
    elError.textContent = "Las contraseñas no coinciden";
    return;
  }

  elBoton.disabled = true;
  try {
    const datos = {
      nombre_usuario: document.getElementById("nombre_usuario").value,
      correo: document.getElementById("correo").value,
      contrasena: contrasena,
    };
    const respuesta = await pedirApi(
      "/api/auth/registro",
      { method: "POST", body: JSON.stringify(datos) },
      false
    );
    // El registro ya inicia la sesión: guardamos el token y entramos
    guardarToken(respuesta.access_token);
    window.location.href = "index.html";
  } catch (error) {
    elError.textContent = error.message;
    elBoton.disabled = false;
  }
});
