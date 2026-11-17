# Catálogo de objetos del avatar (lo que se vende en la tienda).
#
# Cada objeto tiene:
#   categoria        "color" (color del robot), "ropa" o "accesorio"
#   valor            color -> código de color (#58cc02) o nombre de un degradado ("arcoiris");
#                    ropa/accesorio -> nombre del dibujo en frontend/js/avatar.js
#   precio_monedas   0 = es gratis y se desbloquea al llegar al nivel requerido
#   nivel_requerido  nivel mínimo para poder usarlo o comprarlo
#
# Para añadir un objeto: agrega una línea aquí (y, si es ropa, accesorio o degradado, su dibujo en
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
    {"codigo": "color_turquesa", "nombre": "Turquesa", "categoria": "color", "valor": "#14b8a6", "precio_monedas": 25, "nivel_requerido": 1},
    {"codigo": "color_rosa", "nombre": "Rosa", "categoria": "color", "valor": "#ff6fb5", "precio_monedas": 35, "nivel_requerido": 1},
    {"codigo": "color_grafito", "nombre": "Grafito", "categoria": "color", "valor": "#5b6b8a", "precio_monedas": 50, "nivel_requerido": 2},
    {"codigo": "color_plateado", "nombre": "Plateado", "categoria": "color", "valor": "#aab4c0", "precio_monedas": 0, "nivel_requerido": 4},
    {"codigo": "color_arcoiris", "nombre": "Arcoíris", "categoria": "color", "valor": "arcoiris", "precio_monedas": 120, "nivel_requerido": 4},
    {"codigo": "color_galaxia", "nombre": "Galaxia", "categoria": "color", "valor": "galaxia", "precio_monedas": 150, "nivel_requerido": 5},
    # ---- Ropa ----
    {"codigo": "ropa_camiseta", "nombre": "Camiseta", "categoria": "ropa", "valor": "camiseta", "precio_monedas": 0, "nivel_requerido": 1},
    {"codigo": "ropa_sudadera", "nombre": "Sudadera", "categoria": "ropa", "valor": "sudadera", "precio_monedas": 25, "nivel_requerido": 1},
    {"codigo": "ropa_bata", "nombre": "Bata de laboratorio", "categoria": "ropa", "valor": "bata", "precio_monedas": 35, "nivel_requerido": 2},
    {"codigo": "ropa_capa", "nombre": "Capa de héroe", "categoria": "ropa", "valor": "capa", "precio_monedas": 60, "nivel_requerido": 3},
    {"codigo": "ropa_chaleco", "nombre": "Chaleco reflectante", "categoria": "ropa", "valor": "chaleco", "precio_monedas": 30, "nivel_requerido": 2},
    {"codigo": "ropa_poncho", "nombre": "Poncho andino", "categoria": "ropa", "valor": "poncho", "precio_monedas": 45, "nivel_requerido": 2},
    {"codigo": "ropa_overol", "nombre": "Overol", "categoria": "ropa", "valor": "overol", "precio_monedas": 0, "nivel_requerido": 3},
    {"codigo": "ropa_smoking", "nombre": "Esmoquin", "categoria": "ropa", "valor": "smoking", "precio_monedas": 70, "nivel_requerido": 4},
    {"codigo": "ropa_armadura", "nombre": "Armadura", "categoria": "ropa", "valor": "armadura", "precio_monedas": 100, "nivel_requerido": 5},
    {"codigo": "ropa_astronauta", "nombre": "Traje espacial", "categoria": "ropa", "valor": "astronauta", "precio_monedas": 110, "nivel_requerido": 6},
    # ---- Accesorios ----
    {"codigo": "acc_gafas", "nombre": "Gafas", "categoria": "accesorio", "valor": "gafas", "precio_monedas": 15, "nivel_requerido": 1},
    {"codigo": "acc_gorra", "nombre": "Gorra", "categoria": "accesorio", "valor": "gorra", "precio_monedas": 20, "nivel_requerido": 1},
    {"codigo": "acc_audifonos", "nombre": "Audífonos", "categoria": "accesorio", "valor": "audifonos", "precio_monedas": 0, "nivel_requerido": 2},
    {"codigo": "acc_sombrero", "nombre": "Sombrero de mago", "categoria": "accesorio", "valor": "sombrero", "precio_monedas": 45, "nivel_requerido": 2},
    {"codigo": "acc_corona", "nombre": "Corona", "categoria": "accesorio", "valor": "corona", "precio_monedas": 90, "nivel_requerido": 3},
    {"codigo": "acc_bigote", "nombre": "Bigote", "categoria": "accesorio", "valor": "bigote", "precio_monedas": 15, "nivel_requerido": 1},
    {"codigo": "acc_lazo", "nombre": "Moño", "categoria": "accesorio", "valor": "lazo", "precio_monedas": 20, "nivel_requerido": 1},
    {"codigo": "acc_bufanda", "nombre": "Bufanda", "categoria": "accesorio", "valor": "bufanda", "precio_monedas": 25, "nivel_requerido": 1},
    {"codigo": "acc_pirata", "nombre": "Parche pirata", "categoria": "accesorio", "valor": "pirata", "precio_monedas": 25, "nivel_requerido": 2},
    {"codigo": "acc_lentes_sol", "nombre": "Lentes de sol", "categoria": "accesorio", "valor": "lentes_sol", "precio_monedas": 30, "nivel_requerido": 2},
    {"codigo": "acc_gorro_invierno", "nombre": "Gorro de lana", "categoria": "accesorio", "valor": "gorro_invierno", "precio_monedas": 30, "nivel_requerido": 2},
    {"codigo": "acc_orejas_gato", "nombre": "Orejas de gato", "categoria": "accesorio", "valor": "orejas_gato", "precio_monedas": 0, "nivel_requerido": 3},
    {"codigo": "acc_cuernos", "nombre": "Cuernos de diablillo", "categoria": "accesorio", "valor": "cuernos", "precio_monedas": 40, "nivel_requerido": 3},
    {"codigo": "acc_casco", "nombre": "Casco de obra", "categoria": "accesorio", "valor": "casco", "precio_monedas": 40, "nivel_requerido": 3},
    {"codigo": "acc_antifaz", "nombre": "Antifaz de héroe", "categoria": "accesorio", "valor": "antifaz", "precio_monedas": 45, "nivel_requerido": 3},
    {"codigo": "acc_chef", "nombre": "Gorro de chef", "categoria": "accesorio", "valor": "chef", "precio_monedas": 50, "nivel_requerido": 4},
    {"codigo": "acc_halo", "nombre": "Aureola", "categoria": "accesorio", "valor": "halo", "precio_monedas": 60, "nivel_requerido": 4},
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
