# ia - regresion lineal con gradiente descendente (IA PrepaTEC)
# Adrian. Corre el programa `ia` y sale el menu: tecleas los datos
# y saca tablas y sustituciones como se escriben en el examen.
#
# Convenciones del curso (no cambiarlas o no cuadra el solucionario):
#   yh = th0 + th1*x              e = yh - y
#   J = sum(e^2) / (2m)
#   dJ/dth0 = sum(e)/m            dJ/dth1 = sum(e*x)/m
#   th := th - alfa*dJ/dth        los DOS con los th viejos
#   aprobado si y >= 70
#
# Cuentas EXACTAS con fracciones de enteros largos: nada se redondea
# ni se mete ruido binario. En pantalla salen hasta 12 cifras; si hay
# mas, se corta y termina en '...'. Con mas de 5 iteraciones usa los
# decimales de la calc (exacto seria lentisimo) y solo muestra J.
# Todo ASCII, sin f-strings ni operadores sobrecargados: el Python de
# la Nspire es MicroPython 1.11.

_ANCHO = 36    # caracteres por renglon (aprox.) en el shell
_ALTO = 10     # renglones por pantalla antes de pedir [enter]
_CIFRAS = 12   # cifras significativas en pantalla

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


def _out(s=""):
    """print que pide [enter] antes de que se salga de la pantalla."""
    global _lin
    alto = 1 + max(0, len(s) - 1) // _ANCHO
    if _lin + alto > _ALTO:
        _pausa()
    print(s)
    _lin += alto


def _pausa():
    global _lin
    if _lin > 0:
        input("[enter]")
    _lin = 0


def _nueva():
    global _lin
    _lin = 0


def _sust(lado, expr, valor):
    """'th1 = 8 - 0.02(-99.25) = 9.985' en uno o dos renglones."""
    s = "{} = {} = {}".format(lado, expr, valor)
    if len(s) <= _ANCHO:
        _out(s)
    else:
        _out("{} = {}".format(lado, expr))
        _out(" " * len(lado) + " = " + valor)


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
    if t1[0] < 0:
        return "h(x) = {} - {}x".format(_n(t0), _n((-t1[0], t1[1])))
    return "h(x) = {} + {}x".format(_n(t0), _n(t1))


def _tabla(t0, t1, filas):
    _out(_hip(t0, t1))
    _out("x | y | yh | e=yh-y")
    for x, y, yh, e in filas:
        _out("{} | {} | {} | {}".format(_n(x), _n(y), _n(yh), _n(e)))
    _pausa()


def _sumas_txt(m, filas, se, sex, se2):
    """Tabla auxiliar e*x, e^2 (la de la hoja), sumas y J."""
    _out("x | e*x | e^2")
    for x, y, yh, e in filas:
        _out("{} | {} | {}".format(_n(x), _n(_por(e, x)), _n(_por(e, e))))
    _out("sum e   = " + _n(se))
    _out("sum e*x = " + _n(sex))
    _out("sum e^2 = " + _n(se2))
    J = _entre(se2, (2 * m, 1))
    _sust("J", "{}/(2*{})".format(_n(se2), m), _n(J))
    return J


