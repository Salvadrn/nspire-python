# ia - regresion lineal con gradiente descendente (IA PrepaTEC)
# Adrian. Corre el programa `ia` y sale el menu: te pregunta los datos
# y saca el procedimiento escrito como va en el examen.
#
# Formulas del curso (arranca con estas). Antes de resolver las muestra
# todas juntas; enter = son iguales a tu examen, o se editan escribiendo
# la formula tal cual (1/(2m), e^2, theta0 + theta1*x...):
#   h(x) = theta0 + theta1*x        e = yh - y
#   J = 1/(2m) sum(e^2)
#   dJ/dtheta0 = 1/m sum(e)         dJ/dtheta1 = 1/m sum(e*x)
#   theta := theta - alfa*dJ/dtheta (los DOS con los theta viejos)
#   aprobado si yh >= 70
#
# Cuentas EXACTAS con fracciones de enteros largos: nada se redondea
# ni se mete ruido binario. En pantalla salen hasta 12 cifras; si hay
# mas, se corta y termina en '...'. Con mas de 5 iteraciones usa los
# decimales de la calc (exacto seria lentisimo) y solo muestra J.
# Todo ASCII, sin f-strings, sin eval y sin operadores sobrecargados:
# el Python de la Nspire es MicroPython 1.11.

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


def _a(v):
    """int, float, texto o fraccion -> fraccion exacta."""
    if isinstance(v, tuple):
        return v
    if isinstance(v, int):
        return (v, 1)
    if isinstance(v, str):
        return _lee(v)
    return _dec("{:.13g}".format(v))     # MP 1.11 falla en la cifra 15


# ---------- formulas escritas como texto ----------
# Nodos: ("n", fraccion, texto)  numero      ("v", nombre)   variable
#        ("p", nodo)  (parentesis)            ("u", nodo)     -nodo
#        ("b", op, izq, der) con op en + - * / ^ o "" (8x, 2(m))

_ALIAS = {"t0": "theta0", "t1": "theta1", "alpha": "alfa"}
_NOMBRE = {"dj": "dJ/dtheta"}


def _tokens(s):
    s = s.lower().replace("dj/dtheta", "dj")
    t = []
    i = 0
    while i < len(s):
        c = s[i]
        if c == " ":
            i += 1
        elif c.isdigit() or c == ".":
            j = i
            while j < len(s) and (s[j].isdigit() or s[j] == "."):
                j += 1
            t.append(("n", s[i:j]))
            i = j
        elif c.isalpha() or c == "_":
            j = i
            while j < len(s) and (s[j].isalpha() or s[j].isdigit()
                                  or s[j] == "_"):
                j += 1
            nombre = s[i:j]
            t.append(("v", _ALIAS.get(nombre, nombre)))
            i = j
        elif c in "+-*/^()[]":
            if c == "[":
                c = "("
            elif c == "]":
                c = ")"
            t.append(("o", c))
            i += 1
        else:
            raise ValueError("no entiendo '" + c + "'")
    return t


class _Lector:
    """Parser de formulas: + - * / ^, parentesis y 8x = 8*x."""

    def __init__(self, toks):
        self.t = toks
        self.i = 0

    def ver(self):
        if self.i < len(self.t):
            return self.t[self.i]
        return ("", "")

    def toma(self):
        k = self.t[self.i]
        self.i += 1
        return k

    def suma(self):
        nodo = self.producto()
        while self.ver() in (("o", "+"), ("o", "-")):
            op = self.toma()[1]
            nodo = ("b", op, nodo, self.producto())
        return nodo

    def producto(self):
        nodo = self.signo()
        while True:
            k = self.ver()
            if k in (("o", "*"), ("o", "/")):
                op = self.toma()[1]
                nodo = ("b", op, nodo, self.signo())
            elif k[0] in ("n", "v") or k == ("o", "("):
                nodo = ("b", "", nodo, self.potencia())
            else:
                return nodo

    def signo(self):
        if self.ver() == ("o", "-"):
            self.toma()
            return ("u", self.signo())
        if self.ver() == ("o", "+"):
            self.toma()
            return self.signo()
        return self.potencia()

    def potencia(self):
        base = self.atomo()
        if self.ver() == ("o", "^"):
            self.toma()
            return ("b", "^", base, self.signo())
        return base

    def atomo(self):
        k = self.ver()
        if k[0] == "n":
            self.toma()
            return ("n", _dec(k[1]), k[1])
        if k[0] == "v":
            self.toma()
            return ("v", k[1])
        if k == ("o", "("):
            self.toma()
            nodo = self.suma()
            if self.ver() != ("o", ")"):
                raise ValueError("falta cerrar )")
            self.toma()
            return ("p", nodo)
        raise ValueError("formula incompleta")


