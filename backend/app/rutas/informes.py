# Rutas de los informes en PDF: resumen de la cuenta y documentación de la aplicación.
#
# Los PDF se generan en el momento de pedirlos y se envían directamente: no se guardan en disco.
# Las dos rutas exigen sesión (el navegador las pide con el token y luego descarga el archivo).
from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from .. import modelos, generador_pdf, servicio_informes
from ..base_datos import obtener_sesion
from ..dependencias import obtener_usuario_actual

router = APIRouter(prefix="/api/informes", tags=["informes pdf"])


def _respuesta_pdf(contenido: bytes, nombre_archivo: str) -> Response:
    return Response(
        content=contenido,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="' + nombre_archivo + '"'},
    )


@router.get("/resumen")
def resumen_cuenta(
    bd: Session = Depends(obtener_sesion),
    usuario: modelos.Usuario = Depends(obtener_usuario_actual),
):
    """PDF con los datos de la cuenta y el avance del usuario."""
    datos = servicio_informes.datos_resumen(bd, usuario)
    return _respuesta_pdf(generador_pdf.generar_resumen(datos), "resumen_cuenta.pdf")


@router.get("/documentacion")
def documentacion(usuario: modelos.Usuario = Depends(obtener_usuario_actual)):
    """PDF con la documentación de la aplicación."""
    datos = servicio_informes.datos_documentacion()
    return _respuesta_pdf(generador_pdf.generar_documentacion(datos), "documentacion_aplicacion.pdf")
