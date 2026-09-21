# nspire-python

Biblioteca de Python para la TI-Nspire CX II CAS: análisis numérico para
Cálculo AP (`calcpy.py`), herramientas de física (`fisica.py`), un menú
interactivo (`ap.py`) para no tener que aprenderse nada, un formulario
de repaso (`formulas.py`) con puras fórmulas y tips de AP Calc, y
`ia.py` para checar gradiente descendente del curso de IA de PrepaTEC.

## UN solo archivo para todo: `estudio.tns`

**`estudio.tns` trae las tres materias juntas** — Cálculo AP, IA y SAT
Math — en un solo programa. Arrástralo a la calculadora (con
[nspireconnect.ti.com](https://nspireconnect.ti.com) en Chrome o el
Student Software), ábrelo y córrelo (ctrl+R):

```
== ESTUDIO ==
1 Calculo AP: herramientas        (el menu ap)
2 Calculo AP: formulas y tips     (formulario)
3 IA: regresion lineal            (ia)
4 SAT Math (para estudiar)        (sat)
```

- Se genera con `python3 build.py`, que junta `calcpy`, `fisica`,
  `formulas`, `ap`, `ia` y `sat` en `estudio.py` (detecta choques de
  nombres entre módulos, f-strings y caracteres no ASCII) y lo convierte
  a `.tns` con [Luna](https://github.com/ndless-nspire/Luna). **No edites
  `estudio.py` a mano**: edita el módulo y vuelve a correr `build.py`.
- Si el `.tns` generado diera lata en la calc, plan B de siempre: pega
  `estudio.py` completo en una página Python del Student Software y
  guarda el `.tns` desde ahí.
- `sh tests/correr.sh` regenera todo y corre 37 pruebas en Python de
  escritorio **y en MicroPython 1.11** (la versión de la Nspire) con el
  heap limitado a 1 MB — la calc tiene ~2 MB. Incluye el examen de IA de
  punta a punta. Las herramientas (MicroPython 1.11 y Luna) se compilan
  en `.tools/`, que no se sube al repo.

## SAT Math (`sat.py`) — para estudiar, NO para el examen

**Las calculadoras CAS están prohibidas en el SAT** (College Board, desde
2025; la TI-Nspire CX II CAS aparece por nombre en la lista). El día del
examen se usa el Desmos integrado de Bluebook. Por eso `sat` es
herramienta de estudio y sus tips enseñan el camino Desmos:

- **Fórmulas y tips por dominio oficial** (College Board): Algebra ~35%,
  Advanced Math ~35%, Problem-Solving and Data Analysis ~15%, Geometry
  and Trigonometry ~15%, más una hoja de formato del examen, reglas del
  SPR y estrategia. Términos clave también en inglés, como vienen.
- **Solvers con fracciones exactas** (el SPR acepta `7/3`): recta por 2
  puntos, sistema 2x2 (una/ninguna/infinitas), cuadrática (raíces,
  radical simplificado, vértice, suma y producto, formas vertex y
  factored), porcentajes (cambios sucesivos, original), estadística de
  una lista, círculo (centro y radio desde la forma general, arco y
  sector), exponencial y triángulo rectángulo (30-60-90, 45-45-90).

## El menú de Cálculo AP

Corre el programa `ap` (o teclea `ap()` en el shell) y sale un menú en
español: eliges "punto más alto", "sube/cae vertical", "sumas de riemann",
etc., tecleas la función tal cual (`-x^2+4*x`, con `^` y `sen()` válidos)
y te da el resultado. Las funciones de abajo son para cuando quieras
usarlas directo en el shell.

## Formulario de repaso (`formulas.py`)

Puras fórmulas y tips, cero cálculos: límites, derivadas y su tabla,
aplicaciones, integrales y TFC, aplicaciones de integral + EDO, temas de
BC (técnicas, paramétricas/polares, series) y tips del examen (cómo
justificar en los FRQ, redondeo a 3 decimales, sobre/subestimación de
Riemann, velocidad vs rapidez…). Se abre desde `ap()` (opción 12) o
corriendo `formulas` directo; navegas por tema y avanza por pantallas.

## IA PrepaTEC: gradiente descendente (`ia.py`)

Para el curso de IA: regresión lineal de una variable con gradiente
descendente, hecho para que **alguien sin experiencia** lo use. Es un programa
aparte (no importa nada): córrelo y sigue las preguntas.

```
== IA: REGRESION LINEAL ==
1 Resolver examen paso a paso
2 Solo estimar calificacion
3 Conceptos para explicar
4 Ver o cambiar formulas
5 Instrucciones
0 Salir
```

**1 Resolver examen paso a paso** pregunta en el orden del examen y da cada
respuesta con el procedimiento para copiar:

| Pregunta | Qué da |
|---|---|
| Datos | x y y de la tabla, modelo, theta0 y theta1 iniciales y la hipótesis con ellos (`h(x) = 5 + 8x`) (alfa se pide antes del paso 3, porque en la guía viene en la pregunta de los nuevos parámetros) |
| Paso 1 (predicción y errores) | a) `h(x) = 5 + 8x` · b) `yh1 = 5 + 8(1) = 13`… · c) `e1 = 13 - 35 = -22`… y la tabla |
| Paso 2 (función de costo) | `J1 = 1/(2m) sum(yh - y)^2 = 1/(2(4))[(-22)^2 + …] = 1/8(484 + …) = 1/8(5346) = 668.25` y qué resume |
| Paso 3 (primera actualización) | `dJ/dtheta0 = 1/m sum(yh - y) = 1/4(-22 - 29 - 39 - 50) = 1/4(-140) = -35`, `dJ/dtheta1 = 1/m sum[(yh - y)x] = … = -99.25`, `theta0 := theta0 - alfa*dJ/dtheta0`, `theta0 = 5 - 0.02(-35) = 5 + 0.7 = 5.7` |
| Paso 4 (segunda iteración) | a) nuevas predicciones, tablas y J2 · b) `J1 - J2 = 668.25 - 465.23334375 = 203.01665625`, J disminuyó: sí mejoró · c) segunda actualización (6.28675, 11.63725), solo si tu examen la pide · opción de otra iteración |
| Paso 5 (transferencia, si tu examen la pide) | a) `yh = 6.287 + 11.637(5) = 6.287 + 58.185 = 64.472`: NO APROBADO (y aviso de extrapolación si x queda fuera de los datos) · b) tipo de problema con justificación |
| Revisión final | J1, J2, cuánto bajó, conclusión, hipótesis inicial y final (`h(x) = 5 + 8x` → `h(x) = 6.28675 + 11.63725x`) y theta finales |

