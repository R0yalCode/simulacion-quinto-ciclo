# Práctica: Método Monte Carlo para aproximar el valor de π

Implementación del método de Monte Carlo en **Python** y **Java**, con la misma
secuencia de números pseudoaleatorios en ambos lenguajes, arquitectura por capas
y el patrón **Modelo-Vista-Controlador (MVC)**.

---

## 1. Descripción de la práctica

El método de Monte Carlo aproxima el valor de π generando puntos aleatorios
dentro de un cuadrado de lado 1 que contiene un cuarto de círculo de radio 1
(inscrito en el cuadrado unitario). Se cuenta cuántos puntos caen dentro del
círculo y se estima π con la proporción de puntos interioros.

El programa permite:

1. Ejecutar los experimentos con los cuatro tamaños de muestra obligatorios
   (1 000, 10 000, 100 000 y 1 000 000 de puntos).
2. Mostrar los resultados anteriores guardados en CSV.
3. Generar gráficas individuales de cada lenguaje.
4. Comparar los resultados de Python y Java (tabla, CSV y gráficas comparativas).

## 2. Objetivos

- Implementar el método Monte Carlo para aproximar π.
- Reproducir exactamente la misma secuencia pseudoaleatoria en Python y Java.
- Medir el tiempo de ejecución de cada experimento en milisegundos.
- Aplicar una arquitectura por capas con el patrón MVC en ambos lenguajes.
- Guardar resultados en CSV y generar gráficas a partir de datos reales.
- Comparar el rendimiento (tiempo) y la precisión (error) de ambos lenguajes.

## 3. Fundamento matemático

Para cada punto se generan dos números pseudoaleatorios `x` e `y` en `[0, 1)`.
El punto pertenece al círculo unitario si cumple:

```
x² + y² ≤ 1
```

Como el área del cuadrado es 1 y el área del cuarto de círculo es π/4, la
proporción de puntos dentro del círculo aproxima π/4:

```
π ≈ 4 × (Nc / N)
```

Donde:

- `N`: cantidad total de puntos generados.
- `Nc`: cantidad de puntos que pertenecen al círculo.
- `Error absoluto = |π real − π estimado|`.

## 4. Arquitectura seleccionada y sus capas

Se eligió una **arquitectura por capas sencilla** (sin sobreingeniería), donde
cada capa tiene una única responsabilidad:

| Capa | Responsabilidad | Python | Java |
|------|-----------------|--------|------|
| Modelo | Lógica Monte Carlo, LCG y resultados | `modelo/` | `modelo` |
| Vista | Menús y tablas en la terminal | `vista/` | `vista` |
| Controlador | Coordina modelo, vista y capas auxiliares | `controlador/` | `controlador` |
| Persistencia | Lectura y escritura de CSV | `persistencia/` | `persistencia` |
| Gráficas | Generación de imágenes PNG | `graficas/` | `graficas` |

Reglas respetadas:

- La lógica matemática vive **solo** en el modelo.
- La vista **no calcula nada**: solo muestra.
- El controlador **no contiene cálculos matemáticos**: solo coordina.
- No hay bases de datos, interfaces gráficas ni servidores.

## 5. Aplicación del patrón MVC

- **Modelo** (`ExperimentoMonteCarlo`, `LCG`, `ResultadoExperimento`): ejecuta
  los experimentos, genera la secuencia pseudoaleatoria y representa los
  resultados.
- **Vista** (`Vista`): muestra el menú, lee la opción del usuario y presenta las
  tablas de resultados y de comparación.
- **Controlador** (`Controlador`): recibe la opción del menú, pide los
  experimentos al modelo, los muestra por la vista, guarda los CSV con la capa
  de persistencia y solicita las gráficas a la capa de gráficas.

Flujo de la opción "Ejecutar experimentos":

```
Vista (menú) → Controlador → Modelo (experimentos)
                          → Vista (tabla)
                          → Persistencia (CSV)
```

## 6. Estructura del proyecto

```
monte-carlo/
│
├── main.py                     Lanzador principal de toda la práctica
│
├── python/                     Implementación en Python
│   ├── modelo/                 LCG y experimentos Monte Carlo
│   ├── vista/                  Menús y tablas de la terminal
│   ├── controlador/            Coordinador del programa
│   ├── persistencia/           Escritura y lectura de CSV
│   ├── graficas/               Gráficas con Matplotlib
│   ├── resultados/             resultados_python.csv (generado)
│   ├── graficas/               *.png individuales (generado)
│   ├── main.py                 Punto de entrada
│   └── requirements.txt        Dependencias
│
├── java/                       Implementación en Java
│   ├── src/
│   │   ├── modelo/             LCG, experimentos y resultados
│   │   ├── vista/              Menús y tablas de la terminal
│   │   ├── controlador/        Coordinador del programa
│   │   ├── persistencia/       Escritura y lectura de CSV
│   │   ├── graficas/           Gráficas con JFreeChart
│   │   └── Main.java           Punto de entrada
│   ├── lib/                    jfreechart-1.5.5.jar
│   ├── bin/                    Clases compiladas (generado)
│   ├── resultados/             resultados_java.csv (generado)
│   └── graficas/               *.png individuales (generado)
│
├── comparacion/
│   ├── tabla_comparacion.csv   Tabla comparativa (generada)
│   └── graficas/               *.png comparativos (generadas)
│
└── README.md
```

