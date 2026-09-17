# ia - regresion lineal con gradiente descendente (IA PrepaTEC)
# Adrian. Corre el programa y sigue las preguntas: pide los datos en el
# orden del examen y da cada respuesta con su procedimiento para copiar.
#
# Formulas del curso (arranca con estas). Cada una se muestra justo donde
# aparece en el examen; enter = igual, n = no y se escribe como en la hoja:
#   h(x) = theta0 + theta1*x        e = yh - y
#   J = 1/(2m) sum(e^2)
#   dJ/dtheta0 = 1/m sum(e)         dJ/dtheta1 = 1/m sum(e*x)
#   theta := theta - alfa*dJ/dtheta (los DOS con los theta viejos)
#   aprobado si yh >= 70
#
# Cuentas EXACTAS con fracciones de enteros largos: nada se redondea
# ni se mete ruido binario. En pantalla salen hasta 12 cifras; si hay
# mas, se corta y termina en '...'.
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


def _cmp(a, b):
    """-1, 0 o 1 segun a < b, a == b, a > b."""
    d = a[0] * b[1] - b[0] * a[1]
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
            numero = ("n", s[i:j])
            if t and t[-1] == ("o", "/") and j < len(s) and s[j].isalpha():
                # 1/2m se lee 1/(2m), como en papel
                k = j
                while k < len(s) and (s[k].isalpha() or s[k].isdigit()):
                    k += 1
                nombre = s[j:k]
                t.extend([("o", "("), numero,
                          ("v", _ALIAS.get(nombre, nombre)), ("o", ")")])
                i = k
            else:
                t.append(numero)
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


