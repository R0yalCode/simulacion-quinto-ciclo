"""
Conftest de pruebas unitarias de Python.

Añade el directorio `python/` al `sys.path` para que los módulos core,
config, services y visualization se importen igual que en la aplicación.
"""

from __future__ import annotations

import sys
from pathlib import Path

PYTHON_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = PYTHON_DIR.parent
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))
    sys.path.insert(0, str(PROJECT_ROOT))
