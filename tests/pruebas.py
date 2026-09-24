# pruebas.py - bateria de calculadora/general.py (y de src/sat.py)
# Corre IGUAL en CPython y en MicroPython 1.11 (sin f-strings).
# Desde la raiz del repo (ver tests/correr.sh):
#   printf '0\n0\n' | python3 tests/pruebas.py
#   printf '0\n0\n' | .tools/micropython/ports/unix/micropython \
#                  -X heapsize=1M tests/pruebas.py
# Los '0' de stdin cierran los menus que general y sat abren al importarse.

import sys
sys.path.insert(0, "src")
import sat as S


class _Mod:
    pass


def _carga(ruta, nombre):
    """Carga con exec y no con import: general.py se saca solo de
    sys.modules al cerrar su menu (para volver a correrlo en la calc) y
    el import de CPython truena con KeyError si pasa eso."""
    ns = {"__name__": nombre}
    exec(open(ruta).read(), ns)
    m = _Mod()
    for k in ns:
        setattr(m, k, ns[k])
    return m, ns


E, E_NS = _carga("calculadora/general.py", "general")

_buf = []
_cola = []
_llamadas = [0]


def _input(p=""):
    _llamadas[0] += 1
    if _llamadas[0] > 600:
        raise KeyboardInterrupt("demasiados input(): ciclo infinito?")
    if p[:2] == "--" or p[:1] == "[":
        return ""                      # pausas de pantalla
    if not _cola:
        raise KeyboardInterrupt("faltan entradas en: " + p)
    return _cola.pop(0)


def _print(*a, **k):
    _buf.append(" ".join([str(x) for x in a]))


E_NS["input"] = _input
E_NS["print"] = _print
S.input = _input
S.print = _print

fallas = []
total = [0]


def caso(nombre, fn, entradas, esperados):
    total[0] += 1
    del _buf[:]
    del _cola[:]
    _cola.extend(entradas)
    _llamadas[0] = 0
    try:
        fn()
    except KeyboardInterrupt as err:
        fallas.append("{}: {}".format(nombre, err))
        return
    except Exception as err:
        fallas.append("{}: excepcion {}".format(nombre, err))
        return
    texto = "\n".join(_buf)
    for e in esperados:
        if e not in texto:
            fallas.append("{}: falta '{}'".format(nombre, e))
    if _cola:
        fallas.append("{}: sobraron entradas {}".format(nombre, _cola))


# ---------- SAT: solvers ----------

caso("recta", S._s_recta, ["1", "2", "3", "8"],
     ["m = 3", "b = y1 - m*x1 = -1", "y = 3x - 1",
      "corte eje x: x = 1/3 = 0.333333",
      "perpendicular: m = -1/3 = -0.333333",
      "distancia = 2*sqrt(10) = 6.32456", "punto medio = (2, 5)"])
caso("recta vertical", S._s_recta, ["2", "1", "2", "5"],
     ["recta vertical: x = 2", "distancia = 4", "punto medio = (2, 3)"])
caso("recta fracciones", S._s_recta, ["0", "1/2", "3", "5/2"],
     ["m = 2/3 = 0.666667", "y = (2/3)x + 1/2"])
caso("recta decimales", S._s_recta, ["0.5", "1", "2.5", "0"],
     ["m = -1/2 = -0.5", "y = (-1/2)x + 5/4"])

caso("sistema 1 sol", S._s_sistema, ["2", "3", "8", "1", "-1", "1"],
     ["x = 11/5 = 2.2", "y = 6/5 = 1.2", "x + y = 17/5 = 3.4"])
caso("sistema ninguna", S._s_sistema, ["1", "1", "1", "2", "2", "5"],
     ["NINGUNA"])
caso("sistema infinitas", S._s_sistema, ["1", "1", "1", "2", "2", "2"],
     ["INFINITAS"])

caso("cuad racional", S._s_cuad, ["1", "-5", "6"],
     ["D = b^2 - 4ac = 1", "x1 = 2", "x2 = 3",
      "vertice = (5/2, -1/4)", "MINIMO y = -1/4",
      "'factored': (x - 2)(x - 3)", "'vertex': (x - 5/2)^2 - 1/4"])
caso("cuad irracional", S._s_cuad, ["2", "-4", "-1"],
     ["D = b^2 - 4ac = 24", "x = (2 +- sqrt(6))/2",
      "x1 = -0.224745", "x2 = 2.22474", "vertice = (1, -3)",
      "'vertex': 2(x - 1)^2 - 3", "producto = c/a = -1/2 = -0.5"])
