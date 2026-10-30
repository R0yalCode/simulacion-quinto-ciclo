# Práctica: Generador Pseudoaleatorio LCG con Arquitectura MVC (Python y Java)

## 1. Objetivo de la práctica

Implementar un **Generador Congruencial Lineal (LCG)** de números pseudoaleatorios
en dos lenguajes (Python y Java), organizados mediante una arquitectura
**Modelo-Vista-Controlador (MVC) simplificada** para aplicación de consola.
El programa permite generar, comparar y analizar las secuencias desde una única
interfaz de terminal.

## 2. Fundamento matemático del método LCG

El generador se construye manualmente (sin usar `random` de Python ni `Random`
de Java) a partir de la fórmula recursiva:

```text
X(n+1) = (a * X(n) + c) mod m
```

Y cada valor se normaliza entre 0 y 1 con:

```text
U(n) = X(n) / m
```

## 3. Parámetros utilizados

| Parámetro          | Valor       |
|--------------------|-------------|
| Multiplicador a    | 1664525     |
| Incremento c       | 1013904223  |
| Módulo m           | 2^32 = 4294967296 |
| Semilla inicial X0 | 12345       |
| Cantidad de valores| 10000       |

Los parámetros pueden modificarse desde el menú, especialmente la semilla.
Ambos lenguajes usan exactamente los mismos valores: en Python enteros
normales y en Java `long` (con los parámetros indicados el producto cabe en
el rango de `long`). La normalización es `X / m` en Python y
`(double) X / m` en Java.

## 4. Arquitectura MVC implementada

- **Modelo**: lógica matemática del generador (LCG, comparación de secuencias
  y análisis de período). Incluye la implementación Java independiente.
- **Vista**: presentación en consola (menú, parámetros, tablas, mensajes y
  gráfica con Matplotlib). No contiene fórmulas ni ejecuta algoritmos.
- **Controlador**: coordina modelo y vista; ejecuta Java mediante `subprocess`
  (`javac` y `java`), gestiona la semilla y los archivos CSV.

Se mantiene un MVC sencillo: sin interfaces abstractas, inyección de
dependencias, repositorios, servicios ni fábricas.

## 5. Responsabilidad de cada componente

| Componente | Responsabilidad |
|---|---|
| `main.py` | Iniciar la aplicación y arrancar el controlador. |
| `modelo/modelo_lcg.py` | Parámetros, fórmula LCG, normalización, cambio de semilla, CSV de Python, comparación de secuencias y teorema de Hull-Dobell. |
| `modelo/GeneradorLCG.java` | Mismo algoritmo en Java con `long`, exporta el CSV para que Python lo compare. |
| `vista/vista_consola.py` | Menú, validación de entradas, tablas comparativas, mensajes y gráfica (Matplotlib). |
| `controlador/controlador_lcg.py` | Coordinación: compila/ejecuta Java con `subprocess`, ejecuta Python, compara, cambia la semilla y guarda resultados. |

## 6. Estructura del proyecto

```text
practica-lcg/
│
├── main.py                       # Punto de entrada
├── modelo/
│   ├── modelo_lcg.py             # Modelo Python (LCG)
│   └── GeneradorLCG.java         # Modelo Java (LCG)
├── vista/
│   └── vista_consola.py          # Vista (menú, tablas, gráfica)
├── controlador/
│   └── controlador_lcg.py        # Controlador (coordinación)
├── resultados/
│   ├── resultados_lcg_python.csv # Resultados de Python
│   ├── resultados_lcg_java.csv   # Resultados de Java
│   └── grafica_lcg.png           # Gráfica de la secuencia
├── README.md
└── requirements.txt
```

## 7. Requisitos de instalación

- Python 3
- JDK con `javac` y `java` (sin Maven ni Gradle)
- Biblioteca Python: Matplotlib

En Ubuntu:

```bash
sudo apt install python3 python3-pip default-jdk
```

## 8. Cómo instalar las dependencias

```bash
python3 -m pip install -r requirements.txt
```

## 9. Cómo ejecutar el programa

Desde la carpeta del proyecto:

```bash
python3 main.py
```

A la primera ejecución de la opción de Java, `GeneradorLCG.java` se compila
automáticamente con `javac`.

## 10. Cómo utilizar las opciones del menú

| Opción | Descripción |
|---|---|
| 1 | Ejecuta el generador en Python y guarda su CSV. |
| 2 | Compila y ejecuta el generador en Java y guarda su CSV. |
| 3 | Ejecuta ambos generadores con los mismos parámetros. |
| 4 | Compara las secuencias (X(n) exacto, U(n) con tolerancia 1e-12). |
| 5 | Muestra las primeras 20 observaciones de ambos lenguajes. |
| 6 | Cambia la semilla (entero entre 0 y m-1); mantiene a, c y m. |
| 7 | Analiza el período mediante el teorema de Hull-Dobell. |
| 8 | Genera la gráfica U(n) y la guarda en `resultados/grafica_lcg.png`. |
| 9 | Sale del programa. |

Si alguna operación necesita secuencias que aún no se han generado, el
programa las genera automáticamente antes de mostrarlas.

## 11. Cómo se comparan los resultados

La opción 4 compara las 10000 observaciones generadas por ambos lenguajes:

- Los valores enteros **X(n)** se comparan de forma **exacta**.
- Los valores normalizados **U(n)** se comparan con una **tolerancia de 1e-12**
  y se muestran con 10 decimales.
- Se informan coincidencias, diferencias y, si las hay, la posición y los
  valores correspondientes.

## 12. Cómo se interpreta el período

El teorema de **Hull-Dobell** garantiza período completo m en Z_m si:

1. `c` y `m` son coprimos.
2. `a - 1` es divisible por todos los factores primos de `m`.
3. Si `m` es divisible por 4, `a - 1` también lo es.

Para los parámetros de esta práctica las tres condiciones se cumplen
(m = 2^32 solo tiene como factor primo a 2; `a - 1 = 1664524` es divisible
por 2 y por 4), por lo que el **período teórico completo** es:

```text
2^32 = 4.294.967.296 valores
```

En la práctica solo se generan y analizan 10000 valores; no se intenta
comprobar experimentalmente el período completo.

## 13. Dónde se almacenan los CSV y las gráficas

```text
resultados/resultados_lcg_python.csv   # n, X(n), U(n) de Python (10000 filas)
resultados/resultados_lcg_java.csv     # n, X(n), U(n) de Java  (10000 filas)
resultados/grafica_lcg.png             # Gráfica de la secuencia normalizada
```
