# calcpy - analisis numerico para TI-Nspire CX II CAS
# Adrian. Pieza de ap y general (build.py la junta con el menu).
#
# Todo es NUMERICO (Python en la Nspire no habla con el CAS).
# Para simbolico usa la app Calculadora. Ver README.

from math import *

try:
    import ti_plotlib as plt
    _TI = True
except ImportError:
    _TI = False

try:
    from ti_system import store_value, recall_value, store_list, recall_list
    _SYS = True
except ImportError:
    _SYS = False


# ---------- derivadas numericas ----------

def d(f, x, h=0):
    """f'(x) por diferencia central de 5 puntos."""
    if h == 0:
        h = 1e-5 * max(1.0, abs(x))
    return (-f(x + 2*h) + 8*f(x + h) - 8*f(x - h) + f(x - 2*h)) / (12*h)


def d2(f, x, h=0):
    """f''(x)."""
    if h == 0:
        h = 1e-4 * max(1.0, abs(x))
    return (-f(x + 2*h) + 16*f(x + h) - 30*f(x)
            + 16*f(x - h) - f(x - 2*h)) / (12*h*h)


def dn(f, x, n=1):
    """n-esima derivada (recursiva, pierde precision arriba de n=3)."""
    if n <= 0:
        return f(x)
    if n == 1:
        return d(f, x)
    if n == 2:
        return d2(f, x)
    return d(lambda t: dn(f, t, n - 1), x, 1e-3 * max(1.0, abs(x)))


# ---------- raices ----------

INF = float("inf")
NODEF = "no definida"   # limite de un lado donde f no existe (ln en 0-)
_OVF = "desborda"


def _seguro(f, x):
    """f(x) o None si no existe: fuera del dominio, division entre 0,
    desborde, NaN o complejo (x^(1/3) con x<0 da complejo en Python)."""
    try:
        y = f(x)
    except (ValueError, ZeroDivisionError, OverflowError):
        return None
    if isinstance(y, complex) or y != y or abs(y) == INF:
        return None
    return y


def _z(v, eps):
    """0.0 si v es ruido numerico alrededor de cero."""
    return 0.0 if abs(v) < eps else v


def _bonito(x):
    """Quita el ruido de la ultima cifra: 1.9999999999999998 -> 2.0."""
    return float("%.12g" % x)


def _es_num(v):
    """v es un numero finito (no None, NODEF ni +-INF)."""
    return v is not None and v != NODEF and v not in (INF, -INF)


def _malla(f, a, b, n):
    paso = (b - a) / n
    xs = [a + i * paso for i in range(n)] + [b]
    return xs, [_seguro(f, x) for x in xs]


