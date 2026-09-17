# ia - regresion lineal con gradiente descendente (IA PrepaTEC)
# Adrian. Corre el programa y sigue las preguntas: pide los datos en el
# orden del examen y da cada respuesta con su procedimiento para copiar.
#
# Formulas del curso, escritas como en el examen (arranca con estas).
# Cada una se muestra justo donde aparece; enter = igual, n = no y se
# escribe como en la hoja:
#   h(x) = theta0 + theta1*x        e = yh - y
#   J = 1/(2m) sum(yh - y)^2        (suma de los cuadrados)
#   dJ/dtheta0 = 1/m sum(yh - y)    dJ/dtheta1 = 1/m sum[(yh - y)x]
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
_GRANDE = 10 ** 3000   # mas grande que esto ya no es de examen

_MAXIMO = 18   # un decimal que termina en hasta 18 cifras sale completo
_NB = "\x01"   # espacio que no se corta (dentro de un termino)

_D = {}        # ultimos datos tecleados: enter = reusarlos
_lin = 0       # renglones impresos desde la ultima pausa
_abierto = None  # PROCEDIMIENTO en curso (para '-- sigue ... --')
_cab = None      # encabezado que espera a su primer renglon
_sigue = False   # hubo pausa con un procedimiento abierto


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
    sin_signos = t.lstrip("+-")
    neg = t[:len(t) - len(sin_signos)].count("-") % 2 == 1
    t = sin_signos
    if t.count(".") > 1:
        raise ValueError("numero con dos puntos: " + t)
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

_ALIAS = {"t0": "theta0", "t1": "theta1", "alpha": "alfa",
          "yhat": "yh", "ygorro": "yh"}
_NOMBRE = {"dj": "dJ/dtheta"}


def _letra(c):
    return c.isalpha() or c.isdigit() or c == "_"


def _cierra(s, i):
    """Indice del ')' que cierra el '(' en s[i]; -1 si no hay."""
    nivel = 0
    for j in range(i, len(s)):
        if s[j] == "(":
            nivel += 1
        elif s[j] == ")":
            nivel -= 1
            if nivel == 0:
                return j
    return -1


def _sin_espacios(s, i):
    while i < len(s) and s[i] == " ":
        i += 1
    return i


def _tokens(s):
    s = s.lower().replace("**", "^").replace("[", "(").replace("]", ")")
    while " /" in s or "/ " in s:
        s = s.replace(" /", "/").replace("/ ", "/")
    s = s.replace("dj/dtheta", "dj")
    t = []
    cierres = []          # donde cerrar el ( que abre la regla 1/2m
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
            k = _sin_espacios(s, j)
            if t and t[-1] == ("o", "/") and k < len(s):
                # 1/2m, 1/2 m y 1/2(m) se leen 1/(2m), como en papel
                if s[k].isalpha():
                    fin = k
                    while fin < len(s) and _letra(s[fin]):
                        fin += 1
                    nombre = s[k:fin]
                    sig = _sin_espacios(s, fin)
                    if nombre != "sum" and not (sig < len(s)
                                                and s[sig] == "^"):
                        t.extend([("o", "("), numero,
                                  ("v", _ALIAS.get(nombre, nombre)),
                                  ("o", ")")])
                        i = fin
                        continue
                elif s[k] == "(":
                    fin = _cierra(s, k)
                    sig = _sin_espacios(s, fin + 1)
                    if fin > 0 and not (sig < len(s) and s[sig] == "^"):
                        t.extend([("o", "("), numero])
                        cierres.append(fin)
                        i = k
                        continue
            t.append(numero)
            i = j
        elif c.isalpha() or c == "_":
            j = i
            while j < len(s) and _letra(s[j]):
                j += 1
            nombre = s[i:j]
            t.append(("v", _ALIAS.get(nombre, nombre)))
            i = j
        elif c in "+-*/^()":
            t.append(("o", c))
            while c == ")" and i in cierres:
                cierres.remove(i)
                t.append(("o", ")"))
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
            elif k[0] == "v" or k == ("o", "("):
                nodo = ("b", "", nodo, self.potencia())
            elif k[0] == "n":
                raise ValueError("falta un signo antes de " + k[1])
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
        r = _mas(a, b)
    elif op == "-":
        r = _menos(a, b)
    elif op == "/":
        r = _entre(a, b)
    elif op != "^":
        r = _por(a, b)
    else:
        if b[1] != 1 or abs(b[0]) > 50:
            raise ValueError("la potencia debe ser entera (-50 a 50)")
        base = a if b[0] >= 0 else _entre((1, 1), a)
        r = (1, 1)
        for _ in range(abs(b[0])):
            r = _por(r, base)
    if abs(r[0]) > _GRANDE or r[1] > _GRANDE:
        raise ValueError("numero demasiado grande")
    return r


