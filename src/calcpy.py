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
    """Tamano tipico de |f| en la malla (mediana). Contra esto se mide
    el ruido numerico y que tan chico es 'cero'."""
    vs = sorted([abs(y) for y in ys if y is not None])
    if not vs:
        return 1.0
    m = vs[len(vs) // 2]
    if m > 0:
        return m
    return vs[-1] if vs[-1] > 0 else 1.0


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
    un salto igual). Valores al nivel del ruido (<= 1e-12*s) cuentan
    como 0."""
    h = 1e-9 * max(1.0, abs(m))
    for sg in (-1, 1):
        yh = _seguro(f, m + sg * h)
        yH = _seguro(f, m + sg * 1000 * h)
        if yh is None or yH is None or abs(yh) <= 1e-12 * s:
            continue
        if abs(yh) > 0.1 * abs(yH):
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


def _nodos_cero(xs, zs):
    """Nodos donde z vale 0 sin ser parte de una meseta (tramo plano)."""
    out = []
    n = len(xs) - 1
    for i in range(n + 1):
        if zs[i] == 0:
            izq = zs[i - 1] if i > 0 else None
            der = zs[i + 1] if i < n else None
            if izq != 0 and der != 0:
                out.append(xs[i])
    return out


def _ceros(f, xs, ys, s, piso, tol):
    """Raices en la malla: nodos en 0 y cambios de signo continuos.
    Devuelve (raices, saltos): saltos = cambios de signo que NO son
    raiz (polo, salto, o esquina si f es una derivada)."""
    zs = [None if y is None else (0.0 if abs(y) <= piso else y)
          for y in ys]
    out = _nodos_cero(xs, zs)
    saltos = []
    for i in range(len(xs) - 1):
        if zs[i] is not None and zs[i + 1] is not None \
                and zs[i] * zs[i + 1] < 0:
            r = _corte(f, xs[i], xs[i + 1], tol)
            if r is None:
                continue
            if _es_raiz(f, r[0], s):
                out.append(r[0])
            else:
                saltos.append(r[0])
    return out, saltos


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
    """El borde xb es parte del dominio (sqrt(x) en 0 si; ln o x*ln(x)
    en 0 no). Si xb no es 0 y cae fuera, es por redondeo: si cuenta."""
    return _seguro(f, xb) is not None or xb != 0


def _snap(xs, a, b):
    return _limpia([_z(x, 1e-9 * max(1.0, abs(b - a))) for x in xs])


def raices(f, a, b, n=200, tol=1e-12, dobles=True, piso=None, crit=None):
    """Todas las raices de f en [a,b]: nodos en 0, cambios de signo (sin
    polos ni saltos), bordes del dominio donde f llega a 0 (sqrt(4-x^2)
    en 2) y, con dobles, las que solo tocan el eje (x^2 en 0).
    piso: |f| menor que esto cuenta como 0 (ruido numerico)."""
    xs, ys = _malla(f, a, b, n)
    s = _escala(ys)
    if piso is None:
        piso = 1e-12 * s
    out = _ceros(f, xs, ys, s, piso, tol)[0]
    for x, L in _bordes(f, xs, ys):
        if _es_num(L) and abs(L) <= 1e-6 * s and _en_dominio(f, x):
            out.append(x)
    if dobles:
        if crit is None:
            crit = _criticos(f, a, b, n, s)
        for x in crit:
            y = _seguro(f, x)
            if y is not None and abs(y) <= 1e-12 * s:
                out.append(x)
    return _snap(out, a, b)


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


def _pico(f, a, b):
    """Busqueda ternaria hacia donde crece |f| en [a,b]."""
    for _ in range(80):
        m1 = a + (b - a) / 3
        m2 = b - (b - a) / 3
        y1 = _seguro(f, m1)
        y2 = _seguro(f, m2)
        if y1 is None:
            return m1
        if y2 is None:
            return m2
        if abs(y1) < abs(y2):
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
    todos = []
    for x in _limpia(cand):
        x = _z(_bonito(x), 1e-9 * max(1.0, abs(b - a)))
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
            out.append(sorted(grupo, key=lambda q: len("%.6g" % q[0]))[0])
        grupo = [p]
    return out


# ---------- extremos ----------

def _criticos(f, a, b, n, s):
    """Puntos criticos (incluye los extremos del intervalo si caen ahi):
    donde f' = 0 y donde f' cambia de signo sin pasar por 0 (esquina
    como abs(x) en 0, o salto de f)."""
    df = lambda x: d(f, x)
    xs, ds = _malla(df, a, b, n)
    ceros, saltos = _ceros(df, xs, ds, _escala(ds), 1e-8 * s, 1e-12)
    # f' con h fijo 've' la esquina corrida hasta 2h: se afina con una
    # derivada de h muy chico y se redondea si queda pegada a un numero
    # de 6 decimales (esquina en x=1, no en 1.00001)
    fino = lambda x: d(f, x, 1e-9 * max(1.0, abs(x)))
    for i in range(len(saltos)):
        m = saltos[i]
        w = 1e-4 * max(1.0, abs(m))
        r = _corte(fino, m - w, m + w)
        if r is not None:
            m = r[0]
            if abs(m - round(m, 6)) < 1e-8 * max(1.0, abs(m)):
                m = round(m, 6)
            saltos[i] = m
    return _snap(ceros + saltos, a, b)


def criticos(f, a, b, n=200):
    """Puntos criticos interiores: f' = 0 o f' no existe."""
    xs, ys = _malla(f, a, b, n)
    t = 1e-9 * max(1.0, abs(b - a))
    return [x for x in _criticos(f, a, b, n, _escala(ys))
            if abs(x - a) > t and abs(x - b) > t]


def _signo(v, piso):
    if v is None:
        return 0
    return 1 if v > piso else (-1 if v < -piso else 0)


def _clasifica(f, x, paso, piso):
    """Prueba de la primera derivada: 'max' si f' pasa de + a -, 'min'
    si pasa de - a +, 'ni max ni min' si no cambia de signo."""
    df = lambda t: d(f, t)
    sa = _signo(_seguro(df, x - 0.5 * paso), piso)
    sd = _signo(_seguro(df, x + 0.5 * paso), piso)
    if sa > 0 and sd < 0:
        return 'max'
    if sa < 0 and sd > 0:
        return 'min'
    return 'ni max ni min'


def _lejos(x, malos, tol):
    for p in malos:
        if abs(x - p) <= tol:
            return False
    return True


def extremos(f, a, b, n=200, crit=None, pol=None):
    """Extremos LOCALES interiores: lista de (x, f(x), tipo) con tipo
    'max', 'min' o 'ni max ni min' (prueba de la primera derivada).
    No cuenta los extremos del intervalo, huecos ni junto a asintotas."""
    xs, ys = _malla(f, a, b, n)
    s = _escala(ys)
    paso = (b - a) / n
    if crit is None:
        crit = _criticos(f, a, b, n, s)
    if pol is None:
        pol = polos(f, a, b, n)
    t = 1e-9 * max(1.0, abs(b - a))
    out = []
    for x in crit:
        if abs(x - a) <= t or abs(x - b) <= t \
                or not _lejos(x, [p[0] for p in pol], 2 * paso):
            continue
        y = _seguro(f, x)
        if y is not None:
            out.append((x, _z(y, 1e-12 * s),
                        _clasifica(f, x, paso, 1e-8 * s)))
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
        crit = _criticos(f, a, b, n, s)
    if pol is None:
        pol = polos(f, a, b, n)
    tp = 1e-9 * max(1.0, abs(b - a))
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
        if not _lejos(x, [p[0] for p in pol], tp):
            continue
        y = _seguro(f, x)
        if y is not None:
            cand.append((x, y, True))
        else:
            for L in _laterales(f, x, a, b):
                if _es_num(L):
                    cand.append((x, L, False))
    for x, L in _bordes(f, xs, ys):
        if _es_num(L):
            cand.append((x, L, _en_dominio(f, x)))
    cand = [(c[0], _z(c[1], 1e-12 * s), c[2]) for c in cand]

    def mejores(signo):
        if not cand:
            return []
        top = max([signo * c[1] for c in cand])
        tol = 1e-9 * max(1.0, abs(top))
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


def inflexion(f, a, b, n=200, pol=None):
    """Puntos de inflexion interiores: f'' cambia de signo (por encima
    del ruido numerico), f existe ahi y no hay asintota junto."""
    xs, ys = _malla(f, a, b, n)
    s = _escala(ys)
    paso = (b - a) / n
    piso = 1e-5 * s
    if pol is None:
        pol = polos(f, a, b, n)
    malos = [p[0] for p in pol]
    t = 1e-9 * max(1.0, abs(b - a))
    dd = lambda u: d2(f, u)
    out = []
    for x in raices(dd, a, b, n, 1e-12, False, piso):
        if abs(x - a) <= t or abs(x - b) <= t \
                or not _lejos(x, malos, 2 * paso):
            continue
        y = _seguro(f, x)
        i = _seguro(dd, x - paso)
        k = _seguro(dd, x + paso)
        if y is not None and i is not None and k is not None and \
                (i > piso and k < -piso or i < -piso and k > piso):
            out.append((_z(x, 1e-6 * max(1.0, abs(b - a))), y))
    return out


def _abs_txt(nombre, lst, sube):
    if lst is None:
        return ["no hay " + nombre + ": " + sube + " sin tope"]
    if not lst:
        return ["no hay " + nombre + " (f no existe)"]
    alc = [c for c in lst if c[2]]
    if alc:
        return ["{}: y={:.6g} en x={}".format(
            nombre, alc[0][1], _fmt([c[0] for c in alc]))]
    c = lst[0]
    return ["no hay " + nombre + ": y->{:.6g}".format(c[1]),
            "  cuando x->{:.6g} (no se alcanza)".format(c[0])]


def analiza(f, a, b, n=200):
    """Reporte completo listo para leer en pantalla."""
    print("f en [{:g}, {:g}]".format(a, b))
    xs, ys = _malla(f, a, b, n)
    crit = _criticos(f, a, b, n, _escala(ys))
    pol = polos(f, a, b, n)
    r = raices(f, a, b, n, 1e-12, True, None, crit)
    print("raices:", _fmt(r) if r else "ninguna")
    if pol:
        print("asintota en x=" + _fmt([p[0] for p in pol]))
    for x, y, t in extremos(f, a, b, n, crit, pol):
        print("{}: x={:.6g}  y={:.6g}".format(t, x, y))
    infl = inflexion(f, a, b, n, pol)
    if infl:
        print("inflex:", _fmt([p[0] for p in infl]))
    maxs, mins = absolutos(f, a, b, n, crit, pol)
    for linea in _abs_txt("abs max", maxs, "sube") + \
            _abs_txt("abs min", mins, "baja"):
        print(linea)


def alto_bajo(f, a, b, n=200):
    """Punto mas alto y mas bajo en [a,b] y los extremos locales."""
    xs, ys = _malla(f, a, b, n)
    crit = _criticos(f, a, b, n, _escala(ys))
    pol = polos(f, a, b, n)
    if pol:
        print("asintota en x=" + _fmt([p[0] for p in pol]))
    maxs, mins = absolutos(f, a, b, n, crit, pol)
    for linea in _abs_txt("mas alto", maxs, "sube") + \
            _abs_txt("mas bajo", mins, "baja"):
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
    'bonito' (0.5000017 -> 0.5); -0.0 -> 0.0."""
    r = round(L, 3)
    if abs(L - r) < 2e-6 * max(1.0, abs(L)):
        L = r
    return _z(L + 0.0, 1e-12)


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
            1e-6 * max(1.0, max([abs(w) for w in v[:3]])):
        return 0.0
    u = v[-5:]
    if all([abs(u[i + 1]) < abs(u[i]) for i in range(len(u) - 1)]) \
            and all([(w > 0) == (u[-1] > 0) for w in u]) \
            and abs(u[-2] - u[-1]) > 0.05 * abs(u[-1]):
        return 0.0
    # meseta: el valor justo antes de que el redondeo haga crecer las
    # diferencias ((1-cos x)/x^2 da 0 con h muy chico)
    dif = [abs(v[i + 1] - v[i]) for i in range(len(v) - 1)]
    mejor = 0
    for i in range(1, len(dif)):
        if dif[i] > dif[i - 1]:
            break
        mejor = i
    L = v[mejor + 1]
    if dif[mejor] > 1e-3 * max(1.0, abs(L)):
        return None                       # no se asienta: oscila
    return _redondo(L - dif[mejor] * (1 if v[mejor] > L else -1) / 9.0)


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
    if abs(izq - der) <= 1e-5 * max(1.0, abs(izq)):
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
