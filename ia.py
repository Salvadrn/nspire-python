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
_ALTO = 9      # renglones por pantalla + 1 del "enter para seguir"
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
    """Fraccion -> decimal de la calc. Achica enteros enormes antes de
    dividir: MicroPython pasa cada uno a float y daria inf/nan."""
    if not isinstance(a, tuple):
        return float(a)
    p, q = a
    k = max(len(str(abs(p))), len(str(q))) - 20
    if k > 0:
        p = p // 10 ** k
        q = max(1, q // 10 ** k)
    return p / q


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


_PERMITIDOS = "0123456789.+-*/()eE "


def _lee(t):
    """Numero tecleado: 0.02, -3, 1/50 exactos; cuentas (2^3) via eval."""
    t = t.strip()
    try:
        if "/" in t:
            a, b = t.split("/")
            return _entre(_dec(a), _dec(b))
        return _dec(t)
    except ValueError:
        t = t.replace("^", "**")
        for c in t:              # en MicroPython eval no bloquea nombres
            if c not in _PERMITIDOS:
                raise ValueError("no es numero: " + t)
        return _a(eval(t, {}, {}))


def _a(v):
    """int, float, texto o fraccion -> fraccion exacta."""
    if isinstance(v, tuple):
        return v
    if isinstance(v, int):
        return (v, 1)
    if isinstance(v, str):
        return _lee(v)
    return _dec("{:.13g}".format(v))     # MP 1.11 falla en la cifra 15


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
    digs = str(ent)
    if len(digs) > _CIFRAS:              # diverge: notacion cientifica
        return s + digs[0] + "." + digs[1:_CIFRAS] + "...e+" + str(
            len(digs) - 1)
    s += digs
    cifras = len(digs) if ent else 0
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


def _predicciones(titulo, t0, t1, filas, se):
    """Pantallas de yh y e: procedimiento, tabla y sum e."""
    _out(titulo + _hip(t0, t1))
    for x, y, yh, e in filas:
        _out("x=" + _n(x) + ": yh = " + _junta(_n(t0), t1) + _p(x)
             + " = " + _n(yh),
             "     e = " + _junta(_n(yh), y, "-") + " = " + _n(e))
    _pausa()
    t = ["x | y | yh | e=yh-y"]
    for x, y, yh, e in filas:
        t.append("{} | {} | {} | {}".format(_n(x), _n(y), _n(yh), _n(e)))
    _out(*t)
    _pasos("sum e", [_suma_txt([f[3] for f in filas]), _n(se)])
    _pausa()


def _costo_txt(m, filas, se2):
    """Pantalla de J: cada e^2, su suma y J. Regresa J."""
    _out("-- costo J (con cada e^2) --")
    for x, y, yh, e in filas:
        _out("x=" + _n(x) + ": e^2 = " + _p(e) + "^2 = "
             + _n(_por(e, e)))
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
    _predicciones("ITERACION {}: ".format(k), t0, t1, filas, se)
    J = _costo_txt(m, filas, se2)
    _out("-- e*x para dJ/dtheta1 --")
    for x, y, yh, e in filas:
        _out("x=" + _n(x) + ": e*x = " + _n(e) + _p(x)
             + " = " + _n(_por(e, x)))
    _pasos("sum e*x", [_suma_txt([_por(f[3], f[0]) for f in filas]),
                       _n(sex)])
    _pausa()
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


def _compara_txt(antes, ahora, i, j):
    """'J2 < J1: bajo 203.01665625, mejoro'."""
    c = _cmp(ahora, antes)
    if isinstance(antes, tuple) and isinstance(ahora, tuple):
        d = _menos(antes, ahora)
        d = (abs(d[0]), d[1])
    else:
        d = abs(_f(antes) - _f(ahora))
    if c < 0:
        return "J{} < J{}: bajo {}, mejoro".format(j, i, _n(d))
    if c > 0:
        return "J{} > J{}: subio {}, empeoro".format(j, i, _n(d))
    return "J{} = J{}: igual".format(j, i)


def _resumen(Js, t0, t1, todo):
    """Js[k] = J(k+1); el ultimo es J con los theta finales."""
    ult = len(Js) - 1
    _out("== RESUMEN ==")
    if todo:
        for k in range(len(Js)):
            _out("J{} = {}".format(k + 1, _n(Js[k])))
    else:
        _out("J1 = " + _n(Js[0]))
        _out("J{} = {}".format(ult + 1, _n(Js[ult])))
    _out("(J{} usa los theta finales)".format(ult + 1))
    if todo:
        for k in range(1, len(Js)):
            _out(_compara_txt(Js[k - 1], Js[k], k, k + 1))
    else:
        _out(_compara_txt(Js[0], Js[ult], 1, ult + 1))
        _out("(decimales de la calc, aprox.)")
    total = _cmp(Js[ult], Js[0])
    if total < 0:
        _out("Conclusion: J bajo, el modelo mejoro")
    elif total > 0:
        _out("Conclusion: J subio, alfa muy grande",
             "(diverge u oscila)")
    else:
        _out("Conclusion: J no cambio")
    _pausa()
    _out("theta0 final = " + _n(t0), "theta1 final = " + _n(t1))
    _pausa()


def _tabla_costo(xs, ys, t0, t1):
    filas, se, sex, se2 = _sumas(xs, ys, t0, t1)
    _predicciones("TABLA: ", t0, t1, filas, se)
    return _costo_txt(len(xs), filas, se2)


def _predice(t0, t1, x):
    yh = _mas(t0, _por(t1, x))
    _pasos("yh", ["theta0 + theta1(x)",
                  _junta(_n(t0), t1) + _p(x),
                  _junta(_n(t0), _por(t1, x)),
                  _n(yh)])
    if _cmp(yh, (70, 1)) >= 0:
        _out(_n(yh) + " >= 70: APRUEBA")
    else:
        _out(_n(yh) + " < 70: NO APRUEBA")
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
    """Procedimiento, tabla, sumas y J con unos theta (sin actualizar)."""
    _nueva()
    return _f(_tabla_costo([_a(v) for v in xs], [_a(v) for v in ys],
                           _a(theta0), _a(theta1)))


def predice(theta0, theta1, x):
    """yh = theta0 + theta1*x y si aprueba (yh >= 70)."""
    _nueva()
    return _f(_predice(_a(theta0), _a(theta1), _a(x)))


# ---------- conceptos: la idea clave para las interpretaciones ----------

# (nombre corto para el menu, titulo, renglones: max 8 de 36 chars)
_CONCEPTOS = [
    ("IA y tipos", "IA y tipos de aprendizaje", [
        "IA: rama de la informatica que",
        "hace sistemas capaces de tareas",
        "que requieren inteligencia humana",
        "Supervisado: datos etiquetados",
        "(entradas con su salida real).",
        "No supervisado: sin etiquetas, la",
        "maquina busca patrones o grupos.",
        "Refuerzo: aprende con recompensas.",
    ]),
    ("Regr/clasif", "Regresion vs clasificacion", [
        "Supervisado = regresion y",
        "clasificacion (2 subcategorias).",
        "Regresion: salida numero continuo",
        "Ej: calificacion, precio de casa.",
        "Clasificacion: salida = una clase",
        "Ej: spam, frutas, aprobado/no.",
        "Aprobado/no: la salida es 1 de 2",
        "clases -> clasificacion binaria.",
    ]),
    ("No superv.", "No supervisado", [
        "No hay etiquetas: la maquina",
        "reconoce patrones por si sola.",
        "Agrupamiento (clustering):",
        "K-means, Gaussian Mixture Models.",
        "Reduccion de dimensionalidad:",
        "ej. 10 caracteristicas -> 2.",
    ]),
    ("Recta h(x)", "Regresion lineal simple", [
        "Objetivo: la recta que mejor se",
        "ajusta a los puntos para predecir",
        "una variable continua.",
        "h(x) = theta0 + theta1*x",
        "theta0: yh cuando x = 0 (ordenada)",
        "theta1 (pendiente): cuanto cambia",
        "la prediccion yh por cada unidad",
        "de x, ej. puntos por hora.",
    ]),
    ("Residuos", "Residuos e = yh - y", [
        "e < 0: la prediccion se quedo corta",
        "e > 0: la prediccion se paso",
        "e = 0: le atino exacto",
        "Todos e < 0: el modelo subestima,",
        "la recta va abajo de los datos.",
        "|e| crece con x: theta1 muy chica.",
        "Por eso las derivadas salen < 0 y",
        "theta0, theta1 suben al actualizar",
    ]),
    ("Costo J", "Funcion de costo J", [
        "Mide el error de la hipotesis",
        "contra los datos reales (un numero)",
        "J = (1/2m) sum (yh - y)^2; el curso",
        "la llama Error Cuadratico Medio.",
        "J chica = el modelo le atina mas.",
        "Al cuadrado: + y - no se cancelan",
        "y los errores grandes pesan mas.",
        "1/m promedia; 1/2 se va al derivar",
    ]),
    ("Gradiente", "Gradiente descendente", [
        "Optimizador: ajusta theta0 y",
        "theta1 paso a paso para bajar J.",
        "dJ/dtheta = pendiente de J.",
        "theta := theta - alfa*dJ/dtheta",
        "Simultanea: calcula las 2",
        "derivadas con los theta viejos y",
        "hasta despues actualiza los 2.",
        "Batch: cada paso usa los m datos.",
    ]),
    ("Comparar J", "Comparar J y concluir", [
        "J2 < J1: la actualizacion mejoro;",
        "los |e| bajan, yh se acerca a y.",
        "J2 > J1: empeoro (alfa grande).",
        "Conclusion: cita J1, J2 y cuanto",
        "bajo (J1 - J2).",
        "Seguir iterando mientras J baje;",
        "parar cuando casi no cambie.",
    ]),
    ("Alfa", "Tasa de aprendizaje alfa", [
        "alfa muy chica: J baja, pero muy",
        "lento (muchas iteraciones).",
        "alfa muy grande: se pasa del",
        "minimo; J oscila o sube (diverge).",
        "alfa adecuada: J baja rapido y",
        "estable.",
    ]),
    ("Predecir", "Usar el modelo (predecir)", [
        "yh = theta0 + theta1*x con los",
        "theta finales (sustituye x).",
        "Aprueba si yh >= 70.",
        "x fuera del rango de los datos:",
        "es extrapolar, menos confiable.",
        "Con pocas iteraciones J sigue alto",
        "y la prediccion puede quedar baja.",
    ]),
]


def _conceptos():
    total = len(_CONCEPTOS)
    mitad = (total + 1) // 2
    while True:
        print("")
        print("== CONCEPTOS ==")
        for i in range(mitad):
            s = "{} {}".format(i + 1, _CONCEPTOS[i][0])
            if i + mitad < total:
                s += " | {} {}".format(i + mitad + 1,
                                       _CONCEPTOS[i + mitad][0])
            print(s)
        print("0 Regresar al menu")
        s = input("Numero de tema: ").strip()
        if s == "0" or s == "":
            return
        try:
            k = int(s)
        except ValueError:
            k = 0
        if 1 <= k <= total:
            corto, titulo, lineas = _CONCEPTOS[k - 1]
            _nueva()
            _out("-- " + titulo + " --")
            for ln in lineas:
                _out(ln)
            _pausa()
        else:
            print("Ese tema no existe (0 a {}).".format(total))


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
                try:
                    return _a(previo)
                except Exception:        # -inf de un modo rapido que diverge
                    print("Ese dato ya no sirve; escribe otro.")
                    previo = None
                    continue
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
    try:
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
                break
            try:
                _corre(op)
            except Exception as err:
                print("Algo fallo: " + str(err))
    except KeyboardInterrupt:
        pass
    print("Para abrir otra vez: ia()")


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
