# Catálogo de objetos del avatar (lo que se vende en la tienda).
#
# Cada objeto tiene:
#   categoria        "color" (color del robot), "ropa" o "accesorio"
#   valor            color -> código de color; ropa/accesorio -> nombre del dibujo en frontend/js/avatar.js
#   precio_monedas   0 = es gratis y se desbloquea al llegar al nivel requerido
#   nivel_requerido  nivel mínimo para poder usarlo o comprarlo
#
# Para añadir un objeto: agrega una línea aquí (y, si es ropa o accesorio, su dibujo en
# avatar.js) y reinicia el servidor.
from sqlalchemy.orm import Session
from . import modelos

CATALOGO = [
    # ---- Colores del robot ----
    {"codigo": "color_verde", "nombre": "Verde", "categoria": "color", "valor": "#58cc02", "precio_monedas": 0, "nivel_requerido": 1},
    {"codigo": "color_azul", "nombre": "Azul", "categoria": "color", "valor": "#1cb0f6", "precio_monedas": 20, "nivel_requerido": 1},
    {"codigo": "color_naranja", "nombre": "Naranja", "categoria": "color", "valor": "#ff9600", "precio_monedas": 30, "nivel_requerido": 1},
    {"codigo": "color_morado", "nombre": "Morado", "categoria": "color", "valor": "#a560e8", "precio_monedas": 0, "nivel_requerido": 2},
    {"codigo": "color_rojo", "nombre": "Rojo", "categoria": "color", "valor": "#ff4b4b", "precio_monedas": 40, "nivel_requerido": 2},
    {"codigo": "color_dorado", "nombre": "Dorado", "categoria": "color", "valor": "#ffc800", "precio_monedas": 80, "nivel_requerido": 3},
    # ---- Ropa ----
    {"codigo": "ropa_camiseta", "nombre": "Camiseta", "categoria": "ropa", "valor": "camiseta", "precio_monedas": 0, "nivel_requerido": 1},
    {"codigo": "ropa_sudadera", "nombre": "Sudadera", "categoria": "ropa", "valor": "sudadera", "precio_monedas": 25, "nivel_requerido": 1},
    {"codigo": "ropa_bata", "nombre": "Bata de laboratorio", "categoria": "ropa", "valor": "bata", "precio_monedas": 35, "nivel_requerido": 2},
    {"codigo": "ropa_capa", "nombre": "Capa de héroe", "categoria": "ropa", "valor": "capa", "precio_monedas": 60, "nivel_requerido": 3},
    # ---- Accesorios ----
    {"codigo": "acc_gafas", "nombre": "Gafas", "categoria": "accesorio", "valor": "gafas", "precio_monedas": 15, "nivel_requerido": 1},
    {"codigo": "acc_gorra", "nombre": "Gorra", "categoria": "accesorio", "valor": "gorra", "precio_monedas": 20, "nivel_requerido": 1},
    {"codigo": "acc_audifonos", "nombre": "Audífonos", "categoria": "accesorio", "valor": "audifonos", "precio_monedas": 0, "nivel_requerido": 2},
    {"codigo": "acc_sombrero", "nombre": "Sombrero de mago", "categoria": "accesorio", "valor": "sombrero", "precio_monedas": 45, "nivel_requerido": 2},
    {"codigo": "acc_corona", "nombre": "Corona", "categoria": "accesorio", "valor": "corona", "precio_monedas": 90, "nivel_requerido": 3},
]


def asegurar_items(bd: Session) -> None:
    """Se ejecuta al arrancar el servidor: crea los objetos que falten y actualiza los demás.
    Se puede ejecutar muchas veces sin duplicar nada."""
    for datos in CATALOGO:
        item = bd.query(modelos.ItemAvatar).filter(modelos.ItemAvatar.codigo == datos["codigo"]).first()
        if item is None:
            bd.add(modelos.ItemAvatar(**datos))
        else:
            for campo, valor in datos.items():
                setattr(item, campo, valor)
    bd.commit()
