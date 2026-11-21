# Ruta de la teoría breve que se muestra antes de los ejercicios de una lección.
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .. import modelos
from ..base_datos import obtener_sesion
from ..catalogo_teoria import obtener_teoria
from ..dependencias import obtener_usuario_actual

router = APIRouter(prefix="/api", tags=["teoría"])


class SeccionTeoria(BaseModel):
    titulo: str
    texto: str


class TeoriaLeccion(BaseModel):
    titulo: str
    secciones: List[SeccionTeoria]     # vacía si la lección no tiene teoría


@router.get("/lecciones/{leccion_id}/teoria", response_model=TeoriaLeccion)
def ver_teoria(
    leccion_id: int,
    bd: Session = Depends(obtener_sesion),
    usuario: modelos.Usuario = Depends(obtener_usuario_actual),
):
    leccion = bd.get(modelos.Leccion, leccion_id)
    if leccion is None:
        raise HTTPException(status_code=404, detail="Lección no encontrada")
    return TeoriaLeccion(
        titulo=leccion.titulo,
        secciones=[SeccionTeoria(titulo=t, texto=x) for t, x in obtener_teoria(leccion.titulo)],
    )
