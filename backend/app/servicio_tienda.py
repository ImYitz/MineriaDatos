# Lógica de la tienda y del avatar: qué objetos tiene el usuario y qué lleva puesto.
from typing import Set
from sqlalchemy.orm import Session

from . import modelos, esquemas

COLOR_POR_DEFECTO = "#58cc02"


def ids_poseidos(bd: Session, usuario: modelos.Usuario) -> Set[int]:
    """Objetos que el usuario puede usar: los que compró + los gratuitos que su nivel ya desbloqueó."""
    comprados = {
        fila.item_id
        for fila in bd.query(modelos.ItemUsuario).filter(
            modelos.ItemUsuario.usuario_id == usuario.id
        )
    }
    gratis = {
        item.id
        for item in bd.query(modelos.ItemAvatar).filter(
            modelos.ItemAvatar.precio_monedas == 0,
            modelos.ItemAvatar.nivel_requerido <= usuario.nivel,
        )
    }
    return comprados | gratis


def estado_item(item: modelos.ItemAvatar, poseidos: Set[int], usuario: modelos.Usuario) -> str:
    """Situación de un objeto para este usuario:
       poseido | bloqueado_nivel | sin_monedas | comprable"""
    if item.id in poseidos:
        return "poseido"
    if usuario.nivel < item.nivel_requerido:
        return "bloqueado_nivel"
    if usuario.monedas < item.precio_monedas:
        return "sin_monedas"
    return "comprable"


def obtener_avatar(bd: Session, usuario: modelos.Usuario) -> esquemas.AvatarConfig:
    """Lo que lleva puesto el usuario, listo para que el navegador lo dibuje."""
    fila = bd.get(modelos.AvatarUsuario, usuario.id)
    ids = {
        "color": fila.id_item_color if fila else None,
        "ropa": fila.id_item_ropa if fila else None,
        "accesorio": fila.id_item_accesorio if fila else None,
    }
    items = {
        categoria: (bd.get(modelos.ItemAvatar, item_id) if item_id else None)
        for categoria, item_id in ids.items()
    }
    return esquemas.AvatarConfig(
        color_item_id=ids["color"],
        ropa_item_id=ids["ropa"],
        accesorio_item_id=ids["accesorio"],
        color=items["color"].valor if items["color"] else COLOR_POR_DEFECTO,
        ropa=items["ropa"].valor if items["ropa"] else None,
        accesorio=items["accesorio"].valor if items["accesorio"] else None,
    )