caso("cuad a negativa", S._s_cuad, ["-1", "2", "3"],
     ["x1 = 3", "x2 = -1", "vertice = (1, 4)", "MAXIMO y = 4",
      "'vertex': -(x - 1)^2 + 4", "'factored': -(x - 3)(x + 1)"])
caso("cuad sin reales", S._s_cuad, ["1", "0", "4"],
     ["D<0: 0 soluciones reales", "'vertex': x^2 + 4"])
caso("cuad raiz doble", S._s_cuad, ["1", "-6", "9"],
     ["D=0: 1 solucion real", "x = 3", "'factored': (x - 3)(x - 3)"])
caso("cuad a irracional neg", S._s_cuad, ["-2", "4", "1"],
     ["x = (2 +- sqrt(6))/2"])

caso("porc de", S._s_porc, ["1", "15", "80"], ["(p/100)*N = 12"])
caso("porc que %", S._s_porc, ["2", "12", "80"], ["(A/B)*100 = 15 %"])
caso("porc cambio", S._s_porc, ["3", "80", "100"], ["cambio = 25 %"])
caso("porc sucesivos", S._s_porc, ["4", "", "20 -20"],
     ["factor total = 24/25 = 0.96", "final = 96",
      "cambio total = -4 %"])
caso("porc original", S._s_porc, ["5", "96", "-20"], ["original = 120"])

caso("estad", S._s_estad, ["3 5 9 5 8"],
     ["n = 5   suma = 30", "media 'mean' = 6", "mediana 'median' = 5",
      "moda 'mode' = 5", "rango = 9 - 3 = 6",
      "desv.est. poblacion = 2.19089", "desv.est. muestra = 2.44949"])
caso("estad par", S._s_estad, ["1, 2, 3, 4"],
     ["mediana 'median' = 5/2 = 2.5", "no hay"])

caso("circulo general", S._s_circulo, ["1", "", "-6", "4", "-12"],
     ["centro (h,k) = (3, -2)", "r^2 = h^2 + k^2 - F = 25", "r = 5",
      "(x - 3)^2 + (y + 2)^2 = 25"])
caso("circulo coef 2", S._s_circulo, ["1", "2", "0", "0", "-10"],
     ["centro (h,k) = (0, 0)", "r = sqrt(5) = 2.23607",
      "x^2 + y^2 = 5"])
caso("arco y sector", S._s_circulo, ["2", "6", "60"],
     ["= 1/6 = 0.166667", "= 2*pi = 6.28319", "= 6*pi = 18.8496",
      "angulo en rad = (1/3)*pi = 1.0472"])

caso("expo", S._s_expo, ["100", "5", "10", "200"],
     ["y = a*b^t = 162.889", "se duplica cada 14.2067 periodos",
      "t = ln(meta/a)/ln(b) = 14.2067"])
caso("expo decae", S._s_expo, ["80", "-50", "3", ""],
     ["y = a*b^t = 10", "baja a la mitad cada 1 periodos"])

caso("triang 3-4-5", S._s_triang, ["3", "4", ""],
     ["c = 5", "angulo A (frente a a) = 36.8699", "sin A = a/c = 0.6"])
caso("triang 30-60-90", S._s_triang, ["1", "", "2"],
     ["b = sqrt(3) = 1.73205", "30-60-90"])
caso("triang 45-45-90", S._s_triang, ["1", "1", ""],
     ["c = sqrt(2) = 1.41421", "45-45-90"])

# ---------- Calculo AP (menu ap) ----------

caso("ap max", lambda: E._ap_corre("2"), ["-x^2+4*x", "0", "5"],
     ["mas alto: y=4 en x=2"])
caso("ap espacio inicial", lambda: E._ap_corre("3"), [" x^3 ", " 2"],
     ["f'(2)  = 12"])
caso("ap riemann", lambda: E._ap_corre("5"), ["x^2", "0", "1", "4"],
     [" trap: 0.34375", "  izq: 0.21875"])
caso("ap integral", lambda: E._ap_corre("4"), ["x^2", "", "0", "3"],
     ["integral = 9"])
caso("ap area", lambda: E._ap_corre("4"), ["x^2", "x", "0", "2"],
     ["area = 1"])
