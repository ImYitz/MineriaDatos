# Crea estudiantes SIMULADOS con historial de estudio, para tener una base de datos sólida con la que
# practicar minería de datos (modelo de riesgo de abandono y segmentación de estudiantes).
#
# Uso (desde la carpeta backend, con el entorno activado):
#   python sembrar_estudiantes.py                  crea 300 estudiantes (si no hay ya)
#   python sembrar_estudiantes.py --cantidad 500   crea 500
#   python sembrar_estudiantes.py --reiniciar      borra los simulados y los vuelve a crear
#   python sembrar_estudiantes.py --borrar         borra solo los simulados
#
# Los estudiantes se llaman sim_001, sim_002... y no tienen correo ni contraseña (nadie puede iniciar
# sesión con ellos). Los usuarios reales NUNCA se tocan. Los datos salen siempre iguales (semilla fija),
# pero las fechas son relativas a HOY: el historial cubre las últimas semanas.
#
# Cada estudiante tiene un perfil de comportamiento (constante, esporádico, perfeccionista, abandona,
# nuevo). Las lecciones, XP, monedas y rachas se calculan con las MISMAS reglas que la aplicación
# (app/logica.py), así que los datos son coherentes con los de un usuario real.
import argparse
import hashlib
import random
import sys
from datetime import datetime, time, timedelta

from app.base_datos import Base, motor, SesionLocal
from app import modelos, logica
from app import modelos_laboratorios, modelos_r, modelos_libre  # noqa: F401  (para que se conozcan las tablas)
from app.modelos_laboratorios import ProgresoLaboratorio
from app.modelos_r import ProgresoR
from app.modelos_libre import SesionLibre
from app.catalogo_laboratorios import CATALOGO as LABORATORIOS
from app.catalogo_r import CATALOGO as LECCIONES_R
from app.datos_estudio import PREFIJO_SIMULADOS

SEMILLA = 12345
PUNTAJE_MINIMO_R = 60          # como en la aplicación: la práctica de R solo se guarda si se aprueba
EJERCICIOS_POR_LECCION = 4
PREGUNTAS_LIBRE = 8
XP_LECCION = 10
XP_LIBRE = 8
LIMITE_LIBRE_DIA = 3

# Perfiles. inicio = días atrás en que se registró (mín, máx); p_dia = probabilidad de estudiar un día;
# habilidad = probabilidad de acertar cada pregunta; pausa = probabilidad de dejar de estudiar de
# repente en algún momento de los últimos 10 a 25 días; repite = probabilidad de repetir una lección ya hecha.
MEZCLA_NORMAL = {"lecciones": 0.62, "laboratorios": 0.14, "r": 0.14, "libre": 0.10}
MEZCLA_PRACTICA = {"lecciones": 0.40, "laboratorios": 0.25, "r": 0.25, "libre": 0.10}
PERFILES = {
    "constante":      {"peso": 28, "inicio": (35, 75), "p_dia": 0.70, "habilidad": (0.78, 0.95), "pausa": 0.06, "repite": 0.10, "mezcla": MEZCLA_NORMAL, "max_dia": 3},
    "esporadico":     {"peso": 22, "inicio": (35, 75), "p_dia": 0.18, "habilidad": (0.50, 0.80), "pausa": 0.05, "repite": 0.15, "mezcla": MEZCLA_NORMAL, "max_dia": 2},
    "perfeccionista": {"peso": 15, "inicio": (35, 70), "p_dia": 0.38, "habilidad": (0.92, 1.00), "pausa": 0.05, "repite": 0.35, "mezcla": MEZCLA_PRACTICA, "max_dia": 3},
    "abandona":       {"peso": 25, "inicio": (45, 75), "p_dia": 0.55, "habilidad": (0.35, 0.75), "pausa": 1.00, "repite": 0.10, "mezcla": MEZCLA_NORMAL, "max_dia": 2, "parada": (10, 50)},
    "nuevo":          {"peso": 10, "inicio": (2, 10),  "p_dia": 0.60, "habilidad": (0.50, 0.90), "pausa": 0.00, "repite": 0.05, "mezcla": MEZCLA_NORMAL, "max_dia": 2},
}


def limitar(valor, minimo, maximo):
    return max(minimo, min(maximo, valor))


def aciertos_de(azar, total, habilidad):
    """Cuántas preguntas acierta: cada una con probabilidad "habilidad" (con algo de variación)."""
    p = limitar(habilidad + azar.gauss(0, 0.08), 0.05, 1.0)
    return sum(1 for _ in range(total) if azar.random() < p)


