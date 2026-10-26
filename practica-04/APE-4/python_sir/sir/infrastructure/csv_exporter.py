import csv
from pathlib import Path
from sir.domain.model import Snapshot

FIELD_NAMES = ["tiempo", "susceptibles", "infectados", "recuperados"]

def export_csv(history: list[Snapshot], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(FIELD_NAMES)
        for row in history:
            writer.writerow((row.tiempo, row.susceptibles, row.infectados, row.recuperados))