caso("ap particula", lambda: E._ap_corre("8"),
     ["t*t-4", "0", "3", "2", "1"],
     ["desplazamiento: -3", "distancia:      7.66667",
      "pos final:      -1", "la rapidez disminuye"])
caso("ap raiz doble", lambda: E._ap_corre("1"), ["x^2", "-1", "2"],
     ["raices: 0", "min: x=0  y=0", "abs min: y=0 en x=0"])
caso("ap raiz doble corrida", lambda: E._ap_corre("1"), ["(x-1)^2", "0", "3"],
     ["raices: 1", "abs min: y=0 en x=1"])
caso("ap asintota", lambda: E._ap_corre("1"), ["1/(x-1)", "0", "3"],
     ["raices: ninguna", "asintota en x=1", "no hay abs max: sube sin tope",
      "no hay abs min: baja sin tope"])
caso("ap tan", lambda: E._ap_corre("1"), ["tan(x)", "0", "3"],
     ["raices: 0", "asintota en x=1.5708"])
caso("ap sin raiz falsa", lambda: E._ap_corre("1"), ["x^2+1", "-2", "2"],
     ["raices: ninguna", "min: x=0  y=1"])
caso("ap salto no es raiz", lambda: E._ap_corre("1"), ["abs(x)/x", "-1", "2"],
     ["raices: ninguna"])
caso("ap 1/x^2 sin cambio de signo", lambda: E._ap_corre("2"),
     ["1/x^2", "-1", "2"], ["asintota en x=0", "no hay mas alto: sube sin tope",
                            "mas bajo: y=0.25 en x=2"])
caso("ap hueco no es asintota", lambda: E._ap_corre("1"),
     ["sin(x)/x", "-1", "1"], ["raices: ninguna", "abs max"])
caso("ap pico alto no es asintota", lambda: E._ap_corre("2"),
     ["1/(x^2+0.01)", "-1", "1"], ["mas alto: y=100 en x=0"])
caso("ap raiz empinada", lambda: E._ap_corre("1"),
     ["x^3-0.001", "-1", "1"], ["raices: 0.1"])

# ---------- AP: bateria de los revisores (2a ronda) ----------

