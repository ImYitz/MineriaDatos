# Tablas de la base de datos.
# Etapa 1: cursos, lecciones y ejercicios.
# Etapa 2: usuarios y progreso_lecciones.
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON, Date, DateTime
from sqlalchemy.orm import relationship
from .base_datos import Base


class Curso(Base):
    __tablename__ = "cursos"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(100), nullable=False)
    descripcion = Column(Text)

    # Un curso tiene muchas lecciones, ordenadas por el campo "orden"
    lecciones = relationship(
        "Leccion", back_populates="curso", order_by="Leccion.orden"
    )


class Leccion(Base):
    __tablename__ = "lecciones"

    id = Column(Integer, primary_key=True, index=True)
    curso_id = Column(Integer, ForeignKey("cursos.id"), nullable=False)
    titulo = Column(String(100), nullable=False)
    descripcion = Column(Text)
    orden = Column(Integer, nullable=False)          # posición dentro del curso
    xp_recompensa = Column(Integer, default=10)      # XP al completarla por primera vez

    curso = relationship("Curso", back_populates="lecciones")
    ejercicios = relationship(
        "Ejercicio", back_populates="leccion", order_by="Ejercicio.orden"
    )


class Ejercicio(Base):
    __tablename__ = "ejercicios"

    id = Column(Integer, primary_key=True, index=True)
    leccion_id = Column(Integer, ForeignKey("lecciones.id"), nullable=False)
    # tipo: "opcion_multiple" ahora; "completar" y "ordenar" más adelante
    tipo = Column(String(30), nullable=False, default="opcion_multiple")
    enunciado = Column(Text, nullable=False)
    opciones = Column(JSON)                          # lista de textos, p. ej. ["A", "B", "C"]
    respuesta_correcta = Column(Text, nullable=False)
    explicacion = Column(Text)                       # se muestra después de responder
    orden = Column(Integer, nullable=False)

    leccion = relationship("Leccion", back_populates="ejercicios")


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre_usuario = Column(String(50), unique=True, nullable=False)
    # correo y contrasena_hash quedan vacíos para el "invitado"; se usan desde la Etapa 3
    correo = Column(String(120), unique=True)
    contrasena_hash = Column(String(255))

    xp_total = Column(Integer, nullable=False, default=0)
    nivel = Column(Integer, nullable=False, default=1)

    # Estas columnas se usarán en etapas posteriores (se crean ya para no
    # tener que modificar la tabla después)
    monedas = Column(Integer, nullable=False, default=0)
    racha_actual = Column(Integer, nullable=False, default=0)
    racha_maxima = Column(Integer, nullable=False, default=0)
    ultima_fecha_estudio = Column(Date)

    fecha_registro = Column(DateTime, nullable=False, default=datetime.now)

    progresos = relationship("ProgresoLeccion", back_populates="usuario")


class ProgresoLeccion(Base):
    """Un registro por cada vez que un usuario termina una lección."""
    __tablename__ = "progreso_lecciones"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    leccion_id = Column(Integer, ForeignKey("lecciones.id"), nullable=False)
    aciertos = Column(Integer, nullable=False)
    total_ejercicios = Column(Integer, nullable=False)
    puntaje = Column(Integer, nullable=False)        # porcentaje de 0 a 100
    xp_ganada = Column(Integer, nullable=False)
    fecha_completada = Column(DateTime, nullable=False, default=datetime.now)

    usuario = relationship("Usuario", back_populates="progresos")
    leccion = relationship("Leccion")


class Logro(Base):
    """Catálogo de logros. Cada logro tiene una condición: tipo + valor objetivo."""
    __tablename__ = "logros"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(50), unique=True, nullable=False)   # identificador estable
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String(255), nullable=False)
    icono = Column(String(30), nullable=False)                 # nombre del icono (el navegador lo dibuja)
    # Ejemplo: tipo_condicion="racha" y valor_objetivo=7  ->  "7 días de racha"
    tipo_condicion = Column(String(40), nullable=False)
    valor_objetivo = Column(Integer, nullable=False)
    recompensa_monedas = Column(Integer, nullable=False, default=0)


class LogroUsuario(Base):
    """Qué logros ha desbloqueado cada usuario (la clave es la pareja usuario + logro)."""
    __tablename__ = "logros_usuario"

    usuario_id = Column(Integer, ForeignKey("usuarios.id"), primary_key=True)
    logro_id = Column(Integer, ForeignKey("logros.id"), primary_key=True)
    fecha_obtenido = Column(DateTime, nullable=False, default=datetime.now)

    logro = relationship("Logro")


class ItemAvatar(Base):
    """Catálogo de objetos para personalizar el avatar (colores, ropa y accesorios)."""
    __tablename__ = "items_avatar"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(50), unique=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    categoria = Column(String(20), nullable=False)    # "color", "ropa" o "accesorio"
    # color -> código de color (#58cc02); ropa/accesorio -> nombre del dibujo SVG (gorra, capa...)
    valor = Column(String(50), nullable=False)
    precio_monedas = Column(Integer, nullable=False, default=0)   # 0 = se desbloquea gratis por nivel
    nivel_requerido = Column(Integer, nullable=False, default=1)


class ItemUsuario(Base):
    """Objetos que el usuario COMPRÓ (los gratuitos se desbloquean solos por nivel)."""
    __tablename__ = "items_usuario"

    usuario_id = Column(Integer, ForeignKey("usuarios.id"), primary_key=True)
    item_id = Column(Integer, ForeignKey("items_avatar.id"), primary_key=True)
    fecha_compra = Column(DateTime, nullable=False, default=datetime.now)


class AvatarUsuario(Base):
    """Lo que el usuario lleva puesto. Un registro por usuario; vacío = valor por defecto."""
    __tablename__ = "avatar_usuario"

    usuario_id = Column(Integer, ForeignKey("usuarios.id"), primary_key=True)
    id_item_color = Column(Integer, ForeignKey("items_avatar.id"))
    id_item_ropa = Column(Integer, ForeignKey("items_avatar.id"))
    id_item_accesorio = Column(Integer, ForeignKey("items_avatar.id"))