def _parse(s):
    toks = _tokens(s)
    if not toks:
        raise ValueError("formula vacia")
    lector = _Lector(toks)
    nodo = lector.suma()
    if lector.i != len(toks):
        raise ValueError("sobra algo en la formula")
    return nodo


def _vars(nodo, acc):
    if nodo[0] == "v":
        acc.append(nodo[1])
    elif nodo[0] in ("p", "u"):
        _vars(nodo[1], acc)
    elif nodo[0] == "b":
        _vars(nodo[2], acc)
        _vars(nodo[3], acc)
    return acc


def _ev(nodo, env):
    """Valor exacto de la formula con las variables de env."""
    k = nodo[0]
    if k == "n":
        return nodo[1]
    if k == "v":
        if nodo[1] not in env:
            raise ValueError("no conozco '" + nodo[1] + "'")
        return env[nodo[1]]
    if k == "p":
        return _ev(nodo[1], env)
    if k == "u":
        v = _ev(nodo[1], env)
        return (-v[0], v[1])
    op, a, b = nodo[1], _ev(nodo[2], env), _ev(nodo[3], env)
    if op == "+":
        return _mas(a, b)
    if op == "-":
        return _menos(a, b)
    if op == "/":
        return _entre(a, b)
    if op != "^":
        return _por(a, b)
    if b[1] != 1 or abs(b[0]) > 50:
        raise ValueError("la potencia debe ser entera")
    base = a if b[0] >= 0 else _entre((1, 1), a)
    r = (1, 1)
    for _ in range(abs(b[0])):
        r = _por(r, base)
    return r


def _evf(nodo, env):
    """Igual que _ev pero con decimales de la calc (modo rapido)."""
    k = nodo[0]
    if k == "n":
        return _f(nodo[1])
    if k == "v":
        return env[nodo[1]]
    if k == "p":
        return _evf(nodo[1], env)
    if k == "u":
        return -_evf(nodo[1], env)
    op, a, b = nodo[1], _evf(nodo[2], env), _evf(nodo[3], env)
    try:
        if op == "+":
            return a + b
        if op == "-":
            return a - b
        if op == "/":
            return a / b
        if op == "^":
            return a ** b
        return a * b
    except OverflowError:
        return float("inf")


def _tx(nodo, env):
    """La formula escrita con los valores de env sustituidos:
    theta0 + theta1*x -> 5 + 8(1);  e^2 -> (-22)^2;  1/(2m) -> 1/(2(4))."""
    k = nodo[0]
    if k == "n":
        return nodo[2]
    if k == "v":
        if nodo[1] in env:
            s = _n(env[nodo[1]])
            return "(" + s + ")" if s.startswith("-") else s
        return _NOMBRE.get(nodo[1], nodo[1])
    if k == "p":
        return "(" + _tx(nodo[1], env) + ")"
    if k == "u":
        s = _tx(nodo[1], env)
        return "-(" + s + ")" if s.startswith("-") else "-" + s
    op, a, b = nodo[1], nodo[2], nodo[3]
    izq, der = _tx(a, env), _tx(b, env)
    if op in ("+", "-"):
        return izq + " " + op + " " + der
    if op in ("*", ""):
        if b[0] == "v" and b[1] in env and not der.startswith("("):
            der = "(" + der + ")"                     # 8(1)
        pegado = der.startswith("(") or (
            b[0] == "v" and b[1] not in env
            and (a[0] == "n" or (a[0] == "v" and a[1] in env)))
        return izq + der if pegado else izq + "*" + der
    return izq + op + der


def _fr(a):
    """Fraccion como en papel: 1/8, -3/4, 5."""
    if a[1] == 1:
        return str(a[0])
    return str(a[0]) + "/" + str(a[1])


def _terminos(nodo, env):
    """'6.287 + 58.185': cada termino de la suma ya evaluado."""
    if nodo[0] == "b" and nodo[1] in ("+", "-"):
        s = _n(_ev(nodo[3], env))
        if s.startswith("-"):
            s = "(" + s + ")"
        return _terminos(nodo[2], env) + " " + nodo[1] + " " + s
    return _n(_ev(nodo, env))