_AP = [
    ("1", ["tan(x)", "0", "pi"], ["raices: 0, 3.14159", "asintota en x=1.5708"]),
    ("1", ["tan(x)", "0", "pi/2"], ["raices: 0", "asintota en x=1.5708",
                                   "no hay abs max: sube sin tope"]),
    ("1", ["1/(x^2-1)", "-2", "2"], ["asintota en x=-1, 1", "max: x=0  y=-1"]),
    ("1", ["x/(x^2-1)", "-2", "2"], ["raices: 0", "asintota en x=-1, 1", "inflex: 0"]),
    ("1", ["ln(x)", "0", "3"], ["raices: 1", "asintota en x=0",
                               "abs max: y=1.09861 en x=3",
                               "no hay abs min: baja sin tope"]),
    ("1", ["ln(abs(x))", "-2", "2"], ["raices: -1, 1", "asintota en x=0",
                                     "abs max: y=0.693147 en x=-2, 2"]),
    ("1", ["1/x", "0", "1"], ["asintota en x=0", "abs min: y=1 en x=1"]),
    ("1", ["exp(1/x)", "-1", "1"], ["raices: ninguna", "asintota en x=0",
                                   "inflex: -0.5", "no hay abs min: y->0"]),
    ("1", ["sqrt(4-x^2)", "-3", "3"], ["raices: -2, 2", "abs min: y=0 en x=-2, 2",
                                      "abs max: y=2 en x=0"]),
    ("1", ["sqrt(x)", "-1", "2"], ["raices: 0", "abs min: y=0 en x=0"]),
    ("1", ["sqrt(1-x)", "0", "2"], ["raices: 1", "abs min: y=0 en x=1"]),
    ("1", ["sin(x)", "-pi", "pi"], ["raices: -3.14159, 0, 3.14159", "inflex: 0"]),
    ("1", ["cos(x)", "-pi/2", "pi/2"], ["raices: -1.5708, 1.5708"]),
    ("1", ["(x-1)^5", "0", "2"], ["raices: 1", "ni max ni min: x=1  y=0"]),
    ("1", ["x^5-5*x^4+10*x^3-10*x^2+5*x-1", "0", "2"],
     ["raices: 1", "ni max ni min: x=1  y=0"]),
    ("1", ["2*x+1", "-2", "2"], ["raices: -0.5", "abs max: y=5 en x=2"]),
    ("1", ["abs(x)", "-1", "2"], ["raices: 0", "min: x=0  y=0"]),
    ("1", ["x^4", "-1", "1"], ["min: x=0  y=0", "abs max: y=1 en x=-1, 1"]),
    ("1", ["sin(x)*exp(-x)", "0", "25"],
     ["raices: 0, 3.14159, 6.28319, 9.42478, 12.5664, 15.708, 18.8496, 21.9911",
      "min: x=22.7765", "inflex: 1.5708, 4.71239, 7.85398, 10.9956"]),
    ("1", ["3", "0", "1"], ["raices: ninguna", "abs max: y=3 en x=0, 1"]),
    ("1", ["abs(x)/x", "-1", "1"], ["abs max: y=1 en x=1", "abs min: y=-1 en x=-1"]),
    ("1", ["1/(x-1)^2", "0", "3"], ["no hay abs max: sube sin tope",
                                   "abs min: y=0.25 en x=3"]),
    ("1", ["x^2+1e-10", "-1", "1"], ["raices: ninguna"]),
    ("1", ["1/(x^2+1e-10)", "-1", "1"], ["abs max: y=1e+10 en x=0"]),
    ("1", ["(x<1)*(x-2)+(x>=1)*(3-x)", "0", "3"], ["raices: 3", "max: x=1  y=2",
                                                  "abs max: y=2 en x=1"]),
    ("1", ["x^3-3*x", "-2", "2"], ["abs max: y=2 en x=-1, 2",
                                  "abs min: y=-2 en x=-2, 1"]),
    ("1", ["cos(x)", "0", "2*pi"], ["abs max: y=1 en x=0, 6.28319",
                                   "inflex: 1.5708, 4.71239"]),
    ("1", ["sin(x)/x", "-10", "10"], ["no hay abs max: y->1",
                                     "cuando x->0 (no se alcanza)"]),
    ("1", ["x^3", "-3", "3"], ["ni max ni min: x=0  y=0", "inflex: 0"]),
    ("1", ["x^(1/3)", "-1", "1"], ["raices: 0"]),
    ("6", ["(1-cos(x))/x^2", "0"], ["limite = 0.5"]),
    ("6", ["(sin(x)-x)/x^3", "0"], ["limite = -0.166667"]),
    ("6", ["(tan(x)-x)/x^3", "0"], ["limite = 0.333333"]),
    ("6", ["(exp(x)-1-x)/x^2", "0"], ["limite = 0.5"]),
    ("6", ["exp(1/x)", "0"], ["izq: 0", "der: +infinito"]),
    ("6", ["exp(1/x^2)", "0"], ["limite = +infinito"]),
    ("6", ["sqrt(x)", "0"], ["izq: no definida", "der: 0"]),
    ("6", ["log10(x)", "0"], ["der: -infinito"]),
    ("6", ["1/ln(x)", "0"], ["der: 0"]),
    ("6", ["x*ln(x)", "0"], ["der: 0"]),
    ("6", ["x*sin(1/x)", "0"], ["limite = 0"]),
    ("6", ["sin(1/x)", "0"], ["izq: no existe (oscila)"]),
    ("6", ["(1+x)^(1/x)", "0"], ["limite = 2.71828"]),
    ("6", ["(sqrt(x+4)-2)/x", "0"], ["limite = 0.25"]),
    ("6", ["(x^3-8)/(x-2)", "2"], ["limite = 12"]),
    ("6", ["tan(x)", "pi/2"], ["izq: +infinito", "der: -infinito"]),
]
for _op, _ent, _esp in _AP:
    caso("ap " + _op + " " + _ent[0], (lambda o: lambda: E._ap_corre(o))(_op),
         _ent, _esp)


# ---------- AP: bateria de la 3a ronda ----------