def _iteracion(k, xs, ys, t0, t1, alfa):
    """Una iteracion con todo. Regresa (th0, th1 nuevos, J con th viejos)."""
    m = len(xs)
    filas, se, sex, se2 = _sumas(xs, ys, t0, t1)
    g0 = _entre(se, (m, 1))
    g1 = _entre(sex, (m, 1))
    n0 = _menos(t0, _por(alfa, g0))   # simultanea: los dos con t0, t1 viejos
    n1 = _menos(t1, _por(alfa, g1))
    _out("== ITERACION {} ==".format(k))
    _tabla(t0, t1, filas)
    J = _sumas_txt(m, filas, se, sex, se2)
    _pausa()
    _sust("dJ/dth0", "{}/{}".format(_n(se), m), _n(g0))
    _sust("dJ/dth1", "{}/{}".format(_n(sex), m), _n(g1))
    _sust("th0", "{} - {}{}".format(_n(t0), _n(alfa), _p(g0)), _n(n0))
    _sust("th1", "{} - {}{}".format(_n(t1), _n(alfa), _p(g1)), _n(n1))
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
    for k in range(1, n + 2):
        se = sex = se2 = 0.0
        for x, y in zip(X, Y):
            e = a0 + a1 * x - y
            se += e
            sex += e * x
            se2 += e * e
        Js.append(se2 / (2 * m))
        if k > n:
            break                     # esta ya es J con th finales
        if k == 1 or k % cada == 0:
            _out("it {}: J = {}".format(k, _nf(Js[-1])))
        a0, a1 = a0 - al * (se / m), a1 - al * (sex / m)
    _pausa()
    _resumen(Js, a0, a1, False)
    return a0, a1


_VEREDICTO = {-1: "bajo, mejoro", 0: "igual", 1: "subio, empeoro"}


def _resumen(Js, t0, t1, todo):
    """Js[k] = J de la iteracion k+1; el ultimo, J con th finales."""
    _out("== RESUMEN ==")
    ult = len(Js) - 1
    for k in range(len(Js)):
        if not todo and 0 < k < ult:
            continue
        nombre = "J final" if k == ult else "J it " + str(k + 1)
        s = nombre + " = " + _n(Js[k])
        if todo and k > 0:
            s += ": " + _VEREDICTO[_cmp(Js[k], Js[k - 1])]
        _out(s)
    if todo:
        _out("(J final usa th finales, opcion 2)")
    else:
        _out("(decimales de la calc, aprox.)")
    _out("th0 final = " + _n(t0))
    _out("th1 final = " + _n(t1))
    total = _cmp(Js[ult], Js[0])
    if total < 0:
        _out("J bajo: el modelo mejoro")
    elif total > 0:
        _out("J subio: alfa muy grande")
        _out("(diverge u oscila)")
    else:
        _out("J no cambio")
    _pausa()


def _tabla_costo(xs, ys, t0, t1):
    filas, se, sex, se2 = _sumas(xs, ys, t0, t1)
    _tabla(t0, t1, filas)
    J = _sumas_txt(len(xs), filas, se, sex, se2)
    _pausa()
    return J


def _predice(t0, t1, x):
    yh = _mas(t0, _por(t1, x))
    _sust("yh", "{} + {}{}".format(_n(t0), _n(t1), _p(x)), _n(yh))
    if _cmp(yh, (70, 1)) >= 0:
        _out(_n(yh) + " >= 70: APRUEBA")
    else:
        _out(_n(yh) + " < 70: REPRUEBA")
    return yh


# ---------- para usar directo en el shell ----------

def gradiente(xs, ys, th0, th1, alfa, n=2):
    """gradiente([1,2,3,4], [35,50,68,87], 5, 8, 0.02, 2)"""
    _nueva()
    t0, t1 = _gd([_a(v) for v in xs], [_a(v) for v in ys],
                 _a(th0), _a(th1), _a(alfa), n)
    return _f(t0), _f(t1)


def costo(xs, ys, th0, th1):
    """J(th) = sum(e^2)/(2m), sin imprimir."""
    return _f(_costo([_a(v) for v in xs], [_a(v) for v in ys],
                     _a(th0), _a(th1)))


def tabla_costo(xs, ys, th0, th1):
    """Tabla x | y | yh | e, sumas y J con unos th (sin actualizar)."""
    _nueva()
    return _f(_tabla_costo([_a(v) for v in xs], [_a(v) for v in ys],
                           _a(th0), _a(th1)))


