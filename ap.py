# ap - menu interactivo para Calculo AP y fisica
# El unico comando que hay que aprenderse: ap()
# Suelto necesita calcpy y fisica (mismo documento o PyLib); dentro de
# estudio.py (el archivo unico) ya viene todo junto.

# --- bundle: skip ---
from math import *
from calcpy import *
from fisica import *

try:
    from formulas import formulario
except ImportError:
    formulario = None
# --- bundle: end skip ---

_ap_ns = {"sin": sin, "cos": cos, "tan": tan, "asin": asin, "acos": acos,
          "atan": atan, "sqrt": sqrt, "exp": exp, "log": log, "ln": log,
          "log10": log10, "pi": pi, "e": e, "abs": abs,
          "sen": sin, "__builtins__": {}}


def _ap_txt(prompt):
    """Texto tecleado listo para eval: sin espacios a los lados (el eval
    de MicroPython 1.11 truena con espacio inicial) y ^ como potencia."""
    return input(prompt).strip().replace("^", "**")


def _ap_f(prompt="f(x) = "):
    """Lee una funcion tecleada como texto. Acepta ^ como potencia."""
    s = _ap_txt(prompt)
    def g(x):
        return eval(s, _ap_ns, {"x": x, "t": x})
    try:
        g(1.0)  # truena aqui si esta mal tecleada
    except (ValueError, ZeroDivisionError, OverflowError):
        pass    # fuera de dominio en x=1, pero bien tecleada
    return g


def _ap_num(prompt, default=None):
    """Lee un numero. Acepta expresiones tipo pi/2. Enter = default."""
    s = _ap_txt(prompt)
    if s == "" and default is not None:
        return default
    return float(eval(s, _ap_ns, {}))


def _ap_intervalo():
    a = _ap_num("desde a = ")
    b = _ap_num("hasta b = ")
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
            _ap_corre(op)
        except Exception as err:
            print("error:", err)
        input("[enter]")


def _ap_corre(op):
    if op == "1":
        f = _ap_f()
        a, b = _ap_intervalo()
        analiza(f, a, b)
    elif op == "2":
        f = _ap_f()
        a, b = _ap_intervalo()
        (xM, yM), (xm, ym) = maxmin(f, a, b)
        print("mas alto: y={:.6g} en x={:.6g}".format(yM, xM))
        print("mas bajo: y={:.6g} en x={:.6g}".format(ym, xm))
        for x, y, t in extremos(f, a, b):
            print("  {} local en x={:.6g}".format(t, x))
    elif op == "3":
        f = _ap_f()
        x0 = _ap_num("en x = ")
        print("f'({:g})  = {:.6g}".format(x0, d(f, x0)))
        print("f''({:g}) = {:.6g}".format(x0, d2(f, x0)))
    elif op == "4":
        f = _ap_f()
        print("g(x)? (enter = solo integral de f)")
        s = _ap_txt("g(x) = ")
        a, b = _ap_intervalo()
        if s == "":
            print("integral = {:.6g}".format(integra(f, a, b)))
        else:
            g = lambda x: eval(s, _ap_ns, {"x": x, "t": x})
            print("area = {:.6g}".format(area_entre(f, g, a, b)))
    elif op == "5":
        f = _ap_f()
        a, b = _ap_intervalo()
        n = int(_ap_num("n subintervalos = "))
        for m in ("izq", "der", "medio", "trap"):
            print("{:>5}: {:.6g}".format(m, riemann(f, a, b, n, m)))
    elif op == "6":
        f = _ap_f()
        x0 = _ap_num("x tiende a = ")
        L = limite(f, x0)
        if L is None:
            print("izq: ", limite(f, x0, -1))
            print("der: ", limite(f, x0, 1))
            print("(no existe bilateral)")
        else:
            print("limite = {:.6g}".format(L))
    elif op == "7":
        print("y' = F(x,y). Teclea F:")
        s = _ap_txt("F(x,y) = ")
        F = lambda x, y: eval(s, _ap_ns, {"x": x, "y": y, "t": x})
        x0 = _ap_num("x0 = ")
        y0 = _ap_num("y0 = ")
        xf = _ap_num("hasta x = ")
        n = int(_ap_num("pasos n = "))
        euler(F, x0, y0, xf, n)
    elif op == "8":
        v = _ap_f("v(t) = ")
        a, b = _ap_intervalo()
        particula(v, a, b)
        t0 = _ap_num("rapidez en t = ", (a + b) / 2)
        print("la rapidez", rapidez(v, t0))
    elif op == "9":
        v0 = _ap_num("v0 hacia arriba (enter=se suelta) = ", 0)
        h0 = _ap_num("altura inicial (enter=0) = ", 0)
        tiro(v0, 90, h0)
        print("(v impacto = que tan rapido cae al llegar)")
    elif op == "10":
        v0 = _ap_num("v0 (m/s) = ")
        ang = _ap_num("angulo (grados) = ")
        h0 = _ap_num("altura inicial (enter=0) = ", 0)
        tiro(v0, ang, h0)
    elif op == "11":
        print("enter = no la sabes. x es desplazamiento")
        vals = {}
        for nombre in ("v0", "v", "a", "t", "x"):
            s = _ap_txt(nombre + " = ")
            vals[nombre] = float(eval(s, _ap_ns, {})) if s != "" else None
        mrua(vals["v0"], vals["v"], vals["a"], vals["t"], vals["x"])
    elif op == "12":
        if formulario:
            formulario()
        else:
            print("falta formulas.py (ponlo en PyLib)")
    else:
        print("no existe esa opcion")


# --- autorun ---
ap()
