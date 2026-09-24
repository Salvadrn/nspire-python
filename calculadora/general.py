# general - Calculo AP + IA + Fisica
# Para la TI-Nspire CX II CAS de Adrian (MicroPython 1.11).
# GENERADO por build.py desde src/calcpy.py, formulas.py, ap.py, ai.py, fisica.py:
# no lo edites a mano; edita src/ y corre  python3 build.py

from math import *
import sys


# ===================== calcpy =====================

# calcpy - analisis numerico para TI-Nspire CX II CAS
# Adrian. Pieza de ap y general (build.py la junta con el menu).
#
# Todo es NUMERICO (Python en la Nspire no habla con el CAS).
# Para simbolico usa la app Calculadora. Ver README.


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
        if abs(yh) > 0.6 * abs(yH):
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
        if ys[k] != 0 or largo > 1:
            # casi cero (bajo el piso de ruido), p. ej. x^5 en 0 si el nodo
            # mas cercano es 0.005: el centro de la zona plana; cuenta si
            # los flancos cambian de signo o si ahi f toca 0 (y no junto a
            # un hueco: exp(1/x) cerca de 0 es diminuta pero no 0)
            iz = zs[i - 1] if i > 0 else None
            de = zs[j + 1] if j < n else None
            p = pisos[k] if isinstance(pisos, list) else pisos
            ancho = xs[min(j + 1, n)] - xs[max(i - 1, 0)]
            if largo >= 3 and (k == 0 or k == n):
                # cola plana en la orilla (f' de x*exp(-x) en [0,100]): si
                # g sigue bajando afuera, el centro cae fuera de [a,b]
                v = _seguro(f, xs[k] + (ancho if k == n else -ancho))
                if v is not None and abs(v) <= abs(ys[k]):
                    i = j + 1
                    continue
            c = _centro(f, xs[k], p, ancho)
            flancos = iz is not None and de is not None
            if flancos and iz * de < 0 or \
                    _toca_cero(f, c, p if flancos else 0.0):
                out.append(c)
            i = j + 1
            continue
        out.append(xs[k])                 # 0 exacto
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
                out.append(_afina(f, r[0], xs[i + 1] - xs[i]))
            else:
                saltos.append(r[0])
    return out, saltos


def _ruido(g, c, gc=None):
    """Ruido MEDIDO de g junto a c: segundas diferencias con paso
    1e-9|c| (ahi la curvatura de verdad es ~0; lo que queda es el
    redondeo), x2. 0 si g no existe ahi."""
    e = 1e-9 * max(1.0, abs(c))
    if gc is None:
        gc = _seguro(g, c)
    v = [_seguro(g, c + k * e) for k in (-3, -2, -1, 1, 2, 3)]
    if gc is None or None in v:
        return 0.0
    v = v[:3] + [gc] + v[3:]
    return 2 * max([abs(v[k - 1] - 2 * v[k] + v[k + 1])
                    for k in range(1, 6)])


def _afina(g, c, tope):
    """Si junto a c g es solo ruido MEDIDO (f'' de 1e5+sin(x/10)) o 0
    exacto (f'' de 1+x^5(x-3): ahi f vale 1.0 justo), el cero cae en
    cualquier punto de esa zona: se toma su centro."""
    p = _ruido(g, c)
    dz = 1e-6 * max(1.0, abs(c))
    u, v = _seguro(g, c - dz), _seguro(g, c + dz)
    if u is not None and v is not None and abs(u) <= p and abs(v) <= p:
        return _centro(g, c, p, tope)
    return c


def _zona(g, c, T, tope):
    """Orillas de la zona |g| <= T alrededor de c y si alguna quedo
    topada (la zona sigue mas alla del tope: su centro no sirve)."""
    lados = []
    topada = False
    for sg in (-1, 1):
        lim = max(1e-2 * max(1.0, abs(c)), tope)
        w = 1e-9 * max(1.0, abs(c))
        while True:
            if w >= lim:
                w = lim
                v = _seguro(g, c + sg * w)
                if v is not None and abs(v) <= T:
                    topada = True
                break
            v = _seguro(g, c + sg * w)
            if v is None or abs(v) > T:
                break
            w *= 2
        lo, hi = 0.5 * w, w
        for _ in range(32):
            m = 0.5 * (lo + hi)
            v = _seguro(g, c + sg * m)
            if v is not None and abs(v) <= T:
                lo = m
            else:
                hi = m
        lados.append(c + sg * lo)
    return lados[0], lados[1], topada


def _centro(g, c, T, tope=0.0):
    """Centro de la zona plana |g| <= T alrededor de c: el minimo de
    |f'| en x^3 o sin(x)^3 esta en medio de la zona donde f' ya es solo
    ruido (la ternaria cae en cualquier punto de esa zona). Si la zona
    esta inclinada (f'' = 30x^3(x-2) + ruido grande), su centro se corre
    como ancho^2: se mide a T y a 4T y se extrapola a ancho 0."""
    a1, b1, t1 = _zona(g, c, T, tope)
    m1, r1 = 0.5 * (a1 + b1), (b1 - a1) ** 2
    if t1:
        return m1
    a2, b2, t2 = _zona(g, c, 4 * T, tope)
    m2, r2 = 0.5 * (a2 + b2), (b2 - a2) ** 2
    if not t2 and r2 > 1.2 * r1:
        return (m1 * r2 - m2 * r1) / (r2 - r1)
    return m1


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


def _redondea(g, c, piso, tope=0.0, g2=None, redondos=True):
    """Pasa c a un valor REDONDO cercano (0, entero, 1 o 2 decimales, a
    lo mucho 1e-4 relativo) si ahi |g| no pasa de |g(c)| + el ruido MEDIDO
    de g junto a c (f' de x^5-5x^4+... en 1) + su truncado si hay g2 (f''
    de x^5(x-3) en 0), sin pasar de tope. Asi un cero plano cae en 0, 1 o
    0.5 y uno de verdad (1.00005, 2+raiz 2, 2pi) no se mueve. Luego el
    redondeo a 6 decimales de siempre, con piso (ruido estimado)."""
    r = round(c, 6) + 0.0
    if abs(r - c) <= 1e-8 * max(1.0, abs(c)):
        c = r
    gc = _seguro(g, c)
    if gc is None:
        return c
    if redondos:
        w = 1e-4 * max(1.0, abs(c))
        extra = _ruido(g, c, gc) if tope > 0 else 0.0
        for dg in (-1, 0, 1, 2):
            r = 0.0 if dg < 0 else round(c, dg) + 0.0
            if r == c or abs(r - c) > w:
                continue
            gr = _seguro(g, r)
            if gr is None:
                continue
            cr = extra
            if g2 is not None and tope > 0:
                t2 = _seguro(g2, r)
                if t2 is not None:
                    cr = cr + abs(gr - t2) / 15.0
            if abs(gr) <= abs(gc) + min(cr, tope):
                return r
    r = round(c, 6) + 0.0
    if r != c and abs(r - c) <= 1e-5 * max(1.0, abs(c)):
        gr = _seguro(g, r)
        if gr is not None and abs(gr) <= abs(gc) + piso:
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
        v = _seguro(f, x)
        if v is not None and not _hueco(f, x):
            if v == 0 or _toca_cero(f, x):
                out.append(x)
        elif _es_num(L) and abs(L) <= 1e-6 * s and _en_dominio(f, x):
            out.append(x)
    if dobles:
        for c in crit:
            if not _toca_cero(f, c):
                continue
            cerca = [q for q in range(len(out))
                     if abs(out[q] - c) <= 1e-4 * max(1.0, abs(c))]
            if not cerca:
                out.append(c)
                continue
            fc = abs(_seguro(f, c))       # el mismo cero: queda el mejor
            for q in cerca:
                fq = _seguro(f, out[q])
                if fq is None or fc < abs(fq):
                    out[q] = c
    return _snap([_redondea(f, x, 0.0) for x in out], a, b)


def ceros_tramo(f, a, b, n=200):
    """Tramos de [a,b] donde f vale 0 (no solo en un punto)."""
    xs, ys = _malla(f, a, b, n)
    zs = _ceros_z(ys, 0.0)
    out = []
    for i, j in _mesetas(zs):
        p = xs[i] if i == 0 or zs[i - 1] is None else \
            _orilla(f, xs[i - 1], xs[i], 0.0)
        q = xs[j] if j == n or zs[j + 1] is None else \
            _orilla(f, xs[j + 1], xs[j], 0.0)
        out.append((_z(_bonito(p), 1e-12), _z(_bonito(q), 1e-12)))
    return out


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


def _saltos(f, xs, ys):
    """Discontinuidades de salto (x^2 si x<=1, 3-x^2 si no): lista de
    (x, lim izq, lim der) con los dos limites finitos y distintos. Se
    buscan en las celdas donde f brinca mucho mas que en las vecinas."""
    n = len(xs) - 1
    out = []
    for i in range(1, n - 1):
        if None in (ys[i - 1], ys[i], ys[i + 1], ys[i + 2]):
            continue
        dm = abs(ys[i + 1] - ys[i])
        if dm == 0 or dm <= 10 * max(abs(ys[i] - ys[i - 1]),
                                     abs(ys[i + 2] - ys[i + 1])):
            continue
        lo, hi, flo, fhi = xs[i], xs[i + 1], ys[i], ys[i + 1]
        for _ in range(60):
            m = 0.5 * (lo + hi)
            fm = _seguro(f, m)
            if fm is None:
                break
            if abs(fm - flo) > abs(fhi - fm):
                hi, fhi = m, fm
            else:
                lo, flo = m, fm
        c = 0.5 * (lo + hi)
        if abs(c - round(c, 6)) <= 1e-8 * max(1.0, abs(c)):
            c = round(c, 6) + 0.0
        izq, der = limite(f, c, -1), limite(f, c, 1)
        if _es_num(izq) and _es_num(der) and \
                abs(izq - der) > 1e-6 * max(1.0, abs(izq), abs(der)):
            out.append((c, izq, der))
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
    # en una esquina con pendientes distintas (abs(x)+x/2) la f' suavizada
    # cruza 0 corrida unas h: se afina con la derivada fina
    for q in range(len(ceros)):
        c = ceros[q]
        if _esquina(f, c):
            w = 1e-4 * max(1.0, abs(c))
            r = _corte(fino, c - w, c + w)
            if r is not None:
                ceros[q] = r[0]
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
                out.append(_centro(df, c, 10 * T, 4.0 * (b - a) / n))
    df2 = lambda x: d(f, x, 2e-5 * max(1.0, abs(x)))
    res = []
    for c in out:
        fc = _seguro(f, c)
        piso = _ruido1(c, fc) + 1e-14 * s
        c = _redondea(df, c, piso, max(s1, _ruido1(c, fc)), df2)
        res.append(_redondea(fino, c, piso, 0.0, None, False))
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


def _clasifica(f, x, delta, s1=0.0, dmax=0.0):
    """Prueba de la primera derivada con f' a +-delta: 'max' si pasa de
    + a - (o de + a plano), 'min' si pasa de - a +, 'ni max ni min' si
    no cambia de signo. s1: piso minimo de f' (escala). Si f' aun esta
    bajo el ruido (x^6 en 0), delta crece hasta dmax."""
    while True:
        sg = []
        for t in (x - delta, x + delta):
            sg.append(_signo(_seguro(lambda u: d(f, u), t),
                             max(_ruido1(t, _seguro(f, t)), s1)))
        if sg[0] != 0 and sg[1] != 0 or 2 * delta > dmax:
            break
        delta = 2 * delta
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
    for w in (1e-4, 1e-5):
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


def extremos(f, a, b, n=200, crit=None, pol=None, sal=None):
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
    if sal is None:
        sal = _saltos(f, xs, ys)
    ps = [p[0] for p in pol]
    js = [q[0] for q in sal]
    t = 1e-9 * max(1.0, abs(b - a))
    s1 = 1e-8 * _escala([_seguro(lambda u: d(f, u), x) for x in xs])
    out = []
    for c, izq, der in sal:           # en un salto: comparar valores
        y = _seguro(f, c)
        if y is None or abs(c - a) <= t or abs(c - b) <= t:
            continue
        y = 0.0 if _toca_cero(f, c) else y + 0.0
        h = 1e-6 * max(1.0, abs(c))
        yi, yd = _seguro(f, c - h), _seguro(f, c + h)
        if yi is None or yd is None:
            continue
        if y >= yi and y >= yd:
            out.append((c, y, 'max'))
        elif y <= yi and y <= yd:
            out.append((c, y, 'min'))
    for c in crit:
        if abs(c - a) <= t or abs(c - b) <= t \
                or not _lejos(c, ps, _ventana(c, a, b)) \
                or not _lejos(c, js, _ventana(c, a, b)):
            continue
        y = _seguro(f, c)
        if y is None or _hueco(f, c):
            continue
        if _toca_cero(f, c):
            y = 0.0
        otros = [abs(c - o) for o in crit + ps + js if o != c]
        dmax = min([0.5 * v for v in otros] + [abs(b - a)])
        out.append((c, y, _clasifica(f, c, _delta(c, crit + ps, paso), s1,
                                     dmax)))
    return sorted(out, key=lambda q: q[0])


def _sin_repetir(cands):
    """Un candidato por x (el que se alcanza, si hay dos)."""
    out = []
    for c in sorted(cands, key=lambda c: (c[0], not c[2])):
        if not out or abs(c[0] - out[-1][0]) > 1e-7 * max(1.0, abs(c[0])):
            out.append(c)
    return out


