# sat - SAT Math para ESTUDIAR en la TI-Nspire CX II CAS
# Adrian. OJO: las calculadoras CAS estan PROHIBIDAS en el SAT (College
# Board, desde 2025). Esto es para estudiar y checar tus practicas; el
# dia del examen se usa el Desmos integrado de Bluebook.
#
# Formulas y tips por dominio oficial + solvers con fracciones exactas
# (el SPR acepta fracciones: 7/3 vale, 2.33 no siempre).
# ASCII, sin f-strings, sin eval: MicroPython 1.11.

# --- bundle: skip ---
from math import sqrt, log, atan, pi
# --- bundle: end skip ---

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


# --- autorun ---
sat()
