# nspire-python

Programas de Python para la TI-Nspire CX II CAS: **Cálculo AP**, **IA**
(regresión lineal con gradiente descendente, curso de PrepaTEC) y
**Física** (FISICA, el solucionador de mecánica de Adrián).

## Los 4 archivos (`calculadora/`)

Cada uno se instala **solo**, sin PyLib ni otros archivos. Arrastra el
`.tns` a la calculadora (con [nspireconnect.ti.com](https://nspireconnect.ti.com)
en Chrome o el Student Software), ábrelo y córrelo (ctrl+R). Si lo corres
otra vez, el menú se vuelve a abrir.

| Archivo | Qué trae |
|---|---|
| `ap.tns` | Cálculo AP: análisis de funciones, máx/mín, derivadas, integrales y áreas, Riemann, límites, Euler, partícula v(t) y el formulario de fórmulas y tips |
| `ai.tns` | IA: resuelve el examen de regresión lineal paso a paso, con procedimiento y respuesta de cada inciso |
| `fisica.tns` | Física: FISICA v7 (unidades, vectores, gráficas, MRU, MRUA, derrape, caída libre, lanzamiento vertical, proyectil, planos, poleas, energía, trabajo y potencia) |
| `general.tns` | Los 3 juntos, con un menú principal para elegir materia |

```
== GENERAL: elige materia ==
1 Calculo AP
2 IA: regresion lineal
3 Fisica
0 salir
```

- Plan B si un `.tns` diera lata: pega el `.py` del mismo nombre en una
  página Python del Student Software y guarda el `.tns` desde ahí.
- **No edites `calculadora/` a mano.** Las piezas viven en `src/`
  (`calcpy`, `formulas`, `ap`, `ai`, `fisica`, `sat`); `python3 build.py`
  las junta, detecta choques de nombres entre piezas, f-strings y texto
  no ASCII, y genera los `.tns` con [Luna](https://github.com/ndless-nspire/Luna).
- `sh tests/correr.sh` regenera todo y corre las pruebas en Python de
  escritorio **y en MicroPython 1.11** (la versión de la Nspire) con el
  heap limitado a 1 MB (la calc tiene ~2 MB): 43 casos sobre `general`
  (incluye el examen de IA completo y el problema del malabarista de
  física) más los 4 archivos corridos sueltos. MicroPython 1.11 y Luna se
  compilan en `.tools/`, que no se sube al repo.

## Física: lanzamiento vertical completo (opción 8)

Con `v0` da de una vez altura máxima, tiempo de subida, tiempo de vuelo y
con qué rapidez regresa, y luego deja hacer más preguntas del mismo tiro:

```
1) donde esta en un tiempo t         (y y v, si sube o baja)
2) v a d metros ANTES de hmax        (subiendo y bajando)
3) v y t a una altura y              (- si es debajo de la salida)
4) t al piso X m DEBAJO              (tiempo total y v al llegar)
```

Con el malabarista (v0 = 7 m/s): hmax 2.497 m, tsub 0.714 s, tvuelo
1.427 s, y(1.2 s) = 1.337 m bajando, 2.801 m/s a 0.4 m de la cima,
1.616 s al piso 1.5 m abajo. Si la clave redondea tsub antes de
multiplicar (0.71 × 2 = 1.42 en vez de 1.43), el programa lo avisa.

## El menú de Cálculo AP (`ap`)

Eliges "punto más alto", "sumas de riemann", "partícula v(t)", etc.,
tecleas la función tal cual (`-x^2+4*x`, con `^` y `sen()` válidos) y te
da el resultado. La opción 9 abre el formulario.

## Formulario de repaso (dentro de `ap`)

Puras fórmulas y tips, cero cálculos: límites, derivadas y su tabla,
aplicaciones, integrales y TFC, aplicaciones de integral + EDO, temas de
BC (técnicas, paramétricas/polares, series) y tips del examen (cómo
justificar en los FRQ, redondeo a 3 decimales, sobre/subestimación de
Riemann, velocidad vs rapidez…). Navegas por tema y avanza por pantallas.

## SAT Math (`src/sat.py`, aparte)

No va en los 4 archivos. Es un programa suelto que ya no necesita nada
más: fórmulas y tips por dominio oficial del College Board y solvers con
fracciones exactas (recta, sistema 2x2, cuadrática, porcentajes,
estadística, círculo, exponencial, triángulo rectángulo). Ojo: la
[política del College Board](https://satsuite.collegeboard.org/sat/what-to-bring-do/calculator-policy)
no permite calculadoras CAS en el SAT (sí en los exámenes AP), así que es
para estudiar.

## IA PrepaTEC: gradiente descendente (`ai`)

Para el curso de IA: regresión lineal de una variable con gradiente
descendente, hecho para que **alguien sin experiencia** lo use. Corre `ai`
(o entra por la opción 2 de `general`) y sigue las preguntas.

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

Movimiento de partícula (también en `calcpy`):

| Función | Qué hace |
|---|---|
| `particula(v,t1,t2)` | desplazamiento, distancia total, dónde da vuelta |
| `desplazamiento`, `distancia`, `rapidez` | ∫v, ∫\|v\|, ¿la rapidez aumenta o disminuye? |

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

```

## Importante: Python ≠ CAS

El Python de la Nspire **no habla con el motor simbólico**. Todo esto es
numérico (respuestas decimales). Para álgebra exacta, `solve()`, derivadas
simbólicas o series de Taylor, usa la app Calculadora del CAS — para eso la
compraste. Estos programas brillan donde el CAS es lento de teclear: reportes
completos, sumas de Riemann con tabla, movimiento de partícula, física.

Los tests corren en cualquier Python de escritorio porque los módulos de TI
(`ti_plotlib`, `ti_system`) están protegidos con try/except.
