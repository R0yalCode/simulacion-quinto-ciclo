import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_python_csv():
    path = ROOT / "netlogo" / "resultados_python.csv"
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 101
    assert list(rows[0]) == ["tiempo", "susceptibles", "infectados", "recuperados"]
    assert rows[0]["tiempo"] == "0"
    assert rows[-1]["tiempo"] == "100"
    for t, row in enumerate(rows):
        assert int(row["tiempo"]) == t
        assert sum(int(row[k]) for k in ("susceptibles", "infectados", "recuperados")) == 100
    assert rows[0] == dict(tiempo="0", susceptibles="95", infectados="5", recuperados="0")
