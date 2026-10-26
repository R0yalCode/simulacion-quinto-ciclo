from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sir.domain.model import Snapshot

def save_plot(history: list[Snapshot], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    times = [h.tiempo for h in history]
    for name in ("susceptibles", "infectados", "recuperados"):
        plt.plot(times, [getattr(h, name) for h in history], label=name.capitalize())
    plt.xlabel("Tiempo (pasos)")
    plt.ylabel("Número de personas")
    plt.title("Evolución del modelo SIR — Python/SimPy")
    plt.legend()
    plt.grid(alpha=.2)
    plt.savefig(path, dpi=160, bbox_inches="tight")
    plt.close()