def absolutos(f, a, b, n=200, crit=None, pol=None, sal=None):
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
    if sal is None:
        sal = _saltos(f, xs, ys)
    ps = [p[0] for p in pol]
    arriba = abajo = False
    cand = []
    for x, izq, der in sal:           # los lados de un salto no se alcanzan
        cand.append((x, izq, False))
        cand.append((x, der, False))
        y = _seguro(f, x)
        if y is not None:
            cand.append((x, y, True))
    malla = [(xs[i], ys[i], True) for i in range(len(xs))
             if ys[i] is not None and _lejos(xs[i], ps, _ventana(xs[i], a, b))]
    for x, izq, der in pol:
        for L in (izq, der):
            if L == INF:
                arriba = True
            elif L == -INF:
                abajo = True
            elif _es_num(L):
                cand.append((x, L, False))
    js = [q[0] for q in sal]
    for x in [a, b] + crit:
        if not _lejos(x, ps, _ventana(x, a, b)) or \
                x not in (a, b) and not _lejos(x, js, _ventana(x, a, b)):
            continue
        y = _seguro(f, x)
        if y is not None and not _hueco(f, x):
            cand.append((x, 0.0 if _toca_cero(f, x) else y, True))
        else:
            for L in _laterales(f, x, a, b):
                if _es_num(L):
                    cand.append((x, L, False))
    for x, L in _bordes(f, xs, ys):
        y = _seguro(f, x)
        if y is not None and not _hueco(f, x):
            cand.append((x, 0.0 if _toca_cero(f, x) else y, True))
        elif _es_num(L):
            cand.append((x, L, _en_dominio(f, x)))

    def mejores(signo):
        # red de seguridad: un nodo de la malla solo entra si le gana a
        # todos los candidatos (se le escapo algo, p. ej. un punto suelto)
        lista = cand
        if malla:
            m = max(malla, key=lambda c: signo * c[1])
            if not cand or signo * m[1] > max([signo * c[1] for c in cand]) \
                    + 1e-9 * abs(m[1]):
                lista = cand + [m]
        if not lista:
            return []
        vals = [signo * c[1] for c in lista]
        top = max(vals)
        tol = 1e-9 * abs(top)
        return _sin_repetir([c for c in lista
                             if abs(signo * c[1] - top) <= tol])

    return (None if arriba else mejores(1),
            None if abajo else mejores(-1))


def maxmin(f, a, b, n=200):
    """((xmax, ymax), (xmin, ymin)) absolutos; None del lado que no
    existe. El reporte completo (empates, huecos) es absolutos()."""
    maxs, mins = absolutos(f, a, b, n)
    uno = lambda l: (l[0][0], l[0][1]) if l else None
    return uno(maxs), uno(mins)


def inflexion(f, a, b, n=200, pol=None, crit=None, sal=None):
    """Puntos de inflexion interiores: f'' cambia de signo (por encima
    del ruido numerico), f existe ahi y no es una asintota. Si cae
    pegada a una esquina (abs(x^2-3)), la inflexion es la esquina."""
    xs, ys = _malla(f, a, b, n)
    paso = (b - a) / n
    if pol is None:
        pol = polos(f, a, b, n)
    if sal is None:
        sal = _saltos(f, xs, ys)
    ps = [p[0] for p in pol] + [q[0] for q in sal]
    dd = lambda u: d2(f, u)
    dd2 = lambda u: d2(f, u, 2e-4 * max(1.0, abs(u)))
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
        esq = False
        for q in esquinas:            # la inflexion es la esquina misma
            if abs(q - c) < 1e-3 * max(1.0, abs(q)):
                c, esq = q, True
                y = _seguro(f, c)
                break
        # en una esquina f'' numerica tiene un pico falso: sus cruces
        # vecinos no cuentan para el ancho de la prueba de signo
        vec = [o for o in cands + ps
               if not esq or abs(o - c) >= 1e-3 * max(1.0, abs(c))]
        dl = _delta(c, vec, paso)
        otros = [abs(c - o) for o in vec if o != c]
        dmax = min([0.5 * v for v in otros] + [abs(b - a)])
        while True:
            i = _seguro(dd, c - dl)
            k = _seguro(dd, c + dl)
            pi = max(_ruido2(c - dl, _seguro(f, c - dl)), s2)
            pk = max(_ruido2(c + dl, _seguro(f, c + dl)), s2)
            listo = i is not None and k is not None and \
                abs(i) > pi and abs(k) > pk
            if listo or 2 * dl > dmax:
                break
            dl = 2 * dl                   # f'' plana (x^7 en 0)
        if i is None or k is None or \
                not (i > pi and k < -pk or i < -pi and k > pk):
            continue
        if not esq:                   # en la esquina f'' salta: no redondear
            c = _redondea(dd, c, 0.0, max(s2, _ruido2(c, y)), dd2)
            if abs(c - a) <= t or abs(c - b) <= t:
                continue
            y = _seguro(f, c)
        out.append((_z(c, t), y))
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


def _borde_entre(f, dentro, fuera):
    """Borde del dominio entre un punto donde f existe y uno donde no."""
    for _ in range(60):
        m = 0.5 * (dentro + fuera)
        if _seguro(f, m) is None:
            fuera = m
        else:
            dentro = m
    return _z(_bonito(dentro), 1e-12)


def _saltos_txt(sal):
    return ["salto en x={:.6g}: izq {:.6g}, der {:.6g}".format(c, i, k)
            for c, i, k in sal]


def _tramos_txt(f, xs, ys):
    """Avisos: donde f no existe y donde f vale 0 en todo un tramo, con
    los bordes reales ('(' si ahi f si existe, '[' si no)."""
    out = []
    n = len(xs) - 1
    i = 0
    while i <= n:
        if ys[i] is not None:
            i += 1
            continue
        j = i
        while j < n and ys[j + 1] is None:
            j += 1
        if j > i:
            p = xs[0] if i == 0 else _borde_entre(f, xs[i - 1], xs[i])
            q = xs[n] if j == n else _borde_entre(f, xs[j + 1], xs[j])
            ab = "[" if _seguro(f, p) is None else "("
            ci = "]" if _seguro(f, q) is None else ")"
            out.append("f no existe en {}{:.6g}, {:.6g}{}".format(
                ab, p, q, ci))
        i = j + 1
    for p, q in ceros_tramo(f, xs[0], xs[-1], n):
        out.append("f = 0 en todo [{:.6g}, {:.6g}]".format(p, q))
    return out


def analiza(f, a, b, n=200):
    """Reporte completo listo para leer en pantalla."""
    print("f en [{:g}, {:g}]".format(a, b))
    xs, ys = _malla(f, a, b, n)
    s = _escala(ys)
    crit = _criticos(f, a, b, n, s, xs, ys)
    pol = polos(f, a, b, n)
    sal = _saltos(f, xs, ys)
    for linea in _tramos_txt(f, xs, ys) + _saltos_txt(sal):
        print(linea)
    r = raices(f, a, b, n, 1e-12, True, None, crit)
    print("raices:", _fmt(r) if r else "ninguna")
    if pol:
        print("asintota en x=" + _fmt([p[0] for p in pol]))
    for x, y, t in extremos(f, a, b, n, crit, pol, sal):
        print("{}: x={:.6g}  y={:.6g}".format(t, x, y))
    infl = inflexion(f, a, b, n, pol, crit, sal)
    if infl:
        print("inflex:", _fmt([p[0] for p in infl]))
    maxs, mins = absolutos(f, a, b, n, crit, pol, sal)
    for linea in _abs_txt("abs max", maxs, "sube", s) + \
            _abs_txt("abs min", mins, "baja", s):
        print(linea)


def alto_bajo(f, a, b, n=200):
    """Punto mas alto y mas bajo en [a,b] y los extremos locales."""
    xs, ys = _malla(f, a, b, n)
    s = _escala(ys)
    crit = _criticos(f, a, b, n, s, xs, ys)
    pol = polos(f, a, b, n)
    sal = _saltos(f, xs, ys)
    for linea in _tramos_txt(f, xs, ys) + _saltos_txt(sal):
        print(linea)
    if pol:
        print("asintota en x=" + _fmt([p[0] for p in pol]))
    maxs, mins = absolutos(f, a, b, n, crit, pol, sal)
    for linea in _abs_txt("mas alto", maxs, "sube", s) + \
            _abs_txt("mas bajo", mins, "baja", s):
        print(linea)
    for x, y, t in extremos(f, a, b, n, crit, pol, sal):
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


_HS = [10.0 ** (-k) for k in range(1, 10)]
_HS_FINO = [10.0 ** (-1 - j / 4.0) for j in range(13)]   # 0.1 ... 5.6e-5


def _valores(f, x0, signo, hs=_HS):
    """f(x0 + signo*h) para h = 0.1 ... 1e-9: None donde no existe, _OVF
    donde se desborda (exp(1/x) cerca de 0)."""
    out = []
    for h in hs:
        try:
            y = f(x0 + signo * h)
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
    # crece sin frenar con el mismo signo (1/x, ln x): 5% o mas en CADA
    # paso de un tramo de 5+ valores que llega al final o termina porque
    # la cancelacion lo tira a 0 ((1-cos x)/x^4). Si solo se estanca
    # (1/(x^2+1e-10)) es un pico finito.
    for e in range(min(4, len(v))):
        q = e + 1
        while q < len(v) and abs(v[q]) > 1.05 * abs(v[q - 1]) \
                and (v[q] > 0) == (v[e] > 0):
            q += 1
        # si despues se queda quieto (+-5%) es un pico que se estanca; si
        # sigue ruido o cae a 0 por cancelacion, el crecimiento era real
        quieto = len(v) - q >= 2 and all(
            [abs(w - v[q - 1]) <= 0.05 * abs(v[q - 1]) for w in v[q:q + 2]])
        if q - e >= 5 and abs(v[q - 1]) >= 2 * abs(v[e]) and not quieto:
            return INF if v[q - 1] > 0 else -INF
    # se va a 0: rapido (x^2, x*sin(1/x)) o lento (sqrt(x), 1/ln(x)); en
    # los dos ya se nota bajando desde el principio (si no, los ceros del
    # final son cancelacion y no un limite 0)
    temprano = abs(v[3]) <= 0.1 * abs(v[0]) if len(v) > 3 else False
    if temprano and max([abs(w) for w in v[-3:]]) <= \
            1e-5 * max([abs(w) for w in v[:3]]):
        return 0.0
    u = v[-5:]
    if all([abs(u[i + 1]) < abs(u[i]) for i in range(len(u) - 1)]) \
            and all([(w > 0) == (u[-1] > 0) for w in u]) \
            and abs(u[-2] - u[-1]) > 0.05 * abs(u[-1]) \
            and abs(v[-1]) <= 0.5 * abs(v[0]):
        return 0.0
    L, err, fin = _extrapola(v)
    if fin <= 3 or err > 1e-7 * max(1.0, abs(L)):
        # muy pocos valores limpios (cancelacion de orden alto como
        # (cos x - 1 + x^2/2)/x^4): muestreo mas fino entre 0.1 y 6e-5
        vf = [w for w in _valores(f, x0, signo, _HS_FINO)
              if w is not None and w != _OVF]
        if len(vf) >= 4:
            L2, err2, fin2 = _extrapola(vf)
            if fin2 > fin or err2 < err:
                L, err, fin, v = L2, err2, fin2, vf
    if err > 1e-3 * max(1.0, abs(L)):
        return None                       # no se asienta: oscila
    if abs(L) <= 1e-9 * max([abs(w) for w in v[:fin]]):
        return 0.0                        # (1-cos x)/x: ruido de 1e-13
    return _redondo(L)


def _extrapola(v):
    """Meseta de v: se corta donde las diferencias empiezan a crecer
    (desde ahi manda el redondeo), y en la parte limpia extrapolacion de
    Richardson con la razon de convergencia medida q:
    L = v_j - (v_(j-1) - v_j) q/(1-q). Se toma la L que mas coincide
    con su vecina. Devuelve (L, error estimado, largo limpio)."""
    dif = [abs(v[i + 1] - v[i]) for i in range(len(v) - 1)]
    # transitorio inicial (1/(x^2+1e-6) en 0: con h >= 1e-3 el pico aun
    # no se forma y las diferencias CRECEN): se salta
    s0 = 0
    while s0 + 1 < len(dif) and dif[s0 + 1] > dif[s0]:
        s0 += 1
    if not (s0 + 2 < len(dif) and dif[s0 + 1] <= dif[s0]
            and dif[s0 + 2] < dif[s0 + 1]):
        s0 = 0                        # crecer sin bajar despues = ruido
    fin = len(v)
    for i in range(s0 + 1, len(dif)):
        if dif[i] > dif[i - 1]:
            fin = i + 1
            break
    R = []
    for j in range(s0 + 1, fin):
        q = 0.1
        if j >= s0 + 2 and dif[j - 2] > 0:
            q = min(max(dif[j - 1] / dif[j - 2], 1e-4), 0.7)
        R.append(v[j] - (v[j - 1] - v[j]) * q / (1 - q))
    if len(R) >= 2:
        dR = [abs(R[j] - R[j - 1]) for j in range(1, len(R))]
        k = dR.index(min(dR))
        return R[k + 1], dR[k], fin
    return v[fin - 1], dif[max(0, fin - 2)], fin


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


# ===================== formulas =====================

