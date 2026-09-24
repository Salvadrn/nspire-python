#!/usr/bin/env python3
"""build.py - genera los 4 archivos para la calculadora en calculadora/.

Uso:  python3 build.py

    calculadora/ap.py       Calculo AP (calcpy + formulas + menu ap)
    calculadora/ai.py       IA: regresion lineal (ai)
    calculadora/fisica.py   Fisica (FISICA)
    calculadora/general.py  los 3 juntos con un menu principal

Cada uno es autocontenido: se instala solo, sin PyLib ni otros archivos.
Si Luna esta compilado en .tools/Luna, genera tambien el .tns de cada uno.
Las piezas viven en src/; NO edites calculadora/ a mano.

Cada pieza marca lo que no entra cuando se junta con otras:
    # --- bundle: skip ---  ...  # --- bundle: end skip ---   (imports)
    # --- autorun ---        (de aqui al final: el arranque de la pieza)
"""
import ast
import builtins
import math
import os
import subprocess
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(AQUI, "src")
SALIDA = os.path.join(AQUI, "calculadora")
SKIP_INI = "# --- bundle: skip ---"
SKIP_FIN = "# --- bundle: end skip ---"
AUTORUN = "# --- autorun ---"
LUNA = os.path.join(AQUI, ".tools", "Luna", "luna")

# nombre -> (piezas, funcion que arranca, descripcion)
OBJETIVOS = [
    ("ap", ["calcpy", "formulas", "ap"], "ap", "Calculo AP"),
    ("ai", ["ai"], "ia", "IA: regresion lineal"),
    ("fisica", ["fisica"], "fisica", "Fisica"),
    ("general", ["calcpy", "formulas", "ap", "ai", "fisica"], "general",
     "Calculo AP + IA + Fisica"),
]

CABEZA = '''\
# {nombre} - {desc}
# Para la TI-Nspire CX II CAS de Adrian (MicroPython 1.11).
# GENERADO por build.py desde src/{piezas}:
# no lo edites a mano; edita src/ y corre  python3 build.py

from math import *
import sys
'''

MENU_GENERAL = '''

# ===================== menu principal =====================

def general():
    try:
        while True:
            print("")
            print("== GENERAL: elige materia ==")
            print("1 Calculo AP")
            print("2 IA: regresion lineal")
            print("3 Fisica")
            print("0 salir")
            op = input("? ").strip()
            if op == "0":
                break
            try:
                if op == "1":
                    ap()
                elif op == "2":
                    ia()
                elif op == "3":
                    fisica()
                elif op != "":
                    print("escribe 1, 2, 3 o 0")
            except KeyboardInterrupt:
                print("(interrumpido: de vuelta al menu general)")
            except Exception as err:
                print("Algo fallo: " + str(err))
    except KeyboardInterrupt:
        pass
    print("Para abrir otra vez: general()")
'''

ARRANQUE = '''

# correr el programa otra vez vuelve a abrir el menu
try:
    {fn}()
finally:
    sys.modules.pop(__name__, None)
'''


def procesa(nombre):
    ruta = os.path.join(SRC, nombre + ".py")
    out = []
    saltando = False
    for ln in open(ruta, encoding="utf-8").read().split("\n"):
        s = ln.strip()
        if s == AUTORUN:
            break
        if s == SKIP_INI:
            saltando = True
            continue
        if s == SKIP_FIN:
            saltando = False
            continue
        if saltando or ln.startswith("from math import"):
            continue
        out.append(ln)
    if saltando:
        sys.exit("src/{}.py: falta '{}'".format(nombre, SKIP_FIN))
    return "\n".join(out).strip("\n") + "\n"