_AP3 = [
    ("2", ["1/cos(x)", "-pi/2", "pi/2"], ["no hay mas alto: sube sin tope",
                                         "mas bajo: y=1 en x=0"]),
    ("1", ["tan(x)", "0", "pi/2"], ["abs min: y=0 en x=0"]),
    ("2", ["1/(x-pi)", "pi", "4"], ["mas bajo: y=1.16495 en x=4"]),
    ("2", ["1/(x-sqrt(2))", "0", "sqrt(2)"], ["mas alto: y=-0.707107 en x=0"]),
    ("1", ["8/(x^2+4)", "-5", "5"], ["inflex: -1.1547, 1.1547"]),
    ("1", ["1/(1+exp(-x))", "-6", "5"], ["inflex: 0"]),
    ("1", ["abs(sin(x))", "-1", "7"], ["raices: 0, 3.14159, 6.28319"]),
    ("1", ["abs(x^2-4)", "-3", "3"], ["raices: -2, 2", "min: x=-2  y=0",
                                     "inflex: -2, 2"]),
    ("1", ["abs(x^2-3)", "-2.5", "2.5"], ["raices: -1.73205, 1.73205"]),
    ("1", ["sqrt(abs(x-1))", "-2", "3.5"], ["raices: 1", "abs min: y=0 en x=1"]),
    ("1", ["abs(x-1)+abs(x+1)", "-3", "3"], ["abs min: y=2 en x=-1, 1",
                                            "abs max: y=6 en x=-3, 3"]),
    ("1", ["(x+abs(x))/2", "-2", "2"], ["f = 0 en todo [-2, 0]"]),
    ("1", ["(x-1)^3/(x-1)", "0", "3"], ["raices: ninguna",
                                       "cuando x->1 (no se alcanza)"]),
    ("1", ["(x^2-2*x+1)/(x-1)", "0", "3"], ["raices: ninguna"]),
    ("1", ["(x-1)/(x^2-1)", "1", "3"], ["no hay abs max: y->0.5"]),
    ("1", ["x+1/x", "-100", "100"], ["max: x=-1  y=-2", "min: x=1  y=2"]),
    ("2", ["x^2/(x-1)", "-100", "100"], ["max local en x=0", "min local en x=2"]),
    ("6", ["1/(x-1)-2/(x^2-1)", "1"], ["limite = 0.5"]),
    ("6", ["1/(x^2-x)-1/(x-1)", "1"], ["limite = -1"]),
    ("6", ["1/(x-3)-6/(x^2-9)", "3"], ["limite = 0.166667"]),
    ("6", ["(1-cos(x))/x", "0"], ["limite = 0"]),
    ("1", ["x^2-x/2", "-100", "100"], ["raices: 0, 0.5"]),
    ("1", ["x^3-x/4", "-100", "100"], ["raices: -0.5, 0, 0.5"]),
    ("1", ["x^4-4*x^3+2", "-100", "100"], ["inflex: 0, 2", "min: x=3  y=-25"]),
    ("1", ["x^3-3*x", "-1000", "1000"], ["raices: -1.73205, 0, 1.73205",
                                        "max: x=-1  y=2", "inflex: 0"]),
    ("1", ["exp(1/x)", "-2", "2"], ["raices: ninguna"]),
    ("1", ["x^3", "-0.0005", "0.0005"], ["abs max: y=1.25e-10 en x=0.0005"]),
    ("1", ["x^2*exp(-x^2)", "-6", "6"], ["abs min: y=0 en x=0"]),
    ("6", ["1/x^2", "1000"], ["limite = 1e-06"]),
    ("6", ["exp(-x)", "15"], ["limite = 3.05902e-07"]),
    ("1", ["x^3", "-1.3", "2"], ["ni max ni min: x=0  y=0"]),
    ("1", ["sin(x)^3", "-1", "7"], ["raices: 0, 3.14159, 6.28319",
                                   "ni max ni min: x=6.28319"]),
    ("1", ["(x-1)^3+2", "-1.3", "3"], ["ni max ni min: x=1  y=2", "inflex: 1"]),
    ("1", ["x^5-5*x^4", "-2", "5"], ["raices: 0, 5", "max: x=0  y=0"]),
    ("1", ["x-sin(x)", "-4", "5"], ["raices: 0", "ni max ni min: x=0  y=0"]),
    ("2", ["x^(2/3)", "-8", "1"], ["f no existe en [-8", "ojo: x^(p/q) con x<0"]),
]
for _op, _ent, _esp in _AP3:
    caso("ap3 " + _op + " " + _ent[0], (lambda o: lambda: E._ap_corre(o))(_op),
         _ent, _esp)

caso("ap max con asintota", lambda: E._ap_corre("2"), ["1/(x-1)", "0", "3"],
     ["asintota en x=1", "no hay mas alto"])
caso("ap lim 1/x^2", lambda: E._ap_corre("6"), ["1/x^2", "0"],
     ["limite = +infinito"])
