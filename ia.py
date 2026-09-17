# ia - regresion lineal con gradiente descendente (IA PrepaTEC)
# Adrian. Corre el programa `ia` y sale el menu: te pregunta los datos
# y saca el procedimiento como se escribe en el examen.
#
# Convenciones del curso (no cambiarlas o no cuadra el solucionario):
#   yh = theta0 + theta1*x          e = yh - y
#   J = sum(e^2) / (2m)
#   dJ/dtheta0 = sum(e)/m           dJ/dtheta1 = sum(e*x)/m
#   theta := theta - alfa*dJ/dtheta (los DOS con los theta viejos)
#   aprobado si y >= 70
#
# Cuentas EXACTAS con fracciones de enteros largos: nada se redondea
# ni se mete ruido binario. En pantalla salen hasta 12 cifras; si hay
# mas, se corta y termina en '...'. Con mas de 5 iteraciones usa los
# decimales de la calc (exacto seria lentisimo) y solo muestra J.
# Todo ASCII, sin f-strings ni operadores sobrecargados: el Python de
# la Nspire es MicroPython 1.11.

_ANCHO = 36    # caracteres por renglon (aprox.) en el shell
_ALTO = 10     # renglones por pantalla antes de pedir enter
_CIFRAS = 12   # cifras significativas en pantalla
_SIGUE = "-- enter para seguir --"

_D = {}        # ultimos datos tecleados: enter = reusarlos
_lin = 0       # renglones impresos desde la ultima pausa


# ---------- fracciones exactas: (p, q) = p/q, q > 0 ----------

def _mcd(a, b):
    while b:
        a, b = b, a % b
    return a


