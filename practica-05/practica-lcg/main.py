"""
Punto de entrada de la práctica LCG (arquitectura MVC).
Únicamente inicia el controlador.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from controlador.controlador_lcg import ControladorLCG

if __name__ == "__main__":
    app = ControladorLCG()
    app.iniciar()