def elegir(azar, mezcla):
    return azar.choices(list(mezcla), weights=list(mezcla.values()))[0]


def simular(bd, azar, numero, perfil, ids_lecciones, hoy):
    """Crea un estudiante y todo su historial. Devuelve (usuario, cantidad de actividades)."""
    cfg = PERFILES[perfil]
    inicio = azar.randint(*cfg["inicio"])
    habilidad = azar.uniform(*cfg["habilidad"])
    parada = None                       # día (hace cuántos días) en que deja de estudiar
    if perfil == "abandona":
        parada = azar.randint(*cfg["parada"])
        parada = min(parada, max(1, inicio - 5))
    elif azar.random() < cfg["pausa"]:
        parada = azar.randint(10, 25)

    registro = datetime.combine(hoy - timedelta(days=inicio), time(azar.randint(8, 20), azar.randint(0, 59)))
    usuario = modelos.Usuario(
        nombre_usuario=PREFIJO_SIMULADOS + str(numero).zfill(3), fecha_registro=registro,
        xp_total=0, nivel=1, monedas=0, racha_actual=0, racha_maxima=0)
    bd.add(usuario)
    bd.flush()                          # para tener usuario.id

    lecciones_hechas, labs_hechos, r_hechos = set(), set(), set()
    libres_hoy = {}
    actividades = 0

    for dias_atras in range(inicio, -1, -1):
        if parada is not None and dias_atras < parada:
            break
        if azar.random() >= cfg["p_dia"]:
            continue
        dia = hoy - timedelta(days=dias_atras)
        for _ in range(azar.randint(1, cfg["max_dia"])):
            momento = datetime.combine(dia, time(azar.randint(8, 21), azar.randint(0, 59)))
            tipo = elegir(azar, cfg["mezcla"])

            if tipo == "lecciones":
                pendientes = [i for i in ids_lecciones if i not in lecciones_hechas]
                if pendientes and azar.random() >= cfg["repite"]:
                    leccion_id = pendientes[0]
                else:
                    leccion_id = azar.choice(ids_lecciones)
                primera = leccion_id not in lecciones_hechas
                aciertos = aciertos_de(azar, EJERCICIOS_POR_LECCION, habilidad)
                puntaje = round(aciertos * 100 / EJERCICIOS_POR_LECCION)
                xp = logica.calcular_xp_ganada(XP_LECCION, primera)
                monedas = logica.calcular_monedas(aciertos, primera)
                bd.add(modelos.ProgresoLeccion(
                    usuario_id=usuario.id, leccion_id=leccion_id, aciertos=aciertos,
                    total_ejercicios=EJERCICIOS_POR_LECCION, puntaje=puntaje, xp_ganada=xp,
                    fecha_completada=momento))
                lecciones_hechas.add(leccion_id)

            elif tipo == "laboratorios":
                pendientes = [l for l in LABORATORIOS if l["codigo"] not in labs_hechos]
                lab = azar.choice(pendientes) if pendientes and azar.random() >= cfg["repite"] else azar.choice(LABORATORIOS)
                primera = lab["codigo"] not in labs_hechos
                total = len(lab["preguntas"])
                aciertos = aciertos_de(azar, total, habilidad)
                puntaje = round(aciertos * 100 / total)
                xp = logica.calcular_xp_ganada(lab["xp_recompensa"], primera)
                monedas = logica.calcular_monedas(aciertos, primera)
                bd.add(ProgresoLaboratorio(
                    usuario_id=usuario.id, laboratorio=lab["codigo"], aciertos=aciertos,
                    total_preguntas=total, puntaje=puntaje, xp_ganada=xp, fecha_completada=momento))
                labs_hechos.add(lab["codigo"])

            elif tipo == "r":
                pendientes = [l for l in LECCIONES_R if l["codigo"] not in r_hechos]
                leccion = azar.choice(pendientes) if pendientes and azar.random() >= cfg["repite"] else azar.choice(LECCIONES_R)
                aciertos = aciertos_de(azar, 4, habilidad)
                puntaje = round(aciertos * 100 / 4)
                if puntaje < PUNTAJE_MINIMO_R:
                    continue            # práctica no aprobada: no se guarda nada
                primera = leccion["codigo"] not in r_hechos
                xp = logica.calcular_xp_ganada(leccion.get("xp_recompensa", 20), primera)
                monedas = logica.calcular_monedas(aciertos, primera)
                bd.add(ProgresoR(
                    usuario_id=usuario.id, leccion=leccion["codigo"], aciertos=aciertos,
                    total_comprobaciones=4, puntaje=puntaje, xp_ganada=xp, fecha_completada=momento))
                r_hechos.add(leccion["codigo"])

            else:                       # modo libre
                aciertos = aciertos_de(azar, PREGUNTAS_LIBRE, habilidad)
                puntaje = round(aciertos * 100 / PREGUNTAS_LIBRE)
                con_recompensa = libres_hoy.get(dia, 0) < LIMITE_LIBRE_DIA
                libres_hoy[dia] = libres_hoy.get(dia, 0) + 1
                xp = int(XP_LIBRE * puntaje / 100 + 0.5) if con_recompensa else 0
                monedas = aciertos if con_recompensa else 0
                huella = hashlib.sha256((usuario.nombre_usuario + str(actividades)).encode()).hexdigest()
                bd.add(SesionLibre(
                    usuario_id=usuario.id, titulo="Documento simulado " + str(actividades + 1),
                    huella_documento=huella, metodo="local", preguntas=[], fecha_creada=momento,
                    completada=True, con_recompensa=con_recompensa, aciertos=aciertos,
                    total_preguntas=PREGUNTAS_LIBRE, puntaje=puntaje, xp_ganada=xp,
                    fecha_completada=momento))

            usuario.xp_total += xp
            usuario.monedas += monedas
            logica.actualizar_racha(usuario, dia)
            actividades += 1

    usuario.nivel = logica.calcular_nivel(usuario.xp_total)
    return usuario, actividades


