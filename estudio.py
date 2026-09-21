# estudio - UN solo archivo: Calculo AP + IA + SAT Math
# Para la TI-Nspire CX II CAS de Adrian (MicroPython 1.11).
# GENERADO por build.py desde calcpy, fisica, formulas, ap, ia y sat:
# no lo edites a mano; edita el modulo y corre  python3 build.py
# Corre el programa y sale el menu. Para abrirlo otra vez: estudio()

from math import *


# ===================== calcpy =====================

# calcpy - analisis numerico para TI-Nspire CX II CAS
# Adrian. Uso: from calcpy import *
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


# ===================== fisica =====================

# fisica - herramientas de fisica para TI-Nspire CX II CAS
# Adrian. Uso: from fisica import *
# Necesita calcpy en el mismo documento o en PyLib.


g = 9.81       # m/s^2
G = 6.674e-11  # N m^2/kg^2


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


# ---------- cinematica 1D (MRUA / suvat) ----------

def mrua(v0=None, v=None, a=None, t=None, x=None):
    """Dale 3 de las 5 (v0, v, a, t, x) y resuelve las demas.
    x es desplazamiento. Devuelve dict. Ojo: con v0/a/x o v/a/x
    hay dos soluciones de signo; toma la raiz positiva."""
    k = {'v0': v0, 'v': v, 'a': a, 't': t, 'x': x}
    for _ in range(5):
        v0, v, a, t, x = k['v0'], k['v'], k['a'], k['t'], k['x']
        if v0 is not None and a is not None and t is not None:
            if v is None:
                k['v'] = v0 + a*t
            if x is None:
                k['x'] = v0*t + 0.5*a*t*t
        if v is not None and a is not None and t is not None and v0 is None:
            k['v0'] = v - a*t
        if v0 is not None and v is not None and t is not None:
            if x is None:
                k['x'] = 0.5*(v0 + v)*t
            if a is None and t != 0:
                k['a'] = (v - v0)/t
        if v0 is not None and v is not None and a is not None and a != 0:
            if t is None:
                k['t'] = (v - v0)/a
        if v0 is not None and v is not None and x is not None:
            if t is None and (v0 + v) != 0:
                k['t'] = 2*x/(v0 + v)
        if v0 is not None and t is not None and x is not None and t != 0:
            if a is None:
                k['a'] = 2*(x - v0*t)/(t*t)
            if v is None:
                k['v'] = 2*x/t - v0
        if v is not None and t is not None and x is not None and v0 is None and t != 0:
            k['v0'] = 2*x/t - v
        if v0 is not None and a is not None and x is not None and v is None:
            disc = v0*v0 + 2*a*x
            if disc >= 0:
                k['v'] = sqrt(disc)
        if v is not None and a is not None and x is not None and v0 is None:
            disc = v*v - 2*a*x
            if disc >= 0:
                k['v0'] = sqrt(disc)
        if a is not None and t is not None and x is not None and v0 is None and t != 0:
            k['v0'] = x/t - 0.5*a*t
    for nombre in ('v0', 'v', 'a', 't', 'x'):
        val = k[nombre]
        print("{} = {}".format(nombre,
              "?" if val is None else "{:.6g}".format(val)))
    return k


# ---------- tiro parabolico ----------

def tiro(v0, ang, y0=0):
    """Proyectil: v0 en m/s, ang en grados, y0 altura inicial.
    Imprime altura maxima, tiempo de vuelo, alcance, v de impacto."""
    th = radians(ang)
    vx, vy = v0*cos(th), v0*sin(th)
    t_sub = vy/g
    h_max = y0 + vy*vy/(2*g)
    t_vuelo = (vy + sqrt(vy*vy + 2*g*y0))/g
    alcance = vx*t_vuelo
    vy_f = vy - g*t_vuelo
    v_imp = sqrt(vx*vx + vy_f*vy_f)
    print("h max:     {:.4g} m (t={:.4g} s)".format(h_max, t_sub))
    print("t vuelo:   {:.4g} s".format(t_vuelo))
    print("alcance:   {:.4g} m".format(alcance))
    print("v impacto: {:.4g} m/s a {:.4g} deg".format(
        v_imp, degrees(atan2(vy_f, vx))))
    return {'hmax': h_max, 't': t_vuelo, 'x': alcance, 'v': v_imp}


# ---------- vectores 2D ----------

def comp(mag, ang):
    """Componentes (x, y) de un vector con angulo en grados."""
    th = radians(ang)
    return (mag*cos(th), mag*sin(th))


def vmag(v):
    return sqrt(v[0]**2 + v[1]**2)


def vang(v):
    """Angulo en grados, -180 a 180."""
    return degrees(atan2(v[1], v[0]))


def vsuma(*vs):
    """Suma de vectores (tuplas). Util para fuerzas concurrentes."""
    return (sum(v[0] for v in vs), sum(v[1] for v in vs))


def vpunto(u, v):
    return u[0]*v[0] + u[1]*v[1]


# ---------- laboratorio: regresion lineal ----------

def regresion(xs, ys):
    """Minimos cuadrados: imprime y devuelve (m, b, r).
    Para linealizar datos de lab y sacar pendiente con significado."""
    n = len(xs)
    sx, sy = sum(xs), sum(ys)
    sxx = sum(x*x for x in xs)
    sxy = sum(x*y for x, y in zip(xs, ys))
    syy = sum(y*y for y in ys)
    den = n*sxx - sx*sx
    if den == 0:
        return None
    m = (n*sxy - sx*sy)/den
    b = (sy - m*sx)/n
    den_r = sqrt(den*(n*syy - sy*sy))
    r = (n*sxy - sx*sy)/den_r if den_r > 0 else 0.0
    print("y = {:.6g} x + {:.6g}".format(m, b))
    print("r = {:.6g}   r^2 = {:.6g}".format(r, r*r))
    return (m, b, r)


# ===================== formulas =====================

# formulas - formulario de AP Calculus para TI-Nspire CX II CAS
# Adrian. Solo formulas y tips, cero calculos.
# Se abre desde ap() (opcion 12) o corriendo este programa.
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

# ap - menu interactivo para Calculo AP y fisica
# El unico comando que hay que aprenderse: ap()
# Suelto necesita calcpy y fisica (mismo documento o PyLib); dentro de
# estudio.py (el archivo unico) ya viene todo junto.


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
        print("== FISICA ==")
        print("8 particula v(t)")
        print("9 sube / cae vertical")
        print("10 tiro parabolico")
        print("11 despeja mrua")
        print("== REPASO ==")
        print("12 formulario (formulas y tips)")
        print("0 salir")
        try:
            op = input("? ").strip()
            if op == "0" or op == "":
                return
            _ap_corre(op)
        except Exception as err:
            print("error:", err)
        input("[enter]")


