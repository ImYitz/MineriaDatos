# Punto de entrada: crea la aplicación FastAPI.
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .base_datos import Base, motor, SesionLocal
from . import modelos          # importante: así SQLAlchemy conoce las tablas
from .catalogo_logros import asegurar_logros
from .catalogo_items import asegurar_items
from .rutas import contenido, progreso, autenticacion, logros, tienda, avatar

# Crea las tablas que todavía no existan en MySQL
# (en la Etapa 5 se crearán "items_avatar", "items_usuario" y "avatar_usuario")
Base.metadata.create_all(bind=motor)

# Carga (o actualiza) los catálogos de logros y de objetos del avatar
with SesionLocal() as bd:
    asegurar_logros(bd)
    asegurar_items(bd)

app = FastAPI(title="Aprendizaje: Minería de datos")


@app.middleware("http")
async def sin_cache(request, call_next):
    """Hace que el navegador revise siempre si los archivos del frontend cambiaron."""
    respuesta = await call_next(request)
    if not request.url.path.startswith("/api"):
        respuesta.headers["Cache-Control"] = "no-cache"
    return respuesta


# Primero las rutas de la API...
app.include_router(autenticacion.router)
app.include_router(contenido.router)
app.include_router(progreso.router)
app.include_router(logros.router)
app.include_router(tienda.router)
app.include_router(avatar.router)

# ...y al final el frontend (debe ir último porque "/" atrapa todo lo demás).
CARPETA_FRONTEND = Path(__file__).resolve().parent.parent.parent / "frontend"
app.mount("/", StaticFiles(directory=CARPETA_FRONTEND, html=True), name="frontend")
