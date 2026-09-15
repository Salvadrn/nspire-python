# ap - menu interactivo para Calculo AP y fisica
# El unico comando que hay que aprenderse: ap()
# Necesita calcpy y fisica (mismo documento o PyLib).

from math import *
import calcpy as c
import fisica as fis

try:
    import formulas
except ImportError:
    formulas = None

_NS = {"sin": sin, "cos": cos, "tan": tan, "asin": asin, "acos": acos,
       "atan": atan, "sqrt": sqrt, "exp": exp, "log": log, "ln": log,
       "log10": log10, "pi": pi, "e": e, "abs": abs,
       "sen": sin, "__builtins__": {}}


def _f(prompt="f(x) = "):
    """Lee una funcion tecleada como texto. Acepta ^ como potencia."""
    s = input(prompt).replace("^", "**")
    def g(x):
        return eval(s, _NS, {"x": x, "t": x})
    try:
        g(1.0)  # truena aqui si esta mal tecleada
    except (ValueError, ZeroDivisionError, OverflowError):
        pass    # fuera de dominio en x=1, pero bien tecleada
    return g


def _num(prompt, default=None):
    """Lee un numero. Acepta expresiones tipo pi/2. Enter = default."""
    s = input(prompt).replace("^", "**")
    if s == "" and default is not None:
        return default
    return float(eval(s, _NS, {}))


def _intervalo():
    a = _num("desde a = ")
    b = _num("hasta b = ")
    return a, b


def ap():
    while True:
        print("")
        print("== CALCULO ==")
        print("1 analiza f (raices,max,min)")
        print("2 punto mas alto / mas bajo")
        print("3 derivada en un punto")
        print("4 integral / area entre curvas")
        print("5 sumas de riemann")
        print("6 limite")
        print("7 metodo de euler")
        print("== FISICA ==")
        print("8 particula v(t)")
        print("9 sube / cae vertical")
        print("10 tiro parabolico")
        print("11 despeja mrua")
        print("== REPASO ==")
        print("12 formulario (formulas y tips)")
        print("0 salir")
        try:
            op = input("? ").strip()
            if op == "0" or op == "":
                return
            _corre(op)
        except Exception as err:
            print("error:", err)
        input("[enter]")


def _corre(op):
    if op == "1":
        f = _f()
        a, b = _intervalo()
        c.analiza(f, a, b)
    elif op == "2":
        f = _f()
        a, b = _intervalo()
        (xM, yM), (xm, ym) = c.maxmin(f, a, b)
        print("mas alto: y={:.6g} en x={:.6g}".format(yM, xM))
        print("mas bajo: y={:.6g} en x={:.6g}".format(ym, xm))
        for x, y, t in c.extremos(f, a, b):
            print("  {} local en x={:.6g}".format(t, x))
    elif op == "3":
        f = _f()
        x0 = _num("en x = ")
        print("f'({:g})  = {:.6g}".format(x0, c.d(f, x0)))
        print("f''({:g}) = {:.6g}".format(x0, c.d2(f, x0)))
    elif op == "4":
        f = _f()
        print("g(x)? (enter = solo integral de f)")
        s = input("g(x) = ").replace("^", "**")
        a, b = _intervalo()
        if s == "":
            print("integral = {:.6g}".format(c.integra(f, a, b)))
        else:
            g = lambda x: eval(s, _NS, {"x": x, "t": x})
            print("area = {:.6g}".format(c.area_entre(f, g, a, b)))
    elif op == "5":
        f = _f()
        a, b = _intervalo()
        n = int(_num("n subintervalos = "))
        for m in ("izq", "der", "medio", "trap"):
            print("{:>5}: {:.6g}".format(m, c.riemann(f, a, b, n, m)))
    elif op == "6":
        f = _f()
        x0 = _num("x tiende a = ")
        L = c.limite(f, x0)
        if L is None:
            print("izq: ", c.limite(f, x0, -1))
            print("der: ", c.limite(f, x0, 1))
            print("(no existe bilateral)")
        else:
            print("limite = {:.6g}".format(L))
    elif op == "7":
        print("y' = F(x,y). Teclea F:")
        s = input("F(x,y) = ").replace("^", "**")
        F = lambda x, y: eval(s, _NS, {"x": x, "y": y, "t": x})
        x0 = _num("x0 = ")
        y0 = _num("y0 = ")
        xf = _num("hasta x = ")
        n = int(_num("pasos n = "))
        c.euler(F, x0, y0, xf, n)
    elif op == "8":
        v = _f("v(t) = ")
        a, b = _intervalo()
        fis.particula(v, a, b)
        t0 = _num("rapidez en t = ", (a + b) / 2)
        print("la rapidez", fis.rapidez(v, t0))
    elif op == "9":
        v0 = _num("v0 hacia arriba (enter=se suelta) = ", 0)
        h0 = _num("altura inicial (enter=0) = ", 0)
        fis.tiro(v0, 90, h0)
        print("(v impacto = que tan rapido cae al llegar)")
    elif op == "10":
        v0 = _num("v0 (m/s) = ")
        ang = _num("angulo (grados) = ")
        h0 = _num("altura inicial (enter=0) = ", 0)
        fis.tiro(v0, ang, h0)
    elif op == "11":
        print("enter = no la sabes. x es desplazamiento")
        vals = {}
        for nombre in ("v0", "v", "a", "t", "x"):
            s = input(nombre + " = ").replace("^", "**")
            vals[nombre] = float(eval(s, _NS, {})) if s != "" else None
        fis.mrua(vals["v0"], vals["v"], vals["a"], vals["t"], vals["x"])
    elif op == "12":
        if formulas:
            formulas.formulario()
        else:
            print("falta formulas.py (ponlo en PyLib)")
    else:
        print("no existe esa opcion")


ap()
