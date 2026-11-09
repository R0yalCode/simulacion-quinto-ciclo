"""
Pruebas unitarias de exportación (CSV/JSON) y del protocolo headless.

El protocolo headless es idéntico al implementado en Java, por lo que
aquí se valida la estructura del JSON de intercambio sin depender de Java.
"""

from __future__ import annotations

import json
from pathlib import Path

from config.generator_config import (
    AppConfig,
    ParameterValidationError,
    StatisticalParameters,
    load_config,
    save_config,
)
from core.lcg import Lcg
from services.execution_service import ExecutionService


def test_execution_service_full_flow_exports(tmp_path: Path, monkeypatch):
    from services import execution_service as execution_module

    monkeypatch.setattr(execution_module, "SEQUENCES_DIR", tmp_path / "sequences")
    monkeypatch.setattr(execution_module, "REPORTS_DIR", tmp_path / "reports")
    monkeypatch.setattr(execution_module, "GRAPHS_DIR", tmp_path / "graphs")

    config = AppConfig().with_n(200)
    service = execution_module.ExecutionService(config)
    pipeline = service.flow_full()
    assert len(pipeline.states) == 200
    names = [path.name for path in pipeline.exported]
    assert any(name.startswith("frecuencias_chi_square_python") for name in names), names
    assert any(name.startswith("resultados_python_") for name in names), names
    assert pipeline.times["repetitions"] == config.repetitions
    assert pipeline.times["warmup_discarded"] == 1
    sequence_files = list((tmp_path / "sequences").glob("secuencia_*.csv"))
    assert sequence_files, "Debe existir la exportación CSV de secuencias"
    metas = list((tmp_path / "sequences").glob("secuencia_metadatos_*.json"))
    assert metas, "Debe existir el JSON de metadatos de secuencia"
    newest = max(metas, key=lambda path: path.stat().st_mtime)
    loaded = json.loads(newest.read_text(encoding="utf-8"))
    assert loaded["sha256"] == Lcg.sequence_hash(pipeline.states)
    assert len(list((tmp_path / "graphs").glob("*.png"))) == 4


def test_headless_protocol_structure(tmp_path: Path):
    config = AppConfig().with_n(200)
    config.repetitions = 2
    output = tmp_path / "protocol.json"
    payload = ExecutionService(config).headless_run(output, no_plots=True)
    assert output.exists()
    data = json.loads(output.read_text(encoding="utf-8"))
    for key in ("engine", "generator", "statistical", "sequence",
                "chi_square", "kolmogorov_smirnov", "times_seconds"):
        assert key in payload
    assert data["engine"] == "python"
    assert data["sequence"]["count"] == 200
    assert data["sequence"]["sha256"] == payload["sequence"]["sha256"]
    assert data["chi_square"]["degrees_freedom"] == 9
    assert sum(data["chi_square"]["observed"]) == 200
    assert 0.0 <= data["chi_square"]["p_value"] <= 1.0
    assert 0.0 <= data["kolmogorov_smirnov"]["statistic"] <= 1.0
    assert data["times_meta"]["repetitions"] == 2


def test_app_config_json_round_trip(tmp_path: Path):
    config = AppConfig().with_n(1500)
    config.statistical = StatisticalParameters(alpha=0.1)
    path = tmp_path / "cfg.json"
    save_config(config, path)
    loaded = load_config(path)
    assert loaded == config
    assert loaded.generator.n == 1500
    assert loaded.statistical.alpha == 0.1


def test_statistical_parameters_validations():
    import pytest

    for bad in (0.0, 1.0, -0.5, 2.0):
        with pytest.raises(ParameterValidationError):
            StatisticalParameters(alpha=bad).validate()
    with pytest.raises(ParameterValidationError):
        StatisticalParameters(intervals=1).validate()
    with pytest.raises(ParameterValidationError):
        StatisticalParameters(tolerance=0).validate()


def test_invalid_comparison_sizes_rejected():
    config = AppConfig()
    config.comparison_sizes = [0, 100]
    try:
        config.validate()
    except ParameterValidationError:
        return
    raise AssertionError("Se esperaba ParameterValidationError para N=0")


def test_times_block_structure(tmp_path: Path):
    config = AppConfig().with_n(150)
    config.repetitions = 1
    output = tmp_path / "times.json"
    ExecutionService(config).headless_run(output, no_plots=True)
    times = json.loads(output.read_text(encoding="utf-8"))["times_seconds"]
    for key in ("generation", "chi_square", "ks", "total"):
        assert key in times
        assert isinstance(times[key], float)
        assert times[key] >= 0.0
