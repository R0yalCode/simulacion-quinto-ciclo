import argparse
from sir.domain.model import SirConfig
from sir.application.simulate import SirSimulator
from sir.infrastructure.csv_exporter import export_csv
from sir.infrastructure.plotter import save_plot


def main():
    parser = argparse.ArgumentParser(description="Práctica 004: SIR Python/SimPy")
    parser.add_argument("--csv", default="../netlogo/resultados_python.csv",
                        help="Ruta del CSV de salida (compatible con NetLogo)")
    parser.add_argument("--plot", default="../results/grafica_python.png",
                        help="Ruta de la gráfica PNG de salida")
    parser.add_argument("--population", type=int, default=100, help="Población total N")
    parser.add_argument("--infected", type=int, default=5, help="Infectados iniciales I0")
    parser.add_argument("--beta", type=float, default=0.30, help="Parámetro beta")
    parser.add_argument("--gamma", type=float, default=0.10, help="Parámetro gamma")
    parser.add_argument("--steps", type=int, default=100, help="Pasos/tiempo de simulación")
    parser.add_argument("--seed", type=int, default=42, help="Semilla aleatoria para reproducibilidad")
    args = parser.parse_args()

    # Bloque de configuración centralizado (fácil de modificar)
    cfg = SirConfig(
        population=args.population,
        initially_infected=args.infected,
        beta=args.beta,
        gamma=args.gamma,
        steps=args.steps,
        seed=args.seed,
    )
    history = SirSimulator(cfg).run()
    assert len(history) == cfg.steps + 1
    assert all(row.total == cfg.population for row in history)
    export_csv(history, args.csv)
    save_plot(history, args.plot)
    print(f"SimPy: {len(history)} filas, final={history[-1]}")
    print(f"CSV: {args.csv} | Gráfica: {args.plot}")


if __name__ == "__main__":
    main()