def _ap_corre(op):
    if op == "1":
        f = _ap_f()
        a, b = _ap_intervalo()
        analiza(f, a, b)
    elif op == "2":
        f = _ap_f()
        a, b = _ap_intervalo()
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
            print("izq: ", limite(f, x0, -1))
            print("der: ", limite(f, x0, 1))
            print("(no existe bilateral)")
        else:
            print("limite = {:.6g}".format(L))
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
        particula(v, a, b)
        t0 = _ap_num("rapidez en t = ", (a + b) / 2)
        print("la rapidez", rapidez(v, t0))
    elif op == "9":
        v0 = _ap_num("v0 hacia arriba (enter=se suelta) = ", 0)
        h0 = _ap_num("altura inicial (enter=0) = ", 0)
        tiro(v0, 90, h0)
        print("(v impacto = que tan rapido cae al llegar)")
    elif op == "10":
        v0 = _ap_num("v0 (m/s) = ")
        ang = _ap_num("angulo (grados) = ")
        h0 = _ap_num("altura inicial (enter=0) = ", 0)
        tiro(v0, ang, h0)
    elif op == "11":
        print("enter = no la sabes. x es desplazamiento")
        vals = {}
        for nombre in ("v0", "v", "a", "t", "x"):
            s = _ap_txt(nombre + " = ")
            vals[nombre] = float(eval(s, _ap_ns, {})) if s != "" else None
        mrua(vals["v0"], vals["v"], vals["a"], vals["t"], vals["x"])
    elif op == "12":
        if formulario:
            formulario()
        else:
            print("falta formulas.py (ponlo en PyLib)")
    else:
        print("no existe esa opcion")


# ===================== ia =====================

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


# ===================== sat =====================

# sat - SAT Math para ESTUDIAR en la TI-Nspire CX II CAS
# Adrian. OJO: las calculadoras CAS estan PROHIBIDAS en el SAT (College
# Board, desde 2025). Esto es para estudiar y checar tus practicas; el
# dia del examen se usa el Desmos integrado de Bluebook.
#
# Formulas y tips por dominio oficial + solvers con fracciones exactas
# (el SPR acepta fracciones: 7/3 vale, 2.33 no siempre).
# ASCII, sin f-strings, sin eval: MicroPython 1.11.


_S_ANCHO = 36   # caracteres por renglon del shell
_S_ALTO = 8     # renglones por pantalla antes de pausar

