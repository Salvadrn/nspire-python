# nspire-python

Biblioteca de Python para la TI-Nspire CX II CAS: análisis numérico para
Cálculo AP (`calcpy.py`), herramientas de física (`fisica.py`), un menú
interactivo (`ap.py`) para no tener que aprenderse nada, un formulario
de repaso (`formulas.py`) con puras fórmulas y tips de AP Calc, y
`ia.py` para checar gradiente descendente del curso de IA de PrepaTEC.

## El único comando que necesitas

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

Regresión lineal de una variable con gradiente descendente batch. Es un
programa aparte (no importa nada): corre `ia` y sale el menú. Te pregunta lo
que cambia de examen a examen (datos, cuántos alumnos, θ iniciales, α,
iteraciones) y escribe **el procedimiento como va en el examen**: fórmula,
sustitución, operaciones y resultado.

**Fórmulas (todas editables).** Al elegir *Resolver* enseña juntas las
fórmulas que va a usar y pregunta `Iguales? enter = si / # = editar`. Si tu
examen trae otra, tecleas su número y la escribes tal cual (se aceptan
`+ - * / ^`, paréntesis, `8x`, `2m`; `t0`/`t1` = `theta0`/`theta1`). `0` vuelve
a las del curso; la opción 5 las muestra/edita en cualquier momento.

| # | Del curso | Variables que puede usar |
|---|---|---|
| 1 | `h(x) = theta0 + theta1*x` | theta0, theta1, x |
| 2 | `e = yh - y` | yh, y, x |
| 3 | `J = 1/(2m) sum(e^2)` (coef y algo) | coef: m · algo: e, yh, y, x |
| 4 | `dJ/dtheta0 = 1/m sum(e)` | igual que J |
| 5 | `dJ/dtheta1 = 1/m sum(e*x)` | igual que J |
| 6 | `theta := theta - alfa*dJ/dtheta` | theta, alfa, dJ/dtheta |
| 7 | `Aprobado si yh >= 70` | número |

**Así sale** (examen: x = 1,2,3,4; y = 35,50,68,87; θ0 = 5, θ1 = 8, α = 0.02):

```
== ITERACION 1: PREDICCION ==
h(x) = theta0 + theta1*x
h(x) = 5 + 8x
yh1 = 5 + 8(1) = 13
...
e1 = 13 - 35 = -22
...
-- FUNCION DE COSTO J1 --
J1 = 1/(2m) sum(e^2)
   = 1/(2(4))[(-22)^2 + (-29)^2 +
     (-39)^2 + (-50)^2]
   = 1/8(484 + 841 + 1521 + 2500)
   = 1/8(5346)
   = 668.25
(J resume el error de la hipotesis
 actual sobre los datos reales)
-- DERIVADAS (ITERACION 1) --
dJ/dtheta0 = 1/m sum(e)
    = 1/4(-22 - 29 - 39 - 50)
    = 1/4(-140)
    = -35
dJ/dtheta1 = 1/m sum(e*x)
    = 1/4[(-22)(1) + (-29)(2) +
     (-39)(3) + (-50)(4)]
    = 1/4(-22 - 58 - 117 - 200)
    = 1/4(-397)
    = -99.25
-- NUEVOS THETA (ITERACION 1) --
theta := theta - alfa*dJ/dtheta
theta0 = 5 - 0.02(-35) = 5.7
theta1 = 8 - 0.02(-99.25) = 9.985
```

En la iteración 2, después de J2 sale la decisión
(`J2 = 465.23334375 < J1 = 668.25` → `Decision: la actualizacion mejoro`), y al
final el resumen con J1, J2, J3 y los θ finales. Opciones del menú:
1 Resolver · 2 Solo predicción y costo J · 3 Predecir
(`yh = 6.287 + 11.637(5) = 6.287 + 58.185 = 64.472`, `NO APROBADO`) ·
4 Conceptos (opción múltiple e interpretación, incluido "cómo escribirlo en
papel") · 5 Ver o editar fórmulas.

Las cuentas son **exactas** (fracciones con enteros largos, sin `eval`): no se
redondea nada. En pantalla salen hasta 12 cifras; si hay más, se cortan con
`...`. Con más de 5 iteraciones usa decimales normales y solo muestra J.
Enter reusa lo que sale entre `[ ]`; si algo no se entiende, vuelve a
preguntar. Cada pantalla trae máximo 9 renglones y `-- enter para seguir --`.
Probado con MicroPython 1.11 (la versión de la Nspire) compilado en la Mac:
misma salida que Python de escritorio, y corre con solo 350 KB de memoria.

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

## Cómo pasarlo a la calculadora

Python vive **dentro de documentos .tns**, así que un `.py` suelto no se puede
mandar directo:

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