# formulas - formulario de AP Calculus para TI-Nspire CX II CAS
# Adrian. Solo formulas y tips, cero calculos.
# Pieza de ap y general: se abre con la opcion 9 del menu de ap.
# Contenido redactado y verificado matematicamente (2026-09-14).

TEMAS = [
    ('Limites y continuidad', [
        '-- limites notables --',
        'lim x->0 sin(x)/x = 1',
        'lim x->0 (1-cos x)/x = 0',
        'lim x->inf (1+1/x)^x = e',
        'lim x->0 (1+x)^(1/x) = e',
        'TIP: x->0: sin(kx)/(mx) -> k/m',
        '',
        '-- limites laterales --',
        'lim existe si lados coinciden:',
        'lim x->a- f = lim x->a+ f = L',
        'si difieren, lim NO existe',
        'TIP: en |x| y tramos revisa lados',
        '',
        "-- l'hopital --",
        'Solo formas 0/0 o inf/inf',
        "f,g derivables, g'!=0 cerca de a",
        "lim f(x)/g(x) = lim f'(x)/g'(x)",
        'TIP: verifica la forma ANTES',
        'TIP: deriva num y den APARTE,',
        'no es la regla del cociente',
        "TIP: escribe 'forma 0/0' en FRQ",
        '',
        '-- continuidad en x=a --',
        '1) f(a) existe',
        '2) lim x->a f(x) existe',
        '3) lim x->a f(x) = f(a)',
        'TIP: cita las 3 en un FRQ',
        '',
        '-- discontinuidades --',
        'Removible: lim existe, pero',
        'f(a) != lim o f(a) no existe',
        'Salto: lim izq != lim der',
        '(ambos laterales finitos)',
        'Infinita: asintota vertical',
        'TIP: removible = hueco arreglable',
        '',
        '-- asintotas (racionales) --',
        'Vertical: den=0 y num!=0',
        'TIP: num=den=0: simplifica;',
        'queda hueco o AV segun factor',
        'Horizontal: compara grados',
        'grado num < den: y = 0',
        'iguales: y = razon coef lider',
        'grado num > den: no hay AH',
        'TIP: AH = lim x->+-inf f(x)',
        '',
        '-- IVT valor intermedio --',
        'f continua en [a,b], k entre',
        'f(a) y f(b) => existe c en',
        '(a,b) con f(c) = k',
        "TIP: FRQ: di 'f es continua'",
        'TIP: y da f(a), f(b) con signos',
        '',
        '-- teorema del sandwich --',
        'g <= f <= h cerca de a y',
        'lim g = lim h = L => lim f = L',
        'TIP: x^2 sin(1/x) -> 0 si x->0',
    ]),
    ('Derivadas: reglas y tabla', [
        '-- definicion de derivada --',
        "f'(x) = lim h->0 [f(x+h)-f(x)]/h",
        "f'(c) = lim x->c [f(x)-f(c)]/(x-c)",
        'TIP: ese limite = derivada disfrazada',
        '',
        '-- derivable y continua --',
        'derivable => continua (no al reves)',
        '|x| es continua pero no derivable en 0',
        "no hay f'(c) si hay: esquina, cuspide,",
        'tangente vertical o discontinuidad',
        '',
        '-- reglas basicas --',
        "d/dx[c]=0, d/dx[c*f]=c*f', (f+g)'=f'+g'",
        'potencia: d/dx[x^n] = n*x^(n-1)',
        "producto: (f*g)' = f'*g + f*g'",
        "cociente: (f/g)' = (f'*g - f*g')/g^2",
        "TIP: en cociente f' va primero arriba",
        '',
        '-- regla de la cadena --',
        "d/dx[f(g(x))] = f'(g(x)) * g'(x)",
        "TIP: no olvides multiplicar por g'(x)",
        '',
        '-- tabla de derivadas --',
        'd/dx[e^x] = e^x',
        'd/dx[a^x] = a^x * ln(a)',
        'd/dx[ln(x)] = 1/x',
        'd/dx[log_a(x)] = 1/(x*ln(a))',
        'd/dx[sin(x)] = cos(x)',
        'd/dx[cos(x)] = -sin(x)',
        'd/dx[tan(x)] = sec(x)^2',
        'd/dx[sec(x)] = sec(x)*tan(x)',
        'd/dx[csc(x)] = -csc(x)*cot(x)',
        'd/dx[cot(x)] = -csc(x)^2',
        "TIP: las 'co' llevan signo negativo",
        '',
        '-- inversas trigonometricas --',
        'd/dx[arcsin(x)] = 1/sqrt(1-x^2)',
        'd/dx[arccos(x)] = -1/sqrt(1-x^2)',
        'd/dx[arctan(x)] = 1/(1+x^2)',
        '',
        '-- derivacion implicita --',
        '1) deriva ambos lados respecto a x',
        '2) terminos con y: usa cadena (dy/dx)',
        '3) agrupa terminos con dy/dx',
        '4) factoriza dy/dx y despeja',
        'TIP: con punto dado, sustituye (x,y)',
        'tras derivar (nunca antes de derivar)',
        '',
        '-- derivada de la inversa --',
        "(f^-1)'(a) = 1/f'(f^-1(a))",
        "requiere f'(f^-1(a)) != 0",
        "TIP: halla b con f(b)=a; usa 1/f'(b)",
    ]),
    ('Aplicaciones de la derivada', [
        '-- tangente y normal --',
        "tangente: y = f(a) + f'(a)(x-a)",
        "normal: pendiente = -1/f'(a)",
        "requiere f'(a) != 0",
        '',
        '-- linearizacion --',
        "L(x) = f(a) + f'(a)(x-a)",
        'TIP: concava abajo -> L sobreestima',
        'TIP: concava arriba -> L subestima',
        '',
        '-- MVT y Rolle --',
        'f continua en [a,b], derivable (a,b)',
        "-> c en (a,b): f'(c)=(f(b)-f(a))/(b-a)",
        "Rolle: ademas f(a)=f(b) -> f'(c)=0",
        '',
        '-- EVT --',
        'f continua en [a,b] -> max y min abs',
        '',
        '-- criticos y extremos abs --',
        "critico: f'(c)=0 o f'(c) no existe",
        'c debe estar en el dominio de f',
        'abs: evalua f en criticos y bordes',
        '',
        '-- test 1a derivada --',
        "f' de + a - en c -> max relativo",
        "f' de - a + en c -> min relativo",
        '',
        '-- test 2a derivada --',
        "f'(c)=0 y f''(c)<0 -> max rel",
        "f'(c)=0 y f''(c)>0 -> min rel",
        "TIP: f''(c)=0 no concluye, usa f'",
        '',
        '-- concavidad e inflexion --',
        "f''>0 concava arriba, f''<0 abajo",
        "inflexion: f'' cambia de signo",
        "TIP: f''=0 no basta sin cambio",
        '',
        '-- movimiento rectilineo --',
        "v = x'(t), a = v'(t), rapidez = |v|",
        'rapidez sube si v*a>0, baja si v*a<0',
        'derecha si v>0, izquierda si v<0',
        '',
        '-- related rates --',
        '1 ecuacion 2 deriva d/dt 3 sustituye',
        'TIP: sustituye numeros AL FINAL',
        '',
        '-- optimizacion --',
        "1 objetivo 2 restriccion 3 f'=0",
        'TIP: verifica max/min y checa bordes',
        '',
        '-- frases AP --',
        "max rel en c: f' cambia de + a -",
        "min rel en c: f' cambia de - a +",
        'max abs: compara f en candidatos',
        'TIP: justifica con signos, no grafica',
    ]),
    ('Integrales y Teorema Fundamental', [
        '-- teorema fundamental parte 1 --',
        'd/dx Int[a,x] f(t)dt = f(x)',
        "d/dx Int[a,g(x)] f(t)dt = f(g(x))g'(x)",
        '(requiere f continua)',
        'TIP: si la variable esta abajo,',
        'invierte limites y cambia signo',
        '',
        '-- teorema fundamental parte 2 --',
        'Int[a,b] f(x)dx = F(b) - F(a)',
        'F es cualquier antiderivada de f',
        '(requiere f continua en [a,b])',
        '',
        '-- antiderivadas basicas --',
        'Int x^n dx = x^(n+1)/(n+1)+C, n!=-1',
        'Int 1/x dx = ln|x| + C',
        'Int e^x dx = e^x + C',
        'Int cos x dx = sin x + C',
        'Int sin x dx = -cos x + C',
        'Int sec^2 x dx = tan x + C',
        'Int sec x tan x dx = sec x + C',
        'Int 1/(1+x^2) dx = arctan x + C',
        'Int 1/sqrt(1-x^2) dx = arcsin x + C',
        'TIP: no olvides +C en indefinidas,',
        'vale puntos en el FRQ',
        '',
        '-- u-sustitucion --',
        "elige u = parte interna, du = u'dx",
        "Int f(g(x))g'(x)dx = Int f(u)du",
        'TIP: en definidas cambia limites:',
        'x=a -> u=g(a), x=b -> u=g(b)',
        'y ya no regreses a x',
        '',
        '-- propiedades --',
        'Int[a,b] f = -Int[b,a] f',
        'Int[a,b] f + Int[b,c] f = Int[a,c] f',
        'Int (f+g) = Int f + Int g',
        'Int c*f = c*Int f',
        '',
        '-- sumas de riemann --',
        'S = Sum f(x_i)*dx, dx = (b-a)/n',
        'x_i: extremo izq, der o pto medio',
        'trapecio = (izq + der)/2',
        'TIP: f creciente =>',
        'izq subestima, der sobreestima',
        'f decreciente => al reves',
        'TIP: concava arriba => trapecio',
        'sobreestima, pto medio subestima',
        'concava abajo => al reves',
        '',
        '-- valor promedio --',
        'f_prom = 1/(b-a) * Int[a,b] f(x)dx',
        'TIP: no es (f(a)+f(b))/2',
    ]),
    ('Aplicaciones de integral y EDO', [
        '-- area entre curvas --',
        'A = Int[a,b] (arriba - abajo) dx',
        'A = Int[c,d] (der - izq) dy',
        'TIP: si se cruzan, parte la integral',
        'TIP: cruce: resuelve f = g en la calc',
        '',
        '-- volumen: discos y arandelas --',
        'disco: V = pi Int[a,b] R^2 dx',
        'arandela: V = pi Int[a,b] (R^2 - r^2) dx',
        'R y r se miden DESDE el eje de giro',
        'TIP: gira en y=k: R = |curva - k|',
        'TIP: (R^2 - r^2) != (R - r)^2',
        '',
        '-- secciones transversales --',
        'V = Int[a,b] A(x) dx, s = dist curvas',
        'cuadrado: A = s^2',
        'semicirculo: A = (pi/8) s^2',
        'tri equilatero: A = (sqrt(3)/4) s^2',
        'tri rect isosceles: A = (1/2) s^2',
        'TIP: sin pi salvo semicirculo',
        '',
        '-- movimiento --',
        'pos final = pos inicial + Int[a,b] v dt',
        'desplazamiento = Int[a,b] v dt',
        'distancia = Int[a,b] |v| dt',
        'TIP: distancia >= |desplazamiento|',
        '',
        '-- acumulacion --',
        'cantidad = inicial + Int[a,b] razon dt',
        'TIP: entra - sale = razon neta',
        'TIP: max/min: razon neta = 0 o extremos',
        'TIP: max si razon pasa de + a -',
        '',
        '-- EDO separables --',
        '1) separa: g(y) dy = f(x) dx',
        '2) integra ambos lados',
        '3) +C ANTES de despejar y',
        '4) usa condicion inicial para C',
        '5) despeja y si lo piden',
        'TIP: e^C se vuelve una constante A',
        '',
        '-- crecimiento exponencial --',
        'dy/dt = ky => y = C e^(kt)',
        'C = y(0), valor inicial',
        "TIP: 'proporcional a y' => dy/dt = ky",
        '',
        '-- campos de pendientes --',
        'cada segmento tiene pendiente dy/dx',
        'TIP: busca donde dy/dx = 0 (horiz)',
        'TIP: checa signo de dy/dx por region',
        'TIP: solo x en la EDO: columnas iguales',
        'TIP: solo y en la EDO: filas iguales',
    ]),
    ('BC: Tecnicas, Parametricas, Polares', [
        '-- integracion por partes --',
        'Int u dv = uv - Int v du',
        'LIATE: Log, InvTrig, Alg, Trig, Exp',
        'TIP: u = la mas alta en LIATE',
        'TIP: dv debe ser facil de integrar',
        '',
        '-- fracciones parciales --',
        'P/((x-a)(x-b)) = A/(x-a)+B/(x-b)',
        'TIP: evalua x=a y x=b para A y B',
        'TIP: si grado arriba >= abajo, divide',
        '',
        '-- integrales impropias --',
        'Int[a,inf] f dx =',
        '  lim b->inf Int[a,b] f dx',
        'converge si el limite es finito',
        'TIP: escribe el limite en el examen',
        '',
        '-- longitud de arco --',
        "L = Int[a,b] sqrt(1+(f'(x))^2) dx",
        '',
        '-- ecuacion logistica --',
        'dP/dt = kP(1 - P/L)',
        'lim t->inf P = L (capacidad)',
        'crecimiento max en P = L/2',
        'TIP: en P=L/2, dP/dt = kL/4',
        '',
        '-- metodo de euler --',
        'y_sig = y + h*F(x,y)',
        'x_sig = x + h',
        'h = paso, F(x,y) = dy/dx',
        'TIP: haz tabla: x, y, dy/dx, y_sig',
        '',
        '-- parametricas --',
        'dy/dx = (dy/dt)/(dx/dt)',
        'd2y/dx2 = d/dt(dy/dx) / (dx/dt)',
        'L = Int[a,b]',
        '  sqrt((dx/dt)^2+(dy/dt)^2) dt',
        'TIP: tang horiz: dy/dt=0, dx/dt!=0',
        'TIP: tang vert: dx/dt=0, dy/dt!=0',
        '',
        '-- movimiento vectorial --',
        "v(t) = <x'(t), y'(t)>",
        "a(t) = <x''(t), y''(t)>",
        "rapidez = sqrt((x')^2+(y')^2)",
        'distancia = Int[a,b] rapidez dt',
        '',
        '-- polares --',
        'x = r cos(t), y = r sin(t)',
        'Area = (1/2) Int[a,b] r^2 dt',
        'TIP: limites del area: resuelve r=0',
        'TIP: checa interseccion de curvas',
    ]),
    ('BC: Series', [
        '-- serie geometrica --',
        'Sum a*r^n = a/(1-r) si |r| < 1',
        'TIP: a = 1er termino de la serie',
        'TIP: si |r| >= 1 diverge',
        '',
        '-- test del n-esimo termino --',
        'si lim a_n != 0 (o no existe) => div',
        'TIP: lim a_n = 0 NO concluye nada',
        '',
        '-- p-series: Sum 1/n^p --',
        'conv si p > 1; div si p <= 1',
        'TIP: armonica Sum 1/n (p=1) div',
        '',
        '-- comparacion --',
        'Directa, 0 <= a_n <= b_n:',
        'b_n conv=>a_n conv; a_n div=>b_n div',
        'Lim: a_n/b_n->L, 0<L<inf: mismo fin',
        '',
        '-- test de la integral --',
        'f pos, cont, decrec, a_n = f(n):',
        'Sum a_n conv <=> Int[1,inf] f dx conv',
        '',
        '-- serie alternante --',
        'Sum(-1)^n a_n, a_n > 0:',
        'conv si a_n decrece y lim a_n = 0',
        'error: |S - S_n| <= a_(n+1)',
        'TIP: cota = 1er termino omitido',
        '',
        '-- test de la razon --',
        'L = lim |a_(n+1)/a_n|',
        'L<1 conv abs; L>1 div; L=1 no dice',
        'TIP: usalo para radio de conv R',
        '',
        '-- conv absoluta vs condicional --',
        'abs: Sum |a_n| conv => Sum a_n conv',
        'cond: Sum a_n conv, Sum |a_n| div',
        '',
        '-- Taylor en c (Maclaurin: c=0) --',
        'Sum n=0..inf f^(n)(c)(x-c)^n/n!',
        'TIP: coef de (x-c)^n = f^(n)(c)/n!',
        'TIP: polinomio P_n = hasta grado n',
        '',
        '-- Maclaurin (e^x,sin,cos: todo x) --',
        'e^x = Sum x^n/n!',
        'sin x = Sum(-1)^n x^(2n+1)/(2n+1)!',
        'cos x = Sum(-1)^n x^(2n)/(2n)!',
        '1/(1-x) = Sum x^n, |x| < 1',
        'ln(1+x) = Sum(-1)^(n+1) x^n/n, n>=1',
        'ln(1+x): -1 < x <= 1',
        'arctan x = Sum(-1)^n x^(2n+1)/(2n+1)',
        'arctan: -1 <= x <= 1',
        '',
        '-- error de Lagrange --',
        '|R_n| <= M|x-c|^(n+1)/(n+1)!',
        'M = max |f^(n+1)| entre c y x',
        '',
        '-- intervalo de convergencia --',
        'razon da |x-c| < R; checa extremos',
        'TIP: cada extremo aparte, otro test',
    ]),
    ('AP CALC: TIPS DE EXAMEN', [
        '-- decimales y redondeo --',
        'TIP: respuestas con 3 decimales min',
        'TIP: redondea o trunca, ambos ok',
        'TIP: NUNCA redondees pasos intermedios',
        'TIP: guarda valores completos en calc',
        '',
        '-- justifica con calculo --',
        "TIP: nunca 'se ve en la grafica'",
        "max rel: f'(x) cambia de + a -",
        "min rel: f'(x) cambia de - a +",
        "concava arriba: f''(x) > 0",
        "pto inflexion: f'' cambia de signo",
        'MVT: cita f continua en [a,b]',
        'MVT: y derivable en (a,b)',
        'IVT: cita f continua en [a,b]',
        'IVT: y k entre f(a) y f(b)',
        '',
        '-- unidades y contexto --',
        'TIP: pon unidades si hay contexto',
        "TIP: interpreta: 'razon a la que...'",
        'TIP: di que, cuando y unidades',
        '',
        '-- vel vs rapidez, desp vs dist --',
        'velocidad = v(t), tiene signo',
        'rapidez = |v(t)|',
        'desplazamiento = Int[a,b] v(t) dt',
        'distancia = Int[a,b] |v(t)| dt',
        'TIP: lee cual piden, trampa clasica',
        '',
        '-- seccion con calculadora --',
        'TIP: integra/deriva numerico, ok',
        'TIP: sin pasos algebraicos, PERO',
        'TIP: ESCRIBE la integral o ecuacion',
        'TIP: planteada antes del numero',
        '',
        '-- no simplifiques --',
        'TIP: dejar 3/7 + e^2 esta bien',
        '',
        '-- manejo de tiempo --',
        'MCQ A: 30 preg/60 min, ~2 min c/u',
        'MCQ B: 15 preg/45 min, ~3 min c/u',
        'FRQ: 6 problemas, ~15 min c/u',
        'calc solo en MCQ B y FRQ parte A',
        'TIP: si te atoras, marca y sigue',
        '',
        '-- lee EXACTO que piden --',
        'TIP: trapecio? justifica? intervalo?',
        'TIP: subraya los verbos clave',
        '',
        '-- puntos FRQ --',
        'TIP: dan puntos por partes',
        'TIP: intenta TODOS los incisos',
        'TIP: aunque no salga el (a)',
    ]),
]


