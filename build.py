#!/usr/bin/env python3
"""build.py - genera estudio.py: UN solo archivo con Calculo AP + IA + SAT.

Uso:  python3 build.py

Junta calcpy, fisica, formulas, ap, ia y sat en un programa autocontenido
(se pega UNA vez en la calculadora) y, si Luna esta compilado en
.tools/Luna, genera tambien estudio.tns listo para arrastrar a la Nspire.

Cada modulo marca lo que NO entra al archivo unico:
    # --- bundle: skip ---  ...  # --- bundle: end skip ---   (imports)
    # --- autorun ---        (de aqui al final: el arranque del modulo)
"""
import ast
import builtins
import math
import os
import subprocess
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
ORDEN = ["calcpy", "fisica", "formulas", "ap", "ia", "sat"]
SKIP_INI = "# --- bundle: skip ---"
SKIP_FIN = "# --- bundle: end skip ---"
AUTORUN = "# --- autorun ---"
LUNA = os.path.join(AQUI, ".tools", "Luna", "luna")

CABEZA = '''\
# estudio - UN solo archivo: Calculo AP + IA + SAT Math
# Para la TI-Nspire CX II CAS de Adrian (MicroPython 1.11).
# GENERADO por build.py desde calcpy, fisica, formulas, ap, ia y sat:
# no lo edites a mano; edita el modulo y corre  python3 build.py
# Corre el programa y sale el menu. Para abrirlo otra vez: estudio()

from math import *
'''

MENU = '''

# ===================== menu principal =====================

def estudio():
    try:
        while True:
            print("")
            print("== ESTUDIO ==")
            print("1 Calculo AP: herramientas")
            print("2 Calculo AP: formulas y tips")
            print("3 IA: regresion lineal")
            print("4 SAT Math (para estudiar)")
            print("0 salir")
            op = input("? ").strip()
            if op == "0":
                break
            try:
                if op == "1":
                    ap()
                elif op == "2":
                    formulario()
                elif op == "3":
                    ia()
                elif op == "4":
                    sat()
                else:
                    print("escribe un numero del 0 al 4")
            except Exception as err:
                print("Algo fallo: " + str(err))
    except KeyboardInterrupt:
        pass
    print("Para abrir otra vez: estudio()")


estudio()
'''


def procesa(nombre):
    ruta = os.path.join(AQUI, nombre + ".py")
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
        sys.exit("{}.py: falta '{}'".format(nombre, SKIP_FIN))
    return "\n".join(out).strip("\n") + "\n"


def nombres_top(src):
    """Nombres que el modulo define a nivel global."""
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
            elif isinstance(n, (ast.Import, ast.ImportFrom)):
                for a in n.names:
                    ns.add((a.asname or a.name).split(".")[0])
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
    if not src.isascii():
        malos = sorted(set(c for c in src if ord(c) > 127))
        errores.append("{}: caracteres no ASCII {}".format(nombre, malos))
    for n in ast.walk(ast.parse(src)):
        if isinstance(n, ast.JoinedStr):
            errores.append("{}: f-string en linea {}".format(nombre, n.lineno))
        if isinstance(n, ast.NamedExpr):
            errores.append("{}: := en linea {}".format(nombre, n.lineno))
    return errores


def main():
    partes = [CABEZA]
    duenos = {}
    errores = []
    prohibidos = (set(dir(math)) | set(dir(builtins))) - {"__doc__", "__name__"}
    for nombre in ORDEN:
        src = procesa(nombre)
        errores += revisa_micropython(nombre, src)
        for n in sorted(nombres_top(src)):
            if n in duenos:
                errores.append("choque: '{}' en {} y en {}".format(
                    n, duenos[n], nombre))
            elif n in prohibidos:
                errores.append("{}: '{}' tapa un nombre de math/builtins"
                               .format(nombre, n))
            duenos[n] = nombre
        partes.append("\n\n# ===================== {} =====================\n\n"
                      .format(nombre))
        partes.append(src)
    for n in ("estudio",):
        if n in duenos:
            errores.append("choque: '{}' ya existe en {}".format(n, duenos[n]))
    if errores:
        sys.exit("NO se genero estudio.py:\n  " + "\n  ".join(errores))

    partes.append(MENU)
    todo = "".join(partes)
    compile(todo, "estudio.py", "exec")
    salida = os.path.join(AQUI, "estudio.py")
    with open(salida, "w", encoding="utf-8") as f:
        f.write(todo)
    print("estudio.py: {} lineas, {:.0f} KB, {} nombres globales sin choques"
          .format(todo.count("\n"), len(todo) / 1024, len(duenos)))

    tns = os.path.join(AQUI, "estudio.tns")
    if os.path.exists(LUNA):
        r = subprocess.run([LUNA, salida, tns])
        if r.returncode != 0 or not os.path.exists(tns):
            if os.path.exists(tns):
                os.remove(tns)      # luna deja un .tns truncado si falla
            sys.exit("luna fallo: no se genero estudio.tns")
        with open(tns, "rb") as f:
            magia = f.read(10)
        if magia != b"*TIMLP0500":
            sys.exit("estudio.tns no trae la cabecera de la Nspire")
        print("estudio.tns: {:.0f} KB (arrastralo a la calculadora)"
              .format(os.path.getsize(tns) / 1024))
    else:
        print("sin Luna en .tools/: solo estudio.py (pegalo en una pagina"
              " Python del Student Software)")


if __name__ == "__main__":
    main()
