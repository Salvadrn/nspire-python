# calcpy - analisis numerico para TI-Nspire CX II CAS
# Adrian. Uso: from calcpy import *
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

def _seguro(f, x):
    try:
        y = f(x)
        if y != y:            # NaN
            return None
        if abs(y) == float('inf'):
            return None
        return y
    except (ValueError, ZeroDivisionError, OverflowError):
        return None


def biseccion(f, a, b, tol=1e-12, kmax=200):
    """Raiz en [a,b] asumiendo cambio de signo. None si no lo hay."""
    fa, fb = _seguro(f, a), _seguro(f, b)
    if fa is None or fb is None or fa * fb > 0:
        return None
    for _ in range(kmax):
        m = 0.5 * (a + b)
        fm = _seguro(f, m)
        if fm is None:
            return None
        if fm == 0 or (b - a) < tol * max(1.0, abs(m)):
            return m
        if fa * fm < 0:
            b, fb = m, fm
        else:
            a, fa = m, fm
    return 0.5 * (a + b)


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


def raices(f, a, b, n=200, tol=1e-12):
    """Todas las raices de f en [a,b] barriendo n subintervalos."""
    out = []
    paso = (b - a) / n
    x0 = a
    y0 = _seguro(f, x0)
    for i in range(1, n + 1):
        x1 = a + i * paso
        y1 = _seguro(f, x1)
        if y0 is not None and y1 is not None:
            if y0 == 0:
                out.append(x0)
            elif y0 * y1 < 0:
                r = biseccion(f, x0, x1, tol)
                if r is not None:
                    out.append(r)
        x0, y0 = x1, y1
    if _seguro(f, b) == 0:
        out.append(b)
    return _limpia(out)


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


# ---------- extremos ----------

def criticos(f, a, b, n=200):
    """Puntos criticos: raices de f' en [a,b]."""
    return raices(lambda x: d(f, x), a, b, n)


def extremos(f, a, b, n=200):
    """Lista de (x, f(x), tipo) con tipo en 'max','min','silla'.
    Solo extremos LOCALES interiores."""
    out = []
    for x in criticos(f, a, b, n):
        y = _seguro(f, x)
        if y is None:
            continue
        s = d2(f, x)
        if s < -1e-7:
            t = 'max'
        elif s > 1e-7:
            t = 'min'
        else:
            t = 'silla'
        out.append((x, y, t))
    return out


def maxmin(f, a, b, n=200):
    """Maximo y minimo ABSOLUTOS en [a,b] (incluye los bordes).
    Devuelve ((xmax,ymax),(xmin,ymin))."""
    cand = [a, b] + criticos(f, a, b, n)
    mejor = peor = None
    for x in cand:
        y = _seguro(f, x)
        if y is None:
            continue
        if mejor is None or y > mejor[1]:
            mejor = (x, y)
        if peor is None or y < peor[1]:
            peor = (x, y)
    return mejor, peor


def inflexion(f, a, b, n=200):
    """Puntos de inflexion: raices de f'' con cambio de concavidad."""
    out = []
    for x in raices(lambda t: d2(f, t), a, b, n):
        h = 1e-3 * max(1.0, abs(x))
        if d2(f, x - h) * d2(f, x + h) < 0:
            out.append((x, f(x)))
    return out


def analiza(f, a, b, n=200):
    """Reporte completo listo para leer en pantalla."""
    print("f en [{:g}, {:g}]".format(a, b))
    r = raices(f, a, b, n)
    print("raices:", _fmt(r) if r else "ninguna")
    for x, y, t in extremos(f, a, b, n):
        print("{}: x={:.6g}  y={:.6g}".format(t, x, y))
    infl = inflexion(f, a, b, n)
    if infl:
        print("inflex:", _fmt([p[0] for p in infl]))
    (xM, yM), (xm, ym) = maxmin(f, a, b, n)
    print("abs max: {:.6g} en x={:.6g}".format(yM, xM))
    print("abs min: {:.6g} en x={:.6g}".format(ym, xm))


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


# ---------- utilidades ----------

def tabla(f, a, b, n=10):
    """Tabla de valores en pantalla."""
    paso = (b - a) / n
    for i in range(n + 1):
        x = a + i * paso
        y = _seguro(f, x)
        print("{:>10.6g}  {:>12}".format(
            x, "indef" if y is None else "{:.6g}".format(y)))


def limite(f, x0, lado=0):
    """Limite numerico. lado: -1 izq, 1 der, 0 bilateral (None si difieren)."""
    def _ap(signo):
        v = None
        for k in range(3, 10):
            h = signo * 10.0**(-k)
            y = _seguro(f, x0 + h)
            if y is not None:
                v = y
        return v
    if lado < 0:
        return _ap(-1)
    if lado > 0:
        return _ap(1)
    izq, der = _ap(-1), _ap(1)
    if izq is None or der is None:
        return None
    if abs(izq - der) < 1e-4 * max(1.0, abs(izq)):
        return 0.5 * (izq + der)
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
