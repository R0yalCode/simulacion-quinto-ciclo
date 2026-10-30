"""
Controlador: coordina modelo y vista, ejecuta Java con subprocess
y gestiona los archivos CSV y la semilla.
"""
import os
import subprocess
import sys

from modelo.modelo_lcg import ModeloLCG
from vista.vista_consola import VistaConsola

RUTA_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR_RESULTADOS = os.path.join(RUTA_BASE, "resultados")
CSV_PYTHON = os.path.join(DIR_RESULTADOS, "resultados_lcg_python.csv")
CSV_JAVA = os.path.join(DIR_RESULTADOS, "resultados_lcg_java.csv")
GRAFICA = os.path.join(DIR_RESULTADOS, "grafica_lcg.png")


class ControladorLCG:

    def __init__(self):
        self.modelo = ModeloLCG()
        self.vista = VistaConsola()

    # ------------------------------------------------------------------
    # Aplicación principal (bucle del menú)
    # ------------------------------------------------------------------
    def iniciar(self):
        while True:
            self.vista.mostrar_titulo()
            self.vista.mostrar_parametros({
                "a": self.modelo.a,
                "c": self.modelo.c,
                "m": self.modelo.m,
                "semilla": self.modelo.semilla,
                "cantidad": self.modelo.cantidad,
            })
            self.vista.mostrar_menu()
            opcion = self.vista.pedir_opcion()

            if opcion == 1:
                self.ejecutar_python()
            elif opcion == 2:
                self.ejecutar_java()
            elif opcion == 3:
                self.ejecutar_ambos()
            elif opcion == 4:
                self.comparar()
            elif opcion == 5:
                self.mostrar_tabla()
            elif opcion == 6:
                self.cambiar_semilla()
            elif opcion == 7:
                self.analizar_periodo()
            elif opcion == 8:
                self.generar_grafica()
            elif opcion == 9:
                self.vista.mostrar_mensaje("Programa finalizado.")
                break
            self.vista.pausar()

    # ------------------------------------------------------------------
    # Opción 1: generador Python
    # ------------------------------------------------------------------
    def ejecutar_python(self):
        self.vista.mostrar_mensaje("Ejecutando generador en Python...")
        self.modelo.generar()
        self.modelo.exportar_csv(CSV_PYTHON)
        self.vista.mostrar_mensaje(
            "Se generaron {} observaciones. CSV guardado en:\n{}".format(
                len(self.modelo.x_python), CSV_PYTHON))

    # ------------------------------------------------------------------
    # Opción 2: generador Java (se compila y ejecuta con subprocess)
    # ------------------------------------------------------------------
    def ejecutar_java(self):
        # Comprobar si Java está disponible
        try:
            subprocess.run(["java", "-version"], capture_output=True)
        except FileNotFoundError:
            self.vista.mostrar_error(
                "Java no está instalado. Instale el JDK (javac y java) e inténtelo de nuevo.")
            return

        # Compilar (solo si el .class no existe todavía)
        clase = os.path.join(RUTA_BASE, "modelo", "GeneradorLCG.class")
        if not os.path.exists(clase):
            self.vista.mostrar_mensaje("Compilando GeneradorLCG.java...")
            res = subprocess.run(["javac", os.path.join(RUTA_BASE, "modelo", "GeneradorLCG.java")],
                                 capture_output=True, text=True)
            if res.returncode != 0:
                self.vista.mostrar_error("Error al compilar Java:\n" + res.stderr)
                return

        # Ejecutar con los mismos parámetros y la misma semilla
        args = [str(self.modelo.a), str(self.modelo.c), str(self.modelo.m),
                str(self.modelo.semilla), str(self.modelo.cantidad), CSV_JAVA]
        res = subprocess.run(["java", "-cp", os.path.join(RUTA_BASE, "modelo"),
                              "GeneradorLCG"] + args, capture_output=True, text=True)
        if res.returncode != 0:
            self.vista.mostrar_error("Error al ejecutar Java:\n" + res.stderr)
            return

        self.leer_csv_java()
        self.vista.mostrar_mensaje(
            "Java: {}".format(res.stdout.strip()) +
            "\nCSV guardado en:\n" + CSV_JAVA)

    # Lee el CSV generado por Java y llena x_java / u_java
    def leer_csv_java(self):
        x_java = []
        u_java = []
        with open(CSV_JAVA, encoding="utf-8") as f:
            siguiente = f.readline()  # encabezado
            for linea in f:
                partes = linea.strip().split(",")
                if len(partes) == 3:
                    x_java.append(int(partes[1]))
                    u_java.append(float(partes[2]))
        self.modelo.x_java = x_java
        self.modelo.u_java = u_java

    # ------------------------------------------------------------------
    # Opción 3: ambos generadores con los mismos parámetros
    # ------------------------------------------------------------------
    def ejecutar_ambos(self):
        self.ejecutar_python()
        self.ejecutar_java()

    # ------------------------------------------------------------------
    # Opción 4: comparación de secuencias
    # ------------------------------------------------------------------
    def comparar(self):
        # Si falta alguna secuencia, se generan antes de comparar
        if not self.modelo.x_python or not self.modelo.x_java:
            self.vista.mostrar_mensaje(
                "Generando secuencias necesarias para la comparación...")
            self.ejecutar_ambos()
        resumen = self.modelo.comparar_secuencias()
        self.vista.mostrar_comparacion(resumen)

    # ------------------------------------------------------------------
    # Opción 5: primeras 20 observaciones
    # ------------------------------------------------------------------
    def mostrar_tabla(self):
        if not self.modelo.x_python or not self.modelo.x_java:
            self.vista.mostrar_mensaje(
                "Generando secuencias necesarias para mostrar la tabla...")
            self.ejecutar_ambos()
        self.vista.mostrar_tabla(self.modelo.x_python, self.modelo.u_python,
                                 self.modelo.x_java, self.modelo.u_java, 20)

    # ------------------------------------------------------------------
    # Opción 6: cambio de semilla
    # ------------------------------------------------------------------
    def cambiar_semilla(self):
        nueva = self.vista.pedir_semilla(self.modelo.semilla)
        self.modelo.cambiar_semilla(nueva)
        # Las secuencias anteriores ya no corresponden: se limpian
        self.modelo.x_python = []
        self.modelo.u_python = []
        self.modelo.x_java = []
        self.modelo.u_java = []
        self.vista.mostrar_mensaje("Nueva semilla establecida correctamente.")

    # ------------------------------------------------------------------
    # Opción 7: análisis del período (Hull-Dobell)
    # ------------------------------------------------------------------
    def analizar_periodo(self):
        analisis = self.modelo.analizar_periodo()
        self.vista.mostrar_periodo(analisis)

    # ------------------------------------------------------------------
    # Opción 8: gráfica de la secuencia normalizada
    # ------------------------------------------------------------------
    def generar_grafica(self):
        if not self.modelo.x_python or not self.modelo.x_java:
            self.vista.mostrar_mensaje(
                "Generando secuencias necesarias para la gráfica...")
            self.ejecutar_ambos()
        try:
            self.vista.generar_grafica(self.modelo.u_python,
                                       self.modelo.u_java, GRAFICA)
        except Exception as e:
            self.vista.mostrar_error(
                "No se pudo generar la gráfica. Verifique que Matplotlib "
                "está instalado ({})".format(e))