def _q(p, q=1):
    if q == 0:
        raise ZeroDivisionError("division entre 0")
    if q < 0:
        p, q = -p, -q
    g = _mcd(abs(p), q)
    return (p // g, q // g)


def _mas(a, b):
    return _q(a[0] * b[1] + b[0] * a[1], a[1] * b[1])


def _menos(a, b):
    return _q(a[0] * b[1] - b[0] * a[1], a[1] * b[1])


def _por(a, b):
    return _q(a[0] * b[0], a[1] * b[1])


def _entre(a, b):
    return _q(a[0] * b[1], a[1] * b[0])


def _f(a):
    """Fraccion -> decimal de la calc."""
    if isinstance(a, tuple):
        return a[0] / a[1]
    return float(a)


def _cmp(a, b):
    """-1, 0 o 1 segun a < b, a == b, a > b."""
    if isinstance(a, tuple) and isinstance(b, tuple):
        d = a[0] * b[1] - b[0] * a[1]
    else:
        d = _f(a) - _f(b)
        if d != d:
            return 1      # nan: se desbordo, diverge
    return (d > 0) - (d < 0)


def _dec(t):
    """'-1.25', '3', '.5', '2e-3' -> fraccion exacta."""
    t = t.strip().lower()
    ex = 0
    if "e" in t:
        t, e = t.split("e")
        ex = int(e)
    neg = t.startswith("-")
    t = t.lstrip("+-")
    if "." in t:
        ent, frac = t.split(".")
    else:
        ent, frac = t, ""
    if ent + frac == "" or not (ent + frac).isdigit():
        raise ValueError("no es numero: " + t)
    p = int(ent + frac)
    q = 10 ** len(frac)
    if ex > 0:
        p *= 10 ** ex
    else:
        q *= 10 ** (-ex)
    return _q(-p if neg else p, q)


def _lee(t):
    """Numero tecleado: 0.02, -3, 1/50 exactos; otra cosa (2^3) via eval."""
    try:
        if "/" in t:
            a, b = t.split("/")
            return _entre(_dec(a), _dec(b))
        return _dec(t)
    except ValueError:
        return _a(eval(t.replace("^", "**"), {"__builtins__": {}}, {}))


def _a(v):
    """int, float, texto o fraccion -> fraccion exacta."""
    if isinstance(v, tuple):
        return v
    if isinstance(v, int):
        return (v, 1)
    if isinstance(v, str):
        return _lee(v)
    return _dec("{:.15g}".format(v))


# ---------- pantalla ----------

def _n(a):
    """Como en papel y exacto: 9.985, -99.25, 13. Mas de 12 cifras: '...'."""
    if not isinstance(a, tuple):
        return _nf(a)
    p, q = a
    if p == 0:
        return "0"
    s = "-" if p < 0 else ""
    p = abs(p)
    ent, r = p // q, p % q
    s += str(ent)
    cifras = len(str(ent)) if ent else 0
    if r and cifras < _CIFRAS:
        s += "."
        while r and cifras < _CIFRAS:
            r *= 10
            d = r // q
            r = r % q
            s += str(d)
            if cifras or d:          # los ceros de 0.00x no cuentan
                cifras += 1
    if r:
        s += "..."
    return s


def _nf(v):
    """Decimal de la calc (modo rapido): 10 cifras, sin .0."""
    s = "{:.10g}".format(v)
    if "." in s and "e" not in s:
        s = s.rstrip("0").rstrip(".")
    return s


def _p(a):
    return "(" + _n(a) + ")"


def _junta(txt, b, op="+"):
    """txt + b o txt - b como en papel: '13 - 35', no '13 + -35'."""
    if op == "-":
        b = (-b[0], b[1])
    if b[0] < 0:
        return txt + " - " + _n((-b[0], b[1]))
    return txt + " + " + _n(b)


def _suma_txt(vals):
    """[-22, -29, -39] -> '-22 - 29 - 39'."""
    s = _n(vals[0])
    for v in vals[1:]:
        s = _junta(s, v)
    return s


def _alto(s):
    return 1 + max(0, len(s) - 1) // _ANCHO


def _out(*lineas):
    """Imprime renglones que van juntos; si no caben, pide enter antes."""
    global _lin
    alto = 0
    for s in lineas:
        alto += _alto(s)
    if _lin + alto > _ALTO:
        _pausa()
    for s in lineas:
        print(s)
    _lin += alto


def _pausa():
    global _lin
    if _lin > 0:
        input(_SIGUE)
    _lin = 0


def _nueva():
    global _lin
    _lin = 0


def _parte(pre, txt):
    """pre + 'a - b + c' en renglones de _ANCHO, cortando entre terminos."""
    if len(pre) + len(txt) <= _ANCHO:
        return [pre + txt]
    t = txt.split(" ")
    lineas = []
    s = pre + t[0]
    i = 1
    while i + 1 < len(t):
        pieza = t[i] + " " + t[i + 1]
        if len(s) + 1 + len(pieza) > _ANCHO:
            lineas.append(s)
            s = " " * len(pre) + pieza
        else:
            s += " " + pieza
        i += 2
    if i < len(t):
        s += " " + t[i]
    lineas.append(s)
    return lineas


def _pasos(lado, pasos):
    """'J = 5346/(2*4) = 5346/8 = 668.25': en un renglon si cabe;
    si no, cada '= paso' abajo del anterior."""
    s = lado + " = " + " = ".join(pasos)
    if len(s) <= _ANCHO:
        _out(s)
        return
    lineas = []
    pre = lado + " = "
    for paso in pasos:
        lineas.extend(_parte(pre, paso))
        pre = " " * len(lado) + " = "
    _out(*lineas)


# ---------- calculo ----------

def _sumas(xs, ys, t0, t1):
    """Renglones (x, y, yh, e) y sum e, sum e*x, sum e^2."""
    filas = []
    se = sex = se2 = (0, 1)
    for x, y in zip(xs, ys):
        yh = _mas(t0, _por(t1, x))
        e = _menos(yh, y)
        filas.append((x, y, yh, e))
        se = _mas(se, e)
        sex = _mas(sex, _por(e, x))
        se2 = _mas(se2, _por(e, e))
    return filas, se, sex, se2


def _costo(xs, ys, t0, t1):
    return _entre(_sumas(xs, ys, t0, t1)[3], (2 * len(xs), 1))


def _hip(t0, t1):
    """'h(x) = 5 + 8x' con el signo bien puesto."""
    return "h(x) = " + _junta(_n(t0), t1) + "x"


def _procedimiento(t0, t1, filas):
    """yh y e renglon por renglon; luego e*x y e^2."""
    _out(_hip(t0, t1))
    for x, y, yh, e in filas:
        _out("x=" + _n(x) + ": yh = " + _junta(_n(t0), t1) + _p(x)
             + " = " + _n(yh),
             "     e = " + _junta(_n(yh), y, "-") + " = " + _n(e))
    _pausa()
    _out("-- e*x y e^2 --")
    for x, y, yh, e in filas:
        _out("x=" + _n(x) + ": e*x = " + _n(e) + _p(x)
             + " = " + _n(_por(e, x)),
             "     e^2 = " + _p(e) + "^2 = " + _n(_por(e, e)))
    _pausa()


def _tablas(filas):
    """Las dos tablas como van en la hoja."""
    t = ["x | y | yh | e=yh-y"]
    for x, y, yh, e in filas:
        t.append("{} | {} | {} | {}".format(_n(x), _n(y), _n(yh), _n(e)))
    _out(*t)
    t = ["x | e*x | e^2"]
    for x, y, yh, e in filas:
        t.append("{} | {} | {}".format(_n(x), _n(_por(e, x)),
                                       _n(_por(e, e))))
    _out(*t)
    _pausa()


def _sumas_txt(m, filas, se, sex, se2):
    """Sumas termino por termino y J. Regresa J."""
    _pasos("sum e", [_suma_txt([f[3] for f in filas]), _n(se)])
    _pasos("sum e*x", [_suma_txt([_por(f[3], f[0]) for f in filas]),
                       _n(sex)])
    _pasos("sum e^2", [_suma_txt([_por(f[3], f[3]) for f in filas]),
                       _n(se2)])
    J = _entre(se2, (2 * m, 1))
    _pasos("J", ["{}/(2*{})".format(_n(se2), m),
                 "{}/{}".format(_n(se2), 2 * m), _n(J)])
    _pausa()
    return J


def _iteracion(k, xs, ys, t0, t1, alfa):
    """Una iteracion con todo. Regresa (theta0, theta1 nuevos, J)."""
    m = len(xs)
    filas, se, sex, se2 = _sumas(xs, ys, t0, t1)
    g0 = _entre(se, (m, 1))
    g1 = _entre(sex, (m, 1))
    n0 = _menos(t0, _por(alfa, g0))   # simultanea: los dos con t0, t1 viejos
    n1 = _menos(t1, _por(alfa, g1))
    _out("== ITERACION {} ==".format(k))
    _procedimiento(t0, t1, filas)
    _tablas(filas)
    J = _sumas_txt(m, filas, se, sex, se2)
    _out("-- actualizacion simultanea --")
    _pasos("dJ/dtheta0", ["(1/{})({})".format(m, _n(se)), _n(g0)])
    _pasos("dJ/dtheta1", ["(1/{})({})".format(m, _n(sex)), _n(g1)])
    _pasos("theta0", [_n(t0) + " - " + _n(alfa) + _p(g0), _n(n0)])
    _pasos("theta1", [_n(t1) + " - " + _n(alfa) + _p(g1), _n(n1)])
    _pausa()
    return n0, n1, J


def _gd(xs, ys, t0, t1, alfa, n):
    if n < 1:
        raise ValueError("iteraciones >= 1")
    if n > 5:
        return _gd_rapido(xs, ys, t0, t1, alfa, n)
    Js = []
    for k in range(1, n + 1):
        t0, t1, J = _iteracion(k, xs, ys, t0, t1, alfa)
        Js.append(J)
    Js.append(_costo(xs, ys, t0, t1))
    _resumen(Js, t0, t1, True)
    return t0, t1


def _gd_rapido(xs, ys, t0, t1, alfa, n):
    """Muchas iteraciones con decimales de la calc; solo muestra J."""
    X = [_f(v) for v in xs]
    Y = [_f(v) for v in ys]
    a0, a1, al = _f(t0), _f(t1), _f(alfa)
    m = len(X)
    cada = max(1, n // 10)
    Js = []
    _out("== {} ITERACIONES ==".format(n))
    for k in range(1, n + 2):
        se = sex = se2 = 0.0
        for x, y in zip(X, Y):
            e = a0 + a1 * x - y
            se += e
            sex += e * x
            se2 += e * e
        Js.append(se2 / (2 * m))
        if k > n:
            break                     # esta ya es J con theta finales
        if k == 1 or k % cada == 0:
            _out("J{} = {}".format(k, _nf(Js[-1])))
        a0, a1 = a0 - al * (se / m), a1 - al * (sex / m)
    _pausa()
    _resumen(Js, a0, a1, False)
    return a0, a1


_VEREDICTO = {-1: ("<", "bajo, mejoro"), 0: ("=", "igual"),
              1: (">", "subio, empeoro")}


def _resumen(Js, t0, t1, todo):
    """Js[k] = J(k+1); el ultimo es J con los theta finales."""
    ult = len(Js) - 1
    _out("== RESUMEN ==")
    if todo:
        for k in range(len(Js)):
            _out("J{} = {}".format(k + 1, _n(Js[k])))
        _out("(J{} usa los theta finales)".format(ult + 1))
        for k in range(1, len(Js)):
            signo, txt = _VEREDICTO[_cmp(Js[k], Js[k - 1])]
            _out("J{} {} J{}: {}".format(k + 1, signo, k, txt))
    else:
        _out("J1 = " + _n(Js[0]))
        _out("J{} = {} (theta finales)".format(ult + 1, _n(Js[ult])))
        signo, txt = _VEREDICTO[_cmp(Js[ult], Js[0])]
        _out("J{} {} J1: {}".format(ult + 1, signo, txt))
        _out("(decimales de la calc, aprox.)")
    _out("theta0 final = " + _n(t0))
    _out("theta1 final = " + _n(t1))
    total = _cmp(Js[ult], Js[0])
    if total < 0:
        _out("Conclusion: J bajo, el modelo mejoro")
    elif total > 0:
        _out("Conclusion: J subio, alfa muy grande",
             "(diverge u oscila)")
    else:
        _out("Conclusion: J no cambio")
    _pausa()


def _tabla_costo(xs, ys, t0, t1):
    filas, se, sex, se2 = _sumas(xs, ys, t0, t1)
    _out("== TABLA Y COSTO J ==")
    _procedimiento(t0, t1, filas)
    _tablas(filas)
    return _sumas_txt(len(xs), filas, se, sex, se2)


def _predice(t0, t1, x):
    yh = _mas(t0, _por(t1, x))
    _pasos("yh", ["theta0 + theta1(x)",
                  _junta(_n(t0), t1) + _p(x),
                  _junta(_n(t0), _por(t1, x)),
                  _n(yh)])
    if _cmp(yh, (70, 1)) >= 0:
        _out(_n(yh) + " >= 70: APRUEBA")
    else:
        _out(_n(yh) + " < 70: REPRUEBA")
    return yh


# ---------- para usar directo en el shell ----------

def gradiente(xs, ys, theta0, theta1, alfa, n=2):
    """gradiente([1,2,3,4], [35,50,68,87], 5, 8, 0.02, 2)"""
    _nueva()
    t0, t1 = _gd([_a(v) for v in xs], [_a(v) for v in ys],
                 _a(theta0), _a(theta1), _a(alfa), n)
    return _f(t0), _f(t1)


def costo(xs, ys, theta0, theta1):
    """J(theta) = sum(e^2)/(2m), sin imprimir."""
    return _f(_costo([_a(v) for v in xs], [_a(v) for v in ys],
                     _a(theta0), _a(theta1)))


def tabla_costo(xs, ys, theta0, theta1):
    """Procedimiento, tablas, sumas y J con unos theta (sin actualizar)."""
    _nueva()
    return _f(_tabla_costo([_a(v) for v in xs], [_a(v) for v in ys],
                           _a(theta0), _a(theta1)))


def predice(theta0, theta1, x):
    """yh = theta0 + theta1*x y si aprueba (yh >= 70)."""
    _nueva()
    return _f(_predice(_a(theta0), _a(theta1), _a(x)))


# ---------- conceptos: la idea clave para las interpretaciones ----------

_CONCEPTOS = [
    ("Que resume J (costo)", [
        "J = sum(e^2)/(2m): un numero que",
        "resume que tan lejos quedan las",
        "predicciones de los datos reales.",
        "J chica = el modelo le atina mas.",
        "Es la mitad del error cuadratico",
        "medio (el 2 simplifica la derivada)",
        "Al cuadrado: los errores + y - no",
        "se cancelan y los grandes pesan mas",
    ]),
    ("Residuo e = yh - y", [
        "e < 0: la prediccion se quedo corta",
        "e > 0: la prediccion se paso",
        "e = 0: le atino exacto",
    ]),
    ("Hipotesis h(x)", [
        "h(x) = theta0 + theta1*x es una",
        "recta: regresion lineal de una",
        "variable.",
        "theta0: lo que predice con x = 0",
        "(ordenada al origen).",
        "theta1: cuanto cambia y por cada",
        "unidad de x, ej. puntos por hora",
        "de estudio (pendiente).",
    ]),
    ("Gradiente descendente", [
        "Gradiente: pendiente de J con",
        "respecto a cada theta (derivadas).",
        "theta := theta - alfa*gradiente:",
        "va contra la pendiente y baja J.",
        "Batch: cada paso usa los m datos.",
        "Simultanea: los 2 gradientes con",
        "los theta viejos; luego actualiza.",
        "J nueva < J anterior: mejoro.",
    ]),
    ("Tasa de aprendizaje alfa", [
        "alfa muy chica: J baja, pero muy",
        "lento (muchas iteraciones).",
        "alfa muy grande: se pasa del",
        "minimo; J oscila o sube (diverge).",
        "alfa adecuada: J baja rapido y",
        "estable.",
    ]),
    ("Supervisado vs no supervisado", [
        "Supervisado: datos etiquetados;",
        "cada x trae su respuesta real y",
        "(horas -> calificacion).",
        "No supervisado: sin etiquetas;",
        "busca grupos o patrones",
        "(agrupamiento / clustering).",
    ]),
    ("Regresion vs clasificacion", [
        "Regresion: predice un numero",
        "continuo (calificacion 0-100).",
        "Clasificacion: predice una clase",
        "(aprobado / no aprobado).",
        "Aprobado si y >= 70: clasificacion",
        "binaria y supervisada, porque hay",
        "ejemplos etiquetados con su clase.",
    ]),
]


def _conceptos():
    while True:
        print("")
        print("== CONCEPTOS ==")
        for i in range(len(_CONCEPTOS)):
            print("{} {}".format(i + 1, _CONCEPTOS[i][0]))
        print("0 Regresar al menu")
        s = input("Numero de tema: ").strip()
        if s == "0" or s == "":
            return
        try:
            k = int(s)
        except ValueError:
            k = 0
        if 1 <= k <= len(_CONCEPTOS):
            titulo, lineas = _CONCEPTOS[k - 1]
            _nueva()
            _out("-- " + titulo + " --")
            for ln in lineas:
                _out(ln)
            _pausa()
        else:
            print("Ese tema no existe (0 a {}).".format(len(_CONCEPTOS)))


# ---------- menu ----------

def _pregunta(texto, previo):
    """Hace la pregunta; si hay dato anterior lo muestra en [ ]."""
    if previo is None:
        return input(texto + ": ").strip()
    return input("{} [{}]: ".format(texto, previo)).strip()


def _pide(texto, clave, default=None):
    """Lee un numero. Enter = lo de [ ]. Si no se entiende, repite."""
    previo = _D.get(clave, default)
    while True:
        s = _pregunta(texto, None if previo is None else _n(previo))
        if s == "":
            if previo is not None:
                return _a(previo)
            print("Falta este dato.")
            continue
        try:
            v = _lee(s)
        except Exception:
            print("No entendi. Ej: 5, 0.02, -3, 1/50")
            continue
        _D[clave] = v
        return v


def _pide_entero(texto, clave, default):
    while True:
        p, q = _pide(texto, clave, default)
        if q == 1 and p >= 1:
            return p
        print("Debe ser un entero de 1 o mas.")
        _D[clave] = default


def _pide_lista(texto, clave):
    previa = _D.get(clave)
    txt = None
    if previa is not None:
        txt = ",".join([_n(v) for v in previa])
    while True:
        s = _pregunta(texto, txt)
        if s == "":
            if previa is not None:
                return previa
            print("Falta este dato.")
            continue
        for c in "{}[]":
            s = s.replace(c, "")
        try:
            vals = [_lee(t) for t in s.replace(",", " ").split()]
        except Exception:
            vals = []
        if vals:
            return vals
        print("No entendi. Ej: 1,2,3,4")


def _datos():
    print("Separa los valores con comas.")
    print("Enter = usar lo que sale en [ ].")
    xs = _pide_lista("Valores de x", "xs")
    while True:
        ys = _pide_lista("Valores de y", "ys")
        if len(ys) == len(xs):
            break
        print("Hay {} valores de x y {} de y;".format(len(xs), len(ys)))
        print("deben ser iguales. Escribe y.")
    _D["xs"], _D["ys"] = xs, ys
    return xs, ys


def ia():
    while True:
        print("")
        print("== IA: REGRESION LINEAL ==")
        print("1 Resolver (gradiente descendente)")
        print("2 Solo tabla y costo J")
        print("3 Predecir y (aprueba si >= 70)")
        print("4 Conceptos para explicar")
        print("0 Salir")
        op = input("Escribe el numero de opcion: ").strip()
        if op == "0":
            return
        try:
            _corre(op)
        except Exception as err:
            print("Algo fallo: " + str(err))


def _corre(op):
    if op == "1":
        print("-- RESOLVER --")
        xs, ys = _datos()
        t0 = _pide("theta0 inicial", "t0")
        t1 = _pide("theta1 inicial", "t1")
        alfa = _pide("Tasa de aprendizaje alfa", "alfa")
        n = _pide_entero("Cuantas iteraciones", "n", (2, 1))
        _nueva()
        _D["f0"], _D["f1"] = _gd(xs, ys, t0, t1, alfa, n)
    elif op == "2":
        print("-- TABLA Y COSTO J --")
        xs, ys = _datos()
        t0 = _pide("theta0 a evaluar", "f0", _D.get("t0"))
        t1 = _pide("theta1 a evaluar", "f1", _D.get("t1"))
        _nueva()
        _tabla_costo(xs, ys, t0, t1)
    elif op == "3":
        print("-- PREDECIR --")
        t0 = _pide("theta0 a usar", "f0", _D.get("t0"))
        t1 = _pide("theta1 a usar", "f1", _D.get("t1"))
        while True:
            s = input("x a predecir (enter = menu): ").strip()
            if s == "":
                return
            try:
                x = _lee(s)
            except Exception:
                print("No entendi. Ej: 5")
                continue
            _nueva()
            _predice(t0, t1, x)
    elif op == "4":
        _conceptos()
    else:
        print("Esa opcion no existe (0 a 4).")


ia()
