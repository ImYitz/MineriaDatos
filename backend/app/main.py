# Punto de entrada: crea la aplicación FastAPI.
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .base_datos import Base, motor, SesionLocal
from . import modelos          # importante: así SQLAlchemy conoce las tablas
from . import modelos_laboratorios   # tabla de progreso en laboratorios (Etapa 6)
from . import modelos_r              # tabla de progreso en lecciones de R (Etapa 7)
from . import modelos_libre          # tabla de prácticas del modo libre (Etapa 8)
from .catalogo_logros import asegurar_logros
from .catalogo_items import asegurar_items
from .catalogo_lecciones import asegurar_lecciones
from .rutas import contenido, progreso, autenticacion, logros, tienda, avatar, laboratorios, aprende_r, libre

# Crea las tablas que todavía no existan en MySQL
# (en las Etapas 6, 7 y 8 se crean "progreso_laboratorios", "progreso_r" y "sesiones_libres"; las demás ya existen y no se tocan)
Base.metadata.create_all(bind=motor)

# Carga (o actualiza) los catálogos de logros, objetos del avatar y lecciones
with SesionLocal() as bd:
    asegurar_logros(bd)
    asegurar_items(bd)
    asegurar_lecciones(bd)   # añade las lecciones nuevas sin borrar usuarios ni progreso

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
app.include_router(laboratorios.router)
app.include_router(aprende_r.router)
app.include_router(libre.router)

# ...y al final el frontend (debe ir último porque "/" atrapa todo lo demás).
CARPETA_FRONTEND = Path(__file__).resolve().parent.parent.parent / "frontend"
app.mount("/", StaticFiles(directory=CARPETA_FRONTEND, html=True), name="frontend")
