# Esquemas Pydantic: definen qué datos entran y salen de la API.
# Fíjate en que EjercicioPublico NO incluye respuesta_correcta.
import re
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, field_validator


# ---------- Etapa 1: contenido ----------

class EjercicioPublico(BaseModel):
    id: int
    tipo: str
    enunciado: str
    opciones: Optional[List[str]] = None

    model_config = {"from_attributes": True}   # permite leer objetos de SQLAlchemy


class LeccionResumen(BaseModel):
    id: int
    titulo: str
    descripcion: Optional[str] = None
    orden: int
    xp_recompensa: int

    model_config = {"from_attributes": True}


class LeccionDetalle(LeccionResumen):
    ejercicios: List[EjercicioPublico]


class CursoResumen(BaseModel):
    id: int
    titulo: str
    descripcion: Optional[str] = None

    model_config = {"from_attributes": True}


class CursoConLecciones(CursoResumen):
    lecciones: List[LeccionResumen]


class RespuestaEnviada(BaseModel):
    respuesta: str


class ResultadoRespuesta(BaseModel):
    correcto: bool
    respuesta_correcta: str
    explicacion: Optional[str] = None


# ---------- Etapa 2: progreso y XP ----------

class RespuestaDeEjercicio(BaseModel):
    ejercicio_id: int
    respuesta: str


class CompletarLeccion(BaseModel):
    """Lo que envía el navegador al terminar una lección."""
    respuestas: List[RespuestaDeEjercicio]


class LogroPublico(BaseModel):
    codigo: str
    nombre: str
    descripcion: str
    icono: str
    recompensa_monedas: int


class LogroEstado(LogroPublico):
    """Un logro visto desde el punto de vista de un usuario."""
    obtenido: bool
    fecha_obtenido: Optional[datetime] = None
    progreso_actual: int      # cuánto lleva (máximo el valor objetivo)
    valor_objetivo: int


class ResultadoLeccion(BaseModel):
    """Lo que responde el servidor (todo calculado por el servidor)."""
    aciertos: int
    total: int
    puntaje: int
    es_primera_vez: bool
    xp_ganada: int
    xp_total: int
    nivel: int
    subio_de_nivel: bool
    monedas_ganadas: int
    monedas_total: int
    racha_actual: int
    logros_nuevos: List[LogroPublico]


class PerfilUsuario(BaseModel):
    id: int
    nombre_usuario: str
    correo: Optional[str] = None
    fecha_registro: datetime
    xp_total: int
    nivel: int
    xp_en_nivel: int          # XP acumulada dentro del nivel actual
    xp_por_nivel: int         # XP necesaria para pasar al siguiente nivel
    monedas: int
    racha_actual: int         # días seguidos (0 si ya se rompió)
    racha_maxima: int


class ProgresoResumen(BaseModel):
    leccion_id: int
    veces_completada: int
    mejor_puntaje: int


# ---------- Etapa 3: registro e inicio de sesión ----------

class RegistroUsuario(BaseModel):
    nombre_usuario: str
    correo: str
    contrasena: str

    # Los validadores revisan los datos antes de llegar a la ruta.
    # Si algo está mal, FastAPI responde con error 422 y el mensaje que escribimos.
    @field_validator("nombre_usuario")
    @classmethod
    def validar_nombre(cls, valor: str) -> str:
        valor = valor.strip()
        if not re.fullmatch(r"[A-Za-z0-9_]{3,30}", valor):
            raise ValueError(
                "El nombre de usuario debe tener de 3 a 30 caracteres: letras, números o guion bajo"
            )
        return valor

    @field_validator("correo")
    @classmethod
    def validar_correo(cls, valor: str) -> str:
        valor = valor.strip().lower()
        if len(valor) > 120 or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", valor):
            raise ValueError("El correo no tiene un formato válido")
        return valor

    @field_validator("contrasena")
    @classmethod
    def validar_contrasena(cls, valor: str) -> str:
        if len(valor) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        # bcrypt solo admite contraseñas de hasta 72 bytes
        if len(valor.encode("utf-8")) > 72:
            raise ValueError("La contraseña es demasiado larga (máximo 72 caracteres)")
        return valor


class InicioSesion(BaseModel):
    usuario_o_correo: str
    contrasena: str


class TokenRespuesta(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------- Etapa 5: tienda y avatar ----------

class ItemTienda(BaseModel):
    id: int
    codigo: str
    nombre: str
    categoria: str            # "color", "ropa" o "accesorio"
    valor: str                # color (#58cc02) o nombre del dibujo (gorra)
    precio_monedas: int
    nivel_requerido: int
    estado: str               # poseido | bloqueado_nivel | sin_monedas | comprable


class ResultadoCompra(BaseModel):
    item_id: int
    nombre: str
    monedas_restantes: int


class AvatarGuardar(BaseModel):
    """Lo que envía el navegador al guardar: el id de cada objeto puesto (o vacío)."""
    color_item_id: Optional[int] = None
    ropa_item_id: Optional[int] = None
    accesorio_item_id: Optional[int] = None


class AvatarConfig(AvatarGuardar):
    """Lo que devuelve el servidor: los ids y además lo necesario para dibujar."""
    color: str                       # código de color del robot
    ropa: Optional[str] = None       # nombre del dibujo de la ropa
    accesorio: Optional[str] = None  # nombre del dibujo del accesorio