# <<SAT_TEMAS>>
SAT_TEMAS = [
    ('SAT: Algebra (~35%)', [
        '13-15 de las 44 preguntas de Math',
        '',
        "-- pendiente 'slope' --",
        'm = (y2-y1)/(x2-x1)',
        'm>0 sube, m<0 baja, m=0 horizontal',
        'x = k: vertical, m indefinida',
        '',
        '-- formas de la recta --',
        "y = mx + b  'slope-intercept'",
        "y - y1 = m(x - x1)  'point-slope'",
        "Ax + By = C 'standard': m = -A/B",
        "'x-int' = C/A ; 'y-int' = C/B",
        'B = 0: recta vertical x = C/A',
        'TIP: tabla o 2 puntos: saca m,',
        'luego b = y1 - m*x1',
        '',
        '-- paralelas y perpendiculares --',
        "'parallel': m1 = m2, b distinta",
        "'perpendicular': m1*m2 = -1",
        'o sea m2 = -1/m1 (ej. 2 y -1/2)',
        'y = k es perpendicular a x = h',
        '',
        '-- funcion lineal en contexto --',
        'f(x) = mx + b ; f(0) = b',
        "m = 'rate of change' = cambio en y",
        'por cada +1 en x',
        "b = valor inicial 'initial value'",
        "f(x) = 0 -> x = -b/m 'x-int'",
        'TIP: unidades de m = (de y)/(de x)',
        '',
        "-- traducir 'word problems' --",
        "'per', 'each' -> m*x ; fijo -> +b",
        'mezcla: x + y = N ; p1*x + p2*y = T',
        'TIP: define x,y antes de plantear',
        '',
        '-- 1 variable: cuantas soluciones --',
        'ax + b = cx + d',
        'a != c: 1 solucion',
        "a = c, b != d: 0 'no solution'",
        'a = c, b = d: infinitas',
        'se cancela x: 0=0 inf ; 0=5 ninguna',
        'TIP: Desmos: y=lado izq, y=lado der;',
        'la x del cruce es la solucion',
        '',
        "-- sistemas 2x2 'systems' --",
        'sustitucion: despeja y, sustituye',
        'eliminacion: multiplica, suma/resta',
        'a1*x + b1*y = c1 ; a2*x + b2*y = c2',
        'a1/a2 != b1/b2: 1 solucion',
        'a1/a2 = b1/b2 != c1/c2: ninguna',
        'a1/a2 = b1/b2 = c1/c2: infinitas',
        '(se cruzan/paralelas/misma recta)',
        'ojo: si a2, b2 o c2 = 0, usa m y b',
        'TIP: piden x+y? prueba sumar o',
        'restar las ecuaciones tal cual',
        'TIP: Desmos: teclea las 2 rectas,',
        'clic en el cruce da (x,y)',
        'Desmos acepta Ax + By = C tal cual',
        'TIP: k desconocida: iguala razones',
        'o usa slider de k en Desmos',
        '',
        "-- desigualdades 'inequalities' --",
        '* o / por negativo: voltea < por >',
        'ej: -2x < 6  ->  x > -3',
        "'at most', 'no more than': <=",
        "'at least', 'no less than': >=",
        "'maximum': <= ; 'minimum': >=",
        "'more than': > ; 'fewer than': <",
        'y > mx+b: arriba ; y < mx+b: abajo',
        '< > linea punteada ; <= >= solida',
        'TIP: Desmos sombrea cada region;',
        'solucion = donde se traslapan',
        'TIP: duda? prueba (0,0) si no esta',
        'sobre la recta; cumple = ese lado',
    ]),
    ('SAT: Advanced Math (~35%)', [
        '-- cuadraticas: 3 formas --',
        "'standard' ax^2+bx+c: c = y-int",
        "'vertex' a(x-h)^2+k: vertice (h,k)",
        "'factored' a(x-r1)(x-r2): raices",
        'vertice: x=-b/(2a)=(r1+r2)/2',
        'y del vertice: k=f(-b/(2a))',
        'TIP: a>0 min, a<0 max; valor=k, no h',
        'TIP: (x+3)^2 -> h=-3, ojo al signo.',
        '',
        '-- formula general, discriminante --',
        'x=(-b+-sqrt(b^2-4ac))/(2a)',
        'D=b^2-4ac: D>0 2 sol reales,',
        'D=0 1 sol real, D<0 0 sol reales',
        'suma raices=-b/a; producto=c/a',
        'completar: x^2+bx=(x+b/2)^2-(b/2)^2',
        'si a != 1, factoriza a primero.',
        "TIP: 'no real solutions' -> D<0;",
        "'exactly one' -> D=0 y despeja k.",
        '',
        "-- 'equivalent expressions' --",
        'a^2-b^2=(a+b)(a-b)',
        'a^2+-2ab+b^2=(a+-b)^2',
        'TIP: (a+b)^2 != a^2+b^2, falta 2ab',
        'TIP: Desmos: grafica la original y',
        'cada opcion; la que se encima gana.',
        '',
        '-- exponentes y radicales --',
        'x^a*x^b=x^(a+b); (x^a)^b=x^(ab)',
        'x^a/x^b=x^(a-b); x^(-a)=1/x^a; x^0=1',
        '(x^0 y x^(-a) piden x != 0)',
        '(xy)^a=x^a*y^a; (x/y)^a=x^a/y^a',
        'x^(a/b)=raiz b-esima de x^a',
        'x^(1/2)=sqrt(x); x^(1/3)=cbrt(x)',
        'TIP: sqrt(x^2)=|x|, no x.',
        '',
        '-- racional, radical, |x| --',
        'a/b+c/d=(ad+bc)/(bd); denom != 0',
        '(a/b)/(c/d)=ad/(bc)',
        'TIP: cancela FACTORES, no terminos:',
        '(x+2)/(x+3) NO se simplifica.',
        '|A|=k -> A=k o A=-k; k<0 sin sol.',
        '|A|<k -> -k<A<k; |A|>k -> A<-k o A>k',
        "TIP: 'extraneous': si elevaste al",
        'cuadrado, sustituye en la original.',
        'En racionales descarta la x que',
        'hace 0 el denominador.',
        '',
        '-- exponenciales --',
        'y=a(1+r)^t crece; a(1-r)^t decae',
        'a=valor en t=0; r decimal (5%=0.05)',
        'y=a*b^t: b>1 crece, 0<b<1 decae;',
        'cambio % por periodo = (b-1)*100',
        "'compound': A=P(1+r/n)^(nt),",
        "n = veces por 'year', t en 'years'",
        'tasa anual, t en meses -> ^(t/12)',
        "tasa mensual, t en 'years' -> ^(12t)",
        "se duplica cada 3 'years': a*2^(t/3)",
        'TIP: lineal suma igual cada periodo;',
        'exponencial multiplica igual (%).',
        '',
        '-- polinomios y funciones --',
        "f(c)=0 <-> (x-c) 'factor', c 'zero'",
        "'zero' = 'x-intercept' (c,0)",
        "f(0) = 'y-intercept'",
        'residuo de f(x)/(x-c) es f(c)',
        'raiz doble (x-c)^2: toca el eje x',
        'y rebota, no cruza.',
        'f(g(x)): calcula g(x), metelo en f',
        'TIP: f(g(x)) != g(f(x)) en general.',
        'f(x-h)+k: h a la derecha, k arriba',
        '-f(x) refleja en eje x; f(-x) eje y',
        'a*f(x): escala vertical por a',
        'TIP: f(x+3) va a la IZQUIERDA 3.',
        '',
        '-- recta-parabola y Desmos --',
        'iguala: ax^2+bx+c=mx+d, todo a 0:',
        'ax^2+(b-m)x+(c-d)=0',
        'D=(b-m)^2-4a(c-d), el de ESTA ec.',
        'D>0 2 cruces, D=0 tangente, D<0 0',
        'TIP: Desmos: clic en la curva y en',
        'puntos grises = raices, vertice,',
        'intersecciones.',
        'TIP: ec. en 1 variable: grafica',
        'y=izq, y=der; x del cruce = sol.',
        'TIP: constante k? escribela, crea',
        "'slider' y muevelo hasta cumplir.",
    ]),
    ('SAT: Datos y problemas (~15%)', [
        '-- Razones, tasas, unidades --',
        'a/b = c/d  ->  a*d = b*c',
        'd = r*t   r = d/t   t = d/r',
        'rapidez media = d total / t total',
        '(NO es el promedio de las rapideces)',
        'densidad = masa/volumen',
        '1 ft = 12 in -> 1 ft^2 = 144 in^2',
        'TIP: escribe unidades y cancela;',
        'area: factor^2, volumen: factor^3',
        '',
        '-- Porcentajes --',
        'p% de N = (p/100)*N',
        'que % es A de B = (A/B)*100',
        'cambio% = (nuevo-viejo)/viejo*100',
        'subir/bajar p%: N*(1 +- p/100)',
        'original = final/(1 +- p/100)',
        'TIP: cambios sucesivos se',
        'multiplican, NO se suman:',
        '+20% y -20% = 1.2*0.8 = 0.96 (-4%)',
        "TIP: '150% of N' = 1.5*N pero",
        "'150% greater than N' = 2.5*N",
        '',
        '-- Centro y dispersion --',
        "'mean' = suma/n -> suma = media*n",
        "'median': ordena; posicion (n+1)/2",
        'n par: promedia los 2 del centro',
        'tabla de frec.: n = suma de frec.',
        "'range' = max - min",
        "'mode' = valor que mas se repite",
        'media comb.=(n1*m1+n2*m2)/(n1+n2)',
        "'std dev' = dispersion vs la media",
        'TIP: datos pegados a la media =',
        'desv. menor; compara sin calcular',
        'TIP: outlier mueve media, rango y',
        'desv.; casi no mueve la mediana',
        'cola a la derecha: media > mediana',
        'TIP: sumar c a todos: centro +c,',
        'rango y desv. no cambian',
        'TIP: Desmos: L=[3,5,9] y luego',
        'mean(L), median(L), stdev(L)',
        '(stdev = muestral, stdevp = pobl.)',
        '',
        '-- Scatterplots y modelos --',
        "'line of best fit': y = m*x + b",
        'm = cambio predicho en y por +1 x',
        'b = y predicha cuando x = 0',
        'residual = real - predicho',
        'residual > 0: punto sobre la linea',
        'lineal: suma constante, y=m*x+b',
        "'exponential': factor cte, y=a*b^x",
        'sube r% por periodo: b = 1 + r/100',
        'baja r%: b = 1 - r/100; a = inicial',
        'TIP: Desmos: tabla x1,y1 y luego',
        'y1 ~ m*x1 + b  (te da m y b)',
        'exponencial: y1 ~ a*b^x1',
        '',
        '-- Probabilidad --',
        'P(A)=favor./total; P(no A)=1-P(A)',
        'P(A o B) = P(A) + P(B) - P(A y B)',
        'P(A|B) = n(A y B) / n(B)',
        "TIP: tabla: 'given'/'of those' =",
        'denominador es ESA fila o columna',
        '',
        '-- Inferencia y estudios --',
        'total estimado = (prop. muestra)*N',
        'intervalo = estimacion +- margen',
        'muestra mas grande -> margen menor',
        "TIP: 'margin of error' = rango",
        'plausible, NO garantia del real;',
        'habla del parametro poblacional,',
        'no de cada individuo',
        'muestra aleatoria: generaliza solo',
        'a la poblacion muestreada',
        'no aleatoria (voluntarios) = sesgo;',
        'muestra mas grande NO lo arregla',
        'asignacion aleatoria: causa-efecto',
        "observacional: solo 'association'",
    ]),
    ('SAT: Geometria y trig (~15%)', [
        "-- 'reference sheet' (regalado) --",
        'A circ=pi*r^2     C=2*pi*r',
        'A rect=l*w    A tri=(1/2)*b*h',
        'Pitagoras: a^2+b^2=c^2',
        '30-60-90: x, x*sqrt(3), 2x',
        '(x frente a 30; 2x = hipotenusa)',
        '45-45-90: x, x, x*sqrt(2)',
        'V prisma=l*w*h   V cil=pi*r^2*h',
        'V esfera=(4/3)*pi*r^3',
        'V cono=(1/3)*pi*r^2*h',
        'V piramide=(1/3)*l*w*h',
        'Circulo: 360 grados = 2*pi rad',
        'Suma ang de un triangulo = 180',
        "TIP: abre 'Reference' en Bluebook,",
        'no memorices los volumenes.',
        'NO vienen: arco, sector, ecuacion',
        'del circulo, distancia, SOHCAHTOA.',
        '',
        '-- angulos y poligonos --',
        "'vertical angles': son iguales",
        'Par lineal (linea recta): suman 180',
        "Paralelas + 'transversal':",
        'alternos internos: iguales',
        'correspondientes: iguales',
        "'same-side interior': suman 180",
        'Ang exterior = suma de los 2',
        'interiores no adyacentes',
        'Isosceles: 2 lados iguales =>',
        'angulos de la base iguales',
        'Suma int. poligono = (n-2)*180',
        'Suma de ang exteriores = 360',
        'TIP: regular: cada ang=(n-2)*180/n',
        '',
        "-- semejanza 'similar' --",
        'Angulos correspondientes iguales',
        "Lados proporcionales: a/a'=b/b'=k",
        'AA: 2 angulos iguales => semejantes',
        'Perimetros: razon k',
        'Areas: razon k^2   Volumenes: k^3',
        'TIP: lado x2 => area x4, vol x8.',
        'ABC ~ DEF: A<->D, B<->E, C<->F',
        '',
        "-- trig rectangulo 'SOHCAHTOA' --",
        'Ternas: 3-4-5, 5-12-13, 8-15-17,',
        '7-24-25 y multiplos (6-8-10)',
        'sin=op/hip cos=ady/hip tan=op/ady',
        "sin(x)=cos(90-x) 'complementary'",
        'sin(a)=cos(b) => a+b=90 (agudos)',
        'sin(30)=1/2, cos(60)=1/2, tan(45)=1',
        'rad=grados*pi/180',
        'grados=rad*180/pi',
        'TIP: triangulos semejantes =>',
        'mismo sin, cos y tan del angulo.',
        'TIP: Desmos: llave inglesa, elige',
        'Degrees o Radians antes de sin().',
        'Por default inicia en Radians.',
        '',
        '-- circulos --',
        '(x-h)^2+(y-k)^2=r^2  centro (h,k)',
        'OJO signos: (x+3)^2 => h=-3',
        'Derecha es r^2: r^2=49 => r=7',
        'Forma general: completa cuadrado',
        'x^2+bx = (x+b/2)^2-(b/2)^2',
        'x^2+y^2+Dx+Ey+F=0 =>',
        'centro (-D/2,-E/2)',
        'r^2=(D/2)^2+(E/2)^2-F',
        'Si hay 2x^2+2y^2: divide entre 2',
        'Arco=(ang/360)*2*pi*r',
        'Sector=(ang/360)*pi*r^2',
        '(ang = angulo central en grados)',
        'Con t en rad: arco=r*t,',
        'sector=(1/2)*r^2*t',
        "'inscribed angle' = central/2",
        '(mismo arco). En semicirculo = 90',
        "'tangent' es perpendicular al radio",
        'en el punto de tangencia.',
        'TIP: Desmos: grafica la ecuacion',
        'tal cual (forma general sirve).',
        'Centro = medio entre extremos;',
        'r = mitad del ancho.',
        '',
        '-- distancia y punto medio --',
        'd=sqrt((x2-x1)^2+(y2-y1)^2)',
        'M=((x1+x2)/2, (y1+y2)/2)',
        'TIP: extremos del diametro =>',
        'centro=M, r=d/2',
    ]),
    ('SAT: examen y estrategia', [
        '-- formato del examen --',
        '44 preguntas: 2 modulos de 22',
        '35 min por modulo: ~95 s/pregunta',
        'Adaptativo: tu resultado en el',
        'modulo 1 decide dificultad del 2',
        '~75% opcion multiple (4 opciones)',
        '~25% SPR: respuesta tecleada',
        'Puntaje Math: 200-800',
        'TIP: no hay penalizacion: NUNCA',
        'dejes una en blanco, adivina',
        '',
        '-- temas (% del examen) --',
        "'Algebra' ~35%",
        "'Advanced Math' ~35%",
        "'Problem-Solving and Data",
        "Analysis' ~15%",
        "'Geometry and Trigonometry' ~15%",
        '35% = 13-15 preg.; 15% = 5-7 preg.',
        '',
        "-- SPR 'student-produced' --",
        'Vale negativa, fraccion o decimal',
        'Max 5 caracteres (6 si negativa,',
        'el signo cuenta)',
        'Sin %, $, comas ni unidades',
        'Fraccion impropia SI: 7/2',
        'Numero mixto NO: 3 1/2 -> 7/2 o 3.5',
        '(3 1/2 tecleado se lee como 31/2)',
        'Decimal largo: llena TODOS los',
        'espacios (trunca o redondea)',
        '2/3: SI .6666 .6667 0.666 0.667',
        '2/3: NO 0.66 0.67 (muy cortos)',
        'TIP: varias respuestas correctas?',
        'basta con teclear una',
        '',
        '-- calculadora --',
        'CAS (TI-Nspire CX II CAS): PROHIBIDA',
        'desde 2025. Solo se permiten',
        'graficadoras y cientificas NO CAS',
        'Usa Desmos integrado en Bluebook,',
        'esta en toda la seccion: practicalo',
        '',
        '-- Desmos --',
        'TIP: grafica y=lado izq, y=lado der',
        'y lee la interseccion: x = solucion',
        'TIP: sistema: teclea las 2 ecs.;',
        'el cruce (x,y) es la solucion',
        'TIP: clic en la curva marca ceros,',
        'vertice (max/min) e intersecciones',
        'TIP: regresion: tabla + y1~mx1+b',
        'cuadratica: y1~ax1^2+bx1+c',
        'exponencial: y1~a*b^x1',
        'TIP: slider para hallar constante',
        'TIP: teclea directo el circulo o',
        'desigualdad: x^2+y^2=25, y<=2x+1',
        'TIP: lista L=[3,5,8]; luego',
        'mean(L), median(L)',
        '',
        '-- estrategias --',
        "'Plugging in': numeros sencillos",
        'en vez de variables: 2, 3, 5',
        '(evita 0 y 1; usa 100 si es %)',
        "'Backsolving': prueba opciones,",
        'empieza por la de en medio (B o C)',
        'TIP: relee que piden: x o 2x+1?',
        "el valor positivo? 'at most'?",
        "TIP: >2 min? 'mark for review' y",
        'sigue; regresa al final',
        'TIP: las primeras de cada modulo',
        'son mas faciles: aseguralas',
        '',
        "-- hoja 'reference' NO trae --",
        'Formas de la recta, vertice,',
        'discriminante, formula general,',
        'exponentes, cambio %,',
        'ecuacion del circulo, SOHCAHTOA,',
        'media/mediana',
        'TIP: SI trae areas, volumenes,',
        'Pitagoras, 30-60-90 y 45-45-90,',
        'circulo = 360 grados = 2pi rad',
    ]),
]
# <<FIN SAT_TEMAS>>


