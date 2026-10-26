# Práctica 004 — Modelo SIR modular (Python/SimPy, NetLogo)

## Propósito
Implementación del modelo SIR con **Python + SimPy** para la simulación y **NetLogo** para la visualización de los resultados generados en CSV.

Parámetros comunes: `N=100`, `I0=5`, `S0=95`, `R0=0`, `beta=0.30`, `gamma=0.10`, `pasos=100` y semilla experimental `42`.

## Interpretación y supuesto de contagio
La guía no define cuántos contactos tiene cada infectado. Para mantener un algoritmo discreto común se adopta, por cada susceptible y por paso, la probabilidad `1 - (1 - beta/N)^I`, y por cada infectado la probabilidad de recuperación `gamma`. Las transiciones se aplican simultáneamente basadas en el estado al inicio del paso. No se modelan posiciones de contacto ni desplazamiento. Una corrida registra `t=0` hasta `t=100` inclusive (101 filas). Los individuos recuperados no vuelven a infectarse.

## Arquitectura
- `domain`: modelos/estados, validación y regla matemática, sin dependencia de CSV o interfaz.
- `application`: caso de uso para simular pasos con SimPy.
- `infrastructure`: CSV y gráficos, adaptadores externos.
- `presentation`: ejecución por línea de comandos.
- `netlogo`: visualización basada en agentes + lectura de CSV `resultados_python.csv`.

## Ejecución rápida (Linux)
```bash
./run_all.sh        # instala dependencias Python, ejecuta Python + tests
./run_netlogo.sh    # abre NetLogo 7 con el modelo ya armado
```

## Python (requiere Python 3.10+)
Desde `python_sir/`:
```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m sir.presentation.cli
```
Genera `../netlogo/resultados_python.csv` y `../results/grafica_python.png`.

## Cambiar parámetros (población, infectados iniciales, beta, gamma, semilla)
Se pueden modificar directamente en `python_sir/sir/domain/model.py` (bloque de configuración centralizado) o pasar por CLI:
```bash
.venv/bin/python -m sir.presentation.cli --population 200 --infected 10 --beta 0.10 --gamma 0.10 --seed 123
```
Después de ejecutar, se regenerará `netlogo/resultados_python.csv` automáticamente.

## NetLogo 7.x (modelo listo para abrir)
Abrir directamente:
```
netlogo/modelo_sir_netlogo.nlogox
```

1. Ejecutar antes Python para que exista `resultados_python.csv`.
2. Abrir el `.nlogox` y pulsar `setup` (crea 95 S azules y 5 I rojas).
3. Pulsar `go` hasta que `ticks = 100` (se detiene solo) para ver la simulación local.
4. Pulsar `cargar-python`: lee el CSV y dibuja `SIR Python` y las gráficas de comparación con la simulación local.
5. Pulsar `export-local` para guardar `resultados_netlogo.csv` en la misma carpeta del modelo si se desea.

La importación usa la extensión `csv`. El CSV se lee como texto y se convierte con `read-from-string`.

**Importante:** NetLogo importa y visualiza los datos generados por Python. Python + SimPy es el generador de los resultados para este flujo.

## CSV común
Encabezado exacto: `tiempo,susceptibles,infectados,recuperados`.
En cada CSV, validar `S+I+R = población`, `tiempo=0..100`, `t0=(95,5,0)` y ninguna cantidad negativa.

## Organización
```
run_all.sh | run_netlogo.sh
python_sir/sir/domain | application | infrastructure | presentation
netlogo/modelo_sir_netlogo.nlogox   # NetLogo 7, listo para abrir
netlogo/modelo_sir_netlogo.nls      # Código de referencia
netlogo/resultados_python.csv
results/grafica_python.png
tests/test_results.py
```

## Qué hace cada parte
- `domain/model.py`: estados S/I/R, configuración centralizada y validaciones.
- `domain/rules.py`: fórmula `1-(1-beta/N)^I`.
- `application/simulate.py`: crean la población, ejecutan pasos con SimPy y arman el historial.
- `infrastructure/csv_exporter.py`: escriben el CSV común.
- `infrastructure/plotter.py`: genera la gráfica PNG de Python.
- `presentation/cli.py`: punto de entrada y rutas de salida.
- `netlogo/modelo_sir_netlogo.nlogox`: versión basada en agentes + importación de CSV de Python.
- `tests/test_results.py`: valida encabezado, 101 filas, `t=0..100` y `S+I+R=100` para el CSV de Python.