def _revisa_pot(nodo):
    """Las potencias deben ser numeros enteros fijos (e^2, no y^-y)."""
    if nodo[0] in ("p", "u"):
        _revisa_pot(nodo[1])
    elif nodo[0] == "b":
        if nodo[1] == "^":
            if _vars(nodo[3], []):
                raise ValueError("la potencia debe ser un numero, ej e^2")
            v = _ev(nodo[3], {})
            if v[1] != 1 or abs(v[0]) > 50:
                raise ValueError("la potencia debe ser entera (-50 a 50)")
        _revisa_pot(nodo[2])
        _revisa_pot(nodo[3])


def _tx(nodo, env, textos=None):
    """La formula escrita con los valores de env sustituidos:
    theta0 + theta1*x -> 5 + 8(1);  (yh - y)^2 -> (-22)^2;
    1/(2m) -> 1/(2(4)). textos cambia una variable por un texto."""
    k = nodo[0]
    if "e" in env and k != "v" and nodo == _FN.get("e"):
        return _n(env["e"])            # (yh - y) se escribe con su valor
    if k == "n":
        return nodo[2]
    if k == "v":
        if textos and nodo[1] in textos:
            return textos[nodo[1]]
        if nodo[1] in env:
            s = _n(env[nodo[1]])
            return "(" + s + ")" if s.startswith("-") or "e+" in s else s
        return _NOMBRE.get(nodo[1], nodo[1])
    if k == "p":
        return "(" + _tx(nodo[1], env, textos) + ")"
    if k == "u":
        s = _tx(nodo[1], env, textos)
        return "-(" + s + ")" if s.startswith("-") else "-" + s
    op, a, b = nodo[1], nodo[2], nodo[3]
    izq, der = _tx(a, env, textos), _tx(b, env, textos)
    if op in ("+", "-"):
        if a[0] == "v" and a[1] in env and izq.startswith("(-"):
            izq = izq[1:-1]                           # -2.5 + 8x
        return izq + " " + op + " " + der
    if op in ("*", ""):
        if textos and b[0] == "v" and b[1] == "sum":
            return izq + der if der[:1] in "([" else izq + " " + der
        if b[0] == "v" and b[1] in env and not der.startswith("("):
            der = "(" + der + ")"                     # 8(1)
        suelta = b[0] == "v" and b[1] not in env
        pegado = der[:1] in "([" or (suelta and (
            a[0] in ("n", "p") or (a[0] == "v" and a[1] in env)))
        return izq + der if pegado else izq + "*" + der
    return izq + op + der


def _fr(a):
    """Fraccion como en papel: 1/8, -3/4, 5."""
    if a[1] == 1:
        return str(a[0])
    return str(a[0]) + "/" + str(a[1])


def _terminos(nodo, env):
    """'5 + 0.7' o '6.287 + 58.185': cada termino ya evaluado."""
    if nodo[0] == "b" and nodo[1] in ("+", "-"):
        v = _ev(nodo[3], env)
        op = nodo[1]
        if v[0] < 0:
            v = (-v[0], v[1])
            op = "+" if op == "-" else "-"
        return _terminos(nodo[2], env) + " " + op + " " + _n(v)
    return _n(_ev(nodo, env))


# Formulas activas como texto (_FT) y ya leidas (_FN).
_CURSO = {"hip": "theta0 + theta1*x", "e": "yh - y",
          "J": "1/(2m) sum(yh - y)^2", "g0": "1/m sum(yh - y)",
          "g1": "1/m sum[(yh - y)x]", "act": "theta - alfa*dJ/dtheta",
          "umbral": (70, 1)}
_SUMAS = ("J", "g0", "g1")
_PERMITE = {"hip": ("theta0", "theta1", "x"), "e": ("yh", "y", "x"),
            "act": ("theta", "alfa", "dj")}
_ALGO = ("e", "yh", "y", "x")
_FT = {}
_FN = {}


def _revisa(nodo, permite, fuera=False):
    for v in _vars(nodo, []):
        if v in permite:
            continue
        nombre = _NOMBRE.get(v, v)
        if fuera and v in _ALGO:
            raise ValueError("'" + v + "' va dentro de sum( )")
        if "theta" in permite and v in ("theta0", "theta1", "dj0", "dj1"):
            raise ValueError("usa theta y dJ/dtheta (sirve para los 2)")
        for p in permite:
            if v.startswith(p) and len(p) > 1:
                raise ValueError("falta * en '" + nombre + "' (ej 8*x)")
        raise ValueError("aqui no va '" + nombre + "'")