def predice(th0, th1, x):
    """yh = th0 + th1*x y si aprueba (yh >= 70)."""
    _nueva()
    return _f(_predice(_a(th0), _a(th1), _a(x)))


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
    ("Hipotesis h(x) = th0 + th1*x", [
        "Es una recta: regresion lineal",
        "de una variable.",
        "th0: lo que predice con x = 0",
        "(ordenada al origen).",
        "th1: cuanto cambia y por cada",
        "unidad de x, ej. puntos por hora",
        "de estudio (pendiente).",
    ]),
    ("Gradiente descendente", [
        "Gradiente: pendiente de J con",
        "respecto a cada th (derivadas).",
        "th := th - alfa*gradiente: se mueve",
        "contra la pendiente para bajar J.",
        "Batch: cada iteracion usa los m.",
        "Simultanea: los 2 gradientes con",
        "los th viejos, luego se actualiza.",
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
        print("0 regresar")
        s = input("? ").strip()
        if s == "0" or s == "":
            return
        try:
            k = int(s)
        except ValueError:
            continue
        if 1 <= k <= len(_CONCEPTOS):
            titulo, lineas = _CONCEPTOS[k - 1]
            _nueva()
            _out("-- " + titulo + " --")
            for ln in lineas:
                _out(ln)
            _pausa()


# ---------- menu ----------

def _pide(nombre, clave, default=None):
    """Lee un numero. Enter = el ultimo que tecleaste."""
    previo = _D.get(clave, default)
    if previo is None:
        s = input(nombre + " = ")
    else:
        s = input("{} (enter={}) = ".format(nombre, _n(previo)))
    if s.strip() == "":
        if previo is None:
            raise ValueError("falta " + nombre)
        return _a(previo)
    v = _lee(s)
    _D[clave] = v
    return v


def _pide_lista(nombre, clave):
    previa = _D.get(clave)
    if previa is None:
        s = input(nombre + " (con comas) = ")
    else:
        txt = ",".join([_n(v) for v in previa])
        s = input("{} (enter={}) = ".format(nombre, txt))
    if s.strip() == "":
        if previa is None:
            raise ValueError("faltan los " + nombre)
        return previa
    for c in "{}[]":
        s = s.replace(c, "")
    return [_lee(t) for t in s.replace(",", " ").split()]


def _datos():
    xs = _pide_lista("x", "xs")
    ys = _pide_lista("y", "ys")
    if len(xs) == 0 or len(xs) != len(ys):
        raise ValueError("{} valores de x y {} de y".format(
            len(xs), len(ys)))
    _D["xs"], _D["ys"] = xs, ys
    return xs, ys


def ia():
    while True:
        print("")
        print("== IA: REGRESION LINEAL ==")
        print("1 gradiente descendente")
        print("2 tabla y costo J")
        print("3 predecir (aprueba si >=70)")
        print("4 conceptos (interpretacion)")
        print("0 salir")
        try:
            op = input("? ").strip()
            if op == "0" or op == "":
                return
            _corre(op)
        except Exception as err:
            print("error:", err)


def _corre(op):
    if op == "1":
        xs, ys = _datos()
        t0 = _pide("th0 inicial", "t0")
        t1 = _pide("th1 inicial", "t1")
        alfa = _pide("alfa", "alfa")
        p, q = _pide("iteraciones", "n", (2, 1))
        _nueva()
        _D["f0"], _D["f1"] = _gd(xs, ys, t0, t1, alfa, p // q)
    elif op == "2":
        xs, ys = _datos()
        t0 = _pide("th0", "f0", _D.get("t0"))
        t1 = _pide("th1", "f1", _D.get("t1"))
        _nueva()
        _tabla_costo(xs, ys, t0, t1)
    elif op == "3":
        t0 = _pide("th0", "f0", _D.get("t0"))
        t1 = _pide("th1", "f1", _D.get("t1"))
        while True:
            s = input("x (enter=salir) = ").strip()
            if s == "":
                return
            _nueva()
            _predice(t0, t1, _lee(s))
    elif op == "4":
        _conceptos()
    else:
        print("no existe esa opcion")


ia()