# Formulas activas como texto; _FN tiene las mismas ya leidas.
_CURSO = {"hip": "theta0 + theta1*x", "e": "yh - y",
          "J": ("1/(2m)", "e^2"), "g0": ("1/m", "e"),
          "g1": ("1/m", "e*x"), "act": "theta - alfa*dJ/dtheta",
          "umbral": (70, 1)}
_FT = {}
_FN = {}


def _compila():
    for k in _FT:
        v = _FT[k]
        if k == "umbral":
            _FN[k] = v
        elif isinstance(v, tuple):
            _FN[k] = (_parse(v[0]), _parse(v[1]))
        else:
            _FN[k] = _parse(v)


def _curso():
    for k in _CURSO:
        _FT[k] = _CURSO[k]
    _compila()


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


def _junta_txt(partes):
    """['-22', '-29', '(-39)^2'] -> '-22 - 29 + (-39)^2'."""
    s = partes[0]
    for p in partes[1:]:
        if p.startswith("-"):
            s += " - " + p[1:]
        else:
            s += " + " + p
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
    """pre + txt en renglones de _ANCHO, cortando en los espacios."""
    if len(pre) + len(txt) <= _ANCHO:
        return [pre + txt]
    palabras = txt.split(" ")
    sangria = " " * min(len(pre), 5)
    lineas = []
    s = pre + palabras[0]
    for w in palabras[1:]:
        if len(s) + 1 + len(w) > _ANCHO:
            lineas.append(s)
            s = sangria + w
        else:
            s += " " + w
    lineas.append(s)
    return lineas


def _pasos(lado, pasos):
    """'J1 = 1/(2m) sum(e^2) = 1/8(5346) = 668.25' en un renglon si cabe;
    si no, cada '= paso' abajo del anterior. Quita pasos repetidos."""
    limpios = []
    for paso in pasos:
        if not limpios or limpios[-1] != paso:
            limpios.append(paso)
    s = lado + " = " + " = ".join(limpios)
    if len(s) <= _ANCHO:
        _out(s)
        return
    lineas = []
    pre = lado + " = "
    for paso in limpios:
        lineas.extend(_parte(pre, paso))
        pre = " " * min(len(lado), 3) + " = "
    _out(*lineas)


# ---------- calculo con procedimiento ----------

def _filas(xs, ys, t0, t1):
    """Renglones (x, y, yh, e) con las formulas activas."""
    filas = []
    for x, y in zip(xs, ys):
        yh = _ev(_FN["hip"], {"theta0": t0, "theta1": t1, "x": x})
        e = _ev(_FN["e"], {"yh": yh, "y": y, "x": x})
        filas.append((x, y, yh, e))
    return filas


def _env_fila(f):
    return {"x": f[0], "y": f[1], "yh": f[2], "e": f[3]}


def _valor_suma(k, filas):
    """coef * sum(algo) de la formula k (J, g0 o g1), sin imprimir."""
    coef, algo = _FN[k]
    S = (0, 1)
    for f in filas:
        S = _mas(S, _ev(algo, _env_fila(f)))
    return _por(_ev(coef, {"m": (len(filas), 1)}), S)


def _cadena(lado, k, filas):
    """Imprime coef * sum(algo) como en papel y regresa el valor:
    J1 = 1/(2m) sum(e^2) = 1/(2(4))[(-22)^2 + ...]
       = 1/8(484 + ...) = 1/8(5346) = 668.25"""
    coef, algo = _FN[k]
    envm = {"m": (len(filas), 1)}
    c = _ev(coef, envm)
    sust = []
    vals = []
    S = (0, 1)
    for f in filas:
        env = _env_fila(f)
        v = _ev(algo, env)
        vals.append(_n(v))
        sust.append(_n(v) if algo[0] == "v" else _tx(algo, env))
        S = _mas(S, v)
    total = _por(c, S)
    pasos = [_tx(coef, {}) + " sum(" + _tx(algo, {}) + ")"]
    if sust != vals:
        pasos.append(_tx(coef, envm) + "[" + _junta_txt(sust) + "]")
        pasos.append(_fr(c) + "(" + _junta_txt(vals) + ")")
    else:
        pasos.append(_tx(coef, envm) + "(" + _junta_txt(vals) + ")")
    pasos.append(_fr(c) + "(" + _n(S) + ")")
    pasos.append(_n(total))
    _pasos(lado, pasos)
    return total


