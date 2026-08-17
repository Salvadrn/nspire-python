# fisica - herramientas de fisica para TI-Nspire CX II CAS
# Adrian. Uso: from fisica import *
# Necesita calcpy en el mismo documento o en PyLib.

from math import *
from calcpy import d, integra, raices, _seguro, _limpia

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