caso("ap lim 1/x", lambda: E._ap_corre("6"), ["1/x", "0"],
     ["izq: -infinito", "der: +infinito", "(no existe bilateral)"])
caso("ap lim sin(x)/x", lambda: E._ap_corre("6"), ["sin(x)/x", "0"],
     ["limite = 1"])
caso("ap lim salto", lambda: E._ap_corre("6"), ["abs(x)/x", "0"],
     ["izq: -1", "der: 1"])
caso("ap lim (x^2-1)/(x-1)", lambda: E._ap_corre("6"), ["(x^2-1)/(x-1)", "1"],
     ["limite = 2"])

# ---------- hojas: formulario AP y SAT completas ----------


def _hojas_ap():
    n = 0
    for t in E.TEMAS:
        E._fo_muestra(t)
        n += len(t[1])
    _buf.append("renglones={}".format(n))


def _hojas_sat():
    n = 0
    for t in S.SAT_TEMAS:
        S._s_muestra(t)
        n += len(t[1])
    _buf.append("renglones={}".format(n))


caso("hojas AP", _hojas_ap, [], ["renglones=431"])
caso("hojas SAT", _hojas_sat, [], ["renglones=402"])

# ---------- IA: el examen de Adrian de punta a punta ----------

_ia_menu = [0]
_ia_si = [0]


def _input_ia(p=""):
    _llamadas[0] += 1
    if _llamadas[0] > 600:
        raise KeyboardInterrupt("demasiados input() en ia")
    if p[:8] == "enter=si":
        # ("Igual a tu examen? enter=si..." son confirmaciones: enter)
        # como el examen real: 2a actualizacion si; J3 no; estimar no
        _ia_si[0] += 1
        return "" if _ia_si[0] == 1 else "n"
    if "x (ej" in p:
        return "1,2,3,4"
    if "y (ej" in p:
        return "35,50,68,87"
    if "theta0" in p:
        return "5"
    if "theta1" in p:
        return "8"
    if "alfa" in p:
        return "0.02"
    if "Escribe el numero" in p:
        _ia_menu[0] += 1
        return "1" if _ia_menu[0] == 1 else "0"
    return ""                          # enter = si / igual / seguir


def _examen_ia():
    E_NS["input"] = _input_ia
    try:
        E.ia()
    finally:
        E_NS["input"] = _input


caso("ia examen", _examen_ia, [],
     ["668.25", "-35", "-99.25", "5.7", "9.985", "465.23334375",
      "theta0 final = 6.28675", "theta1 final = 11.63725",
      "J disminuyo"])



def _prueba_nval(t):
    try:
        return str(E.nval(t))
    except ValueError:
        return "mal"

# ---------- FISICA: problema del malabarista (FF_CA1.pdf) ----------

caso("fisica vertical", E.vertical,
     ["7", "1", "1.2", "2", "0.4", "3", "-1.5", "4", "1.5", "0"],
     ["h max = 2.497 m", "t subida = 0.714 s", "t vuelo = 1.427 s",
      "ojo: si redondeas tsub a 0.71 antes: 1.42 s",
      "regresa con 7 m/s hacia abajo",
      "y = 1.337 m", "v = -4.772 m/s", "va BAJANDO",
      "subiendo: v = +2.801 m/s  (t = 0.428 s)",
      "v^2=v0^2-2gy = 7^2-19.62(-1.5) = 78.43",
      "bajando:  v = -8.856 m/s  (t = 1.616 s)",
      "t total = 1.616 s", "v al llegar = -8.856 m/s"])
caso("fisica vertical cima", E.vertical, ["7", "3", "2.497451580020387", "0"],
     ["es la cima: v = 0"])
caso("fisica vertical no llega", E.vertical, ["7", "3", "3", "0"],
     ["NO llega a esa altura"])
caso("fisica vertical v0 malo", E.vertical, ["-3"], ["v0 debe ser > 0"])
caso("fisica cima mostrada", E.vertical, ["10", "3", "5.097", "0"],
     ["h max = 5.097 m", "es la cima: v = 0 en t = 1.019 s"])
caso("fisica cima exacta", E.vertical, ["29.43", "3", "44.145", "0"],
     ["es la cima: v = 0 en t = 3.0 s"])
caso("fisica t en la cima", E.vertical, ["7", "1", "0.714", "0"],
     ["esta en la CIMA"])