def nombres_top(src):
    """Nombres que la pieza define a nivel global (sin contar imports)."""
    ns = set()

    def visita(nodos):
        for n in nodos:
            if isinstance(n, (ast.FunctionDef, ast.ClassDef)):
                ns.add(n.name)
            elif isinstance(n, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
                blancos = n.targets if isinstance(n, ast.Assign) else [n.target]
                for t in blancos:
                    for x in ast.walk(t):
                        if isinstance(x, ast.Name):
                            ns.add(x.id)
            elif isinstance(n, ast.Try):
                visita(n.body)
                for h in n.handlers:
                    visita(h.body)
                visita(n.orelse)
                visita(n.finalbody)
            elif isinstance(n, (ast.If, ast.For, ast.While, ast.With)):
                visita(n.body)
                visita(getattr(n, "orelse", []))

    visita(ast.parse(src).body)
    return ns


def revisa_micropython(nombre, src):
    """Lo que truena en MicroPython 1.11 y CPython no avisa."""
    errores = []
    for n in ast.walk(ast.parse(src)):
        if isinstance(n, ast.JoinedStr):
            errores.append("{}: f-string en linea {}".format(nombre, n.lineno))
        if isinstance(n, ast.NamedExpr):
            errores.append("{}: := en linea {}".format(nombre, n.lineno))
    for i, ln in enumerate(src.split("\n")):
        if not ln.isascii() and not ln.lstrip().startswith("#"):
            errores.append("{}: no ASCII fuera de comentario, linea {}"
                           .format(nombre, i + 1))
    return errores


def junta(nombre, piezas, fn, desc):
    partes = [CABEZA.format(nombre=nombre, desc=desc,
                            piezas=", ".join(p + ".py" for p in piezas))]
    duenos = {}
    errores = []
    prohibidos = (set(dir(math)) | set(dir(builtins))) - {"__doc__", "__name__"}
    for p in piezas:
        src = procesa(p)
        errores += revisa_micropython(p, src)
        for n in sorted(nombres_top(src)):
            if n in duenos:
                errores.append("choque: '{}' en {} y en {}".format(
                    n, duenos[n], p))
            elif n in prohibidos:
                errores.append("{}: '{}' tapa un nombre de math/builtins"
                               .format(p, n))
            duenos[n] = p
        partes.append("\n\n# ===================== {} =====================\n\n"
                      .format(p))
        partes.append(src)
    if nombre == "general":
        if "general" in duenos:
            errores.append("choque: 'general' ya existe en " + duenos["general"])
        partes.append(MENU_GENERAL)
    partes.append(ARRANQUE.format(fn=fn))
    if errores:
        sys.exit("NO se genero {}.py:\n  ".format(nombre) + "\n  ".join(errores))
    todo = "".join(partes)
    compile(todo, nombre + ".py", "exec")
    return todo


def a_tns(py):
    tns = py[:-3] + ".tns"
    r = subprocess.run([LUNA, py, tns], stdout=subprocess.DEVNULL)
    if r.returncode != 0 or not os.path.exists(tns):
        if os.path.exists(tns):
            os.remove(tns)      # luna deja un .tns truncado si falla
        sys.exit("luna fallo con " + os.path.basename(py))
    with open(tns, "rb") as f:
        if f.read(10) != b"*TIMLP0500":
            sys.exit(os.path.basename(tns) + " no trae la cabecera de la Nspire")
    return os.path.getsize(tns)


def main():
    os.makedirs(SALIDA, exist_ok=True)
    hay_luna = os.path.exists(LUNA)
    for nombre, piezas, fn, desc in OBJETIVOS:
        todo = junta(nombre, piezas, fn, desc)
        py = os.path.join(SALIDA, nombre + ".py")
        with open(py, "w", encoding="utf-8") as f:
            f.write(todo)
        linea = "calculadora/{}.py: {} lineas, {:.0f} KB".format(
            nombre, todo.count("\n"), len(todo) / 1024)
        if hay_luna:
            linea += " | .tns {:.0f} KB".format(a_tns(py) / 1024)
        print(linea)
    if not hay_luna:
        print("sin Luna en .tools/: solo .py (pegalos en una pagina Python"
              " del Student Software)")


if __name__ == "__main__":
    main()
