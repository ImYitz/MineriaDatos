# Seguridad: contraseñas encriptadas (bcrypt) y tokens de sesión (JWT).
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
import jwt
from dotenv import load_dotenv

load_dotenv()

# La clave secreta firma los tokens. Si alguien la conoce, podría fabricar
# tokens falsos, por eso vive en el archivo .env y no en el código.
CLAVE_SECRETA = os.getenv("CLAVE_SECRETA")
if not CLAVE_SECRETA:
    raise RuntimeError(
        "Falta CLAVE_SECRETA en el archivo backend/.env. "
        "Genera una con: python -c \"import secrets; print(secrets.token_hex(32))\""
    )

ALGORITMO = "HS256"
MINUTOS_EXPIRACION = 60 * 24   # el token dura 24 horas; después hay que iniciar sesión otra vez


def hashear_contrasena(contrasena: str) -> str:
    """Convierte la contraseña en un 'hash' irreversible. Esto es lo que se guarda en la BD."""
    return bcrypt.hashpw(contrasena.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verificar_contrasena(contrasena: str, hash_guardado: Optional[str]) -> bool:
    """Comprueba si la contraseña escrita corresponde al hash guardado."""
    if not hash_guardado:   # por ejemplo, el usuario "invitado" no tiene contraseña
        return False
    try:
        return bcrypt.checkpw(contrasena.encode("utf-8"), hash_guardado.encode("utf-8"))
    except ValueError:
        return False


def crear_token(usuario_id: int) -> str:
    """Crea un token JWT que contiene el id del usuario y una fecha de vencimiento."""
    vence = datetime.now(timezone.utc) + timedelta(minutes=MINUTOS_EXPIRACION)
    datos = {"sub": str(usuario_id), "exp": vence}   # "sub" = a quién pertenece el token
    return jwt.encode(datos, CLAVE_SECRETA, algorithm=ALGORITMO)


def leer_token(token: str) -> Optional[int]:
    """Devuelve el id del usuario si el token es válido; None si es falso o venció."""
    try:
        datos = jwt.decode(token, CLAVE_SECRETA, algorithms=[ALGORITMO])
        return int(datos["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        return None
