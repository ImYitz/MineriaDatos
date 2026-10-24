# Dependencias compartidas por varias rutas.
from typing import Optional
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from . import modelos, seguridad
from .base_datos import obtener_sesion

# Lee la cabecera "Authorization: Bearer <token>" que envía el navegador.
# auto_error=False para poder devolver nuestro propio mensaje en español.
esquema_bearer = HTTPBearer(auto_error=False)


def obtener_usuario_actual(
    credenciales: Optional[HTTPAuthorizationCredentials] = Depends(esquema_bearer),
    bd: Session = Depends(obtener_sesion),
) -> modelos.Usuario:
    """Devuelve el usuario dueño del token. Si no hay token válido, responde 401.

    Cualquier ruta que incluya  usuario = Depends(obtener_usuario_actual)
    queda protegida: solo entra quien haya iniciado sesión.
    """
    if credenciales is None:
        raise HTTPException(
            status_code=401,
            detail="Debes iniciar sesión",
            headers={"WWW-Authenticate": "Bearer"},
        )

    usuario_id = seguridad.leer_token(credenciales.credentials)
    usuario = bd.get(modelos.Usuario, usuario_id) if usuario_id is not None else None
    if usuario is None:
        raise HTTPException(
            status_code=401,
            detail="Sesión inválida o vencida. Inicia sesión de nuevo",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return usuario