def borrar_simulados(bd):
    ids = [i for (i,) in bd.query(modelos.Usuario.id).filter(
        modelos.Usuario.nombre_usuario.startswith(PREFIJO_SIMULADOS, autoescape=True))]
    if not ids:
        return 0
    for tabla in (SesionLibre, ProgresoR, ProgresoLaboratorio, modelos.ProgresoLeccion,
                  modelos.LogroUsuario, modelos.ItemUsuario, modelos.AvatarUsuario):
        bd.query(tabla).filter(tabla.usuario_id.in_(ids)).delete(synchronize_session=False)
    bd.query(modelos.Usuario).filter(modelos.Usuario.id.in_(ids)).delete(synchronize_session=False)
    bd.commit()
    return len(ids)


def main():
    ap = argparse.ArgumentParser(description="Crea estudiantes simulados para practicar minería de datos.")
    ap.add_argument("--cantidad", type=int, default=300, help="cuántos estudiantes crear (por defecto 300)")
    ap.add_argument("--reiniciar", action="store_true", help="borra los simulados y los vuelve a crear")
    ap.add_argument("--borrar", action="store_true", help="borra los simulados y termina")
    args = ap.parse_args()
    if not 10 <= args.cantidad <= 1000:
        sys.exit("La cantidad debe estar entre 10 y 1000.")

    Base.metadata.create_all(bind=motor)
    bd = SesionLocal()
    try:
        if args.borrar or args.reiniciar:
            print("Estudiantes simulados borrados:", borrar_simulados(bd))
            if args.borrar:
                return
        existentes = bd.query(modelos.Usuario).filter(
            modelos.Usuario.nombre_usuario.startswith(PREFIJO_SIMULADOS, autoescape=True)).count()
        if existentes:
            print("Ya hay", existentes, "estudiantes simulados. Usa --reiniciar para volver a crearlos.")
            return
        ids_lecciones = [i for (i,) in bd.query(modelos.Leccion.id).order_by(modelos.Leccion.orden)]
        if not ids_lecciones:
            sys.exit("No hay lecciones. Ejecuta primero sembrar_datos.py y arranca el servidor una vez.")

        azar = random.Random(SEMILLA)
        hoy = logica.fecha_hoy()
        perfiles = azar.choices(list(PERFILES), weights=[c["peso"] for c in PERFILES.values()], k=args.cantidad)
        conteo = {nombre: 0 for nombre in PERFILES}
        total_actividades = 0
        for numero, perfil in enumerate(perfiles, start=1):
            _, n = simular(bd, azar, numero, perfil, ids_lecciones, hoy)
            conteo[perfil] += 1
            total_actividades += n
        bd.commit()
        print("Listo:", args.cantidad, "estudiantes simulados y", total_actividades, "actividades creadas.")
        print("Perfiles:", ", ".join(k + " " + str(v) for k, v in conteo.items()))
        print("Reinicia el servidor para que el panel use estos datos.")
    finally:
        bd.close()


if __name__ == "__main__":
    main()