def _tx(nodo, env, textos=None):
    """La formula escrita con los valores de env sustituidos:
    theta0 + theta1*x -> 5 + 8(1);  e^2 -> (-22)^2;  1/(2m) -> 1/(2(4)).
    textos cambia una variable por un texto (sum -> [484 + 841...])."""
    k = nodo[0]
    if k == "n":
        return nodo[2]
    if k == "v":
        if textos and nodo[1] in textos:
            return textos[nodo[1]]
        if nodo[1] in env:
            s = _n(env[nodo[1]])
            return "(" + s + ")" if s.startswith("-") else s
        return _NOMBRE.get(nodo[1], nodo[1])
    if k == "p":
        return "(" + _tx(nodo[1], env, textos) + ")"
    if k == "u":
        s = _tx(nodo[1], env, textos)
        return "-(" + s + ")" if s.startswith("-") else "-" + s
    op, a, b = nodo[1], nodo[2], nodo[3]
    izq, der = _tx(a, env, textos), _tx(b, env, textos)
    if op in ("+", "-"):
        return izq + " " + op + " " + der
    if op in ("*", ""):
        if textos and b[0] == "v" and b[1] in textos:
            return izq + der if der[:1] in "([" else izq + " " + der
        if b[0] == "v" and b[1] in env and not der.startswith("("):
            der = "(" + der + ")"                     # 8(1)
        pegado = der[:1] in "([" or (
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


# Formulas activas como texto (_FT) y ya leidas (_FN).
_CURSO = {"hip": "theta0 + theta1*x", "e": "yh - y",
          "J": "1/(2m) sum(e^2)", "g0": "1/m sum(e)",
          "g1": "1/m sum(e*x)", "act": "theta - alfa*dJ/dtheta",
          "umbral": (70, 1)}
_SUMAS = ("J", "g0", "g1")
_PERMITE = {"hip": ("theta0", "theta1", "x"), "e": ("yh", "y", "x"),
            "act": ("theta", "alfa", "dj")}
_ALGO = ("e", "yh", "y", "x")
_FT = {}
_FN = {}


def _revisa(nodo, permite):
    for v in _vars(nodo, []):
        if v not in permite:
            raise ValueError("aqui no va '" + _NOMBRE.get(v, v) + "'")


def _separa_sum(texto):
    """'1/(2m) sum(e^2)' -> ('1/(2m) sum', 'e^2')."""
    s = texto.lower().replace("[", "(").replace("]", ")")
    s = s.replace("sum (", "sum(")
    i = s.find("sum(")
    if i < 0 or s.find("sum(", i + 1) >= 0:
        raise ValueError("escribe una vez sum( ... )")
    nivel = 0
    for j in range(i + 3, len(s)):
        if s[j] == "(":
            nivel += 1
        elif s[j] == ")":
            nivel -= 1
            if nivel == 0:
                return s[:i] + " sum " + s[j + 1:], s[i + 4:j]
    raise ValueError("falta cerrar sum( )")


def _lee_una(k, texto):
    """Lee y revisa la formula k; truena con un mensaje si esta mal."""
    if k in _SUMAS:
        fuera, algo = _separa_sum(texto)
        fuera, algo = _parse(fuera), _parse(algo)
        _revisa(fuera, ("m", "sum"))
        _revisa(algo, _ALGO)
        return (fuera, algo)
    nodo = _parse(texto)
    _revisa(nodo, _PERMITE[k])
    return nodo


def _compila():
    for k in _FT:
        if k == "umbral":
            _FN[k] = _FT[k]
        else:
            _FN[k] = _lee_una(k, _FT[k])


def _curso():
    for k in _CURSO:
        _FT[k] = _CURSO[k]
    _compila()


# ---------- pantalla ----------

def _n(a):
    """Como en papel y exacto: 9.985, -99.25, 13. Mas de 12 cifras: '...'."""
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


def _cadena(lado, k, filas):
    """Imprime la formula con sum() como en papel y regresa el valor:
    J1 = 1/(2m) sum(e^2) = 1/(2(4))[(-22)^2 + ...]
       = 1/8(484 + ...) = 1/8(5346) = 668.25"""
    fuera, algo = _FN[k]
    m = (len(filas), 1)
    sust = []
    vals = []
    S = (0, 1)
    for f in filas:
        env = _env_fila(f)
        v = _ev(algo, env)
        vals.append(_n(v))
        sust.append(_n(v) if algo[0] == "v" else _tx(algo, env))
        S = _mas(S, v)
    total = _ev(fuera, {"m": m, "sum": S})
    c = _ev(fuera, {"m": m, "sum": (1, 1)})
    lineal = (_ev(fuera, {"m": m, "sum": (0, 1)}) == (0, 1) and
              _ev(fuera, {"m": m, "sum": (2, 1)}) == _por((2, 1), c))
    envm = {"m": m}
    pasos = [_tx(fuera, {}, {"sum": "sum(" + _tx(algo, {}) + ")"})]
    if sust != vals:
        pasos.append(_tx(fuera, envm, {"sum": "[" + _junta_txt(sust) + "]"}))
    else:
        pasos.append(_tx(fuera, envm, {"sum": "(" + _junta_txt(vals) + ")"}))
    if lineal:
        pasos.append(_fr(c) + "(" + _junta_txt(vals) + ")")
        pasos.append(_fr(c) + "(" + _n(S) + ")")
    else:
        pasos.append(_tx(fuera, envm, {"sum": "(" + _n(S) + ")"}))
    pasos.append(_n(total))
    _pasos(lado, pasos)
    return total


def _bloque_pred(t0, t1, filas, r_hip, r_yh, r_e):
    """h(x), cada yh, cada e y la tabla, como en el examen."""
    hip = _FN["hip"]
    envt = {"theta0": t0, "theta1": t1}
    if r_hip:
        _out(r_hip)
    _out("h(x) = " + _tx(hip, {}), "h(x) = " + _tx(hip, envt))
    if r_yh:
        _out(r_yh)
    for i in range(len(filas)):
        envt["x"] = filas[i][0]
        _pasos("yh" + str(i + 1), [_tx(hip, envt), _n(filas[i][2])])
    _pausa()
    if r_e:
        _out(r_e)
    _out("e = " + _tx(_FN["e"], {}))
    for i in range(len(filas)):
        x, y, yh, e = filas[i]
        _pasos("e" + str(i + 1),
               [_tx(_FN["e"], {"yh": yh, "y": y, "x": x}), _n(e)])
    _pausa()
    t = ["Tabla:", "x | y | yh | e"]
    for x, y, yh, e in filas:
        t.append("{} | {} | {} | {}".format(_n(x), _n(y), _n(yh), _n(e)))
    _out(*t)
    _pausa()


def _bloque_act(filas, t0, t1, alfa):
    """Derivadas y nuevos theta (simultaneo). Regresa los theta nuevos."""
    _out("Derivadas (con los theta viejos):")
    g0 = _cadena("dJ/dtheta0", "g0", filas)
    g1 = _cadena("dJ/dtheta1", "g1", filas)
    _pausa()
    act = _FN["act"]
    e0 = {"theta": t0, "alfa": alfa, "dj": g0}   # simultanea: los dos
    e1 = {"theta": t1, "alfa": alfa, "dj": g1}   # con t0, t1 viejos
    n0 = _ev(act, e0)
    n1 = _ev(act, e1)
    _out("Nuevos parametros (simultaneo):",
         "theta := " + _tx(act, {}))
    _pasos("theta0", [_tx(act, e0), _n(n0)])
    _pasos("theta1", [_tx(act, e1), _n(n1)])
    _pausa()
    return n0, n1


def _decision(k, J, Jprev):
    c = _cmp(J, Jprev)
    signo = "<" if c < 0 else (">" if c > 0 else "=")
    _out("J{} = {} {} J{} = {}".format(k, _n(J), signo, k - 1, _n(Jprev)))
    if c < 0:
        _out("Si mejoro el modelo: J bajo",
             "(el error es mas chico).")
    elif c > 0:
        _out("No mejoro: J subio. Revisa alfa",
             "o las formulas.")
    else:
        _out("J no cambio.")


def _estimar(t0, t1, x):
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


# ---------- preguntas ----------

def _pregunta(texto, previo):
    """Hace la pregunta; si hay dato anterior lo muestra en [ ]."""
    if previo is None:
        return input(texto + ": ").strip()
    return input("{} [{}]: ".format(texto, previo)).strip()


def _lee(t):
    """Numero tecleado, exacto: 0.02, -3, 1/50, 2^3 (sin eval)."""
    t = t.strip()
    try:
        return _dec(t)
    except ValueError:
        return _ev(_parse(t), {})


def _lee_numero(texto, previo):
    """Lee un numero. Enter = lo de [ ]. Si no se entiende, repite."""
    while True:
        s = _pregunta(texto, None if previo is None else _n(previo))
        if s == "":
            if previo is not None:
                return previo
            print("Falta este dato.")
            continue
        try:
            return _lee(s)
        except Exception:
            print("No entendi. Ej: 5, 0.02, -3, 1/50")


def _pide(texto, clave, default=None):
    """Lee un numero y lo recuerda en _D[clave] para el siguiente enter."""
    v = _lee_numero(texto, _D.get(clave, default))
    _D[clave] = v
    return v


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


def _si_no(texto):
    """enter o s = si (True); n = no (False)."""
    while True:
        s = input(texto).strip().lower()
        if s in ("", "s", "si"):
            return True
        if s in ("n", "no"):
            return False
        print("Escribe solo enter (si) o n (no).")


# ---------- formulas: se confirman donde las pide el examen ----------

_LADO = {"hip": "h(x)", "e": "e", "J": "J", "g0": "dJ/dtheta0",
         "g1": "dJ/dtheta1", "act": "theta :"}
_AYUDA = {"hip": ("theta0, theta1, x", "theta0 + theta1*x"),
          "e": ("yh, y, x", "yh - y"),
          "J": ("m, sum( ), e, yh, y, x", "1/(2m) sum(e^2)"),
          "g0": ("m, sum( ), e, yh, y, x", "1/m sum(e)"),
          "g1": ("m, sum( ), e, yh, y, x", "1/m sum(e*x)"),
          "act": ("theta, alfa, dJ/dtheta", "theta - alfa*dJ/dtheta")}


def _ftxt(k):
    if k == "umbral":
        return "Aprobado si yh >= " + _n(_FN["umbral"])
    v = _FN[k]
    if k in _SUMAS:
        return _LADO[k] + " = " + _tx(v[0], {}, {
            "sum": "sum(" + _tx(v[1], {}) + ")"})
    if k == "act":
        return "theta := " + _tx(v, {})
    return _LADO[k] + " = " + _tx(v, {})


def _confirma(claves, titulo):
    """Muestra las formulas como van en el examen y pregunta si son
    iguales. Si no, deja escribir la del examen."""
    while True:
        print("")
        print(titulo)
        if len(claves) == 1:
            print(_ftxt(claves[0]))
            if _si_no("Igual a tu examen? enter=si, n=no: "):
                return
            _edita(claves[0])
        else:
            for i in range(len(claves)):
                print("{} {}".format(i + 1, _ftxt(claves[i])))
            if _si_no("Iguales a tu examen? enter=si,n=no: "):
                return
            s = input("Cual es distinta? (1 a {}): ".format(len(claves)))
            try:
                i = int(s.strip())
            except ValueError:
                i = 0
            if 1 <= i <= len(claves):
                _edita(claves[i - 1])


def _edita(k):
    if k == "umbral":
        print("-- Cambiar calificacion minima --")
        _FT[k] = _lee_numero("Aprobado si yh >=", _FT[k])
        _compila()
        return
    usa, ej = _AYUDA[k]
    print("-- Escribela como en tu examen --")
    print("Puedes usar: " + usa)
    print("Ej: " + ej)
    nombre = "theta :=" if k == "act" else _LADO[k] + " ="
    while True:
        s = input("{} [{}]: ".format(nombre, _FT[k])).strip()
        if s == "":
            return
        try:
            _FN[k] = _lee_una(k, s)
        except Exception as err:
            print("No entendi: " + str(err))
            continue
        _FT[k] = s
        return


def _formulas():
    """Opcion del menu: ver todas y cambiar la que sea."""
    claves = ["hip", "e", "J", "g0", "g1", "act", "umbral"]
    while True:
        print("")
        print("== FORMULAS QUE SE USAN ==")
        for i in range(len(claves)):
            print("{} {}".format(i + 1, _ftxt(claves[i])))
        print("0 volver a las del curso")
        s = input("Numero a cambiar (enter=menu): ").strip()
        if s == "":
            return
        if s == "0":
            _curso()
            continue
        try:
            i = int(s)
        except ValueError:
            i = 0
        if 1 <= i <= len(claves):
            _edita(claves[i - 1])
        else:
            print("Ese numero no esta en la lista.")


# ---------- el examen paso a paso ----------

def _datos():
    print("Separa los valores con comas.")
    xs = _pide_lista("x de la tabla (ej 1,2,3,4)", "xs")
    while True:
        ys = _pide_lista("y de la tabla (ej 35,50,68,87)", "ys")
        if len(ys) == len(xs):
            break
        print("Pusiste {} valores de x y {} de y;".format(len(xs),
                                                          len(ys)))
        print("deben ser los mismos. Otra vez y.")
    _D["xs"], _D["ys"] = xs, ys
    return xs, ys


def _transferencia(t0, t1, titulo, confirmar_modelo):
    _nueva()
    _out(titulo, "Usa los theta que da el examen",
         "(pueden venir redondeados).")
    _pausa()
    t0 = _pide("theta0 para estimar", "f0", t0)
    t1 = _pide("theta1 para estimar", "f1", t1)
    if confirmar_modelo:
        _confirma(["hip"], "Modelo que da tu examen:")
    _confirma(["umbral"], "Regla para aprobar:")
    print("")
    print("a) Estimar la calificacion:")
    x = _pide("x a estimar (ej 5)", "xn")
    while True:
        _nueva()
        _estimar(t0, t1, x)
        _pausa()
        s = input("Otra x? (escribela o enter=no): ").strip()
        if s == "":
            break
        try:
            x = _lee(s)
        except Exception:
            print("No entendi; sigo.")
            break
    _nueva()
    _out("b) Tipo de problema (justifica):",
         "Es CLASIFICACION binaria: la",
         "salida es una clase (aprobado o",
         "no aprobado), no un numero.",
         "Es aprendizaje SUPERVISADO: los",
         "datos vienen etiquetados.",
         "(Estimar calificacion = REGRESION)")
    _pausa()


def _examen():
    _nueva()
    _out("== RESOLVER EXAMEN ==",
         "Te pido los datos en el orden",
         "del examen y te doy cada respuesta",
         "con su procedimiento para copiar.",
         "- Escribe el dato y enter.",
         "- Lo que sale en [ ] se usa con",
         "  solo enter.")
    _pausa()

    print("")
    print("== DATOS DEL EXAMEN ==")
    print("Copia la tabla del examen.")
    xs, ys = _datos()
    _confirma(["hip"], "Modelo que da tu examen:")
    print("")
    print("Parametros iniciales:")
    t0 = _pide("theta0 (ej 5)", "t0")
    t1 = _pide("theta1 (ej 8)", "t1")
    print("Tasa de aprendizaje:")
    alfa = _pide("alfa (ej 0.02)", "alfa")

    _confirma(["e"], "Formula del error e:")
    _nueva()
    _out("== PASO 1: PREDICCION Y ERRORES ==")
    filas = _filas(xs, ys, t0, t1)
    _bloque_pred(t0, t1, filas, "a) Hipotesis con theta iniciales:",
                 "b) Predicciones yh:", "c) Errores:")

    _confirma(["J"], "Formula de la funcion de costo:")
    _nueva()
    _out("== PASO 2: FUNCION DE COSTO ==")
    Js = [_cadena("J1", "J", filas)]
    _out("Que resume: el error de la hipotesis",
         "actual sobre los datos reales.")
    _pausa()

    _confirma(["g0", "g1", "act"], "Formulas de la actualizacion:")
    _nueva()
    _out("== PASO 3: PRIMERA ACTUALIZACION ==")
    t0, t1 = _bloque_act(filas, t0, t1, alfa)

    k = 2
    while True:
        filas = _filas(xs, ys, t0, t1)
        if k == 2:
            _out("== PASO 4: SEGUNDA ITERACION ==")
        else:
            _out("== ITERACION {} ==".format(k))
        _out("a) Nuevas predicciones y J{}:".format(k))
        _bloque_pred(t0, t1, filas, None, None, None)
        Js.append(_cadena("J" + str(k), "J", filas))
        _pausa()
        _out("b) Comparar J{} con J{}:".format(k, k - 1))
        _decision(k, Js[-1], Js[-2])
        _pausa()
        _out("c) Actualizacion {}:".format(k))
        t0, t1 = _bloque_act(filas, t0, t1, alfa)
        otra = input("Otra iteracion? s=si, enter=no: ").strip().lower()
        if otra not in ("s", "si"):
            break
        k += 1

    _D["f0"], _D["f1"] = t0, t1
    _transferencia(t0, t1, "== PASO 5: TRANSFERENCIA ==", False)

    _nueva()
    _out("== REVISION FINAL ==")
    for i in range(len(Js)):
        _out("J{} = {}".format(i + 1, _n(Js[i])))
    d = _menos(Js[0], Js[-1])
    c = _cmp(Js[-1], Js[0])
    if c < 0:
        _out("J{} < J1: bajo {}".format(len(Js), _n(d)),
             "Conclusion: las actualizaciones",
             "mejoraron el modelo (J bajo).")
    elif c > 0:
        _out("J{} > J1: subio".format(len(Js)),
             "Conclusion: no mejoro; revisa",
             "alfa o las formulas.")
    else:
        _out("Conclusion: J no cambio.")
    _out("theta0 final = " + _n(t0), "theta1 final = " + _n(t1))
    _pausa()


def _instrucciones():
    _nueva()
    _out("== INSTRUCCIONES ==",
         "1 Resolver: te pregunta los datos",
         "  en el orden del examen y da las",
         "  respuestas con procedimiento.",
         "2 Estimar: calificacion con los",
         "  theta dados y si aprueba.",
         "3 Conceptos: para explicar.",
         "4 Formulas: ver o cambiar.")
    _out("Al escribir: enter confirma; lo",
         "de [ ] se usa con solo enter.",
         "Fracciones: 1/50. Potencia: x^2.",
         "En papel: theta = letra theta,",
         "yh = y gorro, sum = sigma.")
    _pausa()


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
    ("Estimar", "Usar el modelo (estimar)", [
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
        s = input("Numero de tema (enter=menu): ").strip()
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
            print("Ese tema no existe (1 a {}).".format(total))


# ---------- menu ----------

def ia():
    try:
        while True:
            print("")
            print("== IA: REGRESION LINEAL ==")
            print("1 Resolver examen paso a paso")
            print("2 Solo estimar calificacion")
            print("3 Conceptos para explicar")
            print("4 Ver o cambiar formulas")
            print("5 Instrucciones")
            print("0 Salir")
            op = input("Escribe el numero y enter: ").strip()
            if op == "0":
                break
            try:
                if op == "1":
                    _examen()
                elif op == "2":
                    _transferencia(_D.get("f0"), _D.get("f1"),
                                   "== ESTIMAR CALIFICACION ==", True)
                elif op == "3":
                    _conceptos()
                elif op == "4":
                    _formulas()
                elif op == "5":
                    _instrucciones()
                else:
                    print("Escribe un numero del 0 al 5.")
            except Exception as err:
                print("Algo fallo: " + str(err))
    except KeyboardInterrupt:
        pass
    print("Para abrir otra vez: ia()")


_curso()
ia()