## 7. Responsabilidad de cada módulo y clase principal

### Python

| Módulo / clase | Responsabilidad |
|----------------|-----------------|
| `modelo/lcg.py` (`LCG`) | Generador congruencial lineal con semilla 123456789. |
| `modelo/experimento.py` (`ExperimentoMonteCarlo`, `ResultadoExperimento`) | Ejecuta los experimentos, mide tiempos y calcula π y el error. |
| `vista/vista.py` (`Vista`) | Menú, lectura de opciones y tablas de la terminal. |
| `controlador/controlador.py` (`Controlador`) | Menú principal, coordinación y conclusiones de la comparación. |
| `persistencia/gestor_csv.py` | Guarda/lee `resultados_python.csv`, `resultados_java.csv` y `tabla_comparacion.csv`. |
| `graficas/generador_graficas.py` | Gráficas individuales de Python y comparativas con Matplotlib. |
| `main.py` | Punto de entrada: `python3 main.py`. |

### Java

| Clase (paquete) | Responsabilidad |
|-----------------|-----------------|
| `modelo.LCG` | Generador congruencial lineal con la misma semilla. |
| `modelo.ExperimentoMonteCarlo` | Ejecuta los experimentos con `System.nanoTime()`. |
| `modelo.ResultadoExperimento` | Representa un resultado (N, Nc, π, error, tiempo). |
| `vista.Vista` | Menú, lectura de opciones y tablas de la terminal. |
| `controlador.Controlador` | Coordina modelo, vista, persistencia y gráficas. |
| `persistencia.GestorCSV` | Guarda/lee `resultados_java.csv` (formato compatible con Python). |
| `graficas.GeneradorGraficas` | Tres gráficas PNG con JFreeChart. |
| `Main.java` (raíz de `src/`) | Punto de entrada y bucle del menú. |

### Secuencia pseudoaleatoria compartida

Ambos lenguajes usan el mismo generador congruencial lineal (LCG):

```
X(n+1) = (48271 × X(n)) mod 2147483647
U(n)   = X(n) / 2147483647
```

- Semilla: `123456789`
- Multiplicador: `48271`
- Módulo: `2147483647`
- Cada punto consume dos números: uno para `x` y otro para `y`.
- **No** se usa `random` de Python ni `Random` de Java.

Con esto, ambos programas producen exactamente la misma cantidad de puntos
dentro del círculo y, por tanto, el mismo π estimado y el mismo error.

## 8. Requisitos de instalación (Ubuntu)

### Python

```bash
sudo apt update
sudo apt install python3 python3-pip
pip3 install --user -r python/requirements.txt
# Si Ubuntu lo rechaza (entorno gestionado), use:
#   python3 -m pip install --user --break-system-packages matplotlib
```

Solo se necesita **matplotlib** (instala numpy automáticamente).

### Java

Opción A, con el JDK del sistema:

```bash
sudo apt install default-jdk
```

Opción B, con un JDK local ya descargado (como el de este equipo):

```bash
export JAVA_HOME="$HOME/tools/jdk-21.0.13+9"
export PATH="$JAVA_HOME/bin:$PATH"
```

Comprobar: `javac -version` y `java -version`.

### JFreeChart

Ya está incluido en el proyecto: `java/lib/jfreechart-1.5.5.jar`.
Si se necesitara descargar de nuevo: <https://www.jfree.org/jfreechart/>
(coordenada Maven: `org.jfree:jfreechart:1.5.5`).

## 9. Cómo ejecutar Python

### Ejecución centralizada (lanzador principal)

Todo el proyecto se controla desde la raíz con un único comando:

```bash
cd ~/Documentos/monte-carlo
python3 main.py
```

Menú principal:

```
1. Ejecutar implementacion en Python.
2. Ejecutar implementacion en Java.
3. Comparar resultados de Python y Java.
4. Generar todas las graficas.
5. Salir.
```

- La **opción 1** abre el menú de Python dentro de su carpeta; al salir,
  regresa automáticamente al menú principal.
- La **opción 2** compila automáticamente el programa Java con el JDK
  configurado (`$HOME/tools/jdk-21.0.13+9` si existe, o el `javac` del PATH)
  y abre su menú; al salir, regresa al menú principal.
