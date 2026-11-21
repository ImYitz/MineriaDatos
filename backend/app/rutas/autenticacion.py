# Rutas de registro e inicio de sesión.
import threading
import time
from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import modelos, esquemas, seguridad
from ..base_datos import obtener_sesion

router = APIRouter(prefix="/api/auth", tags=["autenticación"])

# ---------- Límite de intentos fallidos de inicio de sesión ----------
# Se guarda en memoria (por proceso): suficiente para frenar la fuerza bruta en un solo servidor.
# Con varios procesos o servidores habría que usar una base de datos compartida (p. ej. Redis).
INTENTOS_MAXIMOS = 5          # fallos permitidos...
VENTANA_SEGUNDOS = 10 * 60    # ...dentro de esta ventana, por IP + usuario
_fallos: Dict[str, List[float]] = {}
_candado = threading.Lock()


def _clave_intentos(request: Request, identificador: str) -> str:
    ip = request.client.host if request.client else "desconocida"
    return ip + "|" + identificador.strip().lower()


def _fallos_recientes(clave: str) -> List[float]:
    """Fallos vigentes de esta clave (limpia los vencidos). Llamar con el candado tomado."""
    ahora = time.time()
    vigentes = [t for t in _fallos.get(clave, []) if ahora - t < VENTANA_SEGUNDOS]
    if vigentes:
        _fallos[clave] = vigentes
    else:
        _fallos.pop(clave, None)
    return vigentes


def _limpiar_si_crece() -> None:
    """Evita que el diccionario crezca sin límite si alguien prueba miles de usuarios distintos."""
    if len(_fallos) > 10000:
        ahora = time.time()
        for k in [k for k, v in _fallos.items() if not v or ahora - v[-1] >= VENTANA_SEGUNDOS]:
            _fallos.pop(k, None)


@router.post("/registro", response_model=esquemas.TokenRespuesta, status_code=201)
def registrar(datos: esquemas.RegistroUsuario, bd: Session = Depends(obtener_sesion)):
    """Crea una cuenta nueva y deja la sesión iniciada (devuelve el token)."""
    # Los validadores de esquemas.RegistroUsuario ya revisaron el formato de los datos.
    if bd.query(modelos.Usuario).filter(modelos.Usuario.nombre_usuario == datos.nombre_usuario).first():
        raise HTTPException(status_code=409, detail="Ese nombre de usuario ya está en uso")
    if bd.query(modelos.Usuario).filter(modelos.Usuario.correo == datos.correo).first():
        raise HTTPException(status_code=409, detail="Ese correo ya está registrado")

    usuario = modelos.Usuario(
        nombre_usuario=datos.nombre_usuario,
        correo=datos.correo,
        contrasena_hash=seguridad.hashear_contrasena(datos.contrasena),
    )
    bd.add(usuario)
    try:
        bd.commit()
    except IntegrityError:
        # Pasa si dos personas se registran con el mismo dato casi al mismo tiempo
        bd.rollback()
        raise HTTPException(status_code=409, detail="Ese usuario o correo ya está registrado")
    bd.refresh(usuario)

    return esquemas.TokenRespuesta(access_token=seguridad.crear_token(usuario.id))


@router.post("/login", response_model=esquemas.TokenRespuesta)
def iniciar_sesion(datos: esquemas.InicioSesion, request: Request, bd: Session = Depends(obtener_sesion)):
    """Comprueba usuario (o correo) y contraseña; si son correctos, devuelve el token."""
    identificador = datos.usuario_o_correo.strip()
    clave = _clave_intentos(request, identificador)

    with _candado:
        if len(_fallos_recientes(clave)) >= INTENTOS_MAXIMOS:
            raise HTTPException(
                status_code=429,
                detail="Demasiados intentos fallidos. Espera unos minutos e inténtalo de nuevo.",
            )

    if "@" in identificador:
        usuario = bd.query(modelos.Usuario).filter(modelos.Usuario.correo == identificador.lower()).first()
    else:
        usuario = bd.query(modelos.Usuario).filter(modelos.Usuario.nombre_usuario == identificador).first()

    # Mismo mensaje si falla el usuario o la contraseña: así no se revela qué usuarios existen
    if usuario is None or not seguridad.verificar_contrasena(datos.contrasena, usuario.contrasena_hash):
        with _candado:
            _fallos.setdefault(clave, []).append(time.time())
            _limpiar_si_crece()
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")

    with _candado:
        _fallos.pop(clave, None)    # un inicio correcto borra los fallos anteriores
    return esquemas.TokenRespuesta(access_token=seguridad.crear_token(usuario.id))
