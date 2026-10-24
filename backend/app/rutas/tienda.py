# Rutas de la tienda: ver los objetos y comprarlos con monedas.
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import modelos, esquemas, servicio_tienda
from ..base_datos import obtener_sesion
from ..dependencias import obtener_usuario_actual

router = APIRouter(prefix="/api/tienda", tags=["tienda"])


@router.get("", response_model=List[esquemas.ItemTienda])
def ver_tienda(
    bd: Session = Depends(obtener_sesion),
    usuario: modelos.Usuario = Depends(obtener_usuario_actual),
):
    """Todos los objetos, con su estado para este usuario (lo tiene, bloqueado, comprable...)."""
    poseidos = servicio_tienda.ids_poseidos(bd, usuario)
    items = (
        bd.query(modelos.ItemAvatar)
        .order_by(modelos.ItemAvatar.precio_monedas, modelos.ItemAvatar.id)
        .all()
    )
    return [
        esquemas.ItemTienda(
            id=i.id,
            codigo=i.codigo,
            nombre=i.nombre,
            categoria=i.categoria,
            valor=i.valor,
            precio_monedas=i.precio_monedas,
            nivel_requerido=i.nivel_requerido,
            estado=servicio_tienda.estado_item(i, poseidos, usuario),
        )
        for i in items
    ]


@router.post("/comprar/{item_id}", response_model=esquemas.ResultadoCompra)
def comprar(
    item_id: int,
    bd: Session = Depends(obtener_sesion),
    usuario: modelos.Usuario = Depends(obtener_usuario_actual),
):
    """Compra un objeto: descuenta las monedas y lo añade a los objetos del usuario."""
    item = bd.get(modelos.ItemAvatar, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Objeto no encontrado")

    # Bloquea la fila del usuario mientras se hace la compra, así dos compras
    # simultáneas no pueden gastar las mismas monedas dos veces.
    bd.refresh(usuario, with_for_update=True)

    if item.id in servicio_tienda.ids_poseidos(bd, usuario):
        raise HTTPException(status_code=409, detail="Ya tienes este objeto")
    if usuario.nivel < item.nivel_requerido:
        raise HTTPException(
            status_code=403,
            detail="Necesitas el nivel " + str(item.nivel_requerido) + " para este objeto",
        )
    if usuario.monedas < item.precio_monedas:
        raise HTTPException(status_code=400, detail="No tienes suficientes monedas")

    usuario.monedas -= item.precio_monedas
    bd.add(modelos.ItemUsuario(usuario_id=usuario.id, item_id=item.id))
    try:
        bd.commit()
    except IntegrityError:
        bd.rollback()
        raise HTTPException(status_code=409, detail="Ya tienes este objeto")

    return esquemas.ResultadoCompra(
        item_id=item.id, nombre=item.nombre, monedas_restantes=usuario.monedas
    )