def formulario():
    while True:
        print("")
        print("== FORMULARIO AP CALC ==")
        for i, (t, _) in enumerate(TEMAS):
            print("{} {}".format(i + 1, t))
        print("0 salir")
        s = input("? ").strip()
        if s == "0" or s == "":
            return
        try:
            n = int(s)
        except ValueError:
            continue
        if 1 <= n <= len(TEMAS):
            _fo_muestra(TEMAS[n - 1])


_FO_ANCHO = 36   # caracteres por renglon del shell de la Nspire
_FO_ALTO = 8     # renglones por pantalla antes de pausar


def _fo_muestra(tema):
    """Pagina contando los renglones que se doblan en la pantalla."""
    titulo, lineas = tema
    print("")
    print("== " + titulo + " ==")
    c = 1
    for ln in lineas:
        alto = (len(ln) - 1) // _FO_ANCHO + 1 if ln else 1
        if c + alto > _FO_ALTO:
            if input("-- enter=mas, q=menu --").strip() == "q":
                return
            c = 0
        print(ln)
        c += alto
    input("-- fin, enter --")


# ===================== ap =====================

# ap - menu interactivo para Calculo AP
# El unico comando que hay que aprenderse: ap()
# Esta es la pieza del menu: build.py le pega calcpy y formulas y
# genera calculadora/ap.py (y general.py), que ya no necesitan nada.


def _ap_cbrt(x):
    """Raiz cubica real (Python da complejo con x^(1/3) si x<0)."""
    return abs(x) ** (1.0 / 3) if x >= 0 else -(abs(x) ** (1.0 / 3))


_ap_ns = {"sin": sin, "cos": cos, "tan": tan, "asin": asin, "acos": acos,
          "atan": atan, "sqrt": sqrt, "exp": exp, "log": log, "ln": log,
          "log10": log10, "pi": pi, "e": e, "abs": abs,
          "sen": sin, "cbrt": _ap_cbrt, "__builtins__": {}}


def _ap_txt(prompt):
    """Texto tecleado listo para eval: sin espacios a los lados (el eval
    de MicroPython 1.11 truena con espacio inicial) y ^ como potencia."""
    return input(prompt).strip().replace("^", "**")


_ap_ult = [""]    # ultimo texto de funcion tecleado


def _ap_tip_raiz(f, a):
    """x^(p/q) con x<0 da complejo en Python (en la calc, real)."""
    if "**(" in _ap_ult[0] and a < 0 and _seguro(f, a) is None:
        print("ojo: x^(p/q) con x<0 no existe")
        print("en Python. Usa cbrt(x) (raiz")
        print("cubica) o cbrt(x)^2 = x^(2/3)")


def _ap_f(prompt="f(x) = "):
    """Lee una funcion tecleada como texto. Acepta ^ como potencia."""
    s = _ap_txt(prompt)
    _ap_ult[0] = s
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


def _ap_lim(v):
    if v is None:
        return "no existe (oscila)"
    if v == NODEF:
        return "no definida (fuera del dominio)"
    if v == INF:
        return "+infinito (crece sin tope)"
    if v == -INF:
        return "-infinito (baja sin tope)"
    return "{:.6g}".format(v)


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
        print("8 particula v(t)")
        print("== REPASO ==")
        print("9 formulario (formulas y tips)")
        print("0 salir")
        op = ""
        try:
            op = input("? ").strip()
            if op == "0" or op == "":
                return
            _ap_corre(op)
        except Exception as err:
            print("error:", err)
        if op != "9":
            input("[enter]")


def _ap_corre(op):
    if op == "1":
        f = _ap_f()
        a, b = _ap_intervalo()
        analiza(f, a, b)
        _ap_tip_raiz(f, a)
    elif op == "2":
        f = _ap_f()
        a, b = _ap_intervalo()
        alto_bajo(f, a, b)
        _ap_tip_raiz(f, a)
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
            print("izq: " + _ap_lim(limite(f, x0, -1)))
            print("der: " + _ap_lim(limite(f, x0, 1)))
            print("(no existe bilateral)")
        else:
            print("limite = " + _ap_lim(L))
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
        x0 = _ap_num("x(a) pos. inicial (enter=0) = ", 0)
        particula(v, a, b, x0)
        t0 = _ap_num("rapidez en t = ", (a + b) / 2)
        print("la rapidez", rapidez(v, t0))
    elif op == "9":
        if formulario:
            formulario()
        else:
            print("falta formulas.py")
    else:
        print("no existe esa opcion")


# ===================== ai =====================

# ai - regresion lineal con gradiente descendente (IA PrepaTEC)
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


# ===================== fisica =====================

# FISICA.PY — Solucionador de mecanica + conversiones
# Para TI-Nspire CX II (Python / MicroPython)
# Notacion del formulario: g suma (abajo positivo en caida)


G = 9.81

def nval(s):
    # acepta 3e-5, 3x10^-5, 4*10^8, 10^-3
    # (la tecla ^ de la Nspire escribe ** dentro de Python)
    s = s.replace(" ", "")
    for tk in ("x10**", "X10**", "*10**", "x10^", "X10^", "*10^"):
        s = s.replace(tk, "e")
    for pre in ("10**", "10^"):
        if s.startswith(pre):
            s = "1e" + s[len(pre):]
        elif s.startswith("-" + pre):
            s = "-1e" + s[len(pre) + 1:]
    # sin mantisa ('e2', 'x10^2', '.'): MicroPython lo lee como 0.0
    m = s.lstrip("+-").split("e")[0].split("E")[0]
    if m.replace(".", "") == "":
        raise ValueError("falta el numero")
    v = float(s)
    if v != v or abs(v) == float("inf"):
        raise ValueError("nan o inf")
    return v

def num(msg):
    while True:
        try:
            return nval(input(msg))
        except ValueError:
            print("numero no valido (vale: 3e-5 o 3x10^-5)")

def dato(msg):
    while True:
        s = input(msg)
        if s == "":
            return None
        try:
            return nval(s)
        except ValueError:
            print("numero no valido (vale: 3e-5 o 3x10^-5)")

def sep():
    print("-" * 26)

def tip(t):
    print("* TIP:", t)

def r2(x, n=3):
    # n decimales sin colas tipo 78.43000000000001 de MicroPython; el
    # empujoncito redondea .xxx5 hacia arriba, como la calculadora
    if x == x and abs(x) < 1e12:
        x = round(x + (5e-10 if x > 0 else -5e-10), n)
    if x == 0:
        x = 0.0
    if x != x or abs(x) >= 1e12:
        return str(x)
    s = (("%." + str(n) + "f") % x).rstrip("0")
    if s[-1] == ".":
        s = s + "0"
    return s

def rp(x):
    # negativo entre parentesis en restas y potencias: (-8.0)^2
    s = r2(x)
    return "(" + s + ")" if s[:1] == "-" else s

def proc_print(proc):
    if proc:
        print("PROCEDIMIENTO:")
        for p in proc:
            print(" ", p)

CARD = {"E": 0.0, "ENE": 22.5, "NE": 45.0, "NNE": 67.5,
        "N": 90.0, "NNO": 112.5, "NO": 135.0, "ONO": 157.5,
        "O": 180.0, "OSO": 202.5, "SO": 225.0, "SSO": 247.5,
        "S": 270.0, "SSE": 292.5, "SE": 315.0, "ESE": 337.5,
        "W": 180.0, "NW": 135.0, "SW": 225.0}