**Procedimiento y respuesta numerados.** Cada pregunta e inciso sale como un
par con el mismo número (1a, 1b, 1c, 2, 3, 4a, 4b, 4c, 5a, 5b; si pides más
iteraciones se recorren solos). Cada pantalla que continúa un procedimiento
empieza con `-- sigue PROCEDIMIENTO 4a --`, y las tablas dicen para qué
número son (`Tabla (va con 1b y 1c)`, `Tabla auxiliar (para 2 y 3)`: e, e²
y e·x con sus sumas, las que se usan en J y en las derivadas):

```
-- PROCEDIMIENTO 1b: predicciones --
yh (yh1 va con el renglon 1):
yh1 = 5 + 8(1) = 13
...
RF(1b)= yh = 13, 21, 29, 37
```

La respuesta final de cada pregunta o inciso sale marcada con `RF(inciso)=`,
con el mismo número que su procedimiento y con la fórmula y a lo que es igual,
como se escribe en la hoja:

```
RF(3)= dJ/dtheta0 = 1/m sum(yh - y)
RF(3)= dJ/dtheta0 = -35
RF(3)= theta0 := theta0
     - alfa*dJ/dtheta0
RF(3)= theta0 = 5.7
```

**Fórmulas.** Cada fórmula aparece justo donde la usa el examen (el modelo en
los datos, `e` antes del paso 1, J antes del paso 2, las derivadas y la
actualización antes del paso 3, la regla de aprobado en el paso 5) con
`Igual a tu examen? enter=si, n=no`. Con `n` se escribe completa como viene en
la hoja: `y - yh`, `sum(yh - y)^2/(2m)`, `1/2m sum(e^2)`,
`theta + alfa*dJ/dtheta`… Como en papel: `sum(yh - y)^2` es la suma de los
cuadrados, `1/2m` y `1/2 m` se leen `1/(2m)`, y la tecla `^` de la Nspire (que
escribe `**`) también vale. Si algo no cuadra avisa con un mensaje claro
(`falta * en 'theta1x'`, `'x' va dentro de sum( )`, `la potencia debe ser un
numero`…). La opción 4 las muestra todas y `0` regresa a las del curso.

Las cuentas son **exactas** (fracciones con enteros largos, sin `eval`): no se
redondea nada. En pantalla salen hasta 12 cifras; si hay más, se cortan con
`...`. Lo de `[ ]` se usa con solo enter; si algo no se entiende, vuelve a
preguntar ese dato. Cada pantalla trae máximo 9 renglones y
`-- enter para seguir --`. En papel: `theta` = θ, `yh` = ŷ, `sum` = Σ.
Probado con MicroPython 1.11 (la versión de la Nspire) compilado en la Mac:
misma salida que Python de escritorio.

**Pasarlo a la calculadora:** el Student Software no manda `.py`, solo `.tns`.
Crea un documento, Insertar → Python → Nuevo (cualquier nombre), pega todo
`ia.py`, guarda el documento como `.tns` y arrastra ese `.tns` a la
calculadora. Ahí: abre el documento y corre el programa (ctrl+R).

## Qué hay

**calcpy** — cálculo:

| Función | Qué hace |
|---|---|
| `d(f,x)`, `d2(f,x)`, `dn(f,x,n)` | derivadas numéricas |
| `raices(f,a,b)`, `newton(f,x0)`, `resuelve(f,g,a,b)` | raíces y f(x)=g(x) |
| `criticos`, `extremos`, `maxmin`, `inflexion` | puntos críticos, máx/mín locales y absolutos, inflexión |
| `analiza(f,a,b)` | reporte completo de una función |
| `integra(f,a,b)` | integral definida (Simpson) |
| `riemann(f,a,b,n,modo)` | sumas de Riemann `izq/der/medio/trap` (como las pide el AP) |
| `promedio(f,a,b)` | valor promedio de la función |
| `area_entre(f,g,a,b)`, `longitud`, `solido_x` | área entre curvas, longitud de arco, sólidos de revolución |
| `euler(F,x0,y0,xf,n)` | método de Euler con tabla (BC) |
| `rk4(F,x0,y0,xf,n)` | Runge-Kutta 4 (más preciso que Euler) |
| `limite(f,x0,lado)` | límites numéricos, laterales incluidos |
| `tabla(f,a,b,n)`, `graf(f,a,b)` | tabla de valores y gráfica en pantalla |
| `guardar/leer` | intercambiar variables con las apps del documento |

**fisica** — física:

| Función | Qué hace |
|---|---|
| `particula(v,t1,t2)` | movimiento de partícula: desplazamiento, distancia total, vueltas |
| `desplazamiento`, `distancia`, `rapidez` | ∫v, ∫\|v\|, ¿la rapidez aumenta o disminuye? |
| `mrua(v0,v,a,t,x)` | dale 3 de las 5 variables y despeja las demás |
| `tiro(v0, ang, y0)` | tiro parabólico: h máx, tiempo de vuelo, alcance, impacto |
| `comp`, `vmag`, `vang`, `vsuma`, `vpunto` | vectores 2D (fuerzas, componentes) |
| `regresion(xs, ys)` | mínimos cuadrados para datos de laboratorio |

## Cómo pasar los módulos sueltos (si no quieres el archivo único)

Lo más fácil es `estudio.tns` (arriba). Si prefieres los módulos por
separado: Python vive **dentro de documentos .tns**, así que un `.py`
suelto no se puede mandar directo:

1. Abre **TI-Nspire CX Student Software** (o la versión de prueba).
2. Documento nuevo → **Insert → Add Python → New…** → nómbralo `calcpy`.
3. Pega el contenido de `calcpy.py`. Repite con páginas para `fisica`,
   `ap` y `formulas`.
4. Guarda el documento como `biblioteca.tns`.
5. Mándalo a la calculadora **a la carpeta `PyLib`** (Save to Handheld, o
   arrastrándolo en el panel de contenido). Lo que está en `PyLib` se puede
   importar desde cualquier documento.
6. `ia` no depende de nada: puede ir solo en su propio `ia.tns` (un
   programa Python llamado `ia`), dentro o fuera de `PyLib`.
7. Alternativa sin instalar nada: [nspireconnect.ti.com](https://nspireconnect.ti.com)
   (Chrome, por USB) transfiere el `.tns` ya creado.

En la calculadora, en cualquier programa de Python:

```python
from calcpy import *
from fisica import *
```

Si el import no encuentra el módulo, revisa que el documento esté en la
carpeta `PyLib` y que el OS sea 5.2 o más nuevo (Menu → Settings → Status).

## Ejemplos estilo AP

```python
# f(x) = x^3 - 3x en [-3, 3]: raices, extremos, inflexion, abs max/min
analiza(lambda x: x**3 - 3*x, -3, 3)

# suma trapezoidal con 4 subintervalos (pregunta clasica de tabla)
riemann(lambda x: x**2, 0, 1, 4, "trap")

# particula con v(t) = t^2 - 4 en [0, 3]
particula(lambda t: t*t - 4, 0, 3)
rapidez(lambda t: t*t - 4, 1)      # 'disminuye'

# area entre y = x^2 y y = x + 1
area_entre(lambda x: x**2, lambda x: x + 1, -2, 3)

# Euler con 4 pasos (BC)
euler(lambda x, y: x + y, 0, 1, 1, 4)

# caida libre: se suelta desde reposo, cae 20 m; ¿t y v?
mrua(v0=0, a=-9.81, x=-20)

# proyectil a 25 m/s y 40 grados desde 1.5 m de altura
tiro(25, 40, 1.5)
```

## Importante: Python ≠ CAS

El Python de la Nspire **no habla con el motor simbólico**. Todo esto es
numérico (respuestas decimales). Para álgebra exacta, `solve()`, derivadas
simbólicas o series de Taylor, usa la app Calculadora del CAS — para eso la
compraste. Este módulo brilla donde el CAS es lento de teclear: reportes
completos, sumas de Riemann con tabla, movimiento de partícula, física.

Los tests corren en cualquier Python de escritorio porque los módulos de TI
(`ti_plotlib`, `ti_system`) están protegidos con try/except.
