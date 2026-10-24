# Rutas de registro e inicio de sesión.
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import modelos, esquemas, seguridad
from ..base_datos import obtener_sesion

router = APIRouter(prefix="/api/auth", tags=["autenticación"])


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
def iniciar_sesion(datos: esquemas.InicioSesion, bd: Session = Depends(obtener_sesion)):
    """Comprueba usuario (o correo) y contraseña; si son correctos, devuelve el token."""
    identificador = datos.usuario_o_correo.strip()
    if "@" in identificador:
        usuario = bd.query(modelos.Usuario).filter(modelos.Usuario.correo == identificador.lower()).first()
    else:
        usuario = bd.query(modelos.Usuario).filter(modelos.Usuario.nombre_usuario == identificador).first()

    # Mismo mensaje si falla el usuario o la contraseña: así no se revela qué usuarios existen
    if usuario is None or not seguridad.verificar_contrasena(datos.contrasena, usuario.contrasena_hash):
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")

    return esquemas.TokenRespuesta(access_token=seguridad.crear_token(usuario.id))
