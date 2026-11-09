# Práctica LCG — Generador congruencial lineal y pruebas de uniformidad

Implementación completa, en **Python** y **Java**, de un generador
pseudoaleatorio **LCG** y de las pruebas de bondad de ajuste
**Chi-cuadrado** y **Kolmogorov-Smirnov**, con menús interactivos en
español, gráficas, exportación de resultados, pruebas automatizadas y un
**modo comparativo** que verifica que ambas implementaciones producen
exactamente la misma secuencia de enteros `X(n)`.

El proyecto fue desarrollado y ejecutado realmente en este entorno; los
resultados de la sección [Resultados verificados](#resultados-verificados)
provienen de corridas reales, no de valores inventados.

---

## 1. Características

- LCG implementado manualmente (sin generadores nativos de cada lenguaje).
- Misma secuencia entera `X(n)` en Python y Java para los mismos parámetros.
- **Patrón Strategy** para las pruebas estadísticas (`StatisticalTest`,
  `ChiSquareTest`, `KolmogorovSmirnovTest`).
- **Arquitectura en capas**: dominio, aplicación, infraestructura y
  presentación.
- Menús interactivos en español, con tablas y validaciones.
- Gráficas: ECDF empírica, CDF uniforme teórica, comparación ECDF vs CDF
  e histograma de frecuencias.
- Exportación a CSV y JSON sin sobrescribir corridas anteriores (marca de
  tiempo en los nombres).
- Medición separada de generación, Chi-cuadrado, Kolmogorov-Smirnov y
  proceso completo, con calentamiento y promedio de repeticiones.
- Comparación Python ↔ Java por `subprocess` con protocolo JSON común.
- Pruebas automatizadas en ambos lenguajes (incluye casos conocidos
  independientes de las bibliotecas estadísticas).
- Java es **autónomo**: su menú y su JAR funcionan sin Python.

---

## 2. Estructura del proyecto

```text
PRACTICA_LCG/
├── python/
│   ├── main.py                     # Entrada: menús, CLI headless
│   ├── config/
│   │   ├── generator_config.py     # Dataclasses, validación, JSON
│   │   └── parameters.json         # Configuración canónica
│   ├── core/
│   │   ├── lcg.py                  # Generador congruencial lineal
│   │   ├── statistical_test.py     # Interfaz Strategy y TestResult
│   │   ├── chi_square.py           # Estrategia Chi-cuadrado
│   │   └── kolmogorov_smirnov.py   # Estrategia Kolmogorov-Smirnov
│   ├── services/
│   │   ├── execution_service.py    # Pipeline, medición y protocolo
│   │   ├── comparison_service.py   # Coordinador Python ↔ Java
│   │   └── report_service.py       # Tablas Rich y exportaciones
│   ├── visualization/
│   │   └── plots.py                # Gráficas Matplotlib
│   ├── tests/                      # 23 pruebas pytest
│   ├── requirements.txt
│   └── results/                    # Salidas generadas por Python
│
├── java/
│   ├── pom.xml                     # Maven + shade (JAR ejecutable)
│   ├── config/parameters.json      # Configuración de Java
│   └── src/
│       ├── main/java/ec/edu/feirnnr/lcg/
│       │   ├── Main.java           # Entrada interactiva/headless
│       │   ├── config/             # Records de configuración
│       │   ├── core/               # LCG, Strategy y pruebas
│       │   ├── services/           # Ejecución, exportación, menús
│       │   ├── util/               # JSON, ANSI, rutas
│       │   └── visualization/      # Gráficas JFreeChart
│       └── test/java/...           # 27 pruebas JUnit 5
│
├── results/
│   ├── comparison.csv              # Comparación consolidada
│   ├── comparison.json             # Comparación en JSON
│   └── final_report/               # Informe Markdown con marca de tiempo
│
├── scripts/
│   ├── ejecutar_python.sh
│   ├── compilar_java.sh
│   ├── ejecutar_java.sh
│   └── ejecutar_pruebas.sh
└── README.md
```

---

## 3. Requisitos

| Herramienta | Versión usada y verificada |
|---|---|
| Python | 3.14.4 |
| NumPy | 2.5.4 |
| SciPy | 1.18.1 |
| Matplotlib | 3.11.2 |
| Rich | 15.0.0 |
| pytest | 9.2.0 |
| JDK | Temurin 21.0.13+9 |
| Maven | 3.10.0 |
| Apache Commons Math | 3.6.1 |
| JFreeChart | 1.5.5 |
| Gson | 2.11.0 |
| JUnit | 5.10.2 |

En este equipo el JDK y Maven se instalaron sin privilegios de
administrador en:

```text
~/tools/jdk-21.0.13+9
~/tools/apache-maven-3.10.0
```

Los scripts del proyecto buscan automáticamente esas rutas, `JAVA_HOME`,
`/usr/lib/jvm/*` y el `PATH`.

---

## 4. Instalación

### 4.1 Python

```bash
cd PRACTICA_LCG
python3 -m venv .venv
.venv/bin/pip install -r python/requirements.txt
```

En este entorno el `venv` ya existe y las dependencias están instaladas.

### 4.2 Java

Con un JDK 21 y Maven disponibles:

```bash
./scripts/compilar_java.sh
```

o manualmente:

```bash
cd java
JAVA_HOME=~/tools/jdk-21.0.13+9 \
PATH=~/tools/jdk-21.0.13+9/bin:~/tools/apache-maven-3.10.0/bin:$PATH \
mvn package
```

El JAR ejecutable autocontenido queda en `java/target/lcg-simulator.jar`
(Maven Shade incluye Commons Math, JFreeChart y Gson).

---

## 5. Uso rápido

```bash
# Menú interactivo Python
./scripts/ejecutar_python.sh

# Menú interactivo Java (compila el JAR si hace falta)
./scripts/ejecutar_java.sh

# Todas las pruebas automatizadas
./scripts/ejecutar_pruebas.sh
```

También se puede ejecutar directamente:

```bash
.venv/bin/python python/main.py
java -jar java/target/lcg-simulator.jar
```

---

## 6. Menús

### 6.1 Menú principal de Python

```text
[1] Ejecutar implementación Python
[2] Ejecutar implementación Java
[3] Ejecutar ambas implementaciones y comparar
[4] Configurar parámetros del generador
[5] Consultar información de la práctica
[0] Salir del programa
```

### 6.2 Submenú de ejecución (Python y Java)

```text
[1] Generar números pseudoaleatorios (LCG)
[2] Ejecutar prueba Chi-cuadrado
[3] Ejecutar prueba Kolmogorov-Smirnov
[4] Ejecutar proceso completo (pruebas + gráficas + reporte)
[0] Regresar al menú principal
```

La opción `2` del menú principal de Python lanza la implementación Java
en un subproceso; el menú que se muestra entonces es el de Java, que es
autónomo.

El menú principal de Java contiene sus propias opciones: ejecutar su
submenú, configurar parámetros y consultar la información de la práctica.
Java no necesita Python para funcionar.

```text
[1] Ejecutar implementación Java (menú de ejecución)
[2] Configurar parámetros del generador
[3] Consultar información de la práctica
[0] Salir del programa
```

La opción de configuración valida todos los valores y guarda el JSON
correspondiente (`python/config/parameters.json` o
`java/config/parameters.json`). Si un valor es inválido se muestra un
mensaje en español y no se aplican cambios.

---

## 7. Parámetros

Valores por defecto:

| Parámetro | Valor |
|---|---|
| Semilla `X0` | `12345` |
| Multiplicador `a` | `1664525` |
| Incremento `c` | `1013904223` |
| Módulo `m` | `4294967296` (`2^32`) |
| Cantidad de números `N` | `1000` |
| Nivel de significancia `α` | `0.05` |
| Intervalos `k` (Chi-cuadrado) | `10` |
| Grados de libertad | `9` |
| Tolerancia comparativa | `1e-4` |
| Tamaños del modo comparativo | `1000, 10000, 100000, 1000000` |
| Repeticiones de medición | `3` |

Validaciones principales:

- `N > 0` y `N <= 20 000 000` para evitar desbordamientos de memoria.
- `m >= 2`, `0 <= X0 < m`, `a >= 0`, `c >= 0`.
- `0 < α < 1`, `2 <= k <= 1000`.
- Frecuencia esperada `N/k >= 5` para Chi-cuadrado.
- Al menos un tamaño de comparación positivo.
- Entre 1 y 10 repeticiones de medición.

---

## 8. Métodos estadísticos

### 8.1 Generador congruencial lineal

```text
X(n) = (a · X(n-1) + c) mod m
U(n) = X(n) / m
```

Se implementa con aritmética entera exacta. En Java se usa `long` y, si
el producto puede desbordar, se recurre a `BigInteger`; de este modo la
secuencia coincide con la de Python, que usa enteros de precisión
arbitraria.

La identidad entre implementaciones se verifica con:

- el conteo de elementos,
- los primeros y últimos 20 enteros,
- un **SHA-256** calculado sobre los enteros decimales separados por comas.

### 8.2 Chi-cuadrado

- Se divide `[0, 1)` en `k = 10` intervalos semiabiertos.
- Frecuencia esperada `Ei = N/k`.
- Estadístico:

```text
χ² = Σ (Oi − Ei)² / Ei
```

- Grados de libertad: `gl = k − 1 = 9`.
- Valor p: cola superior de la distribución χ².
  - Python: `scipy.stats.chi2.sf`.
  - Java: `1 − ChiSquaredDistribution(gl).cumulativeProbability(χ²)` de
    Apache Commons Math.
- Decisión: se rechaza `H0` si `p < α`.

La tabla de frecuencias muestra intervalo, frecuencia observada,
frecuencia esperada y contribución `(Oi − Ei)²/Ei`.

### 8.3 Kolmogorov-Smirnov

Con los datos ordenados `U(1) ≤ … ≤ U(N)`:

```text
D+ = max( i/N − U(i) )
D− = max( U(i) − (i−1)/N )
D  = max(D+, D−)
```

- Valor p:
  - Python: `scipy.stats.kstest` (exacto para muestras pequeñas,
    asintótico para grandes).
  - Java: `KolmogorovSmirnovTest` de Apache Commons Math contra
    `UniformRealDistribution(0, 1)`.
- Decisión: se rechaza `H0` si `p < α`.

**Limitación documentada:** con módulos pequeños los datos son discretos
y aparecen empates; en ese caso el valor p de KS es aproximado. Con
`m = 2^32` la malla es suficientemente fina y la aproximación es
prácticamente exacta. Las dos bibliotecas pueden usar convenciones
ligeramente distintas para muestras pequeñas; por eso la comparación de
valores p se hace con tolerancia configurable.

---

## 9. Medición de tiempos

La medición sigue esta metodología:

1. Una ejecución de **calentamiento** que **no** se mide.
2. `repetitions` ejecuciones medidas (por defecto 3).
3. Se informa el **promedio** de:
   - generación del LCG,
   - prueba Chi-cuadrado,
   - prueba Kolmogorov-Smirnov,
   - proceso estadístico completo (suma de las tres anteriores).

Se excluyen explícitamente:

- la compilación,
- la inicialización de la JVM y la importación de módulos,
- la escritura de archivos,
- la generación de gráficas.

Python usa `time.perf_counter()`; Java usa `System.nanoTime()`.

---

## 10. Resultados verificados

Corrida real del modo comparativo con la configuración por defecto,
`repetitions = 3`, para los cuatro tamaños requeridos. Todos los valores
provienen de `results/comparison.csv` y
`results/final_report/informe_comparativo_*.md`.

| N | Secuencias iguales | χ² Python | χ² Java | p χ² Python | p χ² Java | D KS Python | D KS Java | p KS Python | p KS Java |
|---:|:---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 000 | Sí | 4.1200 | 4.1200 | 0.903338 | 0.903338 | 0.028642 | 0.028642 | 0.377741 | 0.377741 |
| 10 000 | Sí | 14.1600 | 14.1600 | 0.116746 | 0.116746 | 0.005960 | 0.005960 | 0.867344 | 0.867344 |
| 100 000 | Sí | 9.1600 | 9.1600 | 0.422638 | 0.422638 | 0.002073 | 0.002073 | 0.782460 | 0.782460 |
| 1 000 000 | Sí | 16.0227 | 16.0227 | 0.066409 | 0.066409 | 0.000944 | 0.000944 | 0.334555 | 0.334555 |

En los cuatro tamaños:

- las secuencias de enteros coinciden **exactamente**,
- las frecuencias observadas coinciden,
- las decisiones estadísticas coinciden.

Tiempos promediados del proceso estadístico completo (generación + ambas
pruebas), en milisegundos por implementación. Corresponden a la corrida
final; los tiempos varían entre ejecuciones y por eso se informan aparte:

| N | Python | Java |
|---:|---:|---:|
| 1 000 | 3.5 ms | 7.2 ms |
| 10 000 | 15.7 ms | 14.8 ms |
| 100 000 | 186.2 ms | 102.9 ms |
| 1 000 000 | 2713.6 ms | 349.8 ms |

Los tiempos se muestran **aparte** de los estadísticos y no intervienen
en la decisión de igualdad. No incluyen carga de la JVM, importaciones,
exportaciones ni gráficas.

Hashes SHA-256 de las secuencias comparadas:

| N | SHA-256 |
|---:|---|
| 1 000 | `4bf49238f3eded4551146a269e1556f7f61120295635fa26be6460f2adff377d` |
| 10 000 | `6937830d1d749e3ad7ebbba2c5adb0d11e1928b4d6ec31fa95a05ae170f7388d` |
| 100 000 | `7e0e5ac1c4b91b8c7ad52db9b2db97fbfc3130dd4d1b7d9013e434c786e49810` |
| 1 000 000 | `32b0de87dfc7d581291fabd3c6655f876157e18dfab95539211e9b460c02c128` |

El valor completo está en `results/comparison.csv`.

---

## 11. Archivos generados

### Python (`python/results/`)

- `sequences/secuencia_enteros_python_n<N>_<fecha>.csv`
- `sequences/secuencia_normalizada_python_n<N>_<fecha>.csv`
- `sequences/secuencia_metadatos_python_n<N>_<fecha>.json`
- `reports/frecuencias_chi_square_python_n<N>_<fecha>.csv`
- `reports/resultados_python_<fecha>.json`
- `graphs/ecdf_empirica_lcg.png`
- `graphs/cdf_uniforme_teorica.png`
- `graphs/ecdf_vs_uniforme_lcg.png`
- `graphs/histograma_frecuencias_lcg.png`

### Java (`java/results/`)

- `sequences/secuencia_n<N>_enteros_java_<fecha>.csv`
- `sequences/secuencia_n<N>_normalizada_java_<fecha>.csv`
- `reports/frecuencias_chi_square_java_n<N>_<fecha>.csv`
- `reports/resultados_java_<fecha>.json`
- `graphs/lcg_java_n<N>_ecdf_empirica_java.png`
- `graphs/lcg_java_n<N>_cdf_uniforme_teorica_java.png`
- `graphs/lcg_java_n<N>_ecdf_vs_uniforme_java.png`
- `graphs/lcg_java_n<N>_histograma_frecuencias_java.png`

### Comparación (`results/`)

- `comparison.csv` — tabla consolidada.
- `comparison.json` — misma información en JSON.
- `final_report/comparacion_<fecha>.csv`
- `final_report/informe_comparativo_<fecha>.md`

Los nombres con fecha/hora evitan sobrescribir corridas anteriores.

---

## 12. Modo headless

Ambas implementaciones comparten el mismo protocolo JSON, usado por el
coordinador de Python.

```bash
# Python
.venv/bin/python python/main.py --headless \
  --config python/config/parameters.json \
  --output /tmp/python.json --n 1000 --no-plots

# Java
java -jar java/target/lcg-simulator.jar --headless \
  --config java/config/parameters.json \
  --output /tmp/java.json --n 1000 --no-plots
```

Claves principales del JSON:

```text
engine, generator, statistical, sequence,
chi_square, kolmogorov_smirnov,
times_seconds, times_meta, p_value_source
```

`sequence` contiene `count`, `sha256`, los primeros/últimos 20 enteros y
las primeras/últimas 20 variables uniformes.

El coordinador (`python/services/comparison_service.py`) localiza Java,
compila el JAR con Maven si no existe, ejecuta ambos motores como
subprocesos y compara los resultados.

---

## 13. Pruebas automatizadas

Resultado real de las suites:

```text
Python: 23 passed
Java:   27 tests, 0 failures, 0 errors
```

```bash
# Python
cd python
../.venv/bin/python -m pytest tests -q

# Java
cd java
mvn test
```

Cobertura de las pruebas:

- LCG con el ciclo conocido `m=8, a=5, c=1, X0=1 → 6,7,4,5,2,3,0,1`.
- Hash SHA-256 conocido `9e44f8dc…` de esa secuencia.
- Parámetros por defecto y primeros enteros esperados.
- Aritmética segura con productos que desbordan `long`.
- Chi-cuadrado con uniformidad perfecta (`χ² = 0`) y caso extremo
  (`χ² = 900`).
- Grados de libertad, frecuencias esperadas y decisiones.
- Kolmogorov-Smirnov con `D` conocido para `U(i) = i/(N+1)`.
- Valores fuera de `[0,1)` y secuencias vacías.
- Ida y vuelta de configuración JSON y validaciones.
- Protocolo headless, tiempos y determinismo de la secuencia.

---

## 14. Decisiones de diseño

- **Strategy**: las pruebas implementan una interfaz común y el servicio
  de ejecución no conoce detalles concretos.
- **Capas**: `core` (dominio), `services` (aplicación), `util` /
  `visualization` (infraestructura) y menús (presentación).
- **Protocolo JSON único**: evita formatos distintos entre lenguajes y
  permite comparar secuencias y estadísticos de forma robusta.
- **Java autónomo**: el JAR no invoca Python; solo el coordinador de
  Python invoca Java cuando se elige la opción comparativa.
- **Sin dependencias nativas para el LCG**: la generación se implementa
  manualmente en ambos lenguajes.
- **Bibliotecas solo para valores p**: SciPy y Commons Math se usan para
  las distribuciones, no para generar números.

---

## 15. Solución de problemas

### Java o Maven no encontrados

Defina `JAVA_HOME` o agregue el JDK/Maven al `PATH`. Los scripts buscan
también `~/tools/jdk*`, `~/tools/apache-maven*` y `/usr/lib/jvm/*`.

### El JAR no existe

```bash
./scripts/compilar_java.sh
```

El coordinador de Python también lo compila automáticamente si Maven está
disponible.

### Error «frecuencia esperada menor que 5»

Aumente `N` o reduzca `k`. Para `k = 10` se necesita `N >= 50`.

### Gráficas no generadas

- Python requiere Matplotlib y un backend no interactivo; el proyecto usa
  `Agg`, por lo que funciona sin pantalla.
- Java usa JFreeChart en modo headless (`java.awt.headless=true`).

### Valores p ligeramente distintos entre Python y Java

Es esperable en los últimos decimales por las distintas implementaciones
numéricas. La comparación usa la tolerancia configurada (`1e-4` por
defecto) y las secuencias se comparan de forma exacta.

### Entrada estándar cerrada en los menús

Si se ejecuta con entrada redirigida, los menús terminan de forma
controlada al agotarse las líneas. Para uso normal, ejecute en una
terminal interactiva.

---

## 16. Verificación realizada

- `mvn package` y `mvn test`: compilación y 27 pruebas Java correctas.
- `pytest`: 23 pruebas Python correctas.
- Comparación real para `N = 1000, 10000, 100000, 1000000`: secuencias
  idénticas y estadísticos compatibles dentro de tolerancia.
- Menús interactivos de Python y Java probados con entrada simulada.
- Gráficas PNG generadas en ambas implementaciones.
- Modo headless probado en ambos lenguajes con el mismo SHA-256 para
  `N = 250` y `N = 1000`.

Si alguna herramienta no está disponible en otro equipo, los scripts y
este README documentan la alternativa de instalación; el código no
depende de rutas absolutas del entorno de desarrollo.