def ang_rumbo(s):
    # devuelve angulo estandar (desde +x, antihorario) o None
    s = s.replace(" ", "").upper()
    if s in CARD:
        return CARD[s]
    # formato N30E : desde N, 30 grados hacia E
    if len(s) >= 3 and s[0] in "NS" and s[-1] in "EO" + "W":
        try:
            g = float(s[1:-1])
        except ValueError:
            return None
        base = s[0]
        hacia = "O" if s[-1] == "W" else s[-1]
        if base == "N" and hacia == "E":
            return 90.0 - g
        if base == "N" and hacia == "O":
            return 90.0 + g
        if base == "S" and hacia == "E":
            return 270.0 + g
        if base == "S" and hacia == "O":
            return 270.0 - g
    return None

def pedir_angulo(msg):
    print("  desde donde mides el angulo:")
    print("  1)+x(E) arriba  2)+x(E) abajo")
    print("  3)+y(N) hacia E 4)+y(N) hacia O")
    print("  5)-x(O) abajo   6)-y(S) hacia E")
    print("  7)rumbo N30E/NE 8)ya es estandar")
    ref = input("  > ")
    while True:
        if ref == "7":
            s = input("  rumbo (N30E, NE, S...): ")
            r = ang_rumbo(s)
            if r is None:
                print("  rumbo no valido")
                continue
            print("  ", s, "=", r2(r, 2), "grados estandar")
            return r
        try:
            a = nval(input(msg))
        except ValueError:
            print("  numero no valido")
            continue
        if ref == "2":
            r = -a
        elif ref == "3":
            r = 90.0 - a
        elif ref == "4":
            r = 90.0 + a
        elif ref == "5":
            r = 180.0 + a
        elif ref == "6":
            r = 270.0 - a
        else:
            r = a
        r = r % 360
        if ref != "1" and ref != "8":
            print("  =", r2(r, 2), "grados estandar")
        return r

# ---------- 1. VECTORES CONCURRENTES ----------
def vectores():
    tip("cos va con el eje DESDE el que mides el angulo")
    tip("angulo desde +x (E=0 N=90 O=180 S=270) o rumbo N30E")
    n = int(num("Cuantos vectores? "))
    rx = 0.0
    ry = 0.0
    tab = []
    for i in range(n):
        print("Vector", i + 1)
        m = num("  magnitud (N o m): ")
        a = pedir_angulo("  angulo en grados: ")
        x = m * cos(radians(a))
        y = m * sin(radians(a))
        tab.append((i + 1, m, a, x, y))
        rx = rx + x
        ry = ry + y
    sep()
    print("TABLA DE COMPONENTES")
    print("  #   mag    ang     x       y")
    for (i, m, a, x, y) in tab:
        print(" ", i, " ", r2(m, 2), " ", r2(a, 1), " ",
              r2(x, 2), " ", r2(y, 2))
    print("  SUMA          ", r2(rx, 2), " ", r2(ry, 2))
    sep()
    print("Rx =", r2(rx, 3), " Ry =", r2(ry, 3), "(sumas de componentes)")
    r = sqrt(rx * rx + ry * ry)
    ang = degrees(atan2(ry, rx))
    if ang < 0:
        ang = ang + 360
    print("R (resultante) =", r2(r, 3), "(N o m, segun el dato)")
    print("angulo de R =", r2(ang, 2), "grados (cuadrante ok)")
    print("Equilibrante (la anula):", r2(r, 3), "a", r2((ang + 180) % 360, 2), "grados")

# ---------- MRU (velocidad constante) ----------
def mru():
    tip("a=0: solo x = v*t. No uses las formulas de MRUA aqui")
    print("1) v, x o t (deja VACIO lo que buscas)")
    print("2) encuentro de dos moviles")
    op = input("> ")
    if op == "1":
        v = dato("v (m/s): ")
        x = dato("x (m): ")
        t = dato("t (s): ")
        if v is None and x is not None and t is not None and t != 0:
            v = x / t
            print("PROCEDIMIENTO:  v=x/t = " + r2(x) + "/" + rp(t))
        elif x is None and v is not None and t is not None:
            x = v * t
            print("PROCEDIMIENTO:  x=v*t = " + r2(v) + "(" + r2(t) + ")")
        elif t is None and v is not None and x is not None and v != 0:
            t = x / v
            print("PROCEDIMIENTO:  t=x/v = " + r2(x) + "/" + rp(v))
        else:
            print("Dame 2 de los 3 (y sin ceros que dividan)")
            return
        sep()
        print("v =", r2(v, 3), "m/s (velocidad constante)")
        print("x =", r2(x, 3), "m (distancia)")
        print("t =", r2(t, 3), "s (tiempo)")
    else:
        tip("frente a frente: se suman las rapideces")
        tip("persecucion: se restan")
        x1 = num("posicion inicial de A (m): ")
        v1 = num("velocidad de A (m/s, con signo): ")
        x2 = num("posicion inicial de B (m): ")
        v2 = num("velocidad de B (m/s, con signo): ")
        if v1 == v2:
            print("Misma velocidad: nunca se encuentran (o van juntos)")
            return
        t = (x2 - x1) / (v1 - v2)
        print("PROCEDIMIENTO:")
        print("  x1+v1*t = x2+v2*t  ->  t=(x2-x1)/(v1-v2)")
        print("  t = (" + r2(x2) + "-" + rp(x1) + ")/(" + r2(v1) + "-" + rp(v2) + ")")
        if t < 0:
            print("t negativo: ya se cruzaron antes, revisa signos")
            return
        xe = x1 + v1 * t
        sep()
        print("t =", r2(t, 3), "s (tiempo de encuentro)")
        print("x =", r2(xe, 3), "m (posicion del encuentro)")
        print("A recorrio", r2(abs(v1 * t), 3), "m ; B recorrio", r2(abs(v2 * t), 3), "m")

# ---------- 2. MRUA ----------
def mrua():
    tip("escribe lo que TENGAS; deja VACIO (solo enter) lo demas")
    tip("0 si el dato vale cero (reposo); necesito 3 datos")
    tip("si te dan FUERZA en N y masa, sale la a sola (Newton)")
    mu = num("mu (sin unidad; 0 si no hay): ")
    F = dato("F aplicada en N (enter si no hay): ")
    mm = dato("masa en kg (enter si no hay): ")
    v0 = dato("v0 (m/s): ")
    vf = dato("vf (m/s): ")
    a = dato("a (m/s2, con signo): ")
    t = dato("t (s): ")
    x = dato("x (m): ")
    proc = []
    if F is not None and mm is not None and mm > 0 and a is None:
        f = mu * mm * G
        a = (F - f) / mm
        proc.append("f=mu*m*g = " + r2(mu) + "(" + r2(mm) + ")(9.81) = " + r2(f) + " N")
        proc.append("a=(F-f)/m = (" + r2(F) + "-" + rp(f) + ")/" + rp(mm) + " = " + r2(a))
        if a < 0:
            proc.append("F no vence la friccion: revisa si arranca")
    fric = False
    if F is None and mu > 0 and a is None:
        fric = True                   # la friccion va CONTRA la velocidad
        vref = v0 if v0 is not None and v0 != 0 else vf
        if (vref is None or vref == 0) and x is not None:
            vref = x                  # sin v: el signo de x da el sentido
        if v0 == 0:
            # en reposo y sin F la friccion no lo mueve: se queda quieto
            if vf is not None and vf != 0 or x is not None and x != 0:
                sep()
                print("OJO: en reposo y sin F la")
                print("friccion no lo mueve: vf y x = 0")
                print("datos imposibles, revisa")
                return
            sep()
            print("v0 = 0 y sin F: la friccion no")
            print("lo mueve. Queda quieto:")
            print("vf = 0, x = 0, a = 0 (cualquier t)")
            return
        if vref is not None and vref < 0:
            a = mu * G
            proc.append("a=+mu*g (va hacia -x) = (" + r2(mu) + ")(9.81) = " + r2(a))
        else:
            a = -mu * G
            proc.append("a=-mu*g = -(" + r2(mu) + ")(9.81) = " + r2(a))
    t_dato = t
    if fric and v0 is None and vf is None and t is not None and \
            x is not None and abs(x) < 0.5 * mu * G * t * t * (1 - 1e-9):
        # con x y t: si |x| < mu*g*t^2/2 ya se habia parado antes de t
        v0 = sqrt(2 * mu * G * abs(x))
        if x < 0:
            v0 = -v0
        vf = 0.0
        proc.append("|x| < mu*g*t^2/2: se paro antes de t")
        proc.append("v0=raiz(2*mu*g*|x|) = " + r2(v0) + "; vf = 0")
    if fric and v0 is not None and v0 != 0 and t is not None:
        tpar = abs(v0) / (mu * G)
        if t > tpar * (1 + 1e-9):     # la friccion no lo regresa
            proc.append("se para en t=|v0|/(mu*g) = " + r2(tpar) + " s")
            proc.append("despues queda quieto: vf = 0")
            if vf is None:
                vf = 0.0
            if x is None:
                x = v0 * tpar / 2
                proc.append("x=v0*tpar/2 = " + r2(v0) + "(" + r2(tpar) + ")/2 = " + r2(x))
    try:
        for _ in range(3):
            if v0 is not None and a is not None and t is not None:
                if vf is None:
                    vf = v0 + a * t
                    proc.append("vf=v0+a*t = " + r2(v0) + "+(" + r2(a) + ")(" + r2(t) + ") = " + r2(vf))
                if x is None:
                    x = v0 * t + 0.5 * a * t * t
                    proc.append("x=v0t+.5at^2 = " + r2(v0) + "(" + r2(t) + ")+.5(" + r2(a) + ")(" + r2(t) + ")^2 = " + r2(x))
            if v0 is not None and vf is not None and t is not None:
                if a is None:
                    a = (vf - v0) / t
                    proc.append("a=(vf-v0)/t = (" + r2(vf) + "-" + rp(v0) + ")/" + rp(t) + " = " + r2(a))
                if x is None:
                    x = (v0 + vf) / 2 * t
                    proc.append("x=(v0+vf)/2*t = (" + r2(v0) + "+" + rp(vf) + ")/2*" + r2(t) + " = " + r2(x))
            if v0 is not None and vf is not None and a is not None and a != 0:
                if t is None:
                    t = (vf - v0) / a
                    proc.append("t=(vf-v0)/a = (" + r2(vf) + "-" + rp(v0) + ")/" + rp(a) + " = " + r2(t))
                if x is None:
                    x = (vf * vf - v0 * v0) / (2 * a)
                    proc.append("x=(vf^2-v0^2)/2a = " + r2(x))
            if v0 is not None and vf is not None and x is not None and (v0 + vf) != 0:
                if t is None:
                    t = 2 * x / (v0 + vf)
                    proc.append("t=2x/(v0+vf) = 2(" + r2(x) + ")/(" + r2(v0) + "+" + rp(vf) + ") = " + r2(t))
            if v0 is not None and a is not None and x is not None and vf is None:
                v2 = v0 * v0 + 2 * a * x
                if v2 < 0:
                    print("Imposible: vf^2 negativo, revisa datos")
                    return
                rz = sqrt(v2)
                vf, otro = rz, None
                if a == 0:
                    vf = v0                   # MRU: la v no cambia
                elif t is not None:
                    if abs(-rz - v0 - a * t) < abs(rz - v0 - a * t):
                        vf = -rz
                else:
                    # dos raices: la del MENOR t >= 0 (1a vez que llega a x)
                    tp, tm = (rz - v0) / a, (-rz - v0) / a
                    if tm >= -1e-12 and (tp < -1e-12 or tm < tp):
                        vf = -rz
                        if tp >= -1e-12:
                            otro = tp
                    elif tp >= -1e-12 and tm >= -1e-12:
                        otro = tm
                proc.append("vf=raiz(v0^2+2ax) = raiz(" + rp(v0) + "^2+2(" + r2(a) + ")(" + r2(x) + ")) = " + r2(vf))
                if vf < 0 and a != 0:
                    proc.append("(vf<0: da el menor t >= 0)")
                if otro is not None and rz > 0 and not fric:
                    proc.append("(pasa otra vez por x en t=" + r2(otro) + ")")
            if v0 is not None and t is not None and x is not None and t != 0:
                if a is None:
                    a = 2 * (x - v0 * t) / (t * t)
                    proc.append("a=2(x-v0t)/t^2 = " + r2(a))
            if vf is not None and a is not None and t is not None and v0 is None:
                v0 = vf - a * t
                proc.append("v0=vf-a*t = " + r2(vf) + "-(" + r2(a) + ")(" + r2(t) + ") = " + r2(v0))
            if vf is not None and t is not None and x is not None and v0 is None and t != 0:
                v0 = 2 * x / t - vf
                proc.append("v0=2x/t-vf = " + r2(v0))
            if a is not None and t is not None and x is not None and v0 is None and t != 0:
                v0 = (x - 0.5 * a * t * t) / t
                proc.append("v0=(x-.5at^2)/t = " + r2(v0))
            if vf is not None and a is not None and x is not None and v0 is None:
                v2 = vf * vf - 2 * a * x
                if v2 < 0:
                    print("Imposible: v0^2 negativo, revisa datos")
                    return
                rz = sqrt(v2)
                v0 = rz
                if a == 0:
                    v0 = vf                   # MRU: la v no cambia
                elif t is not None:
                    if abs(vf + rz - a * t) < abs(vf - rz - a * t):
                        v0 = -rz
                else:
                    # primero el signo de vf (no se da la vuelta); t >= 0
                    ops = [rz, -rz] if vf >= 0 else [-rz, rz]
                    v0 = ops[0]
                    for c in ops:
                        if (vf - c) / a >= -1e-12:
                            v0 = c
                            break
                proc.append("v0=raiz(vf^2-2ax) = " + r2(v0))
                if a != 0 and t is None and rz > 0 and not fric \
                        and (vf + v0) / a >= -1e-12:
                    proc.append("(tambien sirve v0 = " + r2(-v0) + ")")
    except ZeroDivisionError:
        print("Division entre cero: si a=0 es MRU, usa x=v*t")
        return
    faltan = [n for n, z in [("v0",v0),("vf",vf),("a",a),("t",t),("x",x)] if z is None]
    if faltan:
        print("Me faltan datos, no pude despejar:", faltan)
        print("Da al menos 3 de las 5 magnitudes")
        return
    sep()
    proc_print(proc)
    sep()
    if t < 0:
        print("OJO: t negativo = datos imposibles")
        print("revisa los signos de v0, vf y a")
    elif fric and t_dato is None and v0 != 0 and \
            t > abs(v0) / (mu * G) * (1 + 1e-9):
        print("OJO: con friccion se para en")
        print("t = " + r2(abs(v0) / (mu * G)) + " s: datos imposibles")
    print("v0 =", r2(v0, 3), "m/s (vel inicial)")
    print("vf =", r2(vf, 3), "m/s (vel final)")
    print("a  =", r2(a, 3), "m/s2 (aceleracion)")
    print("t  =", r2(t, 3), "s (tiempo)")
    print("x  =", r2(x, 3), "m (distancia)")

