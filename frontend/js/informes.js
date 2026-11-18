// Pantalla "Informes en PDF": pide cada PDF al servidor (con el token de sesión) y lo descarga.
//
// pedirApi() de api.js solo entiende JSON, así que aquí se usa fetch directamente y la respuesta
// se convierte en un archivo ("blob") que el navegador guarda como descarga.

function fechaParaArchivo() {
  return new Date().toISOString().slice(0, 10);   // 2026-11-18
}

async function descargarPdf(ruta, nombreArchivo, boton, elMensaje) {
  const textoOriginal = boton.textContent;
  boton.disabled = true;
  boton.textContent = "Generando PDF…";
  elMensaje.textContent = "";
  elMensaje.className = "mensaje-informe";

  try {
    const respuesta = await fetch(ruta, {
      headers: { Authorization: "Bearer " + obtenerToken() },
    });
    // 401 = la sesión venció: volvemos al login
    if (respuesta.status === 401) {
      cerrarSesion();
      return;
    }
    if (!respuesta.ok) {
      throw new Error("El servidor respondió con el error " + respuesta.status);
    }

    const archivo = await respuesta.blob();
    const direccion = URL.createObjectURL(archivo);
    const enlace = document.createElement("a");
    enlace.href = direccion;
    enlace.download = nombreArchivo;
    document.body.appendChild(enlace);
    enlace.click();
    enlace.remove();
    setTimeout(() => URL.revokeObjectURL(direccion), 10000);

    elMensaje.className = "mensaje-informe ok";
    elMensaje.textContent = "✓ Listo: se descargó " + nombreArchivo;
  } catch (error) {
    elMensaje.className = "mensaje-informe error";
    elMensaje.textContent =
      "No se pudo generar el PDF. " + (error && error.message ? error.message : "") +
      " ¿Instalaste las dependencias (pip install -r requirements.txt) y reiniciaste el servidor?";
  } finally {
    boton.disabled = false;
    boton.textContent = textoOriginal;
  }
}

document.getElementById("boton-resumen").addEventListener("click", () => {
  descargarPdf(
    "/api/informes/resumen",
    "resumen_cuenta_" + fechaParaArchivo() + ".pdf",
    document.getElementById("boton-resumen"),
    document.getElementById("mensaje-resumen")
  );
});

document.getElementById("boton-documentacion").addEventListener("click", () => {
  descargarPdf(
    "/api/informes/documentacion",
    "documentacion_aplicacion.pdf",
    document.getElementById("boton-documentacion"),
    document.getElementById("mensaje-documentacion")
  );
});

// Esta página es privada: sin sesión se redirige a login.html
exigirSesion();