def _separa_sum(texto):
    """'1/(2m) sum(yh - y)^2' -> ('1/(2m) sum', '(yh - y)^2').
    Como en papel, el ^ pegado a sum( ) es de cada termino."""
    s = texto.lower().replace("[", "(").replace("]", ")").replace("**", "^")
    while " (" in s:                  # sum (e^2), sum   (e^2)
        s = s.replace(" (", "(")
    i = s.find("sum(")
    if i < 0:
        if "sum" in s:
            raise ValueError("escribe sum( ... ) con parentesis")
        raise ValueError("falta sum( ... )")
    if s.find("sum(", i + 1) >= 0:
        raise ValueError("sum( ) va una sola vez")
    j = _cierra(s, i + 3)
    if j < 0:
        raise ValueError("falta cerrar sum( )")
    algo = s[i + 4:j]
    resto = s[j + 1:]
    r = resto.lstrip()
    if r.startswith("^"):
        k = _sin_espacios(r, 1)
        if k < len(r) and r[k] == "(":
            fin = _cierra(r, k) + 1
        else:
            fin = k + 1 if k < len(r) and r[k] == "-" else k
            while fin < len(r) and (r[fin].isdigit() or r[fin] == "."):
                fin += 1
        algo = "(" + algo + ")" + r[:fin]
        resto = r[fin:]
    return s[:i] + " sum " + resto, algo


def _lee_una(k, texto):
    """Lee y revisa la formula k; truena con un mensaje si esta mal."""
    if "=" in texto:
        texto = texto.split("=")[-1]      # quita 'J =' o 'theta :='
    if k in _SUMAS:
        fuera, algo = _separa_sum(texto)
        fuera, algo = _parse(fuera), _parse(algo)
        _revisa(fuera, ("m", "sum"), True)
        _revisa(algo, _ALGO)
        _revisa_pot(fuera)
        _revisa_pot(algo)
        return (fuera, algo)
    nodo = _parse(texto)
    _revisa(nodo, _PERMITE[k])
    _revisa_pot(nodo)
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


def _sum_txt(algo):
    """Como se escribe la suma: sum(yh - y)^2, sum[(yh - y)x], sum(e)."""
    t = _tx(algo, {})
    if algo[0] == "p" or (algo[0] == "b" and algo[1] == "^"
                          and algo[2][0] == "p"):
        return "sum" + t
    if t.startswith("("):
        return "sum[" + t + "]"
    return "sum(" + t + ")"


# ---------- pantalla ----------