# ---------- 3. MRUA + FRICCION (derrape) ----------
def derrape():
    tip("la masa se cancela: a = mu*g siempre")
    print("1) v0 desde huella (mu, d)")
    print("2) distancia de alto (v0, mu)")
    op = input("> ")
    if op == "1":
        mu = num("mu (sin unidad): "); d = num("d huella (m): ")
        v0 = sqrt(2 * mu * G * d)
        print("PROCEDIMIENTO:")
        print("  a=mu*g = (" + r2(mu) + ")(9.81) = " + r2(mu * G))
        print("  v0=raiz(2*mu*g*d) = raiz(2(" + r2(mu) + ")(9.81)(" + r2(d) + "))")
        print("a =", r2(mu * G, 3), "m/s2 (frenado por friccion)")
        print("v0 (vel al iniciar el derrape) =", r2(v0, 3), "m/s =", r2(v0 * 3.6, 1), "km/h")
    else:
        v0 = num("v0 (m/s): "); mu = num("mu (sin unidad): ")
        print("PROCEDIMIENTO:")
        print("  d=v0^2/(2*mu*g) = " + rp(v0) + "^2/(2(" + r2(mu) + ")(9.81))")
        print("  t=v0/(mu*g)")
        print("d =", r2(v0 * v0 / (2 * mu * G), 3), "m (distancia para parar)")
        print("t =", r2(v0 / (mu * G), 3), "s (tiempo para parar)")

# ---------- 4. CAIDA LIBRE (abajo positivo) ----------
def caida():
    tip("abajo es +; se suelta: v0y=0; sube: v0y NEGATIVA")
    tip("escribe lo que tengas; VACIO lo demas (2 datos minimo)")
    v0 = dato("v0y (m/s): ")
    vf = dato("vf (m/s): ")
    t = dato("t (s): ")
    h = dato("h (m): ")
    proc = []
    for _ in range(3):
        if v0 is not None and t is not None:
            if vf is None:
                vf = v0 + G * t
                proc.append("vf=v0+g*t = " + r2(v0) + "+9.81(" + r2(t) + ") = " + r2(vf))
            if h is None:
                h = v0 * t + 0.5 * G * t * t
                proc.append("h=v0t+.5gt^2 = " + r2(v0) + "(" + r2(t) + ")+4.905(" + r2(t) + ")^2 = " + r2(h))
        if v0 is not None and h is not None and vf is None:
            v2 = v0 * v0 + 2 * G * h
            if v2 < 0:
                print("Imposible: revisa datos")
                return
            vf = sqrt(v2)
            proc.append("vf=raiz(v0^2+2gh) = raiz(" + rp(v0) + "^2+19.62(" + r2(h) + ")) = " + r2(vf))
        if v0 is not None and vf is not None:
            if t is None:
                t = (vf - v0) / G
                proc.append("t=(vf-v0)/g = (" + r2(vf) + "-(" + r2(v0) + "))/9.81 = " + r2(t))
            if h is None:
                h = (vf * vf - v0 * v0) / (2 * G)
                proc.append("h=(vf^2-v0^2)/2g = " + r2(h))
        if vf is not None and t is not None and v0 is None:
            v0 = vf - G * t
            proc.append("v0=vf-g*t = " + r2(vf) + "-9.81(" + r2(t) + ") = " + r2(v0))
        if vf is not None and h is not None and v0 is None:
            v2 = vf * vf - 2 * G * h
            if v2 < 0:
                print("Imposible: vf^2 < 2gh, revisa datos")
                return
            v0 = sqrt(v2)
            proc.append("v0=raiz(vf^2-2gh) = " + r2(v0) + " (se tomo +)")
        if t is not None and h is not None and v0 is None and t != 0:
            v0 = (h - 0.5 * G * t * t) / t
            proc.append("v0=(h-4.905t^2)/t = " + r2(v0))
    faltan = [n for n, z in [("v0y",v0),("vf",vf),("t",t),("h",h)] if z is None]
    if faltan:
        print("Me faltan datos:", faltan, "- da al menos 2")
        return
    sep()
    proc_print(proc)
    sep()
    print("v0y =", r2(v0, 3), "m/s (vel inicial)")
    print("vf  =", r2(vf, 3), "m/s (vel al llegar)")
    print("t   =", r2(t, 3), "s (tiempo en el aire)")
    print("h   =", r2(h, 3), "m (altura/desplazamiento)")
    if v0 < 0:
        print("subio", r2(v0 * v0 / (2 * G), 3), "m antes de caer")

# ---------- 5. LANZAMIENTO VERTICAL ----------
def r6(x):
    # datos y pasos intermedios completos, sin recortar a 3 decimales
    if abs(x) < 1e-12:
        x = 0.0
    return "%.8g" % x

def vert_nivel(v0, y, proc):
    # v y tiempos al pasar por la altura y (arriba +, y=0 en la salida)
    hm = v0 * v0 / (2 * G)
    ts = v0 / G
    if abs(y - hm) < 0.0005:
        proc.append("y = hmax = v0^2/2g = " + r2(hm))
        proc_print(proc)
        sep()
        print("es la cima: v = 0 en t =", r2(ts), "s")
        return
    v2 = v0 * v0 - 2 * G * y
    proc.append("v^2=v0^2-2gy = " + r6(v0) + "^2-19.62(" + r6(y) + ") = " + r6(v2))
    if v2 < 0:
        proc_print(proc)
        sep()
        print("NO llega a esa altura (hmax =", r2(hm), "m)")
        return
    v = sqrt(v2)
    proc.append("v=raiz(" + r6(v2) + ") = " + r2(v))
    proc.append("t=(v0 -+ v)/g = (" + r6(v0) + " -+ " + r6(v) + ")/9.81")
    proc_print(proc)
    sep()
    t1 = (v0 - v) / G
    t2 = (v0 + v) / G
    if y >= 0:
        print("subiendo: v = +" + rp(v), "m/s  (t =", r2(t1), "s)")
    print("bajando:  v = -" + rp(v), "m/s  (t =", r2(t2), "s)")
    print("rapidez =", r2(v), "m/s (sin signo)")

def vertical():
    tip("arriba es +; y=0 donde sale; en la cima v=0 pero a=g")
    v0 = num("v0 hacia arriba (m/s): ")
    if v0 <= 0:
        print("v0 debe ser > 0 (si solo se suelta: Caida libre)")
        return
    hm = v0 * v0 / (2 * G)
    ts = v0 / G
    tv = 2 * v0 / G
    print("PROCEDIMIENTO:")
    print("  hmax=v0^2/2g = " + r6(v0) + "^2/19.62 = " + r2(hm))
    print("  tsub=v0/g = " + r6(v0) + "/9.81 = " + r2(ts))
    print("  tvuelo=2v0/g = 2(" + r6(v0) + ")/9.81 = " + r2(tv))
    sep()
    print("h max =", r2(hm), "m (sobre el punto de salida)")
    print("t subida =", r2(ts), "s (hasta la cima)")
    print("t vuelo =", r2(tv), "s (vuelve al mismo nivel)")
    ta = 2 * float(r2(ts, 2))
    if r2(tv, 2) != r2(ta, 2):
        print("  ojo: si redondeas tsub a", r2(ts, 2), "antes:", r2(ta, 2), "s")
    print("regresa con", r6(v0), "m/s hacia abajo (misma rapidez)")
    while True:
        sep()
        print("MAS del mismo tiro (v0=" + r6(v0) + "):")
        print("1) donde esta en un tiempo t")
        print("2) v a d metros ANTES de hmax")
        print("3) v y t a una altura y")
        print("4) t al piso X m DEBAJO")
        print("0) listo")
        op = input("> ").strip()
        if op == "0":
            return
        if op not in ("1", "2", "3", "4"):
            print("opcion no valida (0 = listo)")
            continue
        sep()
        if op == "1":
            t = num("t (s): ")
            while t < 0:
                print("t debe ser >= 0 (cuenta desde que lo lanza)")
                t = num("t (s): ")
            # si teclea el t de subida o de vuelo que se mostro (recortado a
            # 3 decimales), se usa el exacto y el procedimiento lo dice
            tol = min(0.0005, 0.25 * ts)
            nota = ""
            if t != ts and abs(t - ts) < tol:
                t, nota = ts, "t = t subida exacto"
            elif t != tv and abs(t - tv) < tol:
                t, nota = tv, "t = t vuelo exacto"
            y = v0 * t - 0.5 * G * t * t
            v = v0 - G * t
            print("PROCEDIMIENTO:")
            if nota:
                print("  (" + nota + " = " + r6(t) + ")")
            print("  y=v0t-.5gt^2 = " + r6(v0) + "(" + r6(t) + ")-4.905(" + r6(t) + ")^2 = " + r2(y))
            print("  v=v0-gt = " + r6(v0) + "-9.81(" + r6(t) + ") = " + r2(v))
            sep()
            if t == tv:
                print("y = 0 m: de vuelta al nivel de salida")
                print("v =", "-" + r6(v0), "m/s (misma rapidez, bajando)")
                continue
            print("y =", r2(y), "m (sobre el punto de salida)")
            if y < -0.0005:
                print("  negativo: ya esta DEBAJO de donde salio")
            if t == ts:
                print("v = 0 m/s: esta en la CIMA (y = hmax)")
            else:
                print("v =", r2(v), "m/s")
                if v > 0:
                    print("  + : va SUBIENDO")
                else:
                    print("  - : va BAJANDO")
            if t > tv:
                print("  ojo: t > t vuelo; solo si cae mas abajo")
        elif op == "2":
            tip("'antes de llegar' a hmax = va SUBIENDO (+)")
            d = abs(num("d metros antes de hmax (m): "))
            if d < 0.0005:
                print("d = 0: es la cima: v = 0 en t =", r2(ts), "s")
                continue
            if abs(d - hm) < 0.0005:
                d = hm      # d = hmax: es el punto de salida (y = 0)
            v = sqrt(2 * G * d)
            t1 = ts - v / G
            t2 = ts + v / G
            print("PROCEDIMIENTO:")
            print("  desde la cima cae d: v=raiz(2gd)")
            print("  v=raiz(19.62(" + r6(d) + ")) = " + r2(v))
            print("  t=tsub -+ v/g = " + r6(ts) + " -+ " + r6(v) + "/9.81")
            sep()
            print("altura y = hmax-d =", r2(hm - d), "m")
            if d > hm + 0.0005:
                print("  ojo: d > hmax: queda DEBAJO de la")
                print("  salida; ahi nunca pasa subiendo")
            else:
                print("subiendo: v = +" + rp(v), "m/s  (t =", r2(t1), "s)")
            print("bajando:  v = -" + rp(v), "m/s  (t =", r2(t2), "s)")
        elif op == "3":
            y = num("y sobre la salida (m, - si abajo): ")
            vert_nivel(v0, y, [])
        else:
            h = abs(num("cuantos m DEBAJO de la salida: "))
            v = sqrt(v0 * v0 + 2 * G * h)
            t = (v0 + v) / G
            print("PROCEDIMIENTO:")
            print("  llega a y=-h: -h = v0t-4.905t^2")
            print("  4.905t^2-" + r6(v0) + "t-" + r6(h) + " = 0")
            print("  t=(v0+raiz(v0^2+2gh))/g")
            print("   =(" + r6(v0) + "+raiz(" + r6(v0) + "^2+19.62(" + r6(h) + ")))/9.81")
            sep()
            print("t total =", r2(t), "s (desde que lo lanza)")
            extra = float(r2(t)) - float(r2(tv))
            print("  =", r2(tv), "s de vuelo +", r2(extra), "s de mas")
            print("v al llegar = -" + rp(v), "m/s (hacia abajo)")
            if h > 0:
                tip("la otra raiz de t sale negativa: se descarta")
            else:
                tip("h=0: la otra raiz es t=0 (el lanzamiento)")

