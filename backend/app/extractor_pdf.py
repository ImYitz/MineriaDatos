# Lee el texto de un PDF (con pypdf). No guarda nada en disco.
import io
import re

from pypdf import PdfReader

MAX_PAGINAS = 80
MAX_CARACTERES = 60000
MIN_CARACTERES = 300     # por debajo de esto el PDF casi seguro es una imagen escaneada


class ErrorPdf(Exception):
    """Mensaje pensado para mostrarse tal cual al usuario."""


def _limpiar(texto: str) -> str:
    texto = texto.replace("\x00", "").replace("\r", "\n").replace("\xa0", " ")
    texto = texto.replace("\x7f", "•")                        # muchos PDF exportan la viñeta como este carácter
    texto = re.sub(r"[\x01-\x08\x0b\x0c\x0e-\x1f]", " ", texto)
    texto = re.sub(r"(\w)-\n(\w)", r"\1\2", texto)            # palabras cortadas con guion al final de línea
    texto = re.sub(r"[ \t]+", " ", texto)
    texto = re.sub(r"(?m)^\s*\d{1,3}\s*$", "", texto)         # líneas que solo son un número de página
    texto = re.sub(r"\n{3,}", "\n\n", texto)
    return texto.strip()


def extraer_texto(contenido: bytes) -> str:
    try:
        lector = PdfReader(io.BytesIO(contenido))
        if lector.is_encrypted:
            try:
                ok = lector.decrypt("")
            except Exception:
                ok = 0
            if not ok:
                raise ErrorPdf("El PDF está protegido con contraseña.")
        partes, total = [], 0
        for pagina in lector.pages[:MAX_PAGINAS]:
            t = pagina.extract_text() or ""
            partes.append(t)
            total += len(t)
            if total >= MAX_CARACTERES:
                break
    except ErrorPdf:
        raise
    except Exception:
        raise ErrorPdf("No se pudo leer el archivo. ¿Es un PDF válido?")

    texto = _limpiar("\n".join(partes))[:MAX_CARACTERES]
    if len(texto) < MIN_CARACTERES:
        raise ErrorPdf(
            "El PDF casi no tiene texto seleccionable (¿es una imagen escaneada?). "
            "Prueba con un PDF donde puedas seleccionar y copiar el texto."
        )
    return texto