- La **opción 3** muestra las tablas comparativas, guarda
  `comparacion/tabla_comparacion.csv`, genera las gráficas comparativas e
  imprime las conclusiones (requiere los CSV de ambos lenguajes; si falta
  alguno, indica qué experimentos ejecutar primero).
- La **opción 4** genera las nueve gráficas (3 de Python, 3 de Java y 3
  comparativas) a partir de los CSV existentes, sin ejecutar experimentos ni
  inventar resultados; si falta un CSV, avisa cómo obtenerlo.

El lanzador ejecuta cada programa desde su propio directorio de trabajo y
construye todas las rutas de forma absoluta a partir de la ubicación del
proyecto, por lo que funciona desde cualquier terminal.

### Ejecución directa del programa Python

```bash
cd ~/Documentos/monte-carlo/python
python3 main.py
```

Menú de Python:

```
1. Ejecutar experimentos en Python
2. Mostrar resultados anteriores de Python
3. Generar gráficas de Python
4. Comparar resultados de Python y Java
5. Salir
```

- La **opción 1** ejecuta los cuatro tamaños, muestra la tabla y guarda
  `resultados/resultados_python.csv`.
- La **opción 3** genera `graficas/error_python.png`, `graficas/tiempo_python.png`
  y `graficas/pi_python.png` a partir del CSV guardado.
- La **opción 4** compara ambos lenguajes: muestra las tablas, guarda
  `comparacion/tabla_comparacion.csv` y genera las gráficas comparativas.

## 10. Cómo compilar y ejecutar Java

> Con el lanzador principal de la raíz (opción 2 del menú) la compilación y
> la ejecución son automáticas. Los comandos manuales son los siguientes.

Ejecutar **desde la carpeta `java/`** (las rutas de resultados y gráficas son
relativas a ella):

```bash
cd ~/Documentos/monte-carlo/java

# Compilar (crea la carpeta bin/)
mkdir -p bin
javac -encoding UTF-8 -cp "lib/jfreechart-1.5.5.jar" -d bin $(find src -name "*.java")

# Ejecutar
java -cp "bin:lib/jfreechart-1.5.5.jar" Main
```

Menú de Java:

```
1. Ejecutar experimentos en Java
2. Mostrar resultados anteriores de Java
3. Generar gráficas de Java
4. Salir
```

- La **opción 1** ejecuta los cuatro tamaños y guarda `resultados/resultados_java.csv`.
- La **opción 3** genera `graficas/error_java.png`, `graficas/tiempo_java.png`
  y `graficas/pi_java.png`.

Además, el programa Java admite un modo no interactivo que usa el lanzador
principal para generar solo las gráficas a partir del CSV guardado:

```bash
java -cp "bin:lib/jfreechart-1.5.5.jar" Main graficas
```

## 11. Cómo realizar la comparación

1. Ejecutar los experimentos en **Java** (opción 1 de su menú).
2. Ejecutar los experimentos en **Python** (opción 1 de su menú).
3. En el menú de **Python**, elegir la opción **4**.

La comparación requiere que existan ambos CSV; si falta alguno, el programa lo
indica con un mensaje claro sin fallar. Se muestran las tablas de π/error y de
tiempos, se guardan en `comparacion/tabla_comparacion.csv` y se generan las
gráficas comparativas, finalizando con las conclusiones: qué lenguaje fue más
rápido, con qué N se logró el menor error y si las aproximaciones de π coinciden.

Esta misma comparación está disponible directamente en el lanzador principal
de la raíz como la **opción 3** (`python3 main.py`).

## 12. Dónde se guardan las tablas y gráficas

| Archivo | Ubicación |
|---------|-----------|
| Resultados de Python | `python/resultados/resultados_python.csv` |
| Resultados de Java | `java/resultados/resultados_java.csv` |
| Tabla comparativa | `comparacion/tabla_comparacion.csv` |
| Gráficas de Python | `python/graficas/error_python.png`, `tiempo_python.png`, `pi_python.png` |
| Gráficas de Java | `java/graficas/error_java.png`, `tiempo_java.png`, `pi_java.png` |
| Gráficas comparativas | `comparacion/graficas/comparacion_error.png`, `comparacion_tiempo.png`, `comparacion_pi.png` |

Notas:

- Los tiempos se miden con `time.perf_counter()` (Python) y `System.nanoTime()`
  (Java), únicamente durante el experimento, en milisegundos.
- Cada lenguaje guarda su propio CSV: ejecutar uno no sobrescribe los
  resultados del otro.
- Todas las gráficas usan escala logarítmica en X, marcadores, leyenda,
  cuadrícula, títulos y ejes rotulados; la gráfica de π incluye una línea
  horizontal con el valor real de π.
