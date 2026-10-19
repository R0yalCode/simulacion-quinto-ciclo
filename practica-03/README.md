# QueueLab: simulador M/M/1 animado

Proyecto de la **Práctica 003 de Simulación (15-16/10/2026)**. Implementa una cola M/M/1 FIFO con **SimPy**, muestra una cinta transportadora animada y permite ver métricas, eventos y gráficos sincronizados con el tiempo *simulado*.

## Ejecutar

Se requiere Python 3.10+.

```bash
cd simulador_mm1
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell:
# .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

Abrir **http://127.0.0.1:8501** en el navegador. Todo funciona localmente. La aplicación no requiere Internet ni servicios en la nube.

**Pruebas**: `python -m unittest discover -s tests -v`.

## Arquitectura por capas

```text
simulador_mm1/
├── main.py                         # Punto de entrada
├── domain/
│   ├── models.py                   # Contratos y validación
│   └── queueing.py                 # Fórmulas teóricas
├── application/
│   └── use_cases.py                # Simular y comparar escenarios
├── infrastructure/
│   └── simpy_engine.py             # Adaptador de eventos discretos SimPy
├── presentation/
│   ├── server.py                   # Adaptador API HTTP con stdlib
│   └── static/
│       ├── index.html              # Interfaz
│       ├── styles.css              # Cinta animada y diseño responsivo
│       └── app.js                  # Reproductor, canvas y CSV
├── tests/
│   ├── test_domain.py
│   └── test_integration.py
└── requirements.txt
```

Dependencias: `presentation → application → domain`; `application → infrastructure` (adaptador SimPy); `infrastructure → domain`. El navegador consulta la API sin conocer SimPy. Para sustituir SimPy por otro motor, cambiar `MM1Engine` sin modificar el modelo matemático.

## Funcionalidad

- Eventos de **llegada**, **inicio de servicio**, **salida** y **fin**.
- Intervalos entre llegadas `Exp(λ)` y servicio `Exp(μ)`, usando una semilla aleatoria reproducible.
- Recurso SimPy de capacidad uno; solicitudes en cola FIFO.
- Cinta transportadora animada que representa la cola y una estación de servicio activa/inactiva.
- Reloj de simulación, pausar, continuar, reiniciar, cambiar velocidad y navegar por la línea temporal.
- Gráficas Canvas en vivo de longitud de cola y media de espera, sin CDN.
- Conteo de llegadas, atendidos, cola, utilización y registro de eventos en tiempo simulado.
- Tabla dinámica que contrasta **ρ, L, Lq, W y Wq** teóricos con sus estimaciones simuladas.
- Análisis comparativo de los tres escenarios requeridos por la guía: (2, 3), (2.5, 3), (2.9, 3).
- Exportación de eventos de paquetes atendidos como CSV.

## Fórmulas

Para `λ < μ`, `ρ=λ/μ`, `L=λ/(μ−λ)`, `Lq=λ²/[μ(μ−λ)]`, `W=1/(μ−λ)`, `Wq=λ/[μ(μ−λ)]`.

> **Corrección de la guía**: una línea del fundamento teórico invierte ρ; el pseudocódigo de la misma guía sí indica `ρ=λ/μ`. Aquí se usa la fórmula correcta.

## Estadística simulada

- `Lq_sim = (∫Q(t)dt)/T`; `L_sim = (∫N(t)dt)/T`.
- `ρ_sim = (tiempo ocupado del servidor)/T`.
- `Wq_sim` y `W_sim`: promedios de los paquetes cuyo servicio **terminó** al finalizar el horizonte, para evitar contabilizar tiempos incompletos como cero.
- `throughput = paquetes completados/T`. `pending = llegadas − completados`.
- Gráficas y promedios en vivo utilizan el historial de eventos producido por SimPy; la reproducción visual **no es una segunda simulación** y no modifica los resultados.

**Limitaciones experimentales:** se detienen las llegadas y la observación al alcanzar el horizonte `T`, aunque queden paquetes pendientes. Las métricas teóricas son de largo plazo y pueden diferir, especialmente con `λ ≈ μ`, por transitorios, varianza aleatoria y censura de servicios pendientes. Para estimaciones mejores: más duración, varias semillas, intervalos de confianza y/o un periodo de calentamiento. Las unidades de tasas y tiempo son arbitrarias pero coherentes (p. ej., paquetes/minuto y minutos). No confundir velocidad de reproducción con tiempo de simulación.

## Preguntas de control (resumen)

M/M/1: primera M, llegadas Poisson / entre llegadas exponencial; segunda M, servicios exponenciales; 1, un único servidor. `λ` llegadas por unidad de tiempo, `μ` servicios por unidad de tiempo. `ρ=λ/μ` mide carga; si `λ≥μ`, no existe equilibrio estacionario con espera finita. `W` incluye servicio; `Wq` es solo espera. `L` incluye cola + servicio; `Lq`, solo cola. La exponencial modela tiempos sin memoria. Con `λ→μ⁻` crecen las esperas y longitud de cola; SimPy realiza eventos discretos, no impone una distribución por sí mismo: la distribución se elige en `rng.expovariate`. Los resultados simulados difieren por horizonte finito y aleatoriedad. Si `λ>μ` indefinidamente, la cola crece sin límite en promedio.