def _prediccion_txt(titulo, t0, t1, filas):
    """h(x), cada yh, cada e, la tabla y J como en el examen."""
    hip = _FN["hip"]
    envt = {"theta0": t0, "theta1": t1}
    _out(titulo)
    _out("h(x) = " + _tx(hip, {}), "h(x) = " + _tx(hip, envt))
    for i in range(len(filas)):
        x, y, yh, e = filas[i]
        envt["x"] = x
        _pasos("yh" + str(i + 1), [_tx(hip, envt), _n(yh)])
    _pausa()
    _out("e = " + _tx(_FN["e"], {}))
    for i in range(len(filas)):
        x, y, yh, e = filas[i]
        _pasos("e" + str(i + 1),
               [_tx(_FN["e"], {"yh": yh, "y": y, "x": x}), _n(e)])
    _pausa()
    t = ["x | y | yh | e"]
    for x, y, yh, e in filas:
        t.append("{} | {} | {} | {}".format(_n(x), _n(y), _n(yh), _n(e)))
    _out(*t)
    _pausa()


def _costo_txt(k, filas, Jprev):
    """Funcion de costo con sustitucion; si hay J anterior, decide."""
    _out("-- FUNCION DE COSTO J{} --".format(k))
    J = _cadena("J" + str(k), "J", filas)
    if Jprev is None:
        _out("(J resume el error de la hipotesis",
             " actual sobre los datos reales)")
    else:
        c = _cmp(J, Jprev)
        signo = "<" if c < 0 else (">" if c > 0 else "=")
        _out("J{} = {} {} J{} = {}".format(k, _n(J), signo, k - 1,
                                           _n(Jprev)))
        if c < 0:
            _out("Decision: la actualizacion mejoro",
                 "el modelo (J bajo)")
        elif c > 0:
            _out("Decision: empeoro (J subio);",
                 "revisa alfa o las formulas")
        else:
            _out("Decision: J no cambio")
    _pausa()
    return J


def _iteracion(k, xs, ys, t0, t1, alfa, Jprev=None):
    """Una iteracion con todo el procedimiento. Regresa
    (theta0 nuevo, theta1 nuevo, J con los theta viejos)."""
    filas = _filas(xs, ys, t0, t1)
    _prediccion_txt("== ITERACION {}: PREDICCION ==".format(k),
                    t0, t1, filas)
    J = _costo_txt(k, filas, Jprev)
    _out("-- DERIVADAS (ITERACION {}) --".format(k))
    g0 = _cadena("dJ/dtheta0", "g0", filas)
    g1 = _cadena("dJ/dtheta1", "g1", filas)
    _pausa()
    act = _FN["act"]
    e0 = {"theta": t0, "alfa": alfa, "dj": g0}   # simultanea: los dos
    e1 = {"theta": t1, "alfa": alfa, "dj": g1}   # con t0, t1 viejos
    n0 = _ev(act, e0)
    n1 = _ev(act, e1)
    _out("-- NUEVOS THETA (ITERACION {}) --".format(k),
         "theta := " + _tx(act, {}))
    _pasos("theta0", [_tx(act, e0), _n(n0)])
    _pasos("theta1", [_tx(act, e1), _n(n1)])
    _out("(simultanea: con los theta viejos)")
    _pausa()
    return n0, n1, J


def _gd(xs, ys, t0, t1, alfa, n):
    if n < 1:
        raise ValueError("iteraciones >= 1")
    if n > 5:
        return _gd_rapido(xs, ys, t0, t1, alfa, n)
    Js = []
    for k in range(1, n + 1):
        t0, t1, J = _iteracion(k, xs, ys, t0, t1, alfa,
                               Js[-1] if Js else None)
        Js.append(J)
    Js.append(_valor_suma("J", _filas(xs, ys, t0, t1)))
    _resumen(Js, t0, t1, True)
    return t0, t1