def _n(a):
    """Como en papel y exacto: 9.985, -99.25, 13. Si el decimal termina
    en pocas cifras sale completo (1702.352456125); si no, se corta a 12
    cifras y termina en '...'."""
    p, q = a
    if p == 0:
        return "0"
    s = "-" if p < 0 else ""
    p = abs(p)
    ent, r = p // q, p % q
    digs = str(ent)
    if len(digs) > _CIFRAS or (len(digs) == _CIFRAS and r):
        mas = "..." if (r or digs[_CIFRAS:].strip("0")) else ""
        mant = digs[1:_CIFRAS]
        if not mas:
            mant = mant.rstrip("0")
        return s + digs[0] + ("." + mant if mant else "") + mas + \
            "e+" + str(len(digs) - 1)
    s += digs
    if not r:
        return s
    dec = ""
    cifras = len(digs) if ent else 0
    while r and cifras < _MAXIMO:
        r *= 10
        dec += str(r // q)
        r = r % q
        if cifras or dec[-1] != "0":   # los ceros de 0.00x no cuentan
            cifras += 1
    if not r:
        return s + "." + dec             # termina: completo
    corte = ""
    cifras = len(digs) if ent else 0
    for d in dec:
        if cifras >= _CIFRAS:
            break
        corte += d
        if cifras or d != "0":
            cifras += 1
    return s + "." + corte + "..."


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


def _grupo(lineas, maximo):
    """Imprime renglones que van juntos; si no caben, pide enter antes.
    Un encabezado de PROCEDIMIENTO pendiente viaja con su primer grupo, y
    cada pantalla que continua un procedimiento dice '-- sigue ... --'."""
    global _lin, _cab, _sigue
    if _cab:
        lineas = [_cab] + lineas
        _cab = None
    alto = 0
    for s in lineas:
        alto += _alto(s)
    if alto > maximo and len(lineas) > 1:
        if _lin + 3 > _ALTO:
            _pausa()
        for s in lineas:
            _grupo([s], maximo)
        return
    if _lin + alto > _ALTO:
        _pausa()
    if _sigue:
        _sigue = False
        if _abierto and not lineas[0].startswith("-- PROCEDIMIENTO"):
            print("-- sigue PROCEDIMIENTO " + _abierto + " --")
            _lin += 1
    for s in lineas:
        print(s.replace(_NB, " "))
    _lin += alto


def _out(*lineas):
    _grupo(list(lineas), _ALTO - 1)


def _pausa():
    global _lin, _sigue
    if _lin > 0:
        input(_SIGUE)
        _sigue = _abierto is not None
    _lin = 0


def _nueva():
    global _lin, _sigue
    _lin = 0
    _sigue = False


def _parte(pre, txt):
    """pre + txt en renglones de _ANCHO. Corta en los espacios, y un
    signo + o - se pasa al renglon nuevo junto con su numero."""
    if len(pre) + len(txt) <= _ANCHO:
        return [pre + txt]
    palabras = txt.split(" ")
    unidades = []
    i = 0
    while i < len(palabras):
        w = palabras[i]
        if w in ("+", "-", "<", ">", "|", "=") and i + 1 < len(palabras):
            w = w + " " + palabras[i + 1]
            i += 1
        unidades.append(w)
        i += 1
    sangria = " " * min(len(pre), 5)
    lineas = []
    s = pre + unidades[0]
    for u in unidades[1:]:
        if len(s) + 1 + len(u) > _ANCHO:
            lineas.append(s)
            s = sangria + u
        else:
            s += " " + u
    lineas.append(s)
    return lineas


def _pasos(lado, pasos):
    """'J1 = 1/(2m) sum(yh - y)^2 = 1/8(5346) = 668.25' en un renglon si
    cabe; si no, cada '= paso' abajo del anterior. Quita repetidos."""
    limpios = []
    for paso in pasos:
        if not limpios or limpios[-1] != paso:
            limpios.append(paso)
    s = lado + " = " + " = ".join(limpios)
    if len(s) <= _ANCHO:
        _out(s)
        return
    grupos = []
    pre = lado + " = "
    for paso in limpios:
        grupos.append(_parte(pre, paso))
        pre = " " * min(len(lado), 3) + " = "
    todas = []
    for g in grupos:
        todas.extend(g)
    alto = 1 if _cab else 0
    for s in todas:
        alto += _alto(s)
    if alto <= _ALTO - 1:
        _out(*todas)
    else:                       # no cabe: se corta entre un '=' y otro
        for g in grupos:
            _out(*g)


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
    J1 = 1/(2m) sum(yh - y)^2 = 1/(2(4))[(-22)^2 + ...]
       = 1/8(484 + ...) = 1/8(5346) = 668.25"""
    fuera, algo = _FN[k]
    m = (len(filas), 1)
    solo_e = algo[0] == "v" or algo == _FN["e"] or (
        algo[0] == "p" and algo[1] == _FN["e"])
    sust = []
    vals = []
    S = (0, 1)
    for f in filas:
        env = _env_fila(f)
        v = _ev(algo, env)
        vals.append(_n(v))
        if solo_e:
            sust.append(_n(v))
        elif algo[0] == "b" and algo[1] in ("+", "-"):
            sust.append(("(" + _tx(algo, env) + ")").replace(" ", _NB))
        else:
            sust.append(_tx(algo, env).replace(" ", _NB))
        S = _mas(S, v)
    total = _ev(fuera, {"m": m, "sum": S})
    try:
        c = _ev(fuera, {"m": m, "sum": (1, 1)})
        lineal = (_ev(fuera, {"m": m, "sum": (0, 1)}) == (0, 1) and
                  _ev(fuera, {"m": m, "sum": (2, 1)}) == _por((2, 1), c))
    except Exception:
        lineal = False
    envm = {"m": m}
    pasos = [_tx(fuera, {}, {"sum": _sum_txt(algo)})]
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


def _de_curso():
    for k in ("e", "J", "g0", "g1"):
        if _FT[k] != _CURSO[k]:
            return False
    return True


def _proc(num, que):
    """Encabezado del procedimiento; se imprime junto con su primer
    renglon: -- PROCEDIMIENTO 1b: predicciones --"""
    global _abierto, _cab
    s = "-- PROCEDIMIENTO " + num + ": " + que + " --"
    if len(s) > _ANCHO:
        s = s[:-3]
    _abierto = num
    _cab = s


def _remarca(num, textos):
    """La respuesta final de la pregunta o inciso, marcada con su
    numero: RF(1b)= yh = 13, 21, 29, 37"""
    global _abierto, _sigue
    _abierto = None
    _sigue = False
    pre = "RF(" + num + ")= "
    lineas = []
    for t in textos:
        lineas.extend(_parte(pre, t))
    _grupo(lineas, _ALTO)


def _lista(vals):
    return ", ".join([_n(v) for v in vals])


def _bloque_pred(t0, t1, filas, num, tabla_va, j_en, dj_en):
    """h(x), cada yh, cada e y las tablas, como en el examen. Con num
    (paso 1) cada inciso lleva PROCEDIMIENTO 1a/1b/1c y su RESPUESTA."""
    hip = _FN["hip"]
    envt = {"theta0": t0, "theta1": t1}
    marcar = num is not None
    if marcar:
        _proc(num + "a", "hipotesis")
    hx = _tx(hip, envt)
    thetas = "theta0 = {}, theta1 = {}".format(_n(t0), _n(t1))
    _out(*(["h(x) = " + _tx(hip, {})] + _parte("", thetas) +
           _parte("h(x) = ", hx)))
    if marcar:
        _remarca(num + "a", _igualdad("h(x)", _tx(hip, {}), hx) +
                 ["(" + thetas + ")"])
    _pausa()
    if marcar:
        _proc(num + "b", "predicciones")
    _out("yh (yh1 va con el renglon 1):")
    for i in range(len(filas)):
        envt["x"] = filas[i][0]
        _pasos("yh" + str(i + 1), [_tx(hip, envt), _n(filas[i][2])])
    if marcar:
        _remarca(num + "b", ["yh = " + _lista([f[2] for f in filas])])
    _pausa()
    if marcar:
        _proc(num + "c", "errores")
    _out(*_parte("", "e = " + _tx(_FN["e"], {}) +
                 "  (e1 va con renglon 1)"))
    for i in range(len(filas)):
        x, y, yh, e = filas[i]
        _pasos("e" + str(i + 1),
               [_tx(_FN["e"], {"yh": yh, "y": y, "x": x}), _n(e)])
    if marcar:
        _remarca(num + "c", ["e = " + _lista([f[3] for f in filas])])
    _pausa()
    t = ["Tabla (va con " + tabla_va + "):", "x | y | yh | e"]
    for x, y, yh, e in filas:
        t.extend(_parte("", "{} | {} | {} | {}".format(
            _n(x), _n(y), _n(yh), _n(e))))
    _out(*t)
    _pausa()
    if not _de_curso():
        return
    s0 = s2 = s1 = (0, 1)
    renglones = []
    for i in range(len(filas)):
        x, y, yh, e = filas[i]
        e2, ex = _por(e, e), _por(e, x)
        s0, s2, s1 = _mas(s0, e), _mas(s2, e2), _mas(s1, ex)
        renglones.append((str(i + 1), _n(e), _n(e2), _n(ex)))
    renglones.append(("sum", _n(s0), _n(s2), _n(s1)))
    junta = ["Tabla auxiliar (para " + j_en + " y " + dj_en + "):",
             "i | e | e^2 | e*x"]
    cabe = True
    for r in renglones:
        s = " | ".join(r)
        cabe = cabe and len(s) <= _ANCHO
        junta.append(s)
    if cabe:
        _out(*junta)
        _pausa()
        return
    a = ["Tabla aux. A (e^2, para " + j_en + "):", "i | e^2"]
    b = ["Tabla aux. B (e*x, para " + dj_en + "):", "i | e | e*x"]
    for r in renglones:
        a.extend(_parte("", r[0] + " | " + r[2]))
        b.extend(_parte("", r[0] + " | " + r[1] + " | " + r[3]))
    _out(*a)
    _pausa()
    _out(*b)
    _pausa()


def _bloque_act(filas, t0, t1, alfa, num, fuente):
    """Derivadas y nuevos theta (simultaneo). Regresa los theta nuevos."""
    _proc(num, "nuevos theta")
    _out("Derivadas (usa los e de " + fuente + "):")
    g0 = _cadena("dJ/dtheta0", "g0", filas)
    g1 = _cadena("dJ/dtheta1", "g1", filas)
    _pausa()
    act = _FN["act"]
    e0 = {"theta": t0, "alfa": alfa, "dj": g0}   # simultanea: los dos
    e1 = {"theta": t1, "alfa": alfa, "dj": g1}   # con t0, t1 viejos
    n0 = _ev(act, e0)
    n1 = _ev(act, e1)
    _out("Nuevos parametros (simultaneo):")
    _out("theta0 := " + _tx(act, {}, {"theta": "theta0",
                                      "dj": "dJ/dtheta0"}))
    _pasos("theta0", [_tx(act, e0), _terminos(act, e0), _n(n0)])
    _out("theta1 := " + _tx(act, {}, {"theta": "theta1",
                                      "dj": "dJ/dtheta1"}))
    _pasos("theta1", [_tx(act, e1), _terminos(act, e1), _n(n1)])
    _remarca(num, _igualdad("dJ/dtheta0", _der_txt("g0"), _n(g0)) +
             _igualdad("dJ/dtheta1", _der_txt("g1"), _n(g1)) +
             ["theta0 := " + _tx(act, {}, {"theta": "theta0",
                                           "dj": "dJ/dtheta0"}),
              "theta0 = " + _n(n0),
              "theta1 := " + _tx(act, {}, {"theta": "theta1",
                                           "dj": "dJ/dtheta1"}),
              "theta1 = " + _n(n1)])
    _pausa()
    return n0, n1


def _decision(k, J, Jprev, num):
    _proc(num, "comparar J")
    c = _cmp(J, Jprev)
    _out("J{} = {}".format(k, _n(J)), "J{} = {}".format(k - 1, _n(Jprev)))
    if c < 0:
        _pasos("J{} - J{}".format(k - 1, k),
               [_n(Jprev) + " - " + _n(J), _n(_menos(Jprev, J))])
        _out("J{} < J{}: J disminuyo.".format(k, k - 1),
             "Decision: si mejoro el modelo; se",
             "aceptan los nuevos theta.")
        final = "J{} < J{}: si mejoro el modelo".format(k, k - 1)
    elif c > 0:
        _out("J{} > J{}: J aumento.".format(k, k - 1),
             "Decision: no mejoro; revisa alfa",
             "o las formulas.")
        final = "J{} > J{}: no mejoro el modelo".format(k, k - 1)
    else:
        _out("J{} = J{}: J no cambio.".format(k, k - 1))
        final = "J{} = J{}: el modelo no cambio".format(k, k - 1)
    _remarca(num, [final])


def _estimar(t0, t1, x, num):
    _proc(num, "estimar")
    hip = _FN["hip"]
    env = {"theta0": t0, "theta1": t1, "x": x}
    yh = _ev(hip, env)
    _pasos("yh", [_tx(hip, {}), _tx(hip, env), _terminos(hip, env),
                  _n(yh)])
    u = _FN["umbral"]
    if _cmp(yh, u) >= 0:
        veredicto = _n(yh) + " >= " + _n(u) + ": APROBADO"
    else:
        veredicto = _n(yh) + " < " + _n(u) + ": NO APROBADO"
    _remarca(num, _igualdad("yh", _tx(hip, {}), _n(yh)) +
             ["h(x) = " + _tx(hip, {"theta0": t0, "theta1": t1}),
              "Con x = " + _n(x) + ": yh = " + _n(yh), veredicto])
    xs = _D.get("xs")
    if xs:
        bajo = alto = xs[0]
        for v in xs:
            if _cmp(v, bajo) < 0:
                bajo = v
            if _cmp(v, alto) > 0:
                alto = v
        if _cmp(x, bajo) < 0 or _cmp(x, alto) > 0:
            _out(*_parte("", "Ojo: x = {} esta fuera de los datos "
                             "({} a {}): es extrapolacion.".format(
                                 _n(x), _n(bajo), _n(alto))))


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
        nodo = _parse(t)
        _revisa_pot(nodo)
        return _ev(nodo, {})


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


def _si(texto):
    """True con enter/s/si, False con n/no; si no, vuelve a preguntar."""
    while True:
        r, s = _respuesta(texto)
        if r != "otro":
            return r == "si"
        print("Escribe solo enter (si) o n (no).")


def _respuesta(texto):
    """'si' (enter, s, si), 'no' (n, no) u 'otro' con lo tecleado."""
    s = input(texto).strip().lower()
    if s in ("", "s", "si", "s\xed"):
        return "si", s
    if s in ("n", "no"):
        return "no", s
    return "otro", s


# ---------- formulas: se confirman donde las pide el examen ----------

_LADO = {"hip": "h(x)", "e": "e", "J": "J", "g0": "dJ/dtheta0",
         "g1": "dJ/dtheta1", "act": "theta :"}
_AYUDA = {"hip": ("theta0, theta1, x", "theta0 + theta1*x"),
          "e": ("yh, y, x", "yh - y"),
          "J": ("m, sum( ), yh, y, x, e", "1/(2m) sum(yh - y)^2"),
          "g0": ("m, sum( ), yh, y, x, e", "1/m sum(yh - y)"),
          "g1": ("m, sum( ), yh, y, x, e", "1/m sum[(yh - y)x]"),
          "act": ("theta, alfa, dJ/dtheta", "theta - alfa*dJ/dtheta")}


def _der_txt(k):
    """Lo que va a la derecha del '=': 1/(2m) sum(yh - y)^2."""
    v = _FN[k]
    return _tx(v[0], {}, {"sum": _sum_txt(v[1])})


def _igualdad(lado, formula, valor):
    """Para la RF: en un renglon si cabe, si no formula y resultado
    en dos renglones, como se escribe en la hoja."""
    uno = lado + " = " + formula + " = " + valor
    if len(uno) <= _ANCHO - 8:
        return [uno]
    return [lado + " = " + formula, lado + " = " + valor]


def _ftxt(k):
    if k == "umbral":
        return "Aprobado si yh >= " + _n(_FN["umbral"])
    v = _FN[k]
    if k in _SUMAS:
        return _LADO[k] + " = " + _tx(v[0], {}, {"sum": _sum_txt(v[1])})
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
            r, s = _respuesta("Igual a tu examen? enter=si, n=no: ")
            if r == "si":
                return
            if r == "no":
                _edita(claves[0])
                continue
            if claves[0] == "umbral":
                try:
                    _FT["umbral"] = _lee(s)
                    _compila()
                    continue
                except Exception:
                    pass
            print("Escribe solo enter (si) o n (no).")
        else:
            for i in range(len(claves)):
                print("{} {}".format(i + 1, _ftxt(claves[i])))
            r, s = _respuesta("Iguales a tu examen? enter=si,n=no: ")
            if r == "si":
                return
            if r == "otro":
                print("Escribe solo enter (si) o n (no).")
                continue
            s = input("Cual es distinta? (1 a {}): ".format(len(claves)))
            try:
                i = int(s.strip())
            except ValueError:
                i = 0
            if 1 <= i <= len(claves):
                _edita(claves[i - 1])
            else:
                print("Escribe un numero del 1 al {}.".format(len(claves)))


def _crece_con_m(k):
    """True si el coeficiente de sum crece con m (ej 1/2m mal leido)."""
    try:
        fuera = _FN[k][0]
        c1 = _ev(fuera, {"m": (1, 1), "sum": (1, 1)})
        c2 = _ev(fuera, {"m": (2, 1), "sum": (1, 1)})
        return _cmp((abs(c2[0]), c2[1]), (abs(c1[0]), c1[1])) > 0
    except Exception:
        return False


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
        if k in _SUMAS and _crece_con_m(k):
            print("Ojo: asi crece con m. Si en tu")
            print("examen es 1/(2m), usa parentesis.")
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
    xs = _pide_lista("x (ej 1,2,3,4)", "xs")
    while True:
        ys = _pide_lista("y (ej 35,50,68,87)", "ys")
        if len(ys) == len(xs):
            break
        print("Pusiste {} valores de x y {} de y;".format(len(xs),
                                                          len(ys)))
        print("deben ser los mismos. Otra vez y.")
    _D["xs"], _D["ys"] = xs, ys
    return xs, ys


def _transferencia(t0, t1, titulo, confirmar_modelo, num):
    _nueva()
    _out(titulo, "Usa los theta que da el examen",
         "(pueden venir redondeados).")
    _pausa()
    t0 = _pide("theta0 a usar", "f0", t0)
    t1 = _pide("theta1 a usar", "f1", t1)
    if confirmar_modelo:
        _confirma(["hip"], "Modelo que da tu examen:")
    _confirma(["umbral"], "Regla para aprobar:")
    print("")
    print(num + "a) Estimar la calificacion:")
    x = _pide("x a estimar (ej 5)", "xn")
    veces = 1
    while True:
        _nueva()
        _estimar(t0, t1, x, num + "a" + ("-" + str(veces)
                                         if veces > 1 else ""))
        _pausa()
        otra = None
        while True:
            s = input("Otra x? (escribela o enter=no): ").strip()
            if s == "":
                break
            try:
                otra = _lee(s)
                break
            except Exception:
                print("No entendi. Ej: 6 o 6.5")
        if otra is None:
            break
        x = otra
        veces += 1
    print("")
    print(num + "b) Tu examen pregunta que tipo")
    print("   de problema es?")
    if not _si("enter=si, n=no: "):
        return
    _nueva()
    _proc(num + "b", "que tipo es")
    _out("Salida: aprobado o no aprobado",
         "= 2 clases, no un numero",
         "-> CLASIFICACION binaria.",
         "Los datos traen la y real",
         "(etiquetas) -> SUPERVISADO.",
         "Ojo: predecir la calificacion",
         "(el numero) seria REGRESION.")
    _remarca(num + "b", ["Es CLASIFICACION binaria y",
                         "aprendizaje SUPERVISADO."])
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
    t0i, t1i = t0, t1
    print("Hipotesis con parametros iniciales:")
    for ln in _parte("h(x) = ", _tx(_FN["hip"], {"theta0": t0,
                                                 "theta1": t1})):
        print(ln)

    _confirma(["e"], "Formula del error e:")
    _nueva()
    _out("== PASO 1: PREDICCION Y ERRORES ==")
    filas = _filas(xs, ys, t0, t1)
    _bloque_pred(t0, t1, filas, "1", "1b y 1c", "2", "3")

    _confirma(["J"], "Formula de la funcion de costo:")
    _nueva()
    _out("== PASO 2: FUNCION DE COSTO ==")
    _proc("2", "costo J")
    Js = [_cadena("J1", "J", filas)]
    _remarca("2", _igualdad("J1", _der_txt("J"), _n(Js[0])) +
             ["Resume el error de la",
              "hipotesis vs los datos reales."])
    _pausa()

    print("")
    print("== ANTES DEL PASO 3 ==")
    print("Tasa de aprendizaje (alfa): puede")
    print("venir con los datos o en la")
    print("pregunta de los nuevos theta.")
    alfa = _pide("alfa (ej 0.01 o 0.02)", "alfa")
    _confirma(["g0", "g1", "act"], "Formulas de la actualizacion:")
    _nueva()
    _out("== PASO 3: PRIMERA ACTUALIZACION ==")
    t0, t1 = _bloque_act(filas, t0, t1, alfa, "3", "1c")

    k = 2
    while True:
        filas = _filas(xs, ys, t0, t1)
        p = str(k + 2)                  # paso 4 = iteracion 2
        if k == 2:
            _out("== PASO 4: SEGUNDA ITERACION ==")
        else:
            _out("== PASO {}: ITERACION {} ==".format(p, k))
        _proc(p + "a", "yh y J" + str(k))
        _bloque_pred(t0, t1, filas, None, p + "a", p + "a", p + "c")
        Js.append(_cadena("J" + str(k), "J", filas))
        _remarca(p + "a", ["h(x) = " + _tx(_FN["hip"], {"theta0": t0,
                                                        "theta1": t1}),
                           "yh = " + _lista([f[2] for f in filas]),
                        ] + _igualdad("J" + str(k), _der_txt("J"),
                                      _n(Js[-1])))
        _pausa()
        _decision(k, Js[-1], Js[-2], p + "b")
        _pausa()
        print("")
        print(p + "c) Tu examen pide actualizar")
        print("   theta otra vez? (la guia no)")
        if not _si("enter=si, n=no: "):
            break
        _nueva()
        t0, t1 = _bloque_act(filas, t0, t1, alfa, p + "c", p + "a")
        print("")
        print("Tu examen pide J{} (iteracion {})?".format(k + 1, k + 1))
        if not _si("enter=si, n=no: "):
            break
        k += 1

    _D["f0"], _D["f1"] = t0, t1
    p = str(int(p) + 1)
    _D["paso"] = p
    print("")
    print(p + ") Tu examen pide estimar una")
    print("   calificacion? (la guia no)")
    if _si("enter=si, n=no: "):
        _transferencia(t0, t1, "== PASO {}: TRANSFERENCIA ==".format(p),
                       False, p)

    _nueva()
    _out("== REVISION FINAL ==")
    for i in range(len(Js)):
        _out("J{} = {}".format(i + 1, _n(Js[i])))
    c = _cmp(Js[-1], Js[0])
    if c < 0:
        _out(*_parte("", "J{} < J1: disminuyo {}".format(
            len(Js), _n(_menos(Js[0], Js[-1])))))
        _out("Conclusion: J disminuyo; las",
             "actualizaciones mejoraron el modelo")
    elif c > 0:
        _out("J{} > J1: J aumento.".format(len(Js)),
             "Conclusion: no mejoro; revisa",
             "alfa o las formulas.")
    else:
        _out("Conclusion: J no cambio.")
    hip = _FN["hip"]
    _out(*(["Hipotesis inicial:"] +
           _parte("h(x) = ", _tx(hip, {"theta0": t0i, "theta1": t1i})) +
           ["Hipotesis final:"] +
           _parte("h(x) = ", _tx(hip, {"theta0": t0, "theta1": t1}))))
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
         "Fraccion: 1/50. Potencia: tecla ^",
         "(en la calc sale **, tambien vale)",
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
        "J = 1/(2m) sum(yh - y)^2; el curso",
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
        "J2 < J1: J disminuyo; la",
        "actualizacion mejoro el modelo",
        "(los |e| bajan, yh se acerca a y).",
        "J2 > J1: J aumento; empeoro",
        "(alfa muy grande).",
        "Conclusion: cita J1, J2 y J1 - J2.",
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
        "sum = sigma, alfa = letra alfa,",
        "* = por (8x = 8 por x), := asigna",
        "yh1 = y gorro 1 (dato 1).",
        "Pasos: formula, sustitucion,",
        "operaciones, resultado; compara J.",
        "Ej: J1 = 1/(2m) sum(yh - y)^2",
        "= 1/8(5346) = 668.25",
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
                                   "== ESTIMAR CALIFICACION ==", True,
                                   _D.get("paso", "5"))
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
