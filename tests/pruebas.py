# pruebas.py - bateria del archivo unico estudio.py
# Corre IGUAL en CPython y en MicroPython 1.11 (sin f-strings).
# Desde la raiz del repo (ver tests/correr.sh):
#   printf '0\n' | python3 tests/pruebas.py
#   printf '0\n' | .tools/micropython/ports/unix/micropython \
#                  -X heapsize=1M tests/pruebas.py
# El '0' de stdin cierra el menu que estudio.py abre al importarse.

import sys
sys.path.insert(0, "")
import estudio as E

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


E.input = _input
E.print = _print

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

caso("recta", E._s_recta, ["1", "2", "3", "8"],
     ["m = 3", "b = y1 - m*x1 = -1", "y = 3x - 1",
      "corte eje x: x = 1/3 = 0.333333",
      "perpendicular: m = -1/3 = -0.333333",
      "distancia = 2*sqrt(10) = 6.32456", "punto medio = (2, 5)"])
caso("recta vertical", E._s_recta, ["2", "1", "2", "5"],
     ["recta vertical: x = 2", "distancia = 4", "punto medio = (2, 3)"])
caso("recta fracciones", E._s_recta, ["0", "1/2", "3", "5/2"],
     ["m = 2/3 = 0.666667", "y = (2/3)x + 1/2"])
caso("recta decimales", E._s_recta, ["0.5", "1", "2.5", "0"],
     ["m = -1/2 = -0.5", "y = (-1/2)x + 5/4"])

caso("sistema 1 sol", E._s_sistema, ["2", "3", "8", "1", "-1", "1"],
     ["x = 11/5 = 2.2", "y = 6/5 = 1.2", "x + y = 17/5 = 3.4"])
caso("sistema ninguna", E._s_sistema, ["1", "1", "1", "2", "2", "5"],
     ["NINGUNA"])
caso("sistema infinitas", E._s_sistema, ["1", "1", "1", "2", "2", "2"],
     ["INFINITAS"])

caso("cuad racional", E._s_cuad, ["1", "-5", "6"],
     ["D = b^2 - 4ac = 1", "x1 = 2", "x2 = 3",
      "vertice = (5/2, -1/4)", "MINIMO y = -1/4",
      "'factored': (x - 2)(x - 3)", "'vertex': (x - 5/2)^2 - 1/4"])
caso("cuad irracional", E._s_cuad, ["2", "-4", "-1"],
     ["D = b^2 - 4ac = 24", "x = (2 +- sqrt(6))/2",
      "x1 = -0.224745", "x2 = 2.22474", "vertice = (1, -3)",
      "'vertex': 2(x - 1)^2 - 3", "producto = c/a = -1/2 = -0.5"])
caso("cuad a negativa", E._s_cuad, ["-1", "2", "3"],
     ["x1 = 3", "x2 = -1", "vertice = (1, 4)", "MAXIMO y = 4",
      "'vertex': -(x - 1)^2 + 4", "'factored': -(x - 3)(x + 1)"])
caso("cuad sin reales", E._s_cuad, ["1", "0", "4"],
     ["D<0: 0 soluciones reales", "'vertex': x^2 + 4"])
caso("cuad raiz doble", E._s_cuad, ["1", "-6", "9"],
     ["D=0: 1 solucion real", "x = 3", "'factored': (x - 3)(x - 3)"])
caso("cuad a irracional neg", E._s_cuad, ["-2", "4", "1"],
     ["x = (2 +- sqrt(6))/2"])

caso("porc de", E._s_porc, ["1", "15", "80"], ["(p/100)*N = 12"])
caso("porc que %", E._s_porc, ["2", "12", "80"], ["(A/B)*100 = 15 %"])
caso("porc cambio", E._s_porc, ["3", "80", "100"], ["cambio = 25 %"])
caso("porc sucesivos", E._s_porc, ["4", "", "20 -20"],
     ["factor total = 24/25 = 0.96", "final = 96",
      "cambio total = -4 %"])
caso("porc original", E._s_porc, ["5", "96", "-20"], ["original = 120"])

caso("estad", E._s_estad, ["3 5 9 5 8"],
     ["n = 5   suma = 30", "media 'mean' = 6", "mediana 'median' = 5",
      "moda 'mode' = 5", "rango = 9 - 3 = 6",
      "desv.est. poblacion = 2.19089", "desv.est. muestra = 2.44949"])
caso("estad par", E._s_estad, ["1, 2, 3, 4"],
     ["mediana 'median' = 5/2 = 2.5", "no hay"])

caso("circulo general", E._s_circulo, ["1", "", "-6", "4", "-12"],
     ["centro (h,k) = (3, -2)", "r^2 = h^2 + k^2 - F = 25", "r = 5",
      "(x - 3)^2 + (y + 2)^2 = 25"])
caso("circulo coef 2", E._s_circulo, ["1", "2", "0", "0", "-10"],
     ["centro (h,k) = (0, 0)", "r = sqrt(5) = 2.23607",
      "x^2 + y^2 = 5"])
caso("arco y sector", E._s_circulo, ["2", "6", "60"],
     ["= 1/6 = 0.166667", "= 2*pi = 6.28319", "= 6*pi = 18.8496",
      "angulo en rad = (1/3)*pi = 1.0472"])

caso("expo", E._s_expo, ["100", "5", "10", "200"],
     ["y = a*b^t = 162.889", "se duplica cada 14.2067 periodos",
      "t = ln(meta/a)/ln(b) = 14.2067"])
caso("expo decae", E._s_expo, ["80", "-50", "3", ""],
     ["y = a*b^t = 10", "baja a la mitad cada 1 periodos"])

caso("triang 3-4-5", E._s_triang, ["3", "4", ""],
     ["c = 5", "angulo A (frente a a) = 36.8699", "sin A = a/c = 0.6"])
caso("triang 30-60-90", E._s_triang, ["1", "", "2"],
     ["b = sqrt(3) = 1.73205", "30-60-90"])
caso("triang 45-45-90", E._s_triang, ["1", "1", ""],
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
caso("ap vertical", lambda: E._ap_corre("9"), ["20", ""],
     ["h max:     20.39"])
caso("ap mrua", lambda: E._ap_corre("11"), ["0", "", "-9.81", "1", ""],
     ["v = -9.81", "x = -4.905"])

# ---------- hojas: formulario AP y SAT completas ----------


def _todas_las_hojas():
    n = 0
    for t in E.TEMAS:
        E._fo_muestra(t)
        n += len(t[1])
    for t in E.SAT_TEMAS:
        E._s_muestra(t)
        n += len(t[1])
    _buf.append("renglones={}".format(n))


caso("hojas", _todas_las_hojas, [], ["renglones=833"])

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
    E.input = _input_ia
    try:
        E.ia()
    finally:
        E.input = _input


caso("ia examen", _examen_ia, [],
     ["668.25", "-35", "-99.25", "5.7", "9.985", "465.23334375",
      "theta0 final = 6.28675", "theta1 final = 11.63725",
      "J disminuyo"])

# ---------- resultado ----------

if fallas:
    for f in fallas:
        print("FALLA " + f)
    print("{} de {} casos con falla".format(len(fallas), total[0]))
else:
    print("TODO OK: {} casos".format(total[0]))
