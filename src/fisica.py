# FISICA.PY — Solucionador de mecanica + conversiones
# Para TI-Nspire CX II (Python / MicroPython)
# Notacion del formulario: g suma (abajo positivo en caida)

# --- bundle: skip ---
from math import sin, cos, tan, atan2, sqrt, radians, degrees
import sys


# limpia el cache de modulos al arrancar (blindado)
try:
    for _m in list(sys.modules):
        if _m != __name__:
            sys.modules.pop(_m)
except Exception:
    pass
# --- bundle: end skip ---

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
    elif mu > 0 and a is None:
        a = -mu * G
        proc.append("a=-mu*g = -(" + r2(mu) + ")(9.81) = " + r2(a))
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
                vf = sqrt(v2)
                if t is None and a != 0 and (vf - v0) / a < 0:
                    vf = -vf
                proc.append("vf=raiz(v0^2+2ax) = raiz(" + rp(v0) + "^2+2(" + r2(a) + ")(" + r2(x) + ")) = " + r2(vf))
                if vf < 0:
                    proc.append("(vf negativa: con + saldria t < 0)")
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
                v0 = sqrt(v2)
                if t is None and a != 0 and (vf - v0) / a < 0:
                    v0 = -v0
                proc.append("v0=raiz(vf^2-2ax) = " + r2(v0))
                if v0 < 0:
                    proc.append("(v0 negativa: con + saldria t < 0)")
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
        print("tan(ang) <=", r2(mu), "-> NO desliza (estatico)")
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
            print("=", r6(v * 3600), "s")
        elif d == "2":
            print("=", r6(v * 60), "s")
        else:
            print("=", r6(v / 60), "min =", r6(v / 3600), "h")
    elif op == "6":
        tip("1 m3 = 1000 L; 1 L = 1000 mL; 1 mL = 1 cm3")
        v = num("valor (solo el numero): ")
        print("1) m3 -> L y mL   2) L -> m3 y mL   3) mL -> L y m3")
        d = input("> ")
        if d == "1":
            print("=", r6(v * 1000), "L =", r6(v * 1e6), "mL")
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
            print("=", r6(v * 1000), "kg/m3")
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
    print(">>> FISICA v7.1")
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


# --- autorun ---
try:
    fisica()
finally:
    sys.modules.pop(__name__, None)