def _escala(ys):
    """Tamano tipico de |f| en la malla (mediana)."""
    vs = sorted([abs(y) for y in ys if y is not None])
    if not vs:
        return 1.0
    m = vs[len(vs) // 2]
    if m > 0:
        return m
    return vs[-1] if vs[-1] > 0 else 1.0


# Ruido de redondeo de las derivadas numericas en x cuando f(x) = y
# (x700 de margen). Con h = 1e-5|x| (f') y 1e-4|x| (f''), el error va
# como eps*|f|/h y eps*|f|/h^2: depende de |f| AHI, no de la escala
# de toda la funcion.

def _ruido1(x, y):
    return 0.0 if y is None else 2.2e-8 * abs(y) / max(1.0, abs(x))


def _ruido2(x, y):
    return 0.0 if y is None else 2.2e-5 * abs(y) / max(1.0, x * x)


def _corte(f, a, b, tol=1e-12, kmax=200):
    """Biseccion sobre un cambio de signo. Devuelve (m, |f(m)|, |f| mas
    grande en los bordes) o None si no hay cambio o f no existe."""
    fa, fb = _seguro(f, a), _seguro(f, b)
    if fa is None or fb is None or fa * fb > 0:
        return None
    borde = max(abs(fa), abs(fb))
    m = 0.5 * (a + b)
    fm = _seguro(f, m)
    for _ in range(kmax):
        if fm is None:
            return None
        if fm == 0 or (b - a) < tol * max(1.0, abs(m)):
            break
        if fa * fm < 0:
            b, fb = m, fm
        else:
            a, fa = m, fm
        m = 0.5 * (a + b)
        fm = _seguro(f, m)
    if fm is None:
        return None
    return (m, abs(fm), borde)


def _es_raiz(f, m, s):
    """m es raiz si f se va a 0 al acercarse por los dos lados: a 1e-9
    debe ser mucho mas chica que a 1e-6 (en un polo es mas grande y en
    un salto igual). Valores al nivel del ruido cuentan como 0."""
    h = 1e-9 * max(1.0, abs(m))
    for sg in (-1, 1):
        yh = _seguro(f, m + sg * h)
        yH = _seguro(f, m + sg * 1000 * h)
        if yh is None or yH is None or abs(yh) <= 1e-12 * s:
            continue
        if abs(yh) > 0.1 * abs(yH):
            return False
    return True


def _hueco(f, c):
    """c es un punto suelto donde f no existe (hueco o polo): f existe
    un poquito a los dos lados pero no en c redondeado."""
    r = _bonito(c)
    if _seguro(f, r) is not None:
        return False
    h = 1e-7 * max(1.0, abs(r))
    return _seguro(f, r - h) is not None and _seguro(f, r + h) is not None


def _toca_cero(g, c, ruido=0.0):
    """g toca 0 en c: |g(c)| es mucho mas chica que a 1e-4 de distancia
    (x^2 en 0, abs(x^2-4) en 2), o esta al nivel del ruido. Descarta
    minimos que solo quedan cerca de 0 (x^2+1e-10) y huecos."""
    y = _seguro(g, c)
    if y is None or _hueco(g, c):
        return False
    if y == 0 or abs(y) <= ruido:
        return True
    w = 1e-4 * max(1.0, abs(c))
    for x in (c - w, c + w):
        v = _seguro(g, x)
        if v is not None and abs(y) > 1e-5 * abs(v):
            return False
    return True


def biseccion(f, a, b, tol=1e-12, kmax=200, s=None):
    """Raiz en [a,b] donde f cambia de signo, o None si no lo cambia o
    si ahi hay un polo o un salto. s: tamano tipico de |f|."""
    r = _corte(f, a, b, tol, kmax)
    if r is None:
        return None
    if s is None:
        s = r[2]
    return r[0] if _es_raiz(f, r[0], s) else None


def newton(f, x0, tol=1e-12, kmax=60):
    """Newton-Raphson con derivada numerica."""
    x = float(x0)
    for _ in range(kmax):
        fx = _seguro(f, x)
        if fx is None:
            return None
        dx = d(f, x)
        if dx == 0:
            return None
        paso = fx / dx
        x = x - paso
        if abs(paso) < tol * max(1.0, abs(x)):
            return x
    return x


def _ceros_z(ys, pisos):
    """Valores con lo que esta bajo el piso de ruido convertido en 0."""
    out = []
    for i in range(len(ys)):
        y = ys[i]
        p = pisos[i] if isinstance(pisos, list) else pisos
        out.append(None if y is None else (0.0 if abs(y) <= p else y))
    return out


def _mesetas(zs):
    """Tramos de 2 o mas nodos seguidos en 0: lista de (i, j)."""
    out = []
    i = 0
    n = len(zs)
    while i < n:
        if zs[i] == 0:
            j = i
            while j + 1 < n and zs[j + 1] == 0:
                j += 1
            if j > i:
                out.append((i, j))
            i = j + 1
        else:
            i += 1
    return out


def _ceros(f, xs, ys, s, pisos, tol):
    """Raices en la malla: nodos en 0 (sueltos, no mesetas) y cambios de
    signo continuos. Devuelve (raices, saltos): saltos = cambios de signo
    que NO son raiz (polo, salto, o esquina si f es una derivada)."""
    zs = _ceros_z(ys, pisos)
    n = len(xs) - 1
    out = []
    i = 0
    while i <= n:
        if zs[i] != 0:
            i += 1
            continue
        j = i
        while j < n and zs[j + 1] == 0:
            j += 1
        largo = j - i + 1
        exactos = all([ys[k] == 0 for k in range(i, j + 1)])
        if largo == 2 and exactos or largo >= 3 and exactos:
            i = j + 1                     # meseta: la revisa quien llama
            continue
        k = i
        for q in range(i, j + 1):
            if abs(ys[q]) < abs(ys[k]):
                k = q
        if largo >= 3 and ys[k] != 0 and not _toca_cero(f, xs[k]):
            i = j + 1                     # tramo casi plano que no toca 0
            continue
        izq = zs[i - 1] if i > 0 else 1.0
        der = zs[j + 1] if j < n else 1.0
        if (izq is None or der is None) and ys[k] != 0 \
                and not _toca_cero(f, xs[k]):
            i = j + 1                     # casi 0 junto a un hueco
            continue
        out.append(xs[k])
        i = j + 1
    saltos = []
    for i in range(n):
        if zs[i] is not None and zs[i + 1] is not None \
                and zs[i] * zs[i + 1] < 0:
            r = _corte(f, xs[i], xs[i + 1], tol)
            if r is None:
                continue
            if _hueco(f, r[0]) or _hueco(f, round(r[0], 6)):
                continue                  # (x^2-2x+1)/(x-1) en 1
            if _es_raiz(f, r[0], s):
                out.append(r[0])
            else:
                saltos.append(r[0])
    return out, saltos


def _centro(g, c, T):
    """Centro de la zona plana |g| <= T alrededor de c: el minimo de
    |f'| en x^3 o sin(x)^3 esta en medio de la zona donde f' ya es solo
    ruido (la ternaria cae en cualquier punto de esa zona)."""
    lados = []
    for sg in (-1, 1):
        w = 1e-9 * max(1.0, abs(c))
        while w < 1e-2 * max(1.0, abs(c)):
            v = _seguro(g, c + sg * w)
            if v is None or abs(v) > T:
                break
            w *= 2
        lo, hi = 0.5 * w, w
        for _ in range(40):
            m = 0.5 * (lo + hi)
            v = _seguro(g, c + sg * m)
            if v is not None and abs(v) <= T:
                lo = m
            else:
                hi = m
        lados.append(c + sg * lo)
    return 0.5 * (lados[0] + lados[1])


def _orilla(g, fuera, dentro, piso):
    """Biseccion del borde de una meseta de g (|g| <= piso adentro)."""
    for _ in range(60):
        m = 0.5 * (fuera + dentro)
        v = _seguro(g, m)
        if v is not None and abs(v) <= piso:
            dentro = m
        else:
            fuera = m
    return dentro


def _redondea(g, c, piso):
    """Cambia c por su redondeo a 6 decimales si ahi g es igual de chica
    (quita ruido: -1.26e-07 -> 0, 1.00000000006 -> 1)."""
    r = round(c, 6)
    if r == c:
        return c
    if abs(r - c) <= 1e-8 * max(1.0, abs(c)):
        return r
    if abs(r - c) > 1e-5 * max(1.0, abs(c)):
        return c
    gc, gr = _seguro(g, c), _seguro(g, r)
    if gc is not None and gr is not None and abs(gr) <= abs(gc) + piso:
        return r
    return c


def _bordes(f, xs, ys):
    """Bordes del dominio dentro de [a,b] (sqrt(4-x^2) en -2 y 2, ln en
    0): lista de (x, limite de f al acercarse desde adentro)."""
    out = []
    for i in range(len(xs) - 1):
        dentro = ys[i] is not None
        if dentro == (ys[i + 1] is not None):
            continue
        lo, hi = (xs[i], xs[i + 1]) if dentro else (xs[i + 1], xs[i])
        for _ in range(60):
            m = 0.5 * (lo + hi)
            if _seguro(f, m) is None:
                hi = m
            else:
                lo = m
        xb = _z(_bonito(lo), 1e-12)
        out.append((xb, limite(f, xb, 1 if hi < lo else -1)))
    return out


def _en_dominio(f, xb):
    """El borde xb es parte del dominio: sqrt(x) en 0 si; ln o x*ln(x)
    en 0 no, ni un hueco como (x^2-1)/(x-1) en 1. Si xb no es 0 y cae
    fuera, es por el redondeo de la ultima cifra: si cuenta."""
    if _seguro(f, xb) is not None:
        return True
    if _hueco(f, xb):
        return False
    return xb != 0


def _snap(xs, a, b):
    return _limpia([_z(x, 1e-9 * max(1.0, abs(b - a))) for x in xs])


def raices(f, a, b, n=200, tol=1e-12, dobles=True, piso=None, crit=None):
    """Todas las raices de f en [a,b]: nodos en 0, cambios de signo (sin
    polos ni saltos), bordes del dominio donde f llega a 0 (sqrt(4-x^2)
    en 2), orillas de tramos donde f = 0 y, con dobles, donde f toca el
    eje sin cruzarlo (x^2 en 0). piso: |f| menor que esto cuenta como 0."""
    xs, ys = _malla(f, a, b, n)
    s = _escala(ys)
    if piso is None:
        piso = 1e-12 * s
    ps, pys = xs, ys
    if dobles:
        if crit is None:
            crit = _criticos(f, a, b, n, s, xs, ys)
        # los criticos van a la malla: una raiz que comparte celda con un
        # nodo en 0 (x^2-x/2 en [-100,100]) queda entre nodo y critico
        tp = 1e-12 * max(1.0, abs(b - a))
        extra = [c for c in crit if a < c < b and _lejos(c, xs, tp)]
        if extra:
            pares = sorted([(xs[i], ys[i]) for i in range(len(xs))] +
                           [(c, _seguro(f, c)) for c in extra],
                           key=lambda q: q[0])
            ps = [q[0] for q in pares]
            pys = [q[1] for q in pares]
    out = _ceros(f, ps, pys, s, piso, tol)[0]
    zs = _ceros_z(ys, 0.0)              # tramo donde f = 0 exacto
    for i, j in _mesetas(zs):
        for k, afuera in ((i, i - 1), (j, j + 1)):
            if 0 <= afuera < len(xs) and zs[afuera] is not None:
                out.append(_orilla(f, xs[afuera], xs[k], 0.0))
            else:
                out.append(xs[k])
    for x, L in _bordes(f, xs, ys):
        if _es_num(L) and abs(L) <= 1e-6 * s and _en_dominio(f, x):
            out.append(x)
    if dobles:
        for c in crit:
            if _toca_cero(f, c):
                out.append(c)
    return _snap([_redondea(f, x, 0.0) for x in out], a, b)


def ceros_tramo(f, a, b, n=200):
    """Tramos de [a,b] donde f vale 0 (no solo en un punto)."""
    xs, ys = _malla(f, a, b, n)
    zs = _ceros_z(ys, 0.0)
    return [(xs[i], xs[j]) for i, j in _mesetas(zs)]


def resuelve(f, g, a, b, n=200):
    """Donde f(x) = g(x) en [a,b]."""
    return raices(lambda x: f(x) - g(x), a, b, n)


def _limpia(xs, tol=1e-7):
    """Ordena y quita duplicados cercanos."""
    xs = sorted(xs)
    out = []
    for x in xs:
        if not out or abs(x - out[-1]) > tol * max(1.0, abs(x)):
            out.append(x)
    return out


def _lejos(x, otros, tol):
    for p in otros:
        if abs(x - p) <= tol:
            return False
    return True


def _pico(f, a, b, signo=1):
    """Ternaria hacia donde crece (signo=1) o baja (-1) |f| en [a,b]."""
    for _ in range(80):
        m1 = a + (b - a) / 3
        m2 = b - (b - a) / 3
        y1 = _seguro(f, m1)
        y2 = _seguro(f, m2)
        if y1 is None:
            return m1
        if y2 is None:
            return m2
        if signo * abs(y1) < signo * abs(y2):
            a = m1
        else:
            b = m2
    return 0.5 * (a + b)


def _laterales(f, x, a, b):
    """(limite por la izq, limite por la der) de f en x. El lado que
    queda fuera de [a,b] no se revisa (None)."""
    izq = limite(f, x, -1) if x > a else None
    der = limite(f, x, 1) if x < b else None
    return izq, der


def polos(f, a, b, n=200):
    """Asintotas verticales en [a,b]: lista de (x, lim izq, lim der) con
    al menos un lado +-INF. Revisa los cambios de signo que no son raiz,
    los picos de |f|, los puntos donde f no existe y los extremos."""
    xs, ys = _malla(f, a, b, n)
    s = _escala(ys)
    cand = [a, b] + _ceros(f, xs, ys, s, 1e-12 * s, 1e-12)[1]
    for i in range(1, n):
        y, y0, y1 = ys[i], ys[i - 1], ys[i + 1]
        if y0 is None or y1 is None:
            continue
        if y is None or (abs(y) >= abs(y0) and abs(y) >= abs(y1)):
            cand.append(_pico(f, xs[i - 1], xs[i + 1]))
    cand = cand + [x for x, L in _bordes(f, xs, ys)]
    tp = 1e-9 * max(1.0, abs(b - a))
    todos = []
    for x in _limpia(cand):
        if abs(x - a) <= tp:
            x = a                 # asintota en el extremo: solo adentro
        elif abs(x - b) <= tp:
            x = b
        izq, der = _laterales(f, x, a, b)
        if izq in (INF, -INF) or der in (INF, -INF):
            todos.append((x, izq, der))
    # varias juntas (a menos de 2 pasos) son la misma asintota, p. ej.
    # exp(1/x) se desborda en todo (0, 0.0014): se queda la mas 'bonita'
    paso = (b - a) / n
    out = []
    grupo = []
    for p in todos + [None]:
        if p is not None and grupo and p[0] - grupo[-1][0] <= 2 * paso:
            grupo.append(p)
            continue
        if grupo:
            q = sorted(grupo, key=lambda q: len("%.6g" % q[0]))[0]
            out.append((_z(_bonito(q[0]), tp), q[1], q[2]))
        grupo = [p]
    return out


# ---------- extremos ----------

def _criticos(f, a, b, n, s, xs=None, ys=None):
    """Puntos criticos (incluye los extremos del intervalo si caen ahi):
    donde f' = 0, donde f' cambia de signo sin pasar por 0 (esquina como
    abs(x) en 0, o salto de f), orillas de tramos donde f' = 0 (mesetas
    como abs(x-1)+abs(x+1)) y donde f' toca 0 sin cruzarlo (x^3 en 0)."""
    if xs is None:
        xs, ys = _malla(f, a, b, n)
    df = lambda x: d(f, x)
    fino = lambda x: d(f, x, 1e-9 * max(1.0, abs(x)))
    ds = [_seguro(df, x) for x in xs]
    # piso = ruido de redondeo local o, si es mayor, 1e-8 de la escala
    # de f' (truncado de la formula y cancelacion: (x-1)^5 en 1)
    s1 = 1e-8 * _escala(ds)
    pisos = [max(_ruido1(xs[i], ys[i]), s1) for i in range(len(xs))]
    ceros, saltos = _ceros(df, xs, ds, _escala(ds), pisos, 1e-12)
    out = list(ceros)
    # esquinas y saltos: f' con h fijo los ve corridos hasta 2h
    for m in saltos:
        w = 1e-4 * max(1.0, abs(m))
        r = _corte(fino, m - w, m + w)
        out.append(r[0] if r is not None else m)
    for i, j in _mesetas(_ceros_z(ds, 0.0)):   # f' = 0 exacto: f plana
        for k, afuera in ((i, i - 1), (j, j + 1)):
            if 0 <= afuera < len(xs) and ds[afuera] is not None:
                out.append(_orilla(fino, xs[afuera], xs[k], pisos[k]))
            else:
                out.append(xs[k])
    zs = _ceros_z(ds, pisos)
    for i in range(1, len(xs) - 1):
        u, v, w = zs[i - 1], zs[i], zs[i + 1]
        if u is None or v is None or w is None or v == 0 or u == 0 \
                or w == 0:
            continue
        if abs(v) <= abs(u) and abs(v) <= abs(w) \
                and (u > 0) == (v > 0) == (w > 0):
            c = _pico(df, xs[i - 1], xs[i + 1], -1)
            T = max(10 * _ruido1(c, _seguro(f, c)), s1)
            if _toca_cero(df, c, T):
                out.append(_centro(df, c, 10 * T))
    res = []
    for c in out:
        piso = _ruido1(c, _seguro(f, c)) + 1e-14 * s
        res.append(_redondea(fino, _redondea(df, c, piso), piso))
    return _snap(res, a, b)


def criticos(f, a, b, n=200):
    """Puntos criticos interiores: f' = 0 o f' no existe."""
    xs, ys = _malla(f, a, b, n)
    t = 1e-9 * max(1.0, abs(b - a))
    return [x for x in _criticos(f, a, b, n, _escala(ys), xs, ys)
            if abs(x - a) > t and abs(x - b) > t]


def _signo(v, piso):
    if v is None:
        return 0
    return 1 if v > piso else (-1 if v < -piso else 0)


def _clasifica(f, x, delta, s1=0.0):
    """Prueba de la primera derivada con f' a +-delta: 'max' si pasa de
    + a - (o de + a plano), 'min' si pasa de - a +, 'ni max ni min' si
    no cambia de signo. s1: piso minimo de f' (escala)."""
    sg = []
    for t in (x - delta, x + delta):
        sg.append(_signo(_seguro(lambda u: d(f, u), t),
                         max(_ruido1(t, _seguro(f, t)), s1)))
    sa, sd = sg
    if sa > 0 and sd <= 0 or sa == 0 and sd < 0:
        return 'max'
    if sa < 0 and sd >= 0 or sa == 0 and sd > 0:
        return 'min'
    return 'ni max ni min'


def _esquina(f, q):
    """q es esquina (abs(x^2-4) en 2): el salto de f' entre q-w y q+w no
    se achica al acercarse. En un punto suave se achica 10 veces."""
    fino = lambda x: d(f, x, 1e-10 * max(1.0, abs(x)))
    saltos = []
    for w in (1e-6, 1e-7):
        w = w * max(1.0, abs(q))
        i, k = _seguro(fino, q - w), _seguro(fino, q + w)
        if i is None or k is None:
            return False
        saltos.append(abs(k - i))
    return saltos[0] > 1e-9 * max(1.0, abs(q)) and \
        saltos[1] > 0.5 * saltos[0]


def _ventana(c, a, b):
    """Que tan cerca de una asintota ya no se cree en un critico: las
    derivadas numericas usan puntos a 2h (f'') = 2e-4|x|."""
    return max(3e-4 * max(1.0, abs(c)), 1e-6 * max(1.0, abs(b - a)))


def _delta(c, otros, paso):
    """Distancia para la prueba de la 1a derivada: medio paso, pero sin
    brincar a otro critico o asintota cercana."""
    dd = [paso] + [0.5 * abs(c - o) for o in otros if o != c]
    return max(min(dd), 1e-6 * max(1.0, abs(c)))


def extremos(f, a, b, n=200, crit=None, pol=None):
    """Extremos LOCALES interiores: lista de (x, f(x), tipo) con tipo
    'max', 'min' o 'ni max ni min' (prueba de la primera derivada).
    No cuenta los extremos del intervalo, huecos ni asintotas."""
    xs, ys = _malla(f, a, b, n)
    s = _escala(ys)
    paso = (b - a) / n
    if crit is None:
        crit = _criticos(f, a, b, n, s, xs, ys)
    if pol is None:
        pol = polos(f, a, b, n)
    ps = [p[0] for p in pol]
    t = 1e-9 * max(1.0, abs(b - a))
    s1 = 1e-8 * _escala([_seguro(lambda u: d(f, u), x) for x in xs])
    out = []
    for c in crit:
        if abs(c - a) <= t or abs(c - b) <= t \
                or not _lejos(c, ps, _ventana(c, a, b)):
            continue
        y = _seguro(f, c)
        if y is None or _hueco(f, c):
            continue
        if _toca_cero(f, c):
            y = 0.0
        out.append((c, y, _clasifica(f, c, _delta(c, crit + ps, paso), s1)))
    return out


def _sin_repetir(cands):
    """Un candidato por x (el que se alcanza, si hay dos)."""
    out = []
    for c in sorted(cands, key=lambda c: (c[0], not c[2])):
        if not out or abs(c[0] - out[-1][0]) > 1e-7 * max(1.0, abs(c[0])):
            out.append(c)
    return out


def absolutos(f, a, b, n=200, crit=None, pol=None):
    """Maximo y minimo ABSOLUTOS en [a,b]. Candidatos: extremos del
    intervalo, criticos, bordes del dominio y huecos. Devuelve
    (maxs, mins): None si f sube (baja) sin tope por una asintota, o
    lista de (x, y, se_alcanza) con todos los empates."""
    xs, ys = _malla(f, a, b, n)
    s = _escala(ys)
    if crit is None:
        crit = _criticos(f, a, b, n, s, xs, ys)
    if pol is None:
        pol = polos(f, a, b, n)
    ps = [p[0] for p in pol]
    arriba = abajo = False
    cand = []
    for x, izq, der in pol:
        for L in (izq, der):
            if L == INF:
                arriba = True
            elif L == -INF:
                abajo = True
            elif _es_num(L):
                cand.append((x, L, False))
    for x in [a, b] + crit:
        if not _lejos(x, ps, _ventana(x, a, b)):
            continue
        y = _seguro(f, x)
        if y is not None and not _hueco(f, x):
            cand.append((x, 0.0 if _toca_cero(f, x) else y, True))
        else:
            for L in _laterales(f, x, a, b):
                if _es_num(L):
                    cand.append((x, L, False))
    for x, L in _bordes(f, xs, ys):
        if _es_num(L):
            cand.append((x, L, _en_dominio(f, x)))

    def mejores(signo):
        if not cand:
            return []
        vals = [signo * c[1] for c in cand]
        top = max(vals)
        tol = 1e-9 * abs(top) + 1e-15 * (top - min(vals))
        return _sin_repetir([c for c in cand
                             if abs(signo * c[1] - top) <= tol])

    return (None if arriba else mejores(1),
            None if abajo else mejores(-1))


def maxmin(f, a, b, n=200):
    """((xmax, ymax), (xmin, ymin)) absolutos; None del lado que no
    existe. El reporte completo (empates, huecos) es absolutos()."""
    maxs, mins = absolutos(f, a, b, n)
    uno = lambda l: (l[0][0], l[0][1]) if l else None
    return uno(maxs), uno(mins)


def inflexion(f, a, b, n=200, pol=None, crit=None):
    """Puntos de inflexion interiores: f'' cambia de signo (por encima
    del ruido numerico), f existe ahi y no es una asintota. Si cae
    pegada a una esquina (abs(x^2-3)), la inflexion es la esquina."""
    xs, ys = _malla(f, a, b, n)
    paso = (b - a) / n
    if pol is None:
        pol = polos(f, a, b, n)
    ps = [p[0] for p in pol]
    dd = lambda u: d2(f, u)
    d2s = [_seguro(dd, x) for x in xs]
    s2 = 1e-6 * _escala(d2s)
    pisos = [max(_ruido2(xs[i], ys[i]), s2) for i in range(len(xs))]
    ceros, saltos = _ceros(dd, xs, d2s, _escala(d2s), pisos, 1e-12)
    cands = _limpia(ceros + saltos)
    esquinas = [q for q in (crit or []) if _esquina(f, q)]
    t = 1e-9 * max(1.0, abs(b - a))
    out = []
    for c in cands:
        if abs(c - a) <= t or abs(c - b) <= t \
                or not _lejos(c, ps, _ventana(c, a, b)):
            continue
        y = _seguro(f, c)
        if y is None or _hueco(f, c):
            continue
        dl = _delta(c, cands + ps, paso)
        i = _seguro(dd, c - dl)
        k = _seguro(dd, c + dl)
        pi = max(_ruido2(c - dl, _seguro(f, c - dl)), s2)
        pk = max(_ruido2(c + dl, _seguro(f, c + dl)), s2)
        if i is None or k is None or \
                not (i > pi and k < -pk or i < -pi and k > pk):
            continue
        for q in esquinas:            # la inflexion es la esquina misma
            if abs(q - c) < 1e-3 * max(1.0, abs(q)):
                c = q
                y = _seguro(f, c)
                break
        out.append((_z(_redondea(dd, c, 0.0), t), y))
    return _sin_repetir([(p[0], p[1], True) for p in out])


def _abs_txt(nombre, lst, sube, s):
    if lst is None:
        return ["no hay " + nombre + ": " + sube + " sin tope"]
    if not lst:
        return ["no hay " + nombre + " (f no existe)"]
    alc = [c for c in lst if c[2]]
    if alc:
        return ["{}: y={:.6g} en x={}".format(
            nombre, _z(alc[0][1], 1e-12 * s),
            _fmt([c[0] for c in alc]))]
    c = lst[0]
    return ["no hay " + nombre + ": y->{:.6g}".format(_z(c[1], 1e-12 * s)),
            "  cuando x->{:.6g} (no se alcanza)".format(c[0])]


def _tramos_txt(f, xs, ys):
    """Avisos: donde f no existe y donde f vale 0 en todo un tramo."""
    out = []
    i = 0
    n = len(xs)
    while i < n:
        if ys[i] is None:
            j = i
            while j + 1 < n and ys[j + 1] is None:
                j += 1
            if j > i:
                out.append("f no existe en [{:.6g}, {:.6g}]".format(
                    xs[i], xs[j]))
            i = j + 1
        else:
            i += 1
    for p, q in ceros_tramo(f, xs[0], xs[-1], n - 1):
        out.append("f = 0 en todo [{:.6g}, {:.6g}]".format(p, q))
    return out


def analiza(f, a, b, n=200):
    """Reporte completo listo para leer en pantalla."""
    print("f en [{:g}, {:g}]".format(a, b))
    xs, ys = _malla(f, a, b, n)
    s = _escala(ys)
    crit = _criticos(f, a, b, n, s, xs, ys)
    pol = polos(f, a, b, n)
    for linea in _tramos_txt(f, xs, ys):
        print(linea)
    r = raices(f, a, b, n, 1e-12, True, None, crit)
    print("raices:", _fmt(r) if r else "ninguna")
    if pol:
        print("asintota en x=" + _fmt([p[0] for p in pol]))
    for x, y, t in extremos(f, a, b, n, crit, pol):
        print("{}: x={:.6g}  y={:.6g}".format(t, x, y))
    infl = inflexion(f, a, b, n, pol, crit)
    if infl:
        print("inflex:", _fmt([p[0] for p in infl]))
    maxs, mins = absolutos(f, a, b, n, crit, pol)
    for linea in _abs_txt("abs max", maxs, "sube", s) + \
            _abs_txt("abs min", mins, "baja", s):
        print(linea)


def alto_bajo(f, a, b, n=200):
    """Punto mas alto y mas bajo en [a,b] y los extremos locales."""
    xs, ys = _malla(f, a, b, n)
    s = _escala(ys)
    crit = _criticos(f, a, b, n, s, xs, ys)
    pol = polos(f, a, b, n)
    for linea in _tramos_txt(f, xs, ys):
        print(linea)
    if pol:
        print("asintota en x=" + _fmt([p[0] for p in pol]))
    maxs, mins = absolutos(f, a, b, n, crit, pol)
    for linea in _abs_txt("mas alto", maxs, "sube", s) + \
            _abs_txt("mas bajo", mins, "baja", s):
        print(linea)
    for x, y, t in extremos(f, a, b, n, crit, pol):
        if t == 'ni max ni min':
            print("  x={:.6g}: critico, ni max ni min".format(x))
        else:
            print("  {} local en x={:.6g}".format(t, x))


def _fmt(xs):
    return ", ".join("{:.6g}".format(x) for x in xs)


# ---------- integracion ----------

def integra(f, a, b, n=1000):
    """Integral definida por Simpson compuesto (n par)."""
    if n % 2:
        n += 1
    h = (b - a) / n
    s = f(a) + f(b)
    for i in range(1, n):
        s += f(a + i*h) * (4 if i % 2 else 2)
    return s * h / 3


def riemann(f, a, b, n, modo="izq"):
    """Suma de Riemann. modo: 'izq', 'der', 'medio', 'trap'.
    Con n chico es lo que piden en el examen de AP."""
    h = (b - a) / n
    if modo == "trap":
        s = 0.5 * (f(a) + f(b))
        for i in range(1, n):
            s += f(a + i*h)
        return s * h
    if modo == "medio":
        return h * sum(f(a + (i + 0.5)*h) for i in range(n))
    if modo == "der":
        return h * sum(f(a + (i + 1)*h) for i in range(n))
    return h * sum(f(a + i*h) for i in range(n))


def promedio(f, a, b, n=1000):
    """Valor promedio de f en [a,b]: (1/(b-a)) * integral."""
    return integra(f, a, b, n) / (b - a)


def euler(F, x0, y0, xf, n):
    """Metodo de Euler para y'=F(x,y) (Calculo BC).
    Con n chico imprime la tabla como la pide el examen."""
    h = (xf - x0) / n
    x, y = float(x0), float(y0)
    pts = [(x, y)]
    for _ in range(n):
        y += h * F(x, y)
        x += h
        pts.append((x, y))
    if n <= 12:
        for px, py in pts:
            print("x={:.6g}  y={:.6g}".format(px, py))
    return pts


def area_entre(f, g, a, b, n=1000):
    """Area entre curvas, partiendo en los cruces (siempre positiva)."""
    ptos = [a] + resuelve(f, g, a, b) + [b]
    ptos = _limpia(ptos)
    total = 0.0
    for i in range(len(ptos) - 1):
        total += abs(integra(lambda x: f(x) - g(x), ptos[i], ptos[i+1], n))
    return total


def longitud(f, a, b, n=1000):
    """Longitud de arco de f en [a,b]."""
    return integra(lambda x: sqrt(1 + d(f, x)**2), a, b, n)


def solido_x(f, a, b, n=1000):
    """Volumen del solido de revolucion alrededor del eje x (discos)."""
    return pi * integra(lambda x: f(x)**2, a, b, n)


# ---------- ecuaciones diferenciales ----------

def rk4(F, x0, y0, xf, n=200):
    """y' = F(x,y). Devuelve lista de (x, y). Runge-Kutta 4."""
    h = (xf - x0) / n
    x, y = float(x0), float(y0)
    pts = [(x, y)]
    for _ in range(n):
        k1 = F(x, y)
        k2 = F(x + h/2, y + h*k1/2)
        k3 = F(x + h/2, y + h*k2/2)
        k4 = F(x + h, y + h*k3)
        y += h * (k1 + 2*k2 + 2*k3 + k4) / 6
        x += h
        pts.append((x, y))
    return pts


# ---------- movimiento de particula (clasico de Calculo AP) ----------

def desplazamiento(v, t1, t2):
    """Integral de v(t): cambio de posicion (con signo)."""
    return integra(v, t1, t2)


def distancia(v, t1, t2):
    """Integral de |v(t)|: distancia total recorrida.
    Parte el intervalo donde v cambia de signo."""
    cortes = _limpia([t1] + raices(v, t1, t2) + [t2])
    total = 0.0
    for i in range(len(cortes) - 1):
        total += abs(integra(v, cortes[i], cortes[i+1]))
    return total


def particula(v, t1, t2, x0=0):
    """Reporte completo de movimiento de particula dado v(t)."""
    dx = desplazamiento(v, t1, t2)
    print("desplazamiento: {:.6g}".format(dx))
    print("distancia:      {:.6g}".format(distancia(v, t1, t2)))
    print("pos final:      {:.6g}".format(x0 + dx))
    paradas = raices(v, t1, t2)
    if paradas:
        print("v=0 en t:", ", ".join("{:.6g}".format(t) for t in paradas))
    for t in paradas:
        a = d(v, t)
        if a > 0:
            print("  t={:.4g}: da vuelta (min de x)".format(t))
        elif a < 0:
            print("  t={:.4g}: da vuelta (max de x)".format(t))


def rapidez(v, t):
    """'aumenta' si v y a tienen el mismo signo, 'disminuye' si no.
    (Pregunta favorita del AP.)"""
    vt, at = v(t), d(v, t)
    if vt * at > 0:
        return "aumenta"
    if vt * at < 0:
        return "disminuye"
    return "indeterminado"


# ---------- utilidades ----------

def tabla(f, a, b, n=10):
    """Tabla de valores en pantalla."""
    paso = (b - a) / n
    for i in range(n + 1):
        x = a + i * paso
        y = _seguro(f, x)
        print("{:>10.6g}  {:>12}".format(
            x, "indef" if y is None else "{:.6g}".format(y)))


def _valores(f, x0, signo):
    """f(x0 + signo*10^-k) para k = 1..9: None donde no existe, _OVF
    donde se desborda (exp(1/x) cerca de 0)."""
    out = []
    for k in range(1, 10):
        try:
            y = f(x0 + signo * 10.0 ** (-k))
            if isinstance(y, complex) or y != y:
                y = None
            elif abs(y) == INF:
                y = _OVF
        except OverflowError:
            y = _OVF
        except (ValueError, ZeroDivisionError):
            y = None
        out.append(y)
    return out


def _redondo(L):
    """Quita el error de truncado cuando el limite es un numero
    'bonito' (0.5000017 -> 0.5; nunca un numero chico a 0); -0.0 -> 0."""
    r = round(L, 3)
    if r != 0 and abs(L - r) < 2e-6 * abs(r):
        L = r
    return L + 0.0


def _lateral(f, x0, signo):
    vs = _valores(f, x0, signo)
    # MicroPython avisa el desborde de exp como ValueError (dominio): si
    # f deja de existir justo despues de valores enormes, es desborde
    ult = -1
    for i in range(len(vs)):
        if vs[i] is not None and vs[i] != _OVF:
            ult = i
    if 0 <= ult < len(vs) - 1 and abs(vs[ult]) > 1e30 \
            and all([w is None for w in vs[ult + 1:]]):
        vs = vs[:ult + 1] + [_OVF] * (len(vs) - ult - 1)
    v = [w for w in vs if w is not None and w != _OVF]
    if _OVF in vs and (not v or vs[-1] == _OVF):
        return INF if not v or v[-1] > 0 else -INF
    if not v:
        return NODEF
    if len(v) < 3:
        return _redondo(v[-1])
    # crece sin frenar con el mismo signo: 1/x, ln(x), log10(x)
    # (crecer 5% o mas en CADA paso: el ruido de redondeo, en cambio,
    # salta de golpe despues de una meseta)
    u = v[-6:]
    if len(u) >= 4 \
            and all([abs(u[i + 1]) > 1.05 * abs(u[i])
                     for i in range(len(u) - 1)]) \
            and all([(w > 0) == (u[-1] > 0) for w in u]) \
            and abs(u[-1]) >= 2 * abs(u[0]):
        return INF if u[-1] > 0 else -INF
    # se va a 0: rapido (x^2, x*sin(1/x)) o lento (sqrt(x), 1/ln(x))
    if max([abs(w) for w in v[-3:]]) <= \
            1e-5 * max([abs(w) for w in v[:3]]):
        return 0.0
    u = v[-5:]
    if all([abs(u[i + 1]) < abs(u[i]) for i in range(len(u) - 1)]) \
            and all([(w > 0) == (u[-1] > 0) for w in u]) \
            and abs(u[-2] - u[-1]) > 0.05 * abs(u[-1]):
        return 0.0
    # meseta: se corta donde las diferencias empiezan a crecer (desde
    # ahi manda el redondeo: (1-cos x)/x^2 da 0 con h muy chico). En la
    # parte limpia, extrapolacion de Richardson (error ~ h):
    # R = v_k - (v_(k-1) - v_k)/9, y se toma la R que mas coincide con
    # su vecina (1/(x-3)-6/(x^2-9) en 3 da 0.16666666, no 0.166665)
    dif = [abs(v[i + 1] - v[i]) for i in range(len(v) - 1)]
    fin = len(v)
    for i in range(1, len(dif)):
        if dif[i] > dif[i - 1]:
            fin = i + 1
            break
    R = [v[j] - (v[j - 1] - v[j]) / 9.0 for j in range(1, fin)]
    if len(R) >= 2:
        dR = [abs(R[j] - R[j - 1]) for j in range(1, len(R))]
        k = dR.index(min(dR))
        L, err = R[k + 1], dR[k]
    else:
        L, err = v[fin - 1], dif[max(0, fin - 2)]
    if err > 1e-3 * max(1.0, abs(L)):
        return None                       # no se asienta: oscila
    if abs(L) <= 1e-9 * max([abs(w) for w in v]):
        return 0.0                        # (1-cos x)/x: ruido de 1e-13
    return _redondo(L)


def limite(f, x0, lado=0):
    """Limite numerico. lado: -1 izq, 1 der, 0 bilateral. Devuelve el
    numero, INF o -INF si crece sin tope, None si no existe (oscila o
    los laterales no coinciden) o NODEF si f no existe de ese lado."""
    if lado:
        return _lateral(f, x0, lado)
    izq, der = _lateral(f, x0, -1), _lateral(f, x0, 1)
    if izq is None or der is None or izq == NODEF or der == NODEF:
        return None
    if izq == der:
        return izq
    if izq in (INF, -INF) or der in (INF, -INF):
        return None
    if abs(izq - der) <= 1e-4 * max(abs(izq), abs(der)):
        return _redondo(0.5 * (izq + der))
    return None


def graf(f, a, b, n=100):
    """Grafica f en la pantalla de la calculadora (necesita ti_plotlib)."""
    if not _TI:
        print("ti_plotlib solo existe en la calculadora")
        return
    ys = [y for y in (_seguro(f, a + i*(b-a)/n) for i in range(n+1))
          if y is not None]
    if not ys:
        return
    lo, hi = min(ys), max(ys)
    if hi - lo < 1e-9:
        lo, hi = lo - 1, hi + 1
    m = 0.1 * (hi - lo)
    plt.cls()
    plt.window(a, b, lo - m, hi + m)
    plt.axes("on")
    plt.color(0, 0, 200)
    px = a
    py = _seguro(f, a)
    for i in range(1, n + 1):
        x = a + i*(b-a)/n
        y = _seguro(f, x)
        if py is not None and y is not None:
            plt.line(px, py, x, y, "default")
        px, py = x, y
    plt.show_plot()


# ---------- puente con las apps de la Nspire ----------

def leer(nombre, default=None):
    """Lee una variable del documento (definida en Calculadora/Notas)."""
    if not _SYS:
        return default
    try:
        return recall_value(nombre)
    except (NameError, TypeError, ValueError):
        return default


def guardar(nombre, valor):
    """Guarda una variable para usarla en Calculadora/Graficas."""
    if _SYS:
        store_value(nombre, valor)


def leer_lista(nombre):
    if not _SYS:
        return []
    try:
        return recall_list(nombre)
    except (NameError, TypeError, ValueError):
        return []


def guardar_lista(nombre, datos):
    if _SYS:
        store_list(nombre, [float(v) for v in datos])
