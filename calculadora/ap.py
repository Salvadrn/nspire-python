# ap - Calculo AP
# Para la TI-Nspire CX II CAS de Adrian (MicroPython 1.11).
# GENERADO por build.py desde src/calcpy.py, formulas.py, ap.py:
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


def _z(v, eps):
    """0.0 si v es ruido numerico alrededor de cero."""
    return 0.0 if abs(v) < eps else v


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


def biseccion(f, a, b, tol=1e-12, kmax=200):
    """Raiz en [a,b] asumiendo cambio de signo. None si no lo hay, si
    es un polo (f crece al cerrar el intervalo) o si es un salto (f no
    baja hacia 0, como abs(x)/x)."""
    r = _corte(f, a, b, tol, kmax)
    if r is None or r[1] > 0.5 * r[2]:
        return None
    return r[0]


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


def raices(f, a, b, n=200, tol=1e-12, dobles=True):
    """Todas las raices de f en [a,b] barriendo n subintervalos.
    dobles: tambien las que solo tocan el eje sin cruzarlo (x^2 en 0),
    buscandolas entre los puntos criticos."""
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
    if dobles:
        for x in raices(lambda t: d(f, t), a, b, n, tol, False):
            y = _seguro(f, x)
            if y is not None and abs(y) < 1e-9:
                out.append(x)
    return _limpia([_z(x, 1e-9) for x in out])


def _cerca(f, m):
    """|f| justo a los lados de un punto donde f no existe: enorme en
    un polo (1/x en 0), normal en un hueco (sin(x)/x en 0)."""
    h = 1e-9 * max(1.0, abs(m))
    vs = [_seguro(f, m - h), _seguro(f, m + h)]
    vs = [abs(v) for v in vs if v is not None]
    return max(vs) if vs else 0.0


def _pico(f, a, b):
    """Busqueda ternaria hacia donde crece |f| en [a,b]: (x, |f(x)|)."""
    for _ in range(80):
        m1 = a + (b - a) / 3
        m2 = b - (b - a) / 3
        y1 = _seguro(f, m1)
        y2 = _seguro(f, m2)
        if y1 is None:
            return m1, _cerca(f, m1)
        if y2 is None:
            return m2, _cerca(f, m2)
        if abs(y1) < abs(y2):
            a = m1
        else:
            b = m2
    x = 0.5 * (a + b)
    y = _seguro(f, x)
    return x, (_cerca(f, x) if y is None else abs(y))


def polos(f, a, b, n=200):
    """Asintotas verticales en [a,b]: donde |f| crece sin tope, con o
    sin cambio de signo (tan en pi/2, 1/x^2 en 0, 1/x en 0)."""
    out = []
    paso = (b - a) / n
    xs = [a + i * paso for i in range(n + 1)]
    ys = [_seguro(f, x) for x in xs]
    for i in range(n):
        if ys[i] is not None and ys[i + 1] is not None \
                and ys[i] * ys[i + 1] < 0:
            r = _corte(f, xs[i], xs[i + 1])
            if r is not None and r[1] > r[2]:
                out.append(r[0])
    for i in range(1, n):
        y, y0, y1 = ys[i], ys[i - 1], ys[i + 1]
        if y0 is None or y1 is None:
            continue
        if y is None or (abs(y) >= abs(y0) and abs(y) >= abs(y1)):
            x, m = _pico(f, xs[i - 1], xs[i + 1])
            base = max(abs(y0), abs(y1), 1.0)
            if m > 1e9 and m > 1e3 * base:
                out.append(x)
    return _limpia([_z(x, 1e-9) for x in out])


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
    return raices(lambda x: d(f, x), a, b, n, 1e-12, False)


def extremos(f, a, b, n=200):
    """Lista de (x, f(x), tipo) con tipo en 'max','min','silla'.
    Solo extremos LOCALES interiores."""
    out = []
    for x in criticos(f, a, b, n):
        y = _seguro(f, x)
        if y is None:
            continue
        y = _z(y, 1e-12)
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
        y = _z(y, 1e-12)
        if mejor is None or y > mejor[1]:
            mejor = (x, y)
        if peor is None or y < peor[1]:
            peor = (x, y)
    return mejor, peor


def inflexion(f, a, b, n=200):
    """Puntos de inflexion: raices de f'' con cambio de concavidad."""
    out = []
    for x in raices(lambda t: d2(f, t), a, b, n, 1e-12, False):
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
    p = polos(f, a, b, n)
    if p:
        print("asintota en x=" + _fmt(p))
        print("no hay max/min absolutos")
        return
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


def limite(f, x0, lado=0):
    """Limite numerico. lado: -1 izq, 1 der, 0 bilateral.
    Devuelve el numero, INF o -INF si crece sin tope, o None si no
    existe (oscila, o los laterales no coinciden)."""
    def _ap(signo):
        vals = []
        for k in range(3, 10):
            y = _seguro(f, x0 + signo * 10.0**(-k))
            if y is not None:
                vals.append(y)
        if not vals:
            return None
        v = vals[-1]
        if len(vals) < 3:
            return v
        w, u = vals[-2], vals[-3]
        if abs(v - w) <= 1e-4 * max(1.0, abs(v)):
            return v
        if abs(v) > 10 and abs(v) > abs(w) > abs(u) \
                and (v > 0) == (w > 0) == (u > 0):
            return INF if v > 0 else -INF
        return None
    if lado < 0:
        return _ap(-1)
    if lado > 0:
        return _ap(1)
    izq, der = _ap(-1), _ap(1)
    if izq is None or der is None:
        return None
    if izq == der:
        return izq
    if abs(izq) == INF or abs(der) == INF:
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


_ap_ns = {"sin": sin, "cos": cos, "tan": tan, "asin": asin, "acos": acos,
          "atan": atan, "sqrt": sqrt, "exp": exp, "log": log, "ln": log,
          "log10": log10, "pi": pi, "e": e, "abs": abs,
          "sen": sin, "__builtins__": {}}


def _ap_txt(prompt):
    """Texto tecleado listo para eval: sin espacios a los lados (el eval
    de MicroPython 1.11 truena con espacio inicial) y ^ como potencia."""
    return input(prompt).strip().replace("^", "**")


def _ap_f(prompt="f(x) = "):
    """Lee una funcion tecleada como texto. Acepta ^ como potencia."""
    s = _ap_txt(prompt)
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
    elif op == "2":
        f = _ap_f()
        a, b = _ap_intervalo()
        p = polos(f, a, b)
        if p:
            print("asintota en x=" + _fmt(p) + ":")
            print("sube/baja sin tope, no hay")
            print("punto mas alto ni mas bajo")
        else:
            (xM, yM), (xm, ym) = maxmin(f, a, b)
            print("mas alto: y={:.6g} en x={:.6g}".format(yM, xM))
            print("mas bajo: y={:.6g} en x={:.6g}".format(ym, xm))
        for x, y, t in extremos(f, a, b):
            print("  {} local en x={:.6g}".format(t, x))
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


# correr el programa otra vez vuelve a abrir el menu
try:
    ap()
finally:
    sys.modules.pop(__name__, None)