# ---------- 6. PROYECTILES ----------
def proyectil():
    print("1) con angulo (sale del piso)")
    print("2) horizontal (sale de una altura)")
    sub = input("> ")
    if sub == "2":
        proy_horizontal()
        return
    tip("45 da alcance max; complementarios empatan")
    tip("R, H y t vuelo SOLO a misma altura")
    v0 = num("v0 (m/s): ")
    a = num("angulo en grados: ")
    vx = v0 * cos(radians(a))
    vy = v0 * sin(radians(a))
    print("PROCEDIMIENTO:")
    print("  vx=v0cos(" + r2(a) + ")  v0y=v0sen(" + r2(a) + ")")
    print("  t=2v0y/g  R=vx*t  H=v0y^2/2g")
    print("vx =", r2(vx, 3), "m/s (horizontal, cte)")
    print("v0y =", r2(vy, 3), "m/s (vertical inicial)")
    t = 2 * vy / G
    print("t vuelo =", r2(t, 3), "s (tiempo en el aire)")
    print("R =", r2(vx * t, 3), "m (alcance horizontal)")
    print("H max =", r2(vy * vy / (2 * G), 3), "m (altura maxima)")
    print("(cae a otra altura? -> menu 7 Caida con v0y=", r2(-vy, 2), ")")

def proy_horizontal():
    tip("sale HORIZONTAL: v0y=0; el tiempo lo manda la altura")
    tip("dame 2 de: v0, h, R (vacio lo que no tengas)")
    v0 = dato("v0 horizontal (m/s): ")
    h = dato("h altura (m): ")
    R = dato("R alcance (m): ")
    proc = []
    if h is not None and (v0 is not None or R is not None):
        t = sqrt(2 * h / G)
        proc.append("t=raiz(2h/g) = raiz(2(" + r2(h) + ")/9.81) = " + r2(t))
        if v0 is None:
            v0 = R / t
            proc.append("v0=R/t = " + r2(R) + "/" + rp(t) + " = " + r2(v0))
        if R is None:
            R = v0 * t
            proc.append("R=v0*t = " + r2(v0) + "(" + r2(t) + ") = " + r2(R))
    elif v0 is not None and R is not None:
        if v0 == 0:
            print("v0=0 no es tiro horizontal (cae vertical)")
            return
        t = R / v0
        proc.append("t=R/v0 = " + r2(R) + "/" + rp(v0) + " = " + r2(t))
        h = 0.5 * G * t * t
        proc.append("h=.5gt^2 = 4.905(" + r2(t) + ")^2 = " + r2(h))
    else:
        print("Necesito 2 de los 3 datos (v0, h, R)")
        return
    vfy = G * t
    vf = sqrt(v0 * v0 + vfy * vfy)
    angc = degrees(atan2(vfy, v0))
    proc.append("vfy=g*t = 9.81(" + r2(t) + ") = " + r2(vfy))
    proc.append("vf=raiz(v0^2+vfy^2) = " + r2(vf))
    sep()
    proc_print(proc)
    sep()
    print("v0 =", r2(v0, 3), "m/s (horizontal, cte)")
    print("h  =", r2(h, 3), "m (altura de salida)")
    print("t  =", r2(t, 3), "s (tiempo de caida)")
    print("R  =", r2(R, 3), "m (alcance horizontal)")
    print("vfy =", r2(vfy, 3), "m/s (vertical al llegar)")
    print("vf =", r2(vf, 3), "m/s a", r2(angc, 2), "grados bajo horizontal")

# ---------- 7. PLANO HORIZONTAL ----------
def horizontal():
    print("1) caja jalada/empujada en piso")
    print("2) elevador (bascula): N = m(g +- a)")
    s = input("> ")
    if s == "2":
        tip("la bascula marca la NORMAL, no el peso")
        m = num("masa (kg): ")
        a = num("aceleracion (m/s2, 0 si va constante): ")
        print("1) sube    2) baja")
        d = input("> ")
        if d == "2":
            N = m * (G - a)
            print("PROCEDIMIENTO:  N = m(g - a) = " + r2(m) + "(9.81-" + rp(a) + ")")
        else:
            N = m * (G + a)
            print("PROCEDIMIENTO:  N = m(g + a) = " + r2(m) + "(9.81+" + rp(a) + ")")
        print("peso real mg =", r2(m * G, 3), "N")
        print("N (lo que marca) =", r2(N, 3), "N")
        if abs(a) < 0.0001:
            print("a=0: marca igual que en reposo (equilibrio)")
        elif N <= 0:
            print("N<=0: caida libre, sensacion de ingravidez")
        return
    tip("N NO es mg cuando F tiene angulo")
    m = num("masa (kg): "); F = num("F (N): ")
    a = num("angulo de F en grados (0 si horizontal): ")
    mu = num("mu k (sin unidad): ")
    print("1) F jala hacia arriba   2) F empuja hacia abajo")
    d = input("> ")
    if d == "2":
        N = m * G + F * sin(radians(a))
    else:
        N = m * G - F * sin(radians(a))
    f = mu * N
    ac = (F * cos(radians(a)) - f) / m
    print("PROCEDIMIENTO:")
    if d == "2" or d == "e":
        print("  N=mg+Fsen(" + r2(a) + ") (empuja: aprieta)")
    else:
        print("  N=mg-Fsen(" + r2(a) + ") (jala: alivia)")
    print("  f=mu*N = (" + r2(mu) + ")(" + r2(N) + ")")
    print("  a=(Fcos(" + r2(a) + ")-f)/m")
    print("N =", r2(N, 3), "N (normal)")
    print("f =", r2(f, 3), "N (friccion)")
    print("a =", r2(ac, 3), "m/s2 (aceleracion)")
    if ac < 0:
        print("Ojo: revisa si siquiera arranca (estatica)")

# ---------- 8. PLANO INCLINADO ----------
def inclinado():
    tip("sen = a lo largo de la rampa; checa limite ang->0")
    ang = num("angulo rampa en grados: ")
    mu = num("mu (sin unidad; 0 si no hay): ")
    m = num("masa en kg (0 si no la dan): ")
    t = tan(radians(ang))
    print("PROCEDIMIENTO:")
    print("  N=mg*cos(" + r2(ang) + ")  f=mu*N")
    print("  a=g(sen(" + r2(ang) + ")-mu*cos(" + r2(ang) + "))")
    if m > 0:
        N = m * G * cos(radians(ang))
        print("N =", r2(N, 3), "N (normal)")
        print("f = mu*N =", r2(mu * N, 3), "N (friccion)")
        print("mg sen =", r2(m * G * sin(radians(ang)), 3), "N (jala rampa abajo)")
    else:
        print("N =", r2(G * cos(radians(ang)), 3), "* m  (N, con m en kg)")
    print("mu min para NO deslizar = tan(ang) =", r2(t, 3))
    if t <= mu:
        print("tan(ang) <=", "%g" % mu, "-> NO desliza (estatico)")
    else:
        ab = G * (sin(radians(ang)) - mu * cos(radians(ang)))
        print("a bajando =", r2(ab, 3), "m/s2")
    asu = G * (sin(radians(ang)) + mu * cos(radians(ang)))
    print("a frenando al subir =", r2(asu, 3), "m/s2")
    tip("h = d*sen(ang): altura vs largo de rampa")

# ---------- 9. POLEAS ----------
def poleas():
    tip("misma T y misma a; T queda ENTRE los dos pesos")
    print("1) Atwood  2) mesa+polea  3) rampa+polea")
    op = input("> ")
    if op == "1":
        m1 = num("m1 ligera (kg): "); m2 = num("m2 pesada (kg): ")
        a = (m2 - m1) * G / (m1 + m2)
        T = 2 * m1 * m2 * G / (m1 + m2)
    elif op == "2":
        m1 = num("m1 en mesa (kg): "); m2 = num("m2 colgando (kg): ")
        mu = num("mu (sin unidad; 0 si no hay): ")
        if m2 * G <= mu * m1 * G:
            print("No arranca (estatica). a=0, T =", r2(m2 * G, 2), "N")
            return
        a = (m2 - mu * m1) * G / (m1 + m2)
        T = m2 * (G - a)
    else:
        m1 = num("m1 en rampa (kg): "); ang = num("angulo en grados: ")
        m2 = num("m2 colgando (kg): ")
        a = (m2 * G - m1 * G * sin(radians(ang))) / (m1 + m2)
        T = m2 * (G - a)
        if a < 0:
            print("Gana la rampa: m1 baja, m2 sube")
    print("PROCEDIMIENTO:")
    print("  a=(jala-retiene)/(m1+m2)")
    print("  T=m2(g-a) o T=m1(g+a) segun lado")
    print("a =", r2(abs(a), 3), "m/s2 (aceleracion del sistema)")
    print("T =", r2(T, 3), "N (tension de la cuerda)")

# ---------- 10. ENERGIA ----------
def energia():
    tip("sin tiempo en el problema -> energia es el camino")
    print("1) v = raiz(2gh)")
    print("2) rampa con friccion")
    print("3) energia perdida (Em0 vs Emf)")
    op = input("> ")
    if op == "1":
        h = num("h altura (m): ")
        print("PROCEDIMIENTO:  U=K -> mgh=.5mv^2")
        print("  v=raiz(2gh) = raiz(19.62(" + r2(h) + "))")
        print("v =", r2(sqrt(2 * G * h), 3), "m/s")
    elif op == "2":
        tip("friccion cobra el LARGO de rampa, no la altura")
        m = num("masa (kg): "); h = num("altura (m): ")
        f = num("F friccion (N): "); d = num("largo rampa (m): ")
        e = m * G * h - f * d
        if e < 0:
            print("La friccion gana: no llega abajo")
        else:
            print("v =", r2(sqrt(2 * e / m), 3), "m/s")
    else:
        m = num("masa (kg): "); h = num("h inicial (m): "); v = num("v final (m/s): ")
        e0 = m * G * h
        ef = 0.5 * m * v * v
        print("PROCEDIMIENTO:")
        print("  Em0=mgh = (" + r2(m) + ")(9.81)(" + r2(h) + ")")
        print("  Emf=.5mv^2 = .5(" + r2(m) + ")(" + r2(v) + ")^2")
        print("  Ff*d = Em0-Emf")
        print("Em0 =", r2(e0, 2), "J (energia inicial)")
        print("Emf =", r2(ef, 2), "J (energia final)")
        print("perdida Ff*d =", r2(e0 - ef, 2), "J (se la llevo la friccion)")

# ---------- 11. CONVERSIONES ----------
PRE = {"E": 1e18, "P": 1e15, "T": 1e12, "G": 1e9,
       "M": 1e6, "k": 1e3, "h": 1e2, "da": 1e1,
       "1": 1.0,
       "d": 1e-1, "c": 1e-2, "m": 1e-3, "u": 1e-6,
       "n": 1e-9, "p": 1e-12, "f": 1e-15, "a": 1e-18}

NOM = {"exa": "E", "peta": "P", "tera": "T", "giga": "G",
       "mega": "M", "kilo": "k", "hecto": "h", "deca": "da",
       "deci": "d", "centi": "c", "mili": "m", "micro": "u",
       "nano": "n", "pico": "p", "femto": "f", "atto": "a"}
UNI = ("mol", "cd", "Pa", "Hz", "m", "g", "s", "A", "L", "N", "J", "W")

ORDEN = ["E","P","T","G","M","k","h","da","1","d","c","m","u","n","p","f","a"]
PNOMD = {"E":"exa","P":"peta","T":"tera","G":"giga","M":"mega","k":"kilo",
         "h":"hecto","da":"deca","1":"","d":"deci","c":"centi","m":"mili",
         "u":"micro","n":"nano","p":"pico","f":"femto","a":"atto"}
UNOM = {"m":"metros","g":"gramos","s":"segundos","L":"litros","A":"amperes",
        "N":"newtons","J":"joules","W":"watts","Pa":"pascales",
        "mol":"moles","cd":"candelas"}

def nombre_completo(psym, uni):
    if uni in UNOM:
        base = UNOM[uni]
    elif uni:
        base = uni
    else:
        return ""
    return "(" + PNOMD.get(psym, "") + base + ")"

def tabla_completa(v, fac, uni):
    sep()
    print("valor en TODOS los prefijos:")
    for q in ORDEN:
        if q == "1":
            et = (uni if uni else "base") + " (sin prefijo)"
        else:
            et = q + uni
        print(" ", et, "=", "%g" % (v * fac / PRE[q]))

ULT_UNI = [""]
ULT_SYM = ["1"]

def menu_pref():
    print("1)E   2)P  3)T    4)G  5)M  6)k")
    print("7)h   8)da 9)BASE 10)d 11)c 12)m")
    print("13)u  14)n 15)p   16)f 17)a")

def parse_pref(p):
    if p.isdigit():
        i = int(p)
        if 1 <= i <= 17:
            ULT_SYM[0] = ORDEN[i - 1]
            return PRE[ORDEN[i - 1]]
        return None
    if p in UNI:
        ULT_UNI[0] = p
        ULT_SYM[0] = "1"
        return 1.0
    if p in PRE:
        ULT_SYM[0] = p
        return PRE[p]
    if p in NOM:
        ULT_SYM[0] = NOM[p]
        return PRE[NOM[p]]
    for u in UNI:
        if p.endswith(u):
            r = p[:-len(u)]
            if r in PRE:
                ULT_UNI[0] = u
                ULT_SYM[0] = r
                return PRE[r]
            if r in NOM:
                ULT_UNI[0] = u
                ULT_SYM[0] = NOM[r]
                return PRE[NOM[r]]
    return None

