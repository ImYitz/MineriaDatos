# Rutas del avatar: ver y guardar lo que lleva puesto el usuario.
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import modelos, esquemas, servicio_tienda
from ..base_datos import obtener_sesion
from ..dependencias import obtener_usuario_actual

router = APIRouter(prefix="/api", tags=["avatar"])


@router.get("/avatar", response_model=esquemas.AvatarConfig)
def ver_avatar(
    bd: Session = Depends(obtener_sesion),
    usuario: modelos.Usuario = Depends(obtener_usuario_actual),
):
    """El avatar actual del usuario."""
    return servicio_tienda.obtener_avatar(bd, usuario)


@router.put("/avatar", response_model=esquemas.AvatarConfig)
def guardar_avatar(
    datos: esquemas.AvatarGuardar,
    bd: Session = Depends(obtener_sesion),
    usuario: modelos.Usuario = Depends(obtener_usuario_actual),
):
    """Guarda lo que lleva puesto. Cada campo es el id de un objeto, o vacío para no llevar nada."""
    poseidos = servicio_tienda.ids_poseidos(bd, usuario)

    # (categoría esperada, id enviado por el navegador)
    pedidos = [
        ("color", datos.color_item_id),
        ("ropa", datos.ropa_item_id),
        ("accesorio", datos.accesorio_item_id),
    ]
    for categoria, item_id in pedidos:
        if item_id is None:
            continue
        item = bd.get(modelos.ItemAvatar, item_id)
        if item is None:
            raise HTTPException(status_code=404, detail="Objeto no encontrado")
        if item.categoria != categoria:
            raise HTTPException(status_code=400, detail="Ese objeto no es de la categoría " + categoria)
        if item.id not in poseidos:
            raise HTTPException(status_code=403, detail="Todavía no tienes " + item.nombre)

    fila = bd.get(modelos.AvatarUsuario, usuario.id)
    if fila is None:
        fila = modelos.AvatarUsuario(usuario_id=usuario.id)
        bd.add(fila)
    fila.id_item_color = datos.color_item_id
    fila.id_item_ropa = datos.ropa_item_id
    fila.id_item_accesorio = datos.accesorio_item_id
    bd.commit()

    return servicio_tienda.obtener_avatar(bd, usuario)
