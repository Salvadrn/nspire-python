# sat - SAT Math para ESTUDIAR en la TI-Nspire CX II CAS
# Adrian. OJO: las calculadoras CAS estan PROHIBIDAS en el SAT (College
# Board, desde 2025). Esto es para estudiar y checar tus practicas; el
# dia del examen se usa el Desmos integrado de Bluebook.
#
# Formulas y tips por dominio oficial + solvers con fracciones exactas
# (el SPR acepta fracciones: 7/3 vale, 2.33 no siempre).
# ASCII, sin f-strings, sin eval: MicroPython 1.11.

# --- bundle: skip ---
from math import sqrt, log, atan, pi, sin, cos, tan, exp, log10
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
        "-- area 'surface area' --",
        '(NO viene en la hoja reference)',
        'Cilindro: 2*pi*r*h + 2*pi*r^2',
        '  (lado + 2 tapas)',
        '  ej r=3, h=5: 30pi+18pi = 48pi',
        'Esfera: 4*pi*r^2',
        '  ej r=3: 36pi',
        'Cono: pi*r*(r + sqrt(h^2+r^2))',
        '  = pi*r^2 + pi*r*L, con',
        '  L = sqrt(h^2+r^2) (inclinada)',
        '  ej r=3, h=4: L=5, 24pi',
        'Piramide base l x w, altura h:',
        '  l*w + l*sqrt((w/2)^2+h^2)',
        '      + w*sqrt((l/2)^2+h^2)',
        '  (base + 4 triangulos)',
        '  ej l=w=6, h=4: 36+30+30 = 96',
        'Caja: 2*(l*w + l*h + w*h)',
        'Cubo: 6*s^2',
        'TIP: area superficial = suma de',
        'las areas de todas las caras.',
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
        "-- altura 'altitude' (atajos) --",
        'Triang. rectangulo con la altura',
        'CD a la hipotenusa AB:',
        '1) altura = cateto1*cateto2/hip',
        '   CD = AC*BC/AB',
        '   (ej AC=7, BC=5: hip=sqrt(74),',
        '   CD = 35/sqrt(74) = 4.07)',
        '2) altura = sqrt(x*y), con x=AD,',
        '   y=DB (pedazos de la hipot.)',
        '   (ej AD=4, DB=9: CD = 6)',
        '   y cada cateto: AC^2 = AD*AB,',
        '   BC^2 = DB*AB',
        '3) en CUALQUIER triangulo:',
        '   altura = 2*Area/base  (2A/b)',
        '   (ej A=20, AB=10: altura 4)',
        'Los 3 triangulos son semejantes:',
        'ACD ~ CBD ~ ABC',
        'TIP: menu 17 lo resuelve con',
        '2 datos cualesquiera.',
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
        'Los comandos estan en la seccion',
        '6 (comandos de Desmos).',
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
        'media/mediana, area superficial',
        'TIP: SI trae areas, volumenes,',
        'Pitagoras, 30-60-90 y 45-45-90,',
        'circulo = 360 grados = 2pi rad',
    ]),
    ('SAT: comandos de Desmos', [
        '-- como se teclea --',
        'pi -> escribe pi',
        'sqrt(x) -> escribe sqrt',
        'cbrt(x) raiz cubica',
        'nthroot -> raiz n-esima',
        'x^2 potencia; / arma la fraccion',
        'abs(x) o |x|  valor absoluto',
        'ln(x)   log(x) es base 10',
        'log_2(8) = 3  (base con _)',
        'e^x  (e ya vale 2.718...)',
        '5!   nCr(5,2)=10   nPr(5,2)=20',
        'gcd(12,18)=6  lcm(4,6)=12',
        'mod(17,5)=2   round(x)',
        'x1 -> se vuelve subindice x_1',
        'TIP: junto al resultado sale un',
        'boton a/b: lo pasa a fraccion.',
        '',
        '-- graficar y leer --',
        'y=2x+3   recta',
        'f(x)=x^2-4x+3   luego f(5)',
        'clic en la curva: puntos grises',
        '= ceros, vertice, cruces',
        'y=x^2 {x>0}  dominio limitado',
        'y<2x+1  sombrea la region',
        '(x-2)^2+(y+1)^2=9   circulo',
        '(2,3)  punto',
        'f(x)=10? grafica y=f(x) y y=10;',
        'clic en el cruce',
        '',
        '-- resolver --',
        '1 variable: teclea 3x+5=2x-1',
        'tal cual: sale la linea vertical',
        'x=-6 (la x es la solucion).',
        'o y=lado izq, y=lado der: la x',
        'del cruce = solucion',
        'sistema: teclea las 2 ecs.;',
        'clic en el cruce = (x,y)',
        'paralelas: 0 sol.',
        'misma linea: infinitas',
        '',
        '-- constantes (slider) --',
        'y=kx^2 -> clic en "add slider"',
        'muevelo hasta que cumpla',
        'k=3  fija la constante',
        'OJO: x, y, r, e, t ya estan',
        'tomadas: usa a, b, k, p, h...',
        '(r=3 dibuja un circulo polar)',
        '',
        '-- formulas con letras --',
        'define a=3 y h=5 (renglones)',
        'luego teclea la formula:',
        '2pi a h+2pi a^2  -> 150.8',
        'cambias a o h y se recalcula.',
        'ej cono: pi a(a+sqrt(h^2+a^2))',
        '',
        '-- tabla y regresion ~ --',
        '+ -> table: columnas x1, y1',
        'y1~mx1+b   lineal (da m, b, r)',
        'y1~ax1^2+bx1+c   cuadratica',
        'y1~ab^x1   exponencial',
        '~ = que se parezca: da las',
        'letras y R^2 (1 = exacto)',
        '',
        '-- identidad con ~ (menu 15) --',
        'X=[1...10]+0.5',
        'luego: izq(X) ~ der(X)',
        'ej: (3X+7)/((X-5)(X+4))',
        '   ~ a/(X-5)+b/(X+4)',
        'Desmos da a=2.444 (=22/9) y',
        'b=0.5556 (=5/9)',
        '(+0.5 evita dividir entre 0)',
        '',
        '-- estadistica --',
        'L=[3,5,8,8,10]',
        'mean(L)   median(L)',
        'stdev(L)   (de muestra)',
        'stdevp(L)  (de poblacion)',
        'min(L) max(L); rango: max-min',
        'quartile(L,1)  quartile(L,3)',
        'length(L) cuantos; total(L) suma',
        'sort(L) ordena (moda: a ojo)',
        'tabla de frecuencias:',
        'V=[valores]  C=[cuantas veces]',
        'media = total(V*C)/total(C)',
        'boxplot(L)   histogram(L)',
        '',
        '-- geometria y trig --',
        'llave inglesa -> Degrees',
        'sin(30)  cos  tan  arcsin(0.5)',
        'distance((1,2),(4,6)) = 5',
        'midpoint((1,2),(4,6))',
        '',
        '-- ver mejor --',
        'clic al circulo de color: ocultar',
        'casa = vista normal; +/- = zoom',
        'no ves la curva? llave inglesa',
        'y cambia los ejes',
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


class _SMenu(Exception):
    # 'q' en cualquier dato: regresa al menu del SAT (sin esto, un dato
    # que no se lee deja la pregunta en ciclo y hay que apagar la calc)
    pass


def _sat_entrada(prompt, q_ok=False):
    """input() seguro en la Nspire: si la pregunta no cabe en el renglon
    va en el suyo y se escribe despues de '> ' (si no, la calc regresa
    tambien el pedazo de la pregunta junto con la respuesta).
    'q' o 'menu' regresan al menu; q_ok=True cuando q es una letra."""
    if len(prompt) > 28:
        print(prompt.rstrip())
        r = input("> ")
    else:
        r = input(prompt)
    t = r.strip().lower()
    if t == "menu" or t == "salir" or (t == "q" and not q_ok):
        raise _SMenu()
    return r


def _s_cola(s):
    # si la calc regresa tambien el pedazo de la pregunta ('AC): 90'),
    # queda lo que va despues del ultimo ':' o '>' (un numero no los usa)
    for c in ":>":
        i = s.rfind(c)
        if i >= 0:
            s = s[i + 1:]
    return s.strip()


def _s_pide(texto, default=None):
    while True:
        s = _s_cola(_sat_entrada(texto))
        if s == "" and default is not None:
            return default
        try:
            return _s_lee(s)
        except Exception:
            print("no entendi. ej: 3, -2.5, 7/3")
            print("(q = regresar al menu)")


def _s_pide_lista(texto):
    while True:
        s = _s_cola(_sat_entrada(texto)).replace(",", " ")
        try:
            vals = [_s_lee(p) for p in s.split()]
            if vals:
                return vals
        except Exception:
            pass
        print("ej: 3 5 8.5 7/2  (q = menu)")


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
        if s == "0" or s == "" or s == "q":
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


# ---------- discriminante con k / recta y parabola ----------

def _s_neg(a):
    return (-a[0], a[1])


def _s_cmp0(a):
    return (a[0] > 0) - (a[0] < 0)


def _s_raices_txt(A, B, C):
    """Lineas con las soluciones reales de A x^2 + B x + C = 0."""
    out = []
    D = _s_sub(_s_mul(B, B), _s_mul((4, 1), _s_mul(A, C)))
    dos_a = _s_mul((2, 1), A)
    if D[0] < 0:
        return D, [], out
    rp = _s_isqrt(D[0])
    rq = _s_isqrt(D[1])
    if rp * rp == D[0] and rq * rq == D[1]:
        r = _s_fr(rp, rq)
        xs = [_s_div(_s_sub(_s_neg(B), r), dos_a),
              _s_div(_s_add(_s_neg(B), r), dos_a)]
        if D[0] == 0:
            xs = xs[:1]
        return D, xs, out
    sq = sqrt(_s_float(D))
    fa = _s_float(dos_a)
    fb = _s_float(B)
    out.append("x = (-b +- sqrt(D))/(2a)")
    out.append("  = (" + _s_sh(_s_neg(B)) + " +- "
               + _s_raiz_txt(D).split(" = ")[0] + ")/" + _s_sh(dos_a))
    return D, [(-fb - sq) / fa, (-fb + sq) / fa], out


def _s_num_txt(v):
    if isinstance(v, tuple):
        return _s_txt(v)
    return _s_g(v)


def _s_discr_k():
    print("a*x^2 + b*x + c = 0")
    print("con una letra k que no sabes")
    print("donde esta k? 1) a  2) b  3) c")
    pos = input("? ").strip()
    if pos not in ("1", "2", "3"):
        print("opcion no valida")
        return
    print("cuantas soluciones reales?")
    print("1) exactamente una (D = 0)")
    print("2) ninguna (D < 0)")
    print("3) dos (D > 0)")
    cond = input("? ").strip()
    if cond not in ("1", "2", "3"):
        print("opcion no valida")
        return
    uno = (1, 1)
    if pos != "1":
        a = _s_pide("a = ")
    if pos != "2":
        b = _s_pide("b = ")
    if pos != "3":
        c = _s_pide("c = ")
    signo = {"1": "= 0", "2": "< 0", "3": "> 0"}[cond]
    out = ["discriminante D = b^2 - 4ac",
           "condicion: D " + signo]
    if pos == "2":
        P = _s_mul((4, 1), _s_mul(a, c))
        out.append("D = k^2 - 4(" + _s_sh(a) + ")(" + _s_sh(c) + ")")
        out.append("  = k^2 - " + _s_sh(P))
        out.append("k^2 " + signo.replace("0", _s_sh(P)))
        rz = _s_raiz_txt(P).split(" = ")[0] if P[0] > 0 else "0"
        if cond == "1":
            if P[0] < 0:
                out.append("k^2 no puede ser negativo:")
                out.append("NINGUN k (nunca una sola)")
            elif P[0] == 0:
                out.append("k = 0")
            else:
                out.append("k = +-" + rz)
                if "sqrt" in rz:
                    out.append("k = " + _s_raiz_txt(P) + " o su negativo")
        elif cond == "2":
            if P[0] <= 0:
                out.append("k^2 >= 0 siempre: NINGUN k")
                out.append("(siempre hay solucion real)")
            else:
                out.append("-" + rz + " < k < " + rz)
                out.append("decimal: |k| < " + _s_g(sqrt(_s_float(P))))
        else:
            if P[0] < 0:
                out.append("cualquier k sirve")
            elif P[0] == 0:
                out.append("cualquier k distinto de 0")
            else:
                out.append("k < -" + rz + "  o  k > " + rz)
                out.append("decimal: |k| > " + _s_g(sqrt(_s_float(P))))
    elif pos == "3":
        if a[0] == 0:
            print("a = 0: no es cuadratica")
            return
        Q = _s_div(_s_mul(b, b), _s_mul((4, 1), a))
        out.append("D = (" + _s_sh(b) + ")^2 - 4(" + _s_sh(a) + ")k")
        out.append("  = " + _s_sh(_s_mul(b, b)) + " - "
                   + _s_sh(_s_mul((4, 1), a)) + "k")
        out.append("D = 0 cuando k = b^2/(4a) = " + _s_txt(Q))
        if cond == "1":
            out.append("k = " + _s_txt(Q))
        elif (cond == "2") == (a[0] > 0):
            out.append("k > " + _s_txt(Q))
        else:
            out.append("k < " + _s_txt(Q))
    else:
        if c[0] == 0:
            if b[0] == 0:
                out.append("b = c = 0: D = 0 para todo k")
            else:
                out.append("c = 0: D = b^2 > 0 siempre:")
                out.append("dos soluciones con todo k != 0")
            _s_out(out)
            return
        Q = _s_div(_s_mul(b, b), _s_mul((4, 1), c))
        out.append("D = (" + _s_sh(b) + ")^2 - 4k(" + _s_sh(c) + ")")
        out.append("D = 0 cuando k = b^2/(4c) = " + _s_txt(Q))
        if cond == "1":
            if Q[0] == 0:
                out.append("k = 0 no vale (no seria")
                out.append("cuadratica): NINGUN k")
            else:
                out.append("k = " + _s_txt(Q))
        elif (cond == "2") == (c[0] > 0):
            out.append("k > " + _s_txt(Q))
        else:
            out.append("k < " + _s_txt(Q) + "  (y k != 0)")
    _s_out(out)


def _s_recta_parab():
    print("parabola y = a*x^2 + b*x + c")
    print("recta    y = m*x + n")
    a = _s_pide("a = ")
    b = _s_pide("b = ")
    c = _s_pide("c = ")
    m = _s_pide("m = ")
    n = _s_pide("n = ")
    A = a
    B = _s_sub(b, m)
    C = _s_sub(c, n)
    ec = _s_coef(A, "x^2") if A[0] != 0 else ""
    if B[0] != 0:
        ec = (ec + _s_signo(B)[:3] + _s_coef((abs(B[0]), B[1]), "x")) if ec else _s_coef(B, "x")
    if C[0] != 0 or not ec:
        ec = (ec + _s_signo(C)) if ec else _s_sh(C)
    out = ["igualo: a x^2 + bx + c = mx + n", ec + " = 0"]
    if A[0] == 0:
        if B[0] == 0:
            out.append("misma pendiente y sin x^2:")
            out.append("infinitos cruces" if C[0] == 0 else "NO se cruzan")
        else:
            x = _s_div(_s_neg(C), B)
            out.append("1 cruce: x = " + _s_txt(x))
            out.append("y = " + _s_txt(_s_add(_s_mul(m, x), n)))
        _s_out(out)
        return
    D, xs, extra = _s_raices_txt(A, B, C)
    out.append("D = b^2 - 4ac = " + _s_txt(D))
    if D[0] < 0:
        out.append("D < 0: NO se cruzan")
    elif D[0] == 0:
        out.append("D = 0: se tocan en 1 punto")
        out.append("(la recta es tangente)")
    else:
        out.append("D > 0: se cruzan en 2 puntos")
    out += extra
    for x in xs:
        if isinstance(x, tuple):
            y = _s_add(_s_mul(m, x), n)
            out.append("({}, {})".format(_s_sh(x), _s_sh(y)))
        else:
            y = _s_float(m) * x + _s_float(n)
            out.append("({}, {})".format(_s_g(x), _s_g(y)))
    _s_out(out)


def _s_discr():
    print("1 cuantas soluciones (a,b,c)")
    print("2 hallar k para 1, 0 o 2")
    print("3 recta y parabola: cruces")
    op = input("? ").strip()
    if op == "1":
        _s_cuad()
    elif op == "2":
        _s_discr_k()
    elif op == "3":
        _s_recta_parab()
    else:
        print("opcion no valida")


# ---------- sistema 2x2 con una k ----------

def _s_det3(co):
    a1, b1, c1, a2, b2, c2 = co
    det = _s_sub(_s_mul(a1, b2), _s_mul(a2, b1))
    dx = _s_sub(_s_mul(c1, b2), _s_mul(c2, b1))
    dy = _s_sub(_s_mul(a1, c2), _s_mul(a2, c1))
    return det, dx, dy


def _s_sistema_k():
    print("a1*x + b1*y = c1")
    print("a2*x + b2*y = c2")
    print("donde esta la k?")
    print("1)a1 2)b1 3)c1 4)a2 5)b2 6)c2")
    pos = input("? ").strip()
    if pos not in ("1", "2", "3", "4", "5", "6"):
        print("opcion no valida")
        return
    nombres = ["a1", "b1", "c1", "a2", "b2", "c2"]
    ip = int(pos) - 1
    co = []
    for i in range(6):
        if i == ip:
            co.append(None)
        else:
            co.append(_s_pide(nombres[i] + " = "))
    c0 = list(co)
    c0[ip] = (0, 1)
    c1_ = list(co)
    c1_[ip] = (1, 1)
    e0 = _s_det3(c0)
    e1 = _s_det3(c1_)
    # cada cosa es lineal en k: v(k) = v0 + (v1 - v0) k
    lin = [(e0[i], _s_sub(e1[i], e0[i])) for i in range(3)]
    det0, detk = lin[0]
    out = ["det = a1*b2 - a2*b1"]
    if detk[0] != 0:
        ec = _s_coef(detk, "k") + (_s_signo(det0) if det0[0] != 0 else "")
        out.append("det(k) = " + ec)
    else:
        out.append("det = " + _s_sh(det0) + " (no depende de k)")

    def raiz_lin(v0, vk):
        return _s_div(_s_neg(v0), vk)

    if detk[0] == 0:
        if det0[0] != 0:
            out.append("det != 0: SIEMPRE 1 solucion")
            out.append("(ningun k da 0 o infinitas)")
            _s_out(out)
            return
        out.append("det = 0 siempre: rectas paralelas")
        dx0, dxk = lin[1]
        dy0, dyk = lin[2]
        ks = []
        for v0, vk in ((dx0, dxk), (dy0, dyk)):
            if vk[0] != 0:
                ks.append(raiz_lin(v0, vk))
        if ks and all(_s_det3([co[i] if i != ip else ks[0] for i in range(6)])[j][0] == 0
                      for j in (1, 2)):
            out.append("INFINITAS si k = " + _s_txt(ks[0]))
            out.append("(misma recta)")
            out.append("NINGUNA si k != " + _s_sh(ks[0]))
        else:
            out.append("NINGUNA solucion con todo k")
        _s_out(out)
        return
    k0 = raiz_lin(det0, detk)
    out.append("det = 0  ->  k = " + _s_txt(k0))
    cok = [co[i] if i != ip else k0 for i in range(6)]
    det, dx, dy = _s_det3(cok)
    if dx[0] == 0 and dy[0] == 0:
        out.append("con k = " + _s_sh(k0) + ": INFINITAS")
        out.append("(misma recta, 'infinitely many')")
    else:
        out.append("con k = " + _s_sh(k0) + ": NINGUNA")
        out.append("(paralelas, 'no solution')")
    out.append("con k != " + _s_sh(k0) + ": 1 solucion")
    out.append("TIP: no solution <-> mismas")
    out.append("pendientes, distinto corte")
    _s_out(out)


# ---------- valor absoluto ----------

def _s_absoluto():
    print("|a*x + b| = c")
    a = _s_pide("a = ")
    if a[0] == 0:
        print("a = 0: no hay x")
        return
    b = _s_pide("b = ")
    c = _s_pide("c = ")
    out = []
    if c[0] < 0:
        out.append("c < 0: NINGUNA solucion")
        out.append("(un valor absoluto nunca")
        out.append("es negativo)")
    elif c[0] == 0:
        out.append("c = 0: una solucion")
        out.append("ax + b = 0 -> x = " + _s_txt(_s_div(_s_neg(b), a)))
    else:
        x1 = _s_div(_s_sub(c, b), a)
        x2 = _s_div(_s_sub(_s_neg(c), b), a)
        out.append("ax + b = c   o   ax + b = -c")
        out.append("x = " + _s_txt(x1))
        out.append("x = " + _s_txt(x2))
        out.append("suma = " + _s_txt(_s_add(x1, x2)))
    _s_out(out)


# ---------- exponencial por 2 puntos ----------

def _s_expo_2p():
    print("y = a*b^x por (x1,y1) y (x2,y2)")
    x1 = _s_float(_s_pide("x1 = "))
    y1 = _s_float(_s_pide("y1 = "))
    x2 = _s_float(_s_pide("x2 = "))
    y2 = _s_float(_s_pide("y2 = "))
    if x1 == x2 or y1 <= 0 or y2 <= 0:
        print("necesito x distintas y y > 0")
        return
    bb = (y2 / y1) ** (1 / (x2 - x1))
    aa = y1 / bb ** x1
    pc = (bb - 1) * 100
    _s_out(["b = (y2/y1)^(1/(x2-x1))",
            "b = " + _s_g(bb),
            "a = y1/b^x1 = " + _s_g(aa),
            "y = " + _s_g(aa) + "*(" + _s_g(bb) + ")^x",
            ("crece " if pc > 0 else "decae ") + _s_g(abs(pc))
            + "% por unidad de x"])


# ---------- polinomios (coeficientes de mayor a menor grado) ----------

_S_CERO = (0, 1)


def _s_ptxt(c, var="x"):
    """[2,-3,0,5] -> 2x^3 - 3x^2 + 5."""
    n = len(c) - 1
    out = ""
    for i in range(len(c)):
        a = c[i]
        if a[0] == 0:
            continue
        g = n - i
        mon = "" if g == 0 else (var if g == 1 else "{}^{}".format(var, g))
        if out == "":
            out = _s_sh(a) if g == 0 else _s_coef(a, mon)
        else:
            ab = (abs(a[0]), a[1])
            out += (" - " if a[0] < 0 else " + ") + (_s_sh(ab) if g == 0 else _s_coef(ab, mon))
    return out if out else "0"


def _s_limpia(c):
    """Quita ceros del frente (grado real)."""
    i = 0
    while i < len(c) - 1 and c[i][0] == 0:
        i += 1
    return c[i:]


def _s_ppide(texto):
    print(texto)
    print("coeficientes de mayor a menor;")
    print("pon 0 si falta: 2x^3-3x^2+5")
    print("-> 2 -3 0 5")
    return _s_limpia(_s_pide_lista("coeficientes: "))


def _s_horner(c, a):
    """Division sintetica entre (x - a): (cociente, residuo)."""
    b = [c[0]]
    for k in c[1:]:
        b.append(_s_add(k, _s_mul(b[-1], a)))
    return b[:-1], b[-1]


def _s_pdiv(n, d):
    """n / d con fracciones: (cociente, residuo)."""
    n = list(n)
    d = _s_limpia(d)
    if len(d) == 1 and d[0][0] == 0:
        raise ZeroDivisionError("division entre 0")
    q = []
    while len(n) >= len(d):
        f = _s_div(n[0], d[0])
        q.append(f)
        for i in range(len(d)):
            n[i] = _s_sub(n[i], _s_mul(f, d[i]))
        n = n[1:]
    if not q:
        q = [_S_CERO]
    return q, _s_limpia(n if n else [_S_CERO])


def _s_pmul(a, b):
    r = [_S_CERO] * (len(a) + len(b) - 1)
    for i in range(len(a)):
        for j in range(len(b)):
            r[i + j] = _s_add(r[i + j], _s_mul(a[i], b[j]))
    return r


def _s_divisores(n):
    n = abs(n)
    ds = []
    i = 1
    while i * i <= n:
        if n % i == 0:
            ds.append(i)
            if i * i != n:
                ds.append(n // i)
        i += 1
    return ds


def _s_mcm(a, b):
    return a // _s_mcd(a, b) * b


def _s_p_eval():
    c = _s_ppide("p(x) =")
    a = _s_pide("a (para p(a)) = ")
    q, r = _s_horner(c, a)
    out = ["p(x) = " + _s_ptxt(c)]
    # Horner paso a paso
    acc = c[0]
    out.append("Horner: empiezo con " + _s_sh(acc))
    for k in c[1:]:
        nuevo = _s_add(k, _s_mul(acc, a))
        kk = _s_sh(k) if k[0] >= 0 else "(" + _s_sh(k) + ")"
        aa = _s_sh(a) if a[0] >= 0 else "(" + _s_sh(a) + ")"
        out.append("{}*{} + {} = {}".format(_s_sh(acc), aa, kk, _s_sh(nuevo)))
        acc = nuevo
    out.append("p(" + _s_sh(a) + ") = " + _s_txt(r))
    out.append("residuo de p(x)/(x - " + _s_sh(a) + ") = " + _s_sh(r))
    out.append("(teorema del residuo)")
    if r[0] == 0:
        out.append("p(a) = 0: (x - " + _s_sh(a) + ") SI es factor")
        out.append("y x = " + _s_sh(a) + " es raiz/x-intercept")
    else:
        out.append("p(a) != 0: (x - " + _s_sh(a) + ") NO es factor")
    _s_out(out)


def _s_p_sintetica():
    c = _s_ppide("p(x) =")
    a = _s_pide("divido entre x - a, a = ")
    q, r = _s_horner(c, a)
    fila2 = []
    acc = c[0]
    for k in c[1:]:
        fila2.append(_s_mul(acc, a))
        acc = _s_add(k, _s_mul(acc, a))
    out = ["(" + _s_ptxt(c) + ")/(" + _s_ptxt([(1, 1), _s_neg(a)]) + ")",
           "division sintetica con " + _s_sh(a) + ":",
           "  " + "  ".join([_s_sh(k) for k in c]),
           "    " + "  ".join([_s_sh(k) for k in fila2]),
           "  " + "  ".join([_s_sh(k) for k in q]) + " | " + _s_sh(r),
           "cociente = " + _s_ptxt(q),
           "residuo = " + _s_sh(r)]
    if r[0] == 0:
        out.append("exacta: p(x) = (" + _s_ptxt([(1, 1), _s_neg(a)]) + ")(" + _s_ptxt(q) + ")")
    else:
        out.append("p(x) = (x - a)*cociente + residuo")
    _s_out(out)


def _s_p_division():
    n = _s_ppide("dividendo p(x) =")
    d = _s_ppide("divisor d(x) =")
    q, r = _s_pdiv(n, d)
    _s_out(["(" + _s_ptxt(n) + ")/(" + _s_ptxt(d) + ")",
            "cociente = " + _s_ptxt(q),
            "residuo = " + _s_ptxt(r),
            "p = d*cociente + residuo",
            "d es factor" if r == [_S_CERO] else "d NO es factor (residuo != 0)"])


def _s_p_multiplica():
    a = _s_ppide("primer polinomio =")
    b = _s_ppide("segundo polinomio =")
    print("1 multiplicar  2 sumar  3 restar (1o - 2o)")
    op = input("? ").strip()
    if op == "2" or op == "3":
        n = max(len(a), len(b))
        a2 = [_S_CERO] * (n - len(a)) + a
        b2 = [_S_CERO] * (n - len(b)) + b
        r = [_s_add(a2[i], b2[i]) if op == "2" else _s_sub(a2[i], b2[i]) for i in range(n)]
        r = _s_limpia(r)
        signo = ") + (" if op == "2" else ") - ("
    else:
        r = _s_pmul(a, b)
        signo = ")("
    _s_out(["(" + _s_ptxt(a) + signo + _s_ptxt(b) + ")",
            "= " + _s_ptxt(r),
            "grado " + str(len(r) - 1)
            + ", coef. principal " + _s_sh(r[0])])


def _s_p_raices():
    c = _s_ppide("p(x) = 0 con")
    if len(c) < 2:
        print("p es constante: no tiene raices")
        return
    out = ["p(x) = " + _s_ptxt(c)]
    # a enteros
    L = 1
    for a in c:
        L = _s_mcm(L, a[1])
    ent = [a[0] * (L // a[1]) for a in c]
    g = 0
    for v in ent:
        g = _s_mcd(abs(v), g)
    ent = [v // g for v in ent]
    if ent[0] < 0:
        ent = [-v for v in ent]
    pol = [(v, 1) for v in ent]
    lider = c[0]
    raices = []
    while len(pol) > 1 and pol[-1][0] == 0:
        raices.append(_S_CERO)
        pol = pol[:-1]
    if len(pol) > 1:
        cands = []
        for pp in _s_divisores(pol[-1][0]):
            for qq in _s_divisores(pol[0][0]):
                for sg in (1, -1):
                    f = _s_fr(sg * pp, qq)
                    if f not in cands:
                        cands.append(f)
        cands.sort(key=_s_float)
        for f in cands:
            while len(pol) > 1:
                q, r = _s_horner(pol, f)
                if r[0] != 0:
                    break
                raices.append(f)
                pol = q
    out.append("raices racionales (p/q):")
    if raices:
        vistos = []
        for r in raices:
            if r not in vistos:
                vistos.append(r)
                m = raices.count(r)
                out.append("x = " + _s_txt(r) + ("  (multiplicidad " + str(m) + ")" if m > 1 else ""))
    else:
        out.append("ninguna")
    resto = []
    if len(pol) == 3:
        D, xs, extra = _s_raices_txt(pol[0], pol[1], pol[2])
        out.append("queda " + _s_ptxt(pol) + " = 0")
        out.append("D = " + _s_sh(D))
        if D[0] < 0:
            out.append("D < 0: sin mas raices reales")
        out += extra
        for x in xs:
            out.append("x = " + _s_num_txt(x))
        resto = pol
    elif len(pol) == 2:
        x = _s_div(_s_neg(pol[1]), pol[0])
        raices.append(x)
        out.append("x = " + _s_txt(x))
    elif len(pol) > 3:
        out.append("queda " + _s_ptxt(pol) + " (grado " + str(len(pol) - 1) + ")")
        out.append("sin raices racionales;")
        reales = _s_reales_num(pol)
        if reales:
            out.append("reales aprox: " + ", ".join([_s_g(x) for x in reales]))
        else:
            out.append("no encontre raices reales")
        resto = pol
    # forma factorizada: p = K * prod(q x - p) * resto
    den = resto[0] if resto else (1, 1)
    for r in raices:
        den = _s_mul(den, (r[1], 1))
    K = _s_div(lider, den)
    fac = "" if K == (1, 1) else ("-" if K == (-1, 1) else (_s_sh(K) if K[1] == 1 else "(" + _s_sh(K) + ")"))
    vistos = []
    for r in raices:
        if r in vistos:
            continue
        vistos.append(r)
        f = _s_menos_var("x", r) if r[1] == 1 else "(" + _s_ptxt([(r[1], 1), (-r[0], 1)]) + ")"
        if f == "x" and raices.count(r) > 1:
            f = "x"
        m = raices.count(r)
        fac += f + ("^" + str(m) if m > 1 else "")
    if resto:
        fac += "(" + _s_ptxt(resto) + ")"
    if raices:
        out.append("factorizado: " + fac)
    out.append("x-intercepts = raices reales")
    _s_out(out)


def _s_reales_num(pol):
    """Raices reales aprox de un polinomio por cambios de signo."""
    c = [_s_float(a) for a in pol]
    B = 1 + max([abs(a / c[0]) for a in c[1:]])

    def ev(x):
        v = 0.0
        for a in c:
            v = v * x + a
        return v
    n = 4000
    xs = []
    x0 = -B
    f0 = ev(x0)
    for i in range(1, n + 1):
        x1 = -B + 2 * B * i / n
        f1 = ev(x1)
        if f0 == 0:
            xs.append(x0)
        elif f0 * f1 < 0:
            a, b = x0, x1
            fa = f0
            for _ in range(60):
                m = (a + b) / 2
                fm = ev(m)
                if fa * fm <= 0:
                    b = m
                else:
                    a, fa = m, fm
            xs.append((a + b) / 2)
        x0, f0 = x1, f1
    return xs


def _s_p_vieta():
    c = _s_ppide("p(x) = 0 con")
    n = len(c) - 1
    if n < 1:
        print("necesito grado >= 1")
        return
    suma = _s_div(_s_neg(c[1]), c[0])
    prod = _s_div(c[-1], c[0])
    if n % 2:
        prod = _s_neg(prod)
    _s_out(["grado " + str(n) + ": " + str(n) + " raices (contando",
            "complejas y repetidas)",
            "suma = -(2o coef)/(1er coef)",
            "     = " + _s_txt(suma),
            "producto = (-1)^n*(ultimo)/(1o)",
            "     = " + _s_txt(prod)])


def _s_polinomios():
    print("1 evaluar p(a) / residuo / factor")
    print("2 dividir entre (x - a)")
    print("3 dividir entre otro polinomio")
    print("4 multiplicar / sumar / restar")
    print("5 raices y factorizar")
    print("6 suma y producto de raices")
    op = input("? ").strip()
    fns = {"1": _s_p_eval, "2": _s_p_sintetica, "3": _s_p_division,
           "4": _s_p_multiplica, "5": _s_p_raices, "6": _s_p_vieta}
    if op in fns:
        fns[op]()
    else:
        print("opcion no valida")


# ---------- ecuaciones con letras (multi-variable) ----------

_S_FUNC = ("sqrt", "sin", "cos", "tan", "abs", "ln", "log", "exp")


def _s_expr(t):
    """Texto tecleado -> (expresion de Python, nombres de variables).
    2x -> 2*x, 3(x+1) -> 3*(x+1), ab -> a*b, b1 queda junto, ^ -> **."""
    for a, b in (("\u2212", "-"), ("^", "**"), ("\u03c0", "pi")):
        t = t.replace(a, b)
    toks = []
    i = 0
    n = len(t)
    while i < n:
        ch = t[i]
        if ch == " ":
            i += 1
            continue
        if ch in "0123456789.":
            j = i
            while j < n and t[j] in "0123456789.":
                j += 1
            toks.append(("n", t[i:j]))
            i = j
        elif ("a" <= ch <= "z") or ("A" <= ch <= "Z"):
            j = i
            while j < n and (("a" <= t[j] <= "z") or ("A" <= t[j] <= "Z")):
                j += 1
            letras = t[i:j]
            k = j
            while k < n and t[k] in "0123456789":
                k += 1
            dig = t[j:k]
            if letras in _S_FUNC and dig == "":
                toks.append(("f", letras))
            else:
                q = 0
                while q < len(letras):
                    ult = q == len(letras) - 1
                    if letras[q:q + 2] == "pi" and not (q + 2 == len(letras) and dig):
                        toks.append(("v", "pi"))
                        q += 2
                        continue
                    toks.append(("v", letras[q] + (dig if ult else "")))
                    q += 1
            i = k
        elif ch in "+-*/()":
            if ch == "*" and i + 1 < n and t[i + 1] == "*":
                toks.append(("o", "**"))
                i += 2
            else:
                toks.append(("o", ch))
                i += 1
        else:
            raise ValueError("no entiendo '" + ch + "'")
    out = []
    nombres = []
    prev = None
    for tk in toks:
        if prev is not None:
            pa = prev[0] in ("n", "v") or prev == ("o", ")")
            nx = tk[0] in ("n", "v", "f") or tk == ("o", "(")
            if pa and nx:
                out.append("*")
        if tk[0] == "f":
            out.append({"ln": "log"}.get(tk[1], tk[1]))
        else:
            out.append(tk[1])
        if tk[0] == "v" and tk[1] != "pi" and tk[1] not in nombres:
            nombres.append(tk[1])
        prev = tk
    return "".join(out), nombres


def _s_ecuacion(texto):
    """Pide 'lado = lado' y regresa (funcion f(**vars) = izq - der, vars)."""
    while True:
        e = _sat_entrada(texto).strip()
        if e.count("=") != 1:
            print("escribe UNA igualdad: izq = der")
            continue
        izq, der = e.split("=")
        try:
            pi_, n1 = _s_expr(izq)
            pd_, n2 = _s_expr(der)
            nombres = n1 + [v for v in n2 if v not in n1]
            src = "lambda " + ",".join(nombres) + ": (" + pi_ + ")-(" + pd_ + ")"
            f = eval(src, {"sqrt": sqrt, "sin": sin, "cos": cos, "tan": tan,
                           "abs": abs, "log": log, "exp": exp, "pi": pi})
            return f, nombres, e
        except Exception as err:
            print("no la entendi: " + str(err))


def _s_func(texto, nombres):
    """Expresion en terminos de 'nombres' -> funcion, o None."""
    try:
        pe, ns = _s_expr(texto)
        for v in ns:
            if v not in nombres:
                print("'" + v + "' no esta en la ecuacion")
                return None
        return eval("lambda " + ",".join(nombres) + ": " + pe,
                    {"sqrt": sqrt, "sin": sin, "cos": cos, "tan": tan,
                     "abs": abs, "log": log, "exp": exp, "pi": pi})
    except Exception as err:
        print("no la entendi: " + str(err))
        return None


def _s_frac_aprox(x):
    """2.444444 -> '22/9' si es una fraccion sencilla, si no ''."""
    if abs(x - round(x)) < 1e-9 * max(1.0, abs(x)):
        return str(int(round(x)))
    h0, h1, k0, k1 = 0, 1, 1, 0
    v = x
    for _ in range(20):
        a = int(v // 1)
        h0, h1 = h1, a * h1 + h0
        k0, k1 = k1, a * k1 + k0
        if k1 > 2000:
            return ""
        if abs(x - h1 / k1) < 1e-9 * max(1.0, abs(x)):
            return "{}/{}".format(h1, k1) if k1 != 1 else str(h1)
        r = v - a
        if r == 0:
            break
        v = 1 / r
    return ""


def _s_num_fr(x):
    f = _s_frac_aprox(x)
    if f and "/" in f:
        return f + " = " + _s_g(x)
    return f if f else _s_g(x)


def _s_raices_1(g):
    """Raices reales de g(t) por cambios de signo en una malla amplia."""
    pts = [0.0]
    v = 1e-4
    while v < 1e6:
        pts.append(v)
        pts.append(-v)
        v *= 1.05
    pts.sort()
    vals = []
    for t in pts:
        try:
            vals.append(g(t))
        except Exception:
            vals.append(None)
    rs = []
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        fa, fb = vals[i], vals[i + 1]
        if fa is None or fb is None:
            continue
        if fa == 0:
            rs.append(a)
            continue
        if fa * fb < 0:
            for _ in range(80):
                m = (a + b) / 2
                try:
                    fm = g(m)
                except Exception:
                    break
                if fa * fm <= 0:
                    b = m
                else:
                    a, fa = m, fm
            # salto (asintota) y no raiz: |g| grande junto al corte
            try:
                if abs(g((a + b) / 2)) > 1e-6 * (1 + abs(fb) + abs(vals[i])):
                    continue
            except Exception:
                continue
            rs.append((a + b) / 2)
    limpio = []
    for r in rs:
        if not limpio or abs(r - limpio[-1]) > 1e-7 * max(1.0, abs(r)):
            limpio.append(r)
    return [0.0 if abs(r) < 1e-12 else r for r in limpio]


def _s_gauss(A, b):
    """Resuelve A x = b (pequeno) por eliminacion; None si es singular."""
    n = len(b)
    M = [list(A[i]) + [b[i]] for i in range(n)]
    for c in range(n):
        piv = max(range(c, n), key=lambda r: abs(M[r][c]))
        if abs(M[piv][c]) < 1e-14:
            return None
        M[c], M[piv] = M[piv], M[c]
        for r in range(n):
            if r != c:
                f = M[r][c] / M[c][c]
                for k in range(c, n + 1):
                    M[r][k] -= f * M[c][k]
    return [M[i][n] / M[i][i] for i in range(n)]


def _s_identidad():
    print("ecuacion que vale para TODA x")
    print("con constantes que no sabes,")
    print("ej: a/(x-5) + b/(x+4) =")
    print("    (3x+7)/((x-5)(x+4))")
    f, nombres, e = _s_ecuacion("identidad: ")
    if "x" not in nombres:
        print("necesito la variable x")
        return
    cons = [v for v in nombres if v != "x"]
    if not cons:
        print("no hay constantes que hallar")
        return
    k = len(cons)
    ix = nombres.index("x")
    xs = []
    for x in (6.3, 7.1, 8.7, 9.2, 10.9, -3.7, 2.45, 13.1, -7.9, 0.37, 4.6, -1.3):
        xs.append(x)
    m = max(2 * k + 3, 6)
    xs = xs[:m]

    def res(th):
        r = []
        for x in xs:
            args = []
            j = 0
            for v in nombres:
                if v == "x":
                    args.append(x)
                else:
                    args.append(th[j])
                    j += 1
            r.append(f(*args))
        return r
    sols = []
    for ini in (1.0, 0.5, -1.0, 2.0, -0.5, 3.0, 0.1, -2.0):
        th = [ini + 0.01 * i for i in range(k)]
        try:
            for _ in range(60):
                r = res(th)
                J = []
                for j in range(k):
                    h = 1e-6 * max(1.0, abs(th[j]))
                    t2 = list(th)
                    t2[j] += h
                    r2 = res(t2)
                    J.append([(r2[i] - r[i]) / h for i in range(len(r))])
                A = [[sum([J[a][i] * J[b][i] for i in range(len(r))]) for b in range(k)] for a in range(k)]
                g = [-sum([J[a][i] * r[i] for i in range(len(r))]) for a in range(k)]
                d = _s_gauss(A, g)
                if d is None:
                    break
                th = [th[j] + d[j] for j in range(k)]
                if max([abs(v) for v in d]) < 1e-12 * max([1.0] + [abs(v) for v in th]):
                    break
            r = res(th)
            esc = 1.0 + max([abs(v) for v in th])
            if max([abs(v) for v in r]) < 1e-8 * esc:
                nuevo = True
                for s0 in sols:
                    if max([abs(s0[j] - th[j]) for j in range(k)]) < 1e-6 * esc:
                        nuevo = False
                if nuevo:
                    sols.append(th)
        except Exception:
            pass
    out = ["identidad: " + e]
    if not sols:
        out.append("no encontre constantes que")
        out.append("la cumplan para toda x")
        _s_out(out)
        return
    if len(sols) > 1:
        out.append(str(len(sols)) + " soluciones:")
    for th in sols:
        for j in range(k):
            out.append(cons[j] + " = " + _s_num_fr(th[j]))
        if len(sols) > 1:
            out.append("--")
    out.append("(como la regresion ~ de Desmos)")
    _s_out(out)
    while True:
        t = _sat_entrada("calcula algo (ej a*b), enter=no: ",
                         "q" in cons).strip()
        if t == "":
            return
        fn = _s_func(t, cons)
        if fn is None:
            continue
        for th in sols:
            try:
                print(t + " = " + _s_num_fr(fn(*th)))
            except Exception as err:
                print("no se pudo: " + str(err))


def _s_despeja():
    print("ecuacion con letras: das todas")
    print("menos una y la despejo")
    print("ej: P = 2l + 2w")
    f, nombres, e = _s_ecuacion("ecuacion: ")
    if not nombres:
        print("no hay letras")
        return
    print("letras: " + ", ".join(nombres))
    while True:
        obj = _sat_entrada("cual despejo? ", "q" in nombres).strip()
        if obj in nombres:
            break
        print("escribe una de: " + ", ".join(nombres))
    val = {}
    for v in nombres:
        if v != obj:
            val[v] = _s_float(_s_pide(v + " = "))
    i = nombres.index(obj)

    def g(t):
        args = [val[v] if v != obj else t for v in nombres]
        return f(*args)
    rs = _s_raices_1(g)
    out = [e]
    for v in nombres:
        if v != obj:
            out.append(v + " = " + _s_g(val[v]))
    if not rs:
        out.append("no encontre " + obj + " real")
    for r in rs:
        out.append(obj + " = " + _s_num_fr(r))
    _s_out(out)


def _s_terminos():
    print("'in terms of': checa cual opcion")
    print("despeja bien una letra")
    f, nombres, e = _s_ecuacion("ecuacion: ")
    print("letras: " + ", ".join(nombres))
    while True:
        obj = _sat_entrada("cual despejan? ", "q" in nombres).strip()
        if obj in nombres:
            break
        print("escribe una de: " + ", ".join(nombres))
    otros = [v for v in nombres if v != obj]
    juegos = []
    for base in ((1.7, 2.3, 3.1, 0.6, 4.4, 1.3), (2.9, 0.8, 1.9, 3.7, 2.2, 5.1)):
        val = {}
        for q in range(len(otros)):
            val[otros[q]] = base[q % len(base)] + 0.37 * (q // len(base))

        def g(t, val=val):
            return f(*[val[v] if v != obj else t for v in nombres])
        juegos.append((val, _s_raices_1(g)))
    print("escribe cada opcion en terminos")
    print("de " + ", ".join(otros) + " (enter = salir)")
    while True:
        t = _sat_entrada(obj + " = ", "q" in otros).strip()
        if t == "":
            return
        fn = _s_func(t, otros)
        if fn is None:
            continue
        ok = True
        for val, rs in juegos:
            try:
                y = fn(*[val[v] for v in otros])
            except Exception:
                ok = False
                break
            if not [r for r in rs if abs(r - y) < 1e-6 * max(1.0, abs(r))]:
                ok = False
        print("SI es correcta" if ok else "NO es correcta")


def _s_letras():
    print("1 identidad para toda x:")
    print("  hallar constantes (a, b...)")
    print("2 despejar una letra con valores")
    print("3 checar opciones 'in terms of'")
    op = input("? ").strip()
    if op == "1":
        _s_identidad()
    elif op == "2":
        _s_despeja()
    elif op == "3":
        _s_terminos()
    else:
        print("opcion no valida")


# ---------- triangulos especiales ----------

def _s_kraiz(k, r):
    """k*sqrt(r) simplificado (k fraccion, r entero >= 1): texto."""
    t, u = _s_radical(r) if r > 1 else (1, 1)
    c = _s_mul(k, (t, 1))
    val = _s_float(c) * sqrt(u)
    if u == 1:
        return _s_txt(c)
    if c == (1, 1):
        s = "sqrt({})".format(u)
    elif c[1] == 1:
        s = "{}*sqrt({})".format(c[0], u)
    elif c[0] == 1:
        s = "sqrt({})/{}".format(u, c[1])
    else:
        s = "{}*sqrt({})/{}".format(c[0], u, c[1])
    return "{} = {}".format(s, _s_g(val))


def _s_especiales():
    print("1 45-45-90:  x, x, x*sqrt(2)")
    print("2 30-60-90:  x, x*sqrt(3), 2x")
    tipo = input("? ").strip()
    if tipo == "1":
        print("que lado tienes?")
        print("1 un cateto (leg)  2 la hipotenusa")
    elif tipo == "2":
        print("que lado tienes?")
        print("1 cateto corto (frente a 30)")
        print("2 cateto largo (frente a 60)")
        print("3 hipotenusa (frente a 90)")
    else:
        print("opcion no valida")
        return
    lado = input("? ").strip()
    print("lado = k*sqrt(r)  (ej 4*sqrt(3):")
    print("k = 4, r = 3; sin raiz: r = 1)")
    k = _s_pide("k = ")
    r = _s_pide("r (enter = 1) = ", (1, 1))
    if r[1] != 1 or r[0] < 1:
        print("r debe ser entero >= 1")
        return
    r = r[0]
    out = []
    if tipo == "1":
        if lado == "2":
            # cateto = h/sqrt(2) = h*sqrt(2)/2
            cat = _s_kraiz(_s_div(k, (2, 1)), 2 * r)
            hip = _s_kraiz(k, r)
            out.append("cateto = hip/sqrt(2) = hip*sqrt(2)/2")
        else:
            cat = _s_kraiz(k, r)
            hip = _s_kraiz(k, 2 * r)
            out.append("hip = cateto*sqrt(2)")
        out.append("catetos (legs) = " + cat)
        out.append("hipotenusa = " + hip)
        out.append("angulos: 45, 45, 90")
    else:
        if lado == "1":
            corto = (k, r)
            out.append("largo = corto*sqrt(3), hip = 2*corto")
        elif lado == "2":
            corto = (_s_div(k, (3, 1)), 3 * r)
            out.append("corto = largo/sqrt(3) = largo*sqrt(3)/3")
        else:
            corto = (_s_div(k, (2, 1)), r)
            out.append("corto = hip/2")
        kc, rc = corto
        out.append("corto (frente a 30) = " + _s_kraiz(kc, rc))
        out.append("largo (frente a 60) = " + _s_kraiz(kc, 3 * rc))
        out.append("hipotenusa = " + _s_kraiz(_s_mul((2, 1), kc), rc))
        out.append("sin 30 = cos 60 = 1/2")
        out.append("sin 60 = cos 30 = sqrt(3)/2")
    out.append("TIP: el lado mas chico va")
    out.append("frente al angulo mas chico")
    _s_out(out)


# ---------- semejanza: altura a la hipotenusa y escala ----------

_S_NOSE = (-1, 1)


def _s_largo_txt(v):
    """Largo con raiz exacta si su cuadrado es racional sencillo."""
    f = _s_frac_aprox(v * v)
    if f:
        if "/" in f:
            num, den = f.split("/")
            return _s_raiz_txt(_s_fr(int(num), int(den)))
        return _s_raiz_txt((int(f), 1))
    return _s_g(v)


def _s_pide_num(texto):
    """Numero o cuenta con raiz: 8, 7/2, 6sqrt(13). Enter = None."""
    while True:
        t = _s_cola(_sat_entrada(texto))
        if t == "":
            return None
        try:
            return _s_float(_s_lee(t))
        except Exception:
            pass
        try:
            pe, ns = _s_expr(t)
            if not ns:
                return float(eval(pe, {"sqrt": sqrt, "pi": pi}))
        except Exception:
            pass
        print("no entendi. ej: 8, 7/2, 6sqrt(13)")
        print("(q = regresar al menu)")


def _s_altura_hip():
    print("triangulo ABC con angulo recto")
    print("en C; la altura CD cae en AB.")
    print("AD junto a A, DB junto a B;")
    print("AC cateto de A, BC cateto de B")
    print("da 2 datos (enter = no se)")
    print("con raiz: 6sqrt(13)")
    nombres = ["AD", "DB", "CD", "AC", "BC", "AB"]
    v = {}
    for n in nombres:
        x = _s_pide_num(n + " = ")
        if x is not None:
            if x <= 0:
                print("los lados son > 0")
                return
            v[n] = x
    if len(v) != 2:
        print("necesito exactamente 2 datos")
        return
    g = v.get
    pq = []
    try:
        if "AD" in v and "DB" in v:
            pq = [(g("AD"), g("DB"))]
        elif "AD" in v and "CD" in v:
            pq = [(g("AD"), g("CD") ** 2 / g("AD"))]
        elif "DB" in v and "CD" in v:
            pq = [(g("CD") ** 2 / g("DB"), g("DB"))]
        elif "AD" in v and "AB" in v:
            pq = [(g("AD"), g("AB") - g("AD"))]
        elif "DB" in v and "AB" in v:
            pq = [(g("AB") - g("DB"), g("DB"))]
        elif "AD" in v and "AC" in v:
            c = g("AC") ** 2 / g("AD")
            pq = [(g("AD"), c - g("AD"))]
        elif "DB" in v and "BC" in v:
            c = g("BC") ** 2 / g("DB")
            pq = [(c - g("DB"), g("DB"))]
        elif "AD" in v and "BC" in v:
            p = g("AD")
            q = (-p + sqrt(p * p + 4 * g("BC") ** 2)) / 2
            pq = [(p, q)]
        elif "DB" in v and "AC" in v:
            q = g("DB")
            p = (-q + sqrt(q * q + 4 * g("AC") ** 2)) / 2
            pq = [(p, q)]
        elif "CD" in v and "AB" in v:
            c, h = g("AB"), g("CD")
            dd = c * c - 4 * h * h
            if dd < 0:
                print("imposible: CD > AB/2")
                return
            p1 = (c - sqrt(dd)) / 2
            pq = [(p1, c - p1)]
            if dd > 0:
                pq.append((c - p1, p1))
        elif "AC" in v and "BC" in v:
            c = sqrt(g("AC") ** 2 + g("BC") ** 2)
            pq = [(g("AC") ** 2 / c, g("BC") ** 2 / c)]
        elif "AC" in v and "AB" in v:
            p = g("AC") ** 2 / g("AB")
            pq = [(p, g("AB") - p)]
        elif "BC" in v and "AB" in v:
            q = g("BC") ** 2 / g("AB")
            pq = [(g("AB") - q, q)]
        elif "CD" in v and "BC" in v:
            q = sqrt(g("BC") ** 2 - g("CD") ** 2)
            pq = [(g("CD") ** 2 / q, q)]
        elif "CD" in v and "AC" in v:
            p = sqrt(g("AC") ** 2 - g("CD") ** 2)
            pq = [(p, g("CD") ** 2 / p)]
    except (ValueError, ZeroDivisionError):
        print("imposible con esos datos")
        return
    out = ["triangulos semejantes:",
           "ACD ~ CBD ~ ABC",
           "CD^2 = AD*DB  (media geometrica)",
           "CD = AC*BC/AB  (cateto*cateto/hip)",
           "AC^2 = AD*AB,  BC^2 = DB*AB",
           "AD/CD = CD/DB"]
    for p, q in pq:
        if p <= 0 or q <= 0:
            out.append("imposible con esos datos")
            continue
        c = p + q
        if len(pq) > 1:
            out.append("-- si AD = " + _s_largo_txt(p).split(" = ")[0] + ":")
        out.append("AD = " + _s_largo_txt(p))
        out.append("DB = " + _s_largo_txt(q))
        out.append("CD = " + _s_largo_txt(sqrt(p * q)))
        out.append("AB = " + _s_largo_txt(c))
        out.append("AC = " + _s_largo_txt(sqrt(p * c)))
        out.append("BC = " + _s_largo_txt(sqrt(q * c)))
    _s_out(out)


def _s_semejantes():
    print("triangulos (o figuras) semejantes")
    print("lado de la figura 1 y el que le")
    print("corresponde en la figura 2:")
    a1 = _s_pide("lado en 1 = ")
    a2 = _s_pide("su par en 2 = ")
    if a1[0] == 0:
        print("el lado no puede ser 0")
        return
    k = _s_div(a2, a1)
    out = ["escala k = fig2/fig1 = " + _s_txt(k),
           "areas: k^2 = " + _s_txt(_s_mul(k, k)),
           "volumenes: k^3 = " + _s_txt(_s_mul(k, _s_mul(k, k))),
           "los angulos NO cambian"]
    _s_out(out)
    while True:
        print("otro lado de la figura 1")
        t = _sat_entrada("(enter = salir) = ").strip()
        if t == "":
            return
        try:
            b1 = _s_lee(t)
        except Exception:
            print("no entendi. ej: 3, 7/2")
            continue
        print("en la figura 2: " + _s_txt(_s_mul(b1, k)))


def _s_semejanza():
    print("1 altura a la hipotenusa")
    print("  (AD, DB, CD, catetos)")
    print("2 semejantes: escala y lados")
    op = input("? ").strip()
    if op == "1":
        _s_altura_hip()
    elif op == "2":
        _s_semejantes()
    else:
        print("opcion no valida")


# ---------- menu ----------

def sat():
    print("")
    print("Tu CAS NO entra al SAT: esto es")
    print("para estudiar. Examen = Desmos.")
    print("q en cualquier dato = menu")
    while True:
        print("")
        print("== SAT MATH (estudio) ==")
        print(" 1 formulas y tips por dominio")
        print(" 2 recta por 2 puntos")
        print(" 3 sistema 2x2")
        print(" 4 sistema con k (0/infinitas)")
        print(" 5 cuadratica (D, vertice)")
        print(" 6 discriminante: k, recta-parab")
        print(" 7 porcentajes")
        print(" 8 estadistica de una lista")
        print(" 9 circulo / arco y sector")
        print("10 exponencial (crece o decae)")
        print("11 exponencial por 2 puntos")
        print("12 triangulo rectangulo y trig")
        print("13 valor absoluto |ax+b| = c")
        print("14 polinomios")
        print("15 ecuaciones con letras")
        print("16 triangulos especiales")
        print("17 semejanza / altura a hipot.")
        print(" 0 salir")
        op = input("? ").strip()
        if op == "0" or op == "" or op == "q":
            return
        fns = {"2": _s_recta, "3": _s_sistema, "4": _s_sistema_k,
               "5": _s_cuad, "6": _s_discr, "7": _s_porc,
               "8": _s_estad, "9": _s_circulo, "10": _s_expo,
               "11": _s_expo_2p, "12": _s_triang, "13": _s_absoluto,
               "14": _s_polinomios, "15": _s_letras,
               "16": _s_especiales, "17": _s_semejanza}
        try:
            if op == "1":
                _s_hojas()
                continue
            elif op in fns:
                fns[op]()
            else:
                print("escribe un numero del 0 al 17")
                continue
        except _SMenu:
            continue
        except Exception as err:
            print("Algo fallo: " + str(err))
        input("-- enter --")


# --- autorun ---
sat()