def etiqueta_pref(p, uni):
    if p.isdigit():
        q = ORDEN[int(p) - 1]
        return (uni if uni else "base") if q == "1" else q + uni
    return p

def pedir_prefijo(msg):
    menu_pref()
    print("(numero, o letras tipo km, pico)")
    while True:
        p = input(msg)
        if p == "":
            return 1.0
        f = parse_pref(p)
        if f is not None:
            return f
        msg = "no valido, otra vez: "

def conversiones():
    print("1) prefijos (m, g, s, A, mol, cd...)")
    print("2) area (cm2<->m2 etc)")
    print("3) velocidad km/h <-> m/s")
    print("4) temperatura C <-> K")
    print("5) tiempo h/min <-> s")
    print("6) volumen m3 <-> L <-> mL")
    print("7) densidad g/cm3 <-> kg/m3")
    print("8) chuleta: unidades derivadas")
    print("9) operar en notacion cientifica")
    op = input("> ")
    if op == "1":
        tip("mueve el punto: k=10^3, c=10^-2, m=10^-3")
        v = num("valor (solo el numero): ")
        ULT_UNI[0] = ""
        a = pedir_prefijo("prefijo actual: ")
        uni = ULT_UNI[0]
        if uni == "":
            print("unidad: 1)m 2)g 3)s 4)L 5)N 6)J 7)W 8)Pa 9)mol 10)cd 0)ninguna")
            LU = ["m", "g", "s", "L", "N", "J", "W", "Pa", "mol", "cd"]
            u = input("> ")
            if u.isdigit() and 1 <= int(u) <= 10:
                uni = LU[int(u) - 1]
            elif u in UNOM:
                uni = u
        d = input("destino (ENTER = tabla con TODOS): ")
        if d == "":
            tabla_completa(v, a, uni)
        else:
            b = parse_pref(d)
            if b is None:
                print("no entendi el destino; tabla completa:")
                tabla_completa(v, a, uni)
            else:
                ps = ULT_SYM[0]
                sim = (uni if uni else "base") if ps == "1" else ps + uni
                print("=", "%g" % (v * a / b), sim, nombre_completo(ps, uni))
    elif op == "2":
        tip("el prefijo se ELEVA: 1 cm2 = 10^-4 m2")
        v = num("valor (solo el numero): ")
        a = pedir_prefijo("prefijo actual: ")
        b = pedir_prefijo("prefijo destino: ")
        print("=", "%g" % (v * (a / b) ** 2))
    elif op == "3":
        tip("1 m/s = 3.6 km/h")
        v = num("valor (solo el numero): ")
        print("1) km/h -> m/s    2) m/s -> km/h")
        d = input("> ")
        if d == "1":
            print("=", r2(v / 3.6, 4), "m/s")
        else:
            print("=", r2(v * 3.6, 4), "km/h")
    elif op == "4":
        tip("K = C + 273.15; el Kelvin no usa grados")
        v = num("valor (solo el numero): ")
        print("1) C -> K    2) K -> C")
        d = input("> ")
        if d == "1":
            print("=", r2(v + 273.15, 2), "K")
        else:
            print("=", r2(v - 273.15, 2), "C")
    elif op == "5":
        v = num("valor (solo el numero): ")
        print("1) horas -> s   2) min -> s   3) s -> min y h")
        d = input("> ")
        if d == "1":
            print("=", "%.10g" % (v * 3600), "s")
        elif d == "2":
            print("=", "%.10g" % (v * 60), "s")
        else:
            print("=", "%.10g" % (v / 60), "min =", "%.10g" % (v / 3600), "h")
    elif op == "6":
        tip("1 m3 = 1000 L; 1 L = 1000 mL; 1 mL = 1 cm3")
        v = num("valor (solo el numero): ")
        print("1) m3 -> L y mL   2) L -> m3 y mL   3) mL -> L y m3")
        d = input("> ")
        if d == "1":
            print("=", "%.10g" % (v * 1000), "L =", "%.10g" % (v * 1e6), "mL")
        elif d == "2":
            print("=", "%g" % (v / 1000), "m3 =", "%g" % (v * 1000), "mL")
        else:
            print("=", "%g" % (v / 1000), "L =", "%g" % (v / 1e6), "m3")
    elif op == "7":
        tip("g/cm3 -> kg/m3: multiplica x1000 (agua = 1000)")
        v = num("valor (solo el numero): ")
        print("1) g/cm3 -> kg/m3    2) kg/m3 -> g/cm3")
        d = input("> ")
        if d == "1":
            print("=", "%.10g" % (v * 1000), "kg/m3")
        else:
            print("=", "%g" % (v / 1000), "g/cm3")
    elif op == "9":
        tip("escribe 4e-3 o 4x10^-3; da mantisa entre 1 y 10")
        a = num("primer numero: ")
        o = input("operacion (* / + -): ")
        b = num("segundo numero: ")
        if o == "*":
            r = a * b
        elif o == "/":
            if b == 0:
                print("no se divide entre cero")
                return
            r = a / b
        elif o == "+":
            r = a + b
        else:
            r = a - b
        print("=", "%g" % r)
        print("= ", "%e" % r, "(forma larga)")
    elif op == "8":
        print("N  = kg*m/s2   (fuerza)")
        print("Pa = N/m2      (presion)")
        print("J  = N*m       (trabajo/energia)")
        print("W  = J/s       (potencia)")
        print("L  = 0.001 m3  (volumen)")
        print("rho= kg/m3     (densidad)")
        tip("todo lo no fundamental es derivado")

# ---------- 12. GRAFICAS POR TRAMOS ----------
def graficas():
    tip("x-t: pendiente = v | v-t: pendiente = a, AREA = x")
    m = input("tipo (1=x-t, 2=v-t): ")
    n = int(num("cuantos puntos (esquinas)? "))
    ts = []
    ys = []
    if m == "1":
        et = "x"
        un = " (m): "
    else:
        et = "v"
        un = " (m/s): "
    for i in range(n):
        ts.append(num("t" + str(i + 1) + " (s): "))
        ys.append(num(et + str(i + 1) + un))
    sep()
    dist = 0.0
    despl = 0.0
    for i in range(n - 1):
        dt = ts[i + 1] - ts[i]
        dy = ys[i + 1] - ys[i]
        if dt <= 0:
            print("tramo", i + 1, ": tiempos no crecen, lo salto")
            continue
        print("tramo", r6(ts[i]), "-", r6(ts[i + 1]), "s:")
        if m == "1":
            v = dy / dt
            if v == 0:
                print("  REPOSO (linea plana)")
            elif v > 0:
                print("  MRU direccion + : v =", r2(v, 3), "m/s")
            else:
                print("  MRU direccion - : v =", r2(v, 3), "m/s")
            print("  v=dx/dt = (" + r2(ys[i+1]) + "-" + rp(ys[i]) + ")/" + rp(dt))
            dist = dist + abs(dy)
        else:
            a = dy / dt
            v1 = ys[i]
            v2 = ys[i + 1]
            if v1 == 0 and v2 == 0:
                print("  REPOSO")
            elif a == 0:
                print("  v constante (MRU): v =", r2(v1, 3), "m/s")
            elif v1 * a >= 0 and v2 * a >= 0:
                print("  ACELERA: a =", r2(a, 3), "m/s2")
            else:
                print("  FRENA: a =", r2(a, 3), "m/s2")
            if v1 * v2 < 0:
                tc = -v1 / a
                a1 = 0.5 * v1 * tc
                a2 = 0.5 * v2 * (dt - tc)
                area = a1 + a2
                dist = dist + abs(a1) + abs(a2)
                print("  (cruza v=0: cambia de sentido)")
            else:
                area = (v1 + v2) / 2 * dt
                dist = dist + abs(area)
            print("  area=(v1+v2)/2*dt =", r2(area, 3), "m")
            despl = despl + area
    sep()
    if m == "1":
        despl = ys[-1] - ys[0]
    T = ts[-1] - ts[0]
    print("distancia total =", r2(dist, 3), "m (todo lo recorrido)")
    print("desplazamiento =", r2(despl, 3), "m (final - inicial)")
    if T > 0:
        print("vel media =", r2(despl / T, 3), "m/s (desplaz/t)")
        print("rapidez media =", r2(dist / T, 3), "m/s (dist/t)")

# ---------- 13. TRABAJO Y POTENCIA ----------
def trabajo():
    tip("W = F*d*cos(ang) | solo la componente EN la direccion cuenta")
    print("1) W de una fuerza (F, d, angulo)")
    print("2) W neto por teorema (Kf - Ki)")
    print("3) W contra la gravedad (subir masa)")
    print("4) potencia (W y t, o F y v)")
    op = input("> ")
    if op == "1":
        F = num("F (N): ")
        d = num("d (m): ")
        ang = num("angulo F-d en grados (0 si van juntas): ")
        W = F * d * cos(radians(ang))
        print("PROCEDIMIENTO:")
        print("  W=F*d*cos(ang) = " + r2(F) + "(" + r2(d) + ")cos(" + r2(ang) + ")")
        print("W =", r2(W, 3), "J (trabajo)")
        if abs(ang - 90) < 0.001:
            print("ang=90: la fuerza NO hace trabajo (ni N ni peso horizontal)")
        elif W < 0:
            print("W negativo: la fuerza quita energia (friccion, frenar)")
    elif op == "2":
        tip("W neto = cambio de energia cinetica")
        m = num("masa (kg): ")
        v0 = num("v inicial (m/s): ")
        vf = num("v final (m/s): ")
        Ki = 0.5 * m * v0 * v0
        Kf = 0.5 * m * vf * vf
        print("PROCEDIMIENTO:")
        print("  Ki=.5mv0^2 = " + r2(Ki) + "  Kf=.5mvf^2 = " + r2(Kf))
        print("  W neto = Kf - Ki")
        print("Ki =", r2(Ki, 3), "J (cinetica inicial)")
        print("Kf =", r2(Kf, 3), "J (cinetica final)")
        print("W neto =", r2(Kf - Ki, 3), "J")
    elif op == "3":
        m = num("masa (kg): ")
        h = num("altura (m): ")
        print("PROCEDIMIENTO:  W = mgh (contra la gravedad)")
        print("  W = " + r2(m) + "(9.81)(" + r2(h) + ")")
        print("W =", r2(m * G * h, 3), "J (= U ganada)")
        tip("la gravedad hace -mgh; el camino no importa, solo h")
    elif op == "4":
        print("  1) con trabajo y tiempo   2) con fuerza y velocidad")
        s = input("  > ")
        if s == "2":
            F = num("F (N): ")
            v = num("v (m/s): ")
            print("PROCEDIMIENTO:  P = F*v")
            print("P =", r2(F * v, 3), "W (potencia)")
        else:
            W = num("W (J): ")
            t = num("t (s): ")
            if t == 0:
                print("t no puede ser 0")
                return
            P = W / t
            print("PROCEDIMIENTO:  P = W/t = " + r2(W) + "/" + rp(t))
            print("P =", r2(P, 3), "W (potencia)")
            print("  =", r2(P / 745.7, 4), "hp")

# ---------- MENU PRINCIPAL ----------
ops = [("Unidades", conversiones),
       ("Vectores", vectores),
       ("Graficas", graficas),
       ("MRU", mru),
       ("MRUA", mrua),
       ("Derrape", derrape),
       ("Caida libre", caida),
       ("Lanz vert", vertical),
       ("Proyectil", proyectil),
       ("Horizontal", horizontal),
       ("Inclinado", inclinado),
       ("Poleas", poleas),
       ("Energia", energia),
       ("Trabajo/Potencia", trabajo)]

def fisica():
    print(">>> FISICA v7.2")
    while True:
        sep()
        print("FISICA - menu principal")
        mit = (len(ops) + 1) // 2
        for i in range(mit):
            izq = str(i + 1) + ")" + ops[i][0]
            j = i + mit
            if j < len(ops):
                der = str(j + 1) + ")" + ops[j][0]
            else:
                der = ""
            print(izq + " " * (16 - len(izq)) + der)
        print("0)SALIR")
        op = input("> ").strip()
        if op == "0" or op == "q":
            print("Saliste de FISICA. Exito en el examen!")
            break
        try:
            k = int(op) - 1
        except ValueError:
            k = -1
        if not 0 <= k < len(ops):
            print("Opcion no valida")
            continue
        sep()
        try:
            ops[k][1]()
        except Exception as err:
            print("Error con esos datos:", err)
            print("(revisa ceros, negativos o datos que faltan)")
        input("(enter para volver al menu)")


# ===================== menu principal =====================

def general():
    try:
        while True:
            print("")
            print("== GENERAL: elige materia ==")
            print("1 Calculo AP")
            print("2 IA: regresion lineal")
            print("3 Fisica")
            print("0 salir")
            op = input("? ").strip()
            if op == "0":
                break
            try:
                if op == "1":
                    ap()
                elif op == "2":
                    ia()
                elif op == "3":
                    fisica()
                elif op != "":
                    print("escribe 1, 2, 3 o 0")
            except KeyboardInterrupt:
                print("(interrumpido: de vuelta al menu general)")
            except Exception as err:
                print("Algo fallo: " + str(err))
    except KeyboardInterrupt:
        pass
    print("Para abrir otra vez: general()")


# correr el programa otra vez vuelve a abrir el menu
try:
    general()
finally:
    sys.modules.pop(__name__, None)