def _gd_rapido(xs, ys, t0, t1, alfa, n):
    """Muchas iteraciones con decimales de la calc; solo muestra J."""
    X = [_f(v) for v in xs]
    Y = [_f(v) for v in ys]
    a0, a1, al = _f(t0), _f(t1), _f(alfa)
    m = len(X)
    hip, fe, act = _FN["hip"], _FN["e"], _FN["act"]
    coefs = [_evf(_FN[k][0], {"m": float(m)}) for k in ("J", "g0", "g1")]
    algos = [_FN[k][1] for k in ("J", "g0", "g1")]
    cada = max(1, n // 10)
    Js = []
    _out("== {} ITERACIONES ==".format(n))
    for k in range(1, n + 2):
        sumas = [0.0, 0.0, 0.0]
        for x, y in zip(X, Y):
            yh = _evf(hip, {"theta0": a0, "theta1": a1, "x": x})
            env = {"x": x, "y": y, "yh": yh,
                   "e": _evf(fe, {"yh": yh, "y": y, "x": x})}
            for j in range(3):
                sumas[j] += _evf(algos[j], env)
        Js.append(coefs[0] * sumas[0])
        if k > n:
            break                     # esta ya es J con theta finales
        if k == 1 or k % cada == 0:
            _out("J{} = {}".format(k, _nf(Js[-1])))
        g0, g1 = coefs[1] * sumas[1], coefs[2] * sumas[2]
        a0, a1 = (_evf(act, {"theta": a0, "alfa": al, "dj": g0}),
                  _evf(act, {"theta": a1, "alfa": al, "dj": g1}))
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
        _out("Conclusion: J subio; alfa muy",
             "grande o revisa las formulas")
    else:
        _out("Conclusion: J no cambio")
    _pausa()
    _out("theta0 final = " + _n(t0), "theta1 final = " + _n(t1))
    _pausa()


def _tabla_costo(xs, ys, t0, t1):
    filas = _filas(xs, ys, t0, t1)
    _prediccion_txt("== PREDICCION Y COSTO ==", t0, t1, filas)
    return _costo_txt("", filas, None)


def _predice(t0, t1, x):
    hip = _FN["hip"]
    env = {"theta0": t0, "theta1": t1, "x": x}
    yh = _ev(hip, env)
    _pasos("yh", [_tx(hip, {}), _tx(hip, env), _terminos(hip, env),
                  _n(yh)])
    u = _FN["umbral"]
    if _cmp(yh, u) >= 0:
        _out(_n(yh) + " >= " + _n(u) + ": APROBADO")
    else:
        _out(_n(yh) + " < " + _n(u) + ": NO APROBADO")
    return yh


# ---------- formulas: se muestran juntas y se pueden editar ----------

_ORDEN = ["hip", "e", "J", "g0", "g1", "act", "umbral"]
_LADO = {"hip": "h(x)", "e": "e", "J": "J", "g0": "dJ/dtheta0",
         "g1": "dJ/dtheta1", "act": "theta :"}
_PERMITE = {"hip": ("theta0", "theta1", "x"), "e": ("yh", "y", "x"),
            "coef": ("m",), "algo": ("e", "yh", "y", "x"),
            "act": ("theta", "alfa", "dj")}


def _ftxt(k):
    if k == "umbral":
        return "Aprobado si yh >= " + _n(_FN["umbral"])
    v = _FN[k]
    if k in ("J", "g0", "g1"):            # (coef, algo); los nodos
        return "{} = {} sum({})".format(  # tambien son tuplas
            _LADO[k], _tx(v[0], {}), _tx(v[1], {}))
    return _LADO[k] + "= " + _tx(v, {}) if k == "act" else \
        _LADO[k] + " = " + _tx(v, {})


def _formulas():
    """Todas las formulas juntas. Enter = son iguales a tu examen;
    su numero = editarla; 0 = volver a las del curso."""
    while True:
        print("")
        print("== FORMULAS (checa tu examen) ==")
        for i in range(len(_ORDEN)):
            print("{} {}".format(i + 1, _ftxt(_ORDEN[i])))
        print("0 volver a las del curso")
        s = input("Iguales? enter = si / # = editar: ").strip()
        if s == "":
            return
        if s == "0":
            _curso()
            continue
        try:
            i = int(s)
        except ValueError:
            i = 0
        if 1 <= i <= len(_ORDEN):
            _edita(_ORDEN[i - 1])
        else:
            print("Ese numero no esta en la lista.")


def _lee_formula(nombre, actual, permite):
    """Pide una formula como texto; enter = dejar la actual."""
    print("Variables: " + ", ".join([_NOMBRE.get(v, v) for v in permite]))
    while True:
        s = input("{} [{}]: ".format(nombre, actual)).strip()
        if s == "":
            return actual
        try:
            malas = [v for v in _vars(_parse(s), []) if v not in permite]
        except Exception as err:
            print("No entendi: " + str(err))
            continue
        if malas:
            print("Aqui no se usa '{}'.".format(_NOMBRE.get(malas[0],
                                                            malas[0])))
            continue
        return s


def _edita(k):
    if k == "umbral":
        _FT[k] = _lee_numero("Calificacion minima para aprobar", _FT[k])
    elif k in ("J", "g0", "g1"):
        print("-- {} = coef sum(algo) --".format(_LADO[k]))
        print("Ej: coef 1/(2m), algo e^2")
        coef = _lee_formula("coef", _FT[k][0], _PERMITE["coef"])
        algo = _lee_formula("algo", _FT[k][1], _PERMITE["algo"])
        _FT[k] = (coef, algo)
    else:
        print("-- " + _ftxt(k) + " --")
        nombre = "theta :=" if k == "act" else _LADO[k]
        _FT[k] = _lee_formula(nombre, _FT[k], _PERMITE[k])
    _compila()


# ---------- para usar directo en el shell ----------

def gradiente(xs, ys, theta0, theta1, alfa, n=2):
    """gradiente([1,2,3,4], [35,50,68,87], 5, 8, 0.02, 2)"""
    _nueva()
    t0, t1 = _gd([_a(v) for v in xs], [_a(v) for v in ys],
                 _a(theta0), _a(theta1), _a(alfa), n)
    return _f(t0), _f(t1)


def costo(xs, ys, theta0, theta1):
    """J(theta) con la formula activa, sin imprimir."""
    return _f(_valor_suma("J", _filas([_a(v) for v in xs],
                                      [_a(v) for v in ys],
                                      _a(theta0), _a(theta1))))


def tabla_costo(xs, ys, theta0, theta1):
    """Procedimiento, tabla y J con unos theta (sin actualizar)."""
    _nueva()
    return _f(_tabla_costo([_a(v) for v in xs], [_a(v) for v in ys],
                           _a(theta0), _a(theta1)))


def predice(theta0, theta1, x):
    """yh con la hipotesis activa y si aprueba."""
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
        "Aprobado si yh >= 70.",
        "x fuera del rango de los datos:",
        "es extrapolar, menos confiable.",
        "Con pocas iteraciones J sigue alto",
        "y la prediccion puede quedar baja.",
    ]),
    ("En papel", "Como escribirlo en el examen", [
        "theta = letra theta, yh = y gorro,",
        "sum = sigma, alfa = letra alfa.",
        "Escribe: formula, sustitucion,",
        "operaciones y resultado.",
        "Ej: J1 = 1/(2m) sum(yh - y)^2",
        "= 1/8(5346) = 668.25",
        "Siempre compara J y concluye.",
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

def _lee(t):
    """Numero tecleado, exacto: 0.02, -3, 1/50, 2^3 (sin eval)."""
    t = t.strip()
    try:
        return _dec(t)
    except ValueError:
        return _ev(_parse(t), {})


def _pregunta(texto, previo):
    """Hace la pregunta; si hay dato anterior lo muestra en [ ]."""
    if previo is None:
        return input(texto + ": ").strip()
    return input("{} [{}]: ".format(texto, previo)).strip()


def _pide(texto, clave, default=None):
    """Lee un numero y lo recuerda en _D[clave] para el siguiente enter."""
    v = _lee_numero(texto, _D.get(clave, default))
    _D[clave] = v
    return v


def _lee_numero(texto, previo):
    """Lee un numero. Enter = lo de [ ]. Si no se entiende, repite."""
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
            return _lee(s)
        except Exception:
            print("No entendi. Ej: 5, 0.02, -3, 1/50")


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
            print("2 Solo prediccion y costo J")
            print("3 Predecir y (aprobado si >= {})".format(
                _n(_FN["umbral"])))
            print("4 Conceptos para explicar")
            print("5 Ver o editar formulas")
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
        _formulas()
        print("-- RESOLVER: datos --")
        xs, ys = _datos()
        t0 = _pide("theta0 inicial", "t0")
        t1 = _pide("theta1 inicial", "t1")
        alfa = _pide("Tasa de aprendizaje alfa", "alfa")
        n = _pide_entero("Cuantas iteraciones", "n", (2, 1))
        _nueva()
        _D["f0"], _D["f1"] = _gd(xs, ys, t0, t1, alfa, n)
    elif op == "2":
        print("-- PREDICCION Y COSTO: datos --")
        xs, ys = _datos()
        t0 = _pide("theta0 a evaluar", "f0", _D.get("t0"))
        t1 = _pide("theta1 a evaluar", "f1", _D.get("t1"))
        _nueva()
        _tabla_costo(xs, ys, t0, t1)
    elif op == "3":
        print("-- PREDECIR: datos --")
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
    elif op == "5":
        _formulas()
    else:
        print("Esa opcion no existe (0 a 5).")


_curso()
ia()
