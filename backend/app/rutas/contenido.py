# Rutas (endpoints) para consultar el contenido y corregir respuestas.
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import modelos, esquemas, logica
from ..base_datos import obtener_sesion

router = APIRouter(prefix="/api", tags=["contenido"])


@router.get("/cursos", response_model=List[esquemas.CursoResumen])
def listar_cursos(bd: Session = Depends(obtener_sesion)):
    """Devuelve todos los cursos."""
    return bd.query(modelos.Curso).all()


@router.get("/cursos/{curso_id}", response_model=esquemas.CursoConLecciones)
def obtener_curso(curso_id: int, bd: Session = Depends(obtener_sesion)):
    """Devuelve un curso con la lista de sus lecciones."""
    curso = bd.get(modelos.Curso, curso_id)
    if curso is None:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    return curso


@router.get("/lecciones/{leccion_id}", response_model=esquemas.LeccionDetalle)
def obtener_leccion(leccion_id: int, bd: Session = Depends(obtener_sesion)):
    """Devuelve una lección con sus ejercicios (sin las respuestas correctas)."""
    leccion = bd.get(modelos.Leccion, leccion_id)
    if leccion is None:
        raise HTTPException(status_code=404, detail="Lección no encontrada")
    return leccion


@router.post(
    "/ejercicios/{ejercicio_id}/responder",
    response_model=esquemas.ResultadoRespuesta,
)
def responder_ejercicio(
    ejercicio_id: int,
    datos: esquemas.RespuestaEnviada,
    bd: Session = Depends(obtener_sesion),
):
    """Corrige la respuesta enviada por el estudiante."""
    ejercicio = bd.get(modelos.Ejercicio, ejercicio_id)
    if ejercicio is None:
        raise HTTPException(status_code=404, detail="Ejercicio no encontrado")

    correcto = logica.es_respuesta_correcta(datos.respuesta, ejercicio.respuesta_correcta)
    return esquemas.ResultadoRespuesta(
        correcto=correcto,
        respuesta_correcta=ejercicio.respuesta_correcta,
        explicacion=ejercicio.explicacion,
    )
