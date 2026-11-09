"""
Prueba de integración del CLI headless (main.py) de Python.

Ejecuta el programa real por subprocess con una configuración pequeña
(N = 250) y valida el protocolo JSON completo de salida.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PYTHON_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = PYTHON_DIR.parent


def run_headless(tmp_path: Path, n: int = 250):
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps({
            "generator": {"seed": 12345, "multiplier": 1664525,
                          "increment": 1013904223, "modulus": 4294967296, "n": n},
            "statistical": {"alpha": 0.05, "intervals": 10, "tolerance": 0.0001},
            "comparison_sizes": [1000, 10000, 100000, 1000000],
            "repetitions": 3,
        }),
        encoding="utf-8",
    )
    output_path = tmp_path / "out.json"
    subprocess.run(
        [
            sys.executable, str(PYTHON_DIR / "main.py"),
            "--headless", "--config", str(config_path),
            "--output", str(output_path), "--n", str(n), "--no-plots",
        ],
        check=True, capture_output=True, text=True, cwd=PROJECT_ROOT,
    )
    assert output_path.exists()
    return json.loads(output_path.read_text(encoding="utf-8"))


def test_cli_headless_end_to_end(tmp_path: Path):
    payload = run_headless(tmp_path)
    assert payload["engine"] == "python"
    assert payload["generator"]["n"] == 250
    assert payload["chi_square"]["degrees_freedom"] == 9
    assert sum(payload["chi_square"]["observed"]) == 250
    assert 0.0 <= payload["chi_square"]["p_value"] <= 1.0
    assert 0.0 <= payload["kolmogorov_smirnov"]["p_value"] <= 1.0
    assert payload["times_meta"]["repetitions"] == 3
    assert len(payload["sequence"]["sha256"]) == 64


def test_cli_headless_respects_repetitions(tmp_path: Path):
    import json as _json

    config_path = tmp_path / "config.json"
    config = _json.loads((PYTHON_DIR / "config" / "parameters.json").read_text())
    config["repetitions"] = 1
    config["generator"]["n"] = 120
    config_path.write_text(_json.dumps(config), encoding="utf-8")
    output_path = tmp_path / "out.json"
    subprocess.run(
        [
            sys.executable, str(PYTHON_DIR / "main.py"),
            "--headless", "--config", str(config_path),
            "--output", str(output_path), "--no-plots",
        ],
        check=True, capture_output=True, text=True, cwd=PROJECT_ROOT,
    )
    data = json.loads(output_path.read_text(encoding="utf-8"))
    assert data["generator"]["n"] == 120
    assert data["times_meta"]["repetitions"] == 1