caso("fisica t negativo", E.vertical, ["7", "1", "-1", "1.2", "0"],
     ["t debe ser >= 0", "y = 1.337 m"])
caso("fisica dato completo", E.vertical, ["7", "1", "0.7135", "0"],
     ["(t = t subida exacto = 0.71355759)", "v=v0-gt = 7-9.81(0.71355759) = 0.0",
      "esta en la CIMA"])
caso("fisica d > hmax", E.vertical, ["7", "2", "3", "0"],
     ["ojo: d > hmax", "bajando:  v = -7.672 m/s"])
caso("fisica d = 0", E.vertical, ["7", "2", "0", "0"],
     ["d = 0: es la cima"])
caso("fisica opcion mala", E.vertical, ["7", "5", "1 ", "1.2", "0"],
     ["opcion no valida", "y = 1.337 m"])
caso("fisica ojo sin colas", E.vertical, ["2.3", "0"],
     ["ojo: si redondeas tsub a 0.23 antes: 0.46 s"])
caso("fisica piso suma", E.vertical, ["1", "4", "10", "0"],
     ["t total = 1.533 s", "= 0.204 s de vuelo + 1.329 s de mas"])
caso("fisica piso h=0", E.vertical, ["7", "4", "0", "0"],
     ["la otra raiz es t=0"])
caso("fisica t vuelo mostrado", E.vertical, ["10", "1", "2.039", "0"],
     ["de vuelta al nivel de salida", "v = -10 m/s"])
caso("fisica d = hmax", E.vertical, ["0.5", "2", "0.013", "0"],
     ["subiendo: v = +0.5 m/s  (t = 0.0 s)"])
caso("fisica paso opcion 2 cuadra", E.vertical, ["10", "2", "2", "0"],
     ["t=tsub -+ v/g = 1.019368 -+ 6.2641839/9.81"])
caso("fisica nval sin mantisa", lambda: _buf.append(
         " ".join([_prueba_nval(t) for t in ("e2", "x10^2", ".", "-e5", "2e3")])),
     [], ["mal mal mal mal 2000.0"])
caso("fisica r2 medio arriba", lambda: _buf.append(
         E.r2(0.5095) + " " + E.r2(0.0025) + " " + E.r2(-7.3385)),
     [], ["0.51 0.003 -7.339"])
caso("fisica rp negativo", E.caida, ["-8", "", "", "30"],
     ["raiz((-8.0)^2+19.62(30.0))", "vf  = 25.546 m/s"])
caso("fisica resultado = procedimiento", E.derrape, ["1", "0.25", "25"],
     ["(0.25)(9.81) = 2.453", "a = 2.453 m/s2"])
caso("fisica nan", lambda: _buf.append(_prueba_nval("nan") + " " + _prueba_nval("inf")),
     [], ["mal mal"])
caso("fisica t vuelo exacto", E.vertical, ["100", "1", "20.387", "0"],
     ["(t = t vuelo exacto = 20.38736)", "de vuelta al nivel de salida"])
caso("fisica derrape mu=0", E.fisica, ["6", "2", "20", "0", "", "0"],
     ["Error con esos datos", "Saliste de FISICA"])
caso("fisica graficas 0 puntos", E.fisica, ["3", "2", "0", "", "0"],
     ["Error con esos datos", "Saliste de FISICA"])
caso("fisica nval **", lambda: _buf.append(
         str(E.nval("3*10**-1")) + " " + str(E.nval("10**3"))
         + " " + str(E.nval("-10^2")) + " " + str(E.nval("2x10^3"))),
     [], ["0.3 1000.0 -100.0 2000.0"])
caso("fisica mrua", E.mrua, ["0", "", "", "0", "", "2", "3", ""],
     ["vf = 6.0 m/s", "x  = 9.0 m"])
caso("fisica r2", lambda: _buf.append(
         E.r2(78.43000000000001) + " " + E.r2(7) + " " + E.r2(1.3368)
         + " " + E.r2(-0.0004) + " " + E.r2(2970024100.046)
         + " " + E.r2(123456789012.345) + " " + E.r2(1e20)),
     [], ["78.43 7.0 1.337 0.0 2970024100.046 123456789012.345 1e+20"])

# ---------- resultado ----------

if fallas:
    for f in fallas:
        print("FALLA " + f)
    print("{} de {} casos con falla".format(len(fallas), total[0]))
else:
    print("TODO OK: {} casos".format(total[0]))