# ---------- fracciones exactas: (p, q) con q > 0 ----------

def _s_mcd(a, b):
    while b:
        a, b = b, a % b
    return a


def _s_fr(p, q=1):
    if q == 0:
        raise ZeroDivisionError("division entre 0")
    if q < 0:
        p, q = -p, -q
    g = _s_mcd(abs(p), q)
    return (p // g, q // g)


def _s_add(a, b):
    return _s_fr(a[0] * b[1] + b[0] * a[1], a[1] * b[1])


def _s_sub(a, b):
    return _s_fr(a[0] * b[1] - b[0] * a[1], a[1] * b[1])


def _s_mul(a, b):
    return _s_fr(a[0] * b[0], a[1] * b[1])


def _s_div(a, b):
    return _s_fr(a[0] * b[1], a[1] * b[0])


def _s_float(a):
    return a[0] / a[1]


def _s_g(x):
    return "{:.6g}".format(x)


def _s_sh(a):
    """Forma corta: 7/3 o 5."""
    if a[1] == 1:
        return str(a[0])
    return "{}/{}".format(a[0], a[1])


def _s_txt(a):
    """Fraccion y decimal: 7/3 = 2.33333 (o solo 5)."""
    if a[1] == 1:
        return str(a[0])
    return "{} = {}".format(_s_sh(a), _s_g(_s_float(a)))


# ---------- leer numeros: 3, -2.5, 7/3, 40% ----------

def _s_lee_dec(t):
    neg = False
    if t[:1] == "-":
        neg = True
        t = t[1:]
    elif t[:1] == "+":
        t = t[1:]
    if t.count(".") > 1:
        raise ValueError("numero no valido")
    if "." in t:
        i = t.index(".")
        a = t[:i]
        b = t[i + 1:]
    else:
        a = t
        b = ""
    if a + b == "" or not (a + b).isdigit():
        raise ValueError("numero no valido")
    p = int(a + b)
    if neg:
        p = -p
    return _s_fr(p, 10 ** len(b))


def _s_lee(t):
    t = t.strip().replace(" ", "")
    if t[-1:] == "%":
        t = t[:-1]
    if "/" in t:
        i = t.index("/")
        return _s_div(_s_lee_dec(t[:i]), _s_lee_dec(t[i + 1:]))
    return _s_lee_dec(t)


def _s_pide(texto, default=None):
    while True:
        s = input(texto).strip()
        if s == "" and default is not None:
            return default
        try:
            return _s_lee(s)
        except Exception:
            print("no entendi. ej: 3, -2.5, 7/3")


def _s_pide_lista(texto):
    while True:
        s = input(texto).strip().replace(",", " ")
        try:
            vals = [_s_lee(p) for p in s.split()]
            if vals:
                return vals
        except Exception:
            pass
        print("ej: 3 5 8.5 7/2")


# ---------- raices exactas y radicales simplificados ----------

def _s_isqrt(n):
    if n < 2:
        return n
    x = n
    y = (x + 1) // 2
    while y < x:
        x = y
        y = (x + n // x) // 2
    return x


def _s_radical(n):
    """n entero > 0 -> (k, r) con n = k*k*r."""
    k = 1
    i = 2
    while i * i <= n and i < 3000:
        while n % (i * i) == 0:
            n //= i * i
            k *= i
        i += 1
    return (k, n)


def _s_raiz_txt(a):
    """sqrt de una fraccion >= 0: exacta si se puede, si no radical
    simplificado y decimal."""
    p, q = a
    rp = _s_isqrt(p)
    rq = _s_isqrt(q)
    if rp * rp == p and rq * rq == q:
        return _s_txt(_s_fr(rp, rq))
    k, r = _s_radical(p * q)       # sqrt(p/q) = sqrt(p*q)/q
    g = _s_mcd(k, q)
    k //= g
    den = q // g
    s = "sqrt({})".format(r)
    if k != 1:
        s = "{}*{}".format(k, s)
    if den != 1:
        s = "{}/{}".format(s, den)
    return "{} = {}".format(s, _s_g(sqrt(p / q)))


# ---------- salida paginada ----------

def _s_out(lineas):
    c = 0
    for ln in lineas:
        alto = (len(ln) - 1) // _S_ANCHO + 1 if ln else 1
        if c + alto > _S_ALTO:
            input("-- enter para seguir --")
            c = 0
        print(ln)
        c += alto


def _s_muestra(tema):
    titulo, lineas = tema
    print("")
    print("== " + titulo + " ==")
    c = 1
    for ln in lineas:
        alto = (len(ln) - 1) // _S_ANCHO + 1 if ln else 1
        if c + alto > _S_ALTO:
            if input("-- enter=mas, q=menu --").strip() == "q":
                return
            c = 0
        print(ln)
        c += alto
    input("-- fin, enter --")


def _s_hojas():
    while True:
        print("")
        print("== SAT: FORMULAS Y TIPS ==")
        i = 1
        for t in SAT_TEMAS:
            print("{} {}".format(i, t[0]))
            i += 1
        print("0 regresar")
        s = input("? ").strip()
        if s == "0" or s == "":
            return
        if s.isdigit() and 1 <= int(s) <= len(SAT_TEMAS):
            _s_muestra(SAT_TEMAS[int(s) - 1])


# ---------- solvers ----------

def _s_signo(a):
    """' + 5' o ' - 5' para armar ecuaciones."""
    if a[0] < 0:
        return " - " + _s_sh((-a[0], a[1]))
    return " + " + _s_sh(a)


def _s_coef(a, var):
    """Coeficiente pegado a una variable: x, -x, 3x, (2/3)x."""
    if a == (1, 1):
        return var
    if a == (-1, 1):
        return "-" + var
    if a[1] == 1:
        return str(a[0]) + var
    return "(" + _s_sh(a) + ")" + var


def _s_menos_var(var, h):
    """(x - h) con el signo ya resuelto."""
    if h[0] == 0:
        return var
    if h[0] < 0:
        return "({} + {})".format(var, _s_sh((-h[0], h[1])))
    return "({} - {})".format(var, _s_sh(h))


def _s_recta():
    print("Recta por (x1,y1) y (x2,y2)")
    x1 = _s_pide("x1 = ")
    y1 = _s_pide("y1 = ")
    x2 = _s_pide("x2 = ")
    y2 = _s_pide("y2 = ")
    dx = _s_sub(x2, x1)
    dy = _s_sub(y2, y1)
    out = []
    if dx[0] == 0 and dy[0] == 0:
        print("son el mismo punto")
        return
    if dx[0] == 0:
        out.append("recta vertical: x = " + _s_sh(x1))
        out.append("pendiente indefinida")
    else:
        m = _s_div(dy, dx)
        b = _s_sub(y1, _s_mul(m, x1))
        out.append("m = (y2-y1)/(x2-x1)")
        out.append("m = " + _s_txt(m))
        out.append("b = y1 - m*x1 = " + _s_txt(b))
        if m[0] == 0:
            out.append("y = " + _s_sh(b) + "  (horizontal)")
        else:
            ec = "y = " + _s_coef(m, "x")
            if b[0] != 0:
                ec += _s_signo(b)
            out.append(ec)
            cx = _s_div((-b[0], b[1]), m)
            out.append("corte eje x: x = " + _s_txt(cx))
            out.append("perpendicular: m = "
                       + _s_txt(_s_div((-1, 1), m)))
        out.append("paralela: misma m")
    d2 = _s_add(_s_mul(dx, dx), _s_mul(dy, dy))
    out.append("distancia = " + _s_raiz_txt(d2))
    mx = _s_div(_s_add(x1, x2), (2, 1))
    my = _s_div(_s_add(y1, y2), (2, 1))
    out.append("punto medio = ({}, {})".format(_s_sh(mx), _s_sh(my)))
    _s_out(out)


def _s_sistema():
    print("a1*x + b1*y = c1")
    print("a2*x + b2*y = c2")
    a1 = _s_pide("a1 = ")
    b1 = _s_pide("b1 = ")
    c1 = _s_pide("c1 = ")
    a2 = _s_pide("a2 = ")
    b2 = _s_pide("b2 = ")
    c2 = _s_pide("c2 = ")
    det = _s_sub(_s_mul(a1, b2), _s_mul(a2, b1))
    dx = _s_sub(_s_mul(c1, b2), _s_mul(c2, b1))
    dy = _s_sub(_s_mul(a1, c2), _s_mul(a2, c1))
    out = ["det = a1*b2 - a2*b1 = " + _s_sh(det)]
    if det[0] != 0:
        x = _s_div(dx, det)
        y = _s_div(dy, det)
        out.append("1 solucion (se cruzan):")
        out.append("x = " + _s_txt(x))
        out.append("y = " + _s_txt(y))
        out.append("x + y = " + _s_txt(_s_add(x, y)))
    elif dx[0] == 0 and dy[0] == 0:
        out.append("INFINITAS soluciones:")
        out.append("es la misma recta")
        out.append("a1/a2 = b1/b2 = c1/c2")
    else:
        out.append("NINGUNA solucion:")
        out.append("paralelas ('no solution')")
        out.append("a1/a2 = b1/b2 != c1/c2")
    _s_out(out)


def _s_cuad():
    print("a*x^2 + b*x + c = 0")
    a = _s_pide("a = ")
    if a[0] == 0:
        print("a = 0: no es cuadratica")
        return
    b = _s_pide("b = ")
    c = _s_pide("c = ")
    dos_a = _s_mul((2, 1), a)
    D = _s_sub(_s_mul(b, b), _s_mul((4, 1), _s_mul(a, c)))
    h = _s_div((-b[0], b[1]), dos_a)
    k = _s_sub(c, _s_div(_s_mul(b, b), _s_mul((4, 1), a)))
    out = ["D = b^2 - 4ac = " + _s_sh(D)]
    raices = None
    if D[0] < 0:
        out.append("D<0: 0 soluciones reales")
    elif D[0] == 0:
        out.append("D=0: 1 solucion real")
        out.append("x = " + _s_txt(h))
        raices = (h, h)
    else:
        out.append("D>0: 2 soluciones reales")
        rp = _s_isqrt(D[0])
        rq = _s_isqrt(D[1])
        if rp * rp == D[0] and rq * rq == D[1]:
            r = _s_fr(rp, rq)
            xa = _s_div(_s_sub((-b[0], b[1]), r), dos_a)
            xb = _s_div(_s_add((-b[0], b[1]), r), dos_a)
            out.append("x1 = " + _s_txt(xa))
            out.append("x2 = " + _s_txt(xb))
            raices = (xa, xb)
        else:
            if a[1] == 1 and b[1] == 1 and c[1] == 1:
                kk, rr = _s_radical(D[0])
                nb = -b[0]
                den = dos_a[0]
                if den < 0:        # el +- absorbe el signo de la raiz
                    nb = -nb
                    den = -den
                g = _s_mcd(_s_mcd(abs(nb), kk), den)
                nb //= g
                kk //= g
                den //= g
                rad = "sqrt({})".format(rr)
                if kk != 1:
                    rad = "{}*{}".format(kk, rad)
                s = "{} +- {}".format(nb, rad) if nb else "+-" + rad
                if den != 1:
                    s = "({})/{}".format(s, den)
                out.append("x = " + s)
            else:
                out.append("x = (-b +- sqrt(D))/(2a)")
            sq = sqrt(_s_float(D))
            fa = _s_float(dos_a)
            fb = _s_float(b)
            out.append("x1 = " + _s_g((-fb - sq) / fa))
            out.append("x2 = " + _s_g((-fb + sq) / fa))
    out.append("suma raices = -b/a = "
               + _s_txt(_s_div((-b[0], b[1]), a)))
    out.append("producto = c/a = " + _s_txt(_s_div(c, a)))
    out.append("vertice = ({}, {})".format(_s_sh(h), _s_sh(k)))
    if a[0] > 0:
        out.append("abre arriba: MINIMO y = " + _s_sh(k))
    else:
        out.append("abre abajo: MAXIMO y = " + _s_sh(k))
    fv = _s_coef(a, _s_menos_var("x", h) + "^2")
    if k[0] != 0:
        fv += _s_signo(k)
    out.append("'vertex': " + fv)
    if raices:
        ff = _s_coef(a, _s_menos_var("x", raices[0])
                     + _s_menos_var("x", raices[1]))
        out.append("'factored': " + ff)
    out.append("corte eje y = c = " + _s_sh(c))
    _s_out(out)


def _s_porc():
    print("1 p% de N")
    print("2 A es que % de B")
    print("3 cambio % de viejo a nuevo")
    print("4 cambios sucesivos (+20, -10..)")
    print("5 hallar el original")
    op = input("? ").strip()
    cien = (100, 1)
    uno = (1, 1)
    if op == "1":
        p = _s_pide("p (%) = ")
        n = _s_pide("N = ")
        print("(p/100)*N = " + _s_txt(_s_div(_s_mul(p, n), cien)))
    elif op == "2":
        a = _s_pide("A = ")
        b = _s_pide("B = ")
        print("(A/B)*100 = " + _s_txt(_s_mul(_s_div(a, b), cien)) + " %")
    elif op == "3":
        v = _s_pide("viejo = ")
        n = _s_pide("nuevo = ")
        ch = _s_mul(_s_div(_s_sub(n, v), v), cien)
        _s_out(["(nuevo-viejo)/viejo*100",
                "cambio = " + _s_txt(ch) + " %",
                "factor = nuevo/viejo = " + _s_txt(_s_div(n, v))])
    elif op == "4":
        n = _s_pide("valor inicial (enter=100) = ", cien)
        ps = _s_pide_lista("cambios en % (ej: 20 -10): ")
        f = uno
        for p in ps:
            f = _s_mul(f, _s_add(uno, _s_div(p, cien)))
        tot = _s_mul(_s_sub(f, uno), cien)
        _s_out(["factor total = " + _s_txt(f),
                "final = " + _s_txt(_s_mul(n, f)),
                "cambio total = " + _s_txt(tot) + " %",
                "TIP: se multiplican, no se suman"])
    elif op == "5":
        fin = _s_pide("valor final = ")
        p = _s_pide("cambio que tuvo, % (-20 = bajo) = ")
        f = _s_add(uno, _s_div(p, cien))
        _s_out(["original = final/(1 + p/100)",
                "original = " + _s_txt(_s_div(fin, f))])
    else:
        print("opcion no valida")


def _s_estad():
    vals = _s_pide_lista("datos (con espacios): ")
    n = len(vals)
    orden = sorted(vals, key=_s_float)
    suma = (0, 1)
    for v in vals:
        suma = _s_add(suma, v)
    media = _s_div(suma, (n, 1))
    if n % 2:
        med = orden[n // 2]
    else:
        med = _s_div(_s_add(orden[n // 2 - 1], orden[n // 2]), (2, 1))
    cuenta = {}
    for v in vals:
        cuenta[v] = cuenta.get(v, 0) + 1
    tope = max(cuenta.values())
    if tope == 1:
        moda = "no hay (nadie se repite)"
    else:
        ms = sorted([v for v in cuenta if cuenta[v] == tope],
                    key=_s_float)
        moda = ", ".join([_s_sh(v) for v in ms])
    sc = (0, 1)
    for v in vals:
        dd = _s_sub(v, media)
        sc = _s_add(sc, _s_mul(dd, dd))
    out = ["n = {}   suma = {}".format(n, _s_sh(suma)),
           "media 'mean' = " + _s_txt(media),
           "mediana 'median' = " + _s_txt(med),
           "moda 'mode' = " + moda,
           "rango = {} - {} = {}".format(
               _s_sh(orden[-1]), _s_sh(orden[0]),
               _s_sh(_s_sub(orden[-1], orden[0]))),
           "desv.est. poblacion = "
           + _s_g(sqrt(_s_float(sc) / n))]
    if n > 1:
        out.append("desv.est. muestra = "
                   + _s_g(sqrt(_s_float(sc) / (n - 1))))
    out.append("TIP: el SAT casi nunca pide")
    out.append("calcular la desv.: compara")
    out.append("que tan dispersos estan")
    _s_out(out)


def _s_pi_txt(a):
    """a*pi con decimal: (5/2)*pi = 7.85398."""
    if a == (1, 1):
        s = "pi"
    elif a[1] == 1:
        s = "{}*pi".format(a[0])
    else:
        s = "({})*pi".format(_s_sh(a))
    return "{} = {}".format(s, _s_g(_s_float(a) * pi))


def _s_circulo():
    print("1 centro y radio desde")
    print("  x^2+y^2+Dx+Ey+F = 0")
    print("2 arco y sector (r y angulo)")
    op = input("? ").strip()
    if op == "1":
        A = _s_pide("coef de x^2 y y^2 (enter=1) = ", (1, 1))
        if A[0] == 0:
            print("no es un circulo")
            return
        D = _s_div(_s_pide("D = "), A)
        E = _s_div(_s_pide("E = "), A)
        F = _s_div(_s_pide("F = "), A)
        h = _s_div((-D[0], D[1]), (2, 1))
        k = _s_div((-E[0], E[1]), (2, 1))
        r2 = _s_sub(_s_add(_s_mul(h, h), _s_mul(k, k)), F)
        if r2[0] <= 0:
            print("r^2 = " + _s_sh(r2) + ": no es un circulo")
            return
        _s_out(["completando cuadrados:",
                "centro (h,k) = ({}, {})".format(_s_sh(h), _s_sh(k)),
                "h = -D/2, k = -E/2",
                "r^2 = h^2 + k^2 - F = " + _s_sh(r2),
                "r = " + _s_raiz_txt(r2),
                "{}^2 + {}^2 = {}".format(_s_menos_var("x", h),
                                          _s_menos_var("y", k),
                                          _s_sh(r2)),
                "diametro = 2r"])
    elif op == "2":
        r = _s_pide("r = ")
        ang = _s_pide("angulo central (grados) = ")
        fr = _s_div(ang, (360, 1))
        arco = _s_mul(fr, _s_mul((2, 1), r))
        sector = _s_mul(fr, _s_mul(r, r))
        _s_out(["fraccion del circulo = ang/360",
                "= " + _s_txt(fr),
                "arco = frac*2*pi*r",
                "= " + _s_pi_txt(arco),
                "sector = frac*pi*r^2",
                "= " + _s_pi_txt(sector),
                "angulo en rad = "
                + _s_pi_txt(_s_div(ang, (180, 1)))])
    else:
        print("opcion no valida")


def _s_expo():
    print("y = a*(1 + r/100)^t")
    a = _s_float(_s_pide("a (valor inicial) = "))
    r = _s_float(_s_pide("r en % (-5 = decae 5%) = "))
    base = 1 + r / 100
    if base <= 0:
        print("1 + r/100 debe ser > 0")
        return
    t = _s_float(_s_pide("t (periodos) = "))
    out = ["factor por periodo b = " + _s_g(base),
           "y = a*b^t = " + _s_g(a * base ** t)]
    if base > 1:
        out.append("se duplica cada "
                   + _s_g(log(2) / log(base)) + " periodos")
    elif base < 1:
        out.append("baja a la mitad cada "
                   + _s_g(log(0.5) / log(base)) + " periodos")
    _s_out(out)
    meta = _s_pide("meta de y (enter=saltar) = ", (0, 1))
    m = _s_float(meta)
    if m != 0 and base != 1 and a != 0 and m / a > 0:
        print("t = ln(meta/a)/ln(b) = " + _s_g(log(m / a) / log(base)))
    print("TIP: tasa anual con t en meses:")
    print("usa el exponente t/12")


def _s_triang():
    print("Triangulo rectangulo: da 2 lados")
    print("(enter en el que no sabes)")
    cero = (0, 1)
    a = _s_pide("cateto a = ", cero)
    b = _s_pide("cateto b = ", cero)
    c = _s_pide("hipotenusa c = ", cero)
    dados = [v for v in (a, b, c) if v[0] > 0]
    if len(dados) != 2:
        print("necesito exactamente 2 lados")
        return
    a2 = _s_mul(a, a)
    b2 = _s_mul(b, b)
    c2 = _s_mul(c, c)
    out = []
    if c[0] == 0:
        c2 = _s_add(a2, b2)
        out.append("c^2 = a^2 + b^2 = " + _s_sh(c2))
        out.append("c = " + _s_raiz_txt(c2))
    elif a[0] == 0:
        a2 = _s_sub(c2, b2)
        if a2[0] <= 0:
            print("la hipotenusa debe ser mayor")
            return
        out.append("a^2 = c^2 - b^2 = " + _s_sh(a2))
        out.append("a = " + _s_raiz_txt(a2))
    else:
        b2 = _s_sub(c2, a2)
        if b2[0] <= 0:
            print("la hipotenusa debe ser mayor")
            return
        out.append("b^2 = c^2 - a^2 = " + _s_sh(b2))
        out.append("b = " + _s_raiz_txt(b2))
    fa = sqrt(_s_float(a2))
    fb = sqrt(_s_float(b2))
    fc = sqrt(_s_float(c2))
    angA = atan(fa / fb) * 180 / pi
    out.append("angulo A (frente a a) = " + _s_g(angA))
    out.append("angulo B = 90 - A = " + _s_g(90 - angA))
    out.append("sin A = a/c = " + _s_g(fa / fc))
    out.append("cos A = b/c = " + _s_g(fb / fc))
    out.append("tan A = a/b = " + _s_g(fa / fb))
    out.append("TIP: sin A = cos B (suman 90)")
    if a2 == b2:
        out.append("es 45-45-90: x, x, x*sqrt(2)")
    elif _s_mul((4, 1), a2) == c2 or _s_mul((4, 1), b2) == c2:
        out.append("es 30-60-90: x, x*sqrt(3), 2x")
    out.append("area = a*b/2 = " + _s_g(fa * fb / 2))
    _s_out(out)


# ---------- menu ----------

def sat():
    print("")
    print("Tu CAS NO entra al SAT: esto es")
    print("para estudiar. Examen = Desmos.")
    while True:
        print("")
        print("== SAT MATH (estudio) ==")
        print("1 formulas y tips por dominio")
        print("2 recta por 2 puntos")
        print("3 sistema 2x2")
        print("4 cuadratica")
        print("5 porcentajes")
        print("6 estadistica de una lista")
        print("7 circulo / arco y sector")
        print("8 exponencial (crece o decae)")
        print("9 triangulo rectangulo y trig")
        print("0 salir")
        op = input("? ").strip()
        if op == "0" or op == "":
            return
        try:
            if op == "1":
                _s_hojas()
                continue
            elif op == "2":
                _s_recta()
            elif op == "3":
                _s_sistema()
            elif op == "4":
                _s_cuad()
            elif op == "5":
                _s_porc()
            elif op == "6":
                _s_estad()
            elif op == "7":
                _s_circulo()
            elif op == "8":
                _s_expo()
            elif op == "9":
                _s_triang()
            else:
                print("escribe un numero del 0 al 9")
                continue
        except Exception as err:
            print("Algo fallo: " + str(err))
        input("-- enter --")


# ===================== menu principal =====================

def estudio():
    try:
        while True:
            print("")
            print("== ESTUDIO ==")
            print("1 Calculo AP: herramientas")
            print("2 Calculo AP: formulas y tips")
            print("3 IA: regresion lineal")
            print("4 SAT Math (para estudiar)")
            print("0 salir")
            op = input("? ").strip()
            if op == "0":
                break
            try:
                if op == "1":
                    ap()
                elif op == "2":
                    formulario()
                elif op == "3":
                    ia()
                elif op == "4":
                    sat()
                else:
                    print("escribe un numero del 0 al 4")
            except Exception as err:
                print("Algo fallo: " + str(err))
    except KeyboardInterrupt:
        pass
    print("Para abrir otra vez: estudio()")


estudio()
