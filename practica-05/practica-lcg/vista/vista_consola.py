"""
Vista: presentación en consola (menú, tablas, mensajes y gráfica).
No contiene fórmulas ni ejecuta algoritmos.
"""


class VistaConsola:

    # ------------------------------------------------------------------
    # Menú principal
    # ------------------------------------------------------------------
    def mostrar_titulo(self):
        print("========================================")
        print("GENERADOR PSEUDOALEATORIO LCG")
        print("ARQUITECTURA MVC")
        print("========================================")

    def mostrar_parametros(self, params):
        print("\nPARÁMETROS ACTUALES\n")
        print("a = {}".format(params["a"]))
        print("c = {}".format(params["c"]))
        print("m = {}".format(params["m"]))
        print("Semilla = {}".format(params["semilla"]))
        print("Cantidad de valores = {}".format(params["cantidad"]))

    def mostrar_menu(self):
        print("\nSeleccione una opción:\n")
        print("1. Ejecutar generador en Python.")
        print("2. Ejecutar generador en Java.")
        print("3. Ejecutar ambos generadores.")
        print("4. Comparar las secuencias (Python vs Java).")
        print("5. Mostrar las primeras 20 observaciones.")
        print("6. Cambiar la semilla.")
        print("7. Analizar el período del generador.")
        print("8. Generar gráfica de la secuencia.")
        print("9. Salir.")

    # ------------------------------------------------------------------
    # Entradas con validación
    # ------------------------------------------------------------------
    def pedir_opcion(self):
        """Lee la opción del menú y valida que sea 1-9."""
        while True:
            texto = input("\nSeleccione una opción: ").strip()
            if texto.isdigit() and 1 <= int(texto) <= 9:
                return int(texto)
            self.mostrar_error("Opción no válida. Introduzca un número entre 1 y 9.")

    def pedir_semilla(self, semilla_actual):
        """Solicita la nueva semilla (entero entre 0 y m-1)."""
        print("\nSemilla actual: {}".format(semilla_actual))
        while True:
            texto = input("Ingrese la nueva semilla: ").strip()
            if texto.isdigit():
                valor = int(texto)
                if 0 <= valor <= 4294967295:
                    return valor
            self.mostrar_error("La semilla debe ser un entero entre 0 y m-1 (4294967295).")

    def pausar(self):
        input("\nPresione Enter para continuar...")

    # ------------------------------------------------------------------
    # Mensajes y resultados
    # ------------------------------------------------------------------
    def mostrar_mensaje(self, mensaje):
        print("\n" + mensaje)

    def mostrar_error(self, mensaje):
        print("\n[ERROR] " + mensaje)

    def mostrar_comparacion(self, resumen):
        print("\n========================================")
        print("COMPARACIÓN PYTHON VS JAVA")
        print("========================================")
        print("\nValores generados en Python: {}".format(resumen["n_python"]))
        print("Valores generados en Java:   {}".format(resumen["n_java"]))
        print("\nCoincidencias: {}".format(resumen["coincidencias"]))
        print("Diferencias:   {}".format(resumen["diferencias"]))

        if resumen["diferencias"] == 0:
            print("\nRESULTADO: Las secuencias son idénticas.")
        else:
            print("\nRESULTADO: Las secuencias NO coinciden.")
            print("Primeras diferencias encontradas:")
            for d in resumen["ejemplos"]:
                print("  n = {}".format(d["n"]))
                print("  X Python: {} | X Java: {}".format(d["x_py"], d["x_jv"]))
                print("  U Python: {:.10f} | U Java: {:.10f}".format(d["u_py"], d["u_jv"]))

    # ------------------------------------------------------------------
    # Tabla de las primeras 20 observaciones
    # ------------------------------------------------------------------
    def mostrar_tabla(self, x_py, u_py, x_jv, u_jv, cantidad=20):
        print("\nPRIMERAS {} OBSERVACIONES\n".format(cantidad))
        encabezado = ("{:>4} | {:>12} | {:>12} | {:>12} | {:>12} | {:>9}"
                      .format("n", "X(n) Python", "U(n) Python", "X(n) Java", "U(n) Java", "Coinciden"))
        print(encabezado)
        print("-" * len(encabezado))
        total = min(cantidad, len(x_py), len(x_jv))
        for i in range(total):
            coincide = (x_py[i] == x_jv[i]
                        and abs(u_py[i] - u_jv[i]) <= 1e-12)
            fila = ("{:>4} | {:>12} | {:>12.10f} | {:>12} | {:>12.10f} | {:>9}"
                    .format(i, x_py[i], u_py[i], x_jv[i], u_jv[i],
                            "SI" if coincide else "NO"))
            print(fila)

    # ------------------------------------------------------------------
    # Análisis del período (Hull-Dobell)
    # ------------------------------------------------------------------
    def mostrar_periodo(self, analisis):
        print("\n========================================")
        print("ANÁLISIS DEL PERÍODO (HULL-DOBELL)")
        print("========================================\n")
        print("Factores primos de m: {}".format(analisis["primos"]))
        tabla = [
            ("1. c y m coprimos", analisis["condicion1"]),
            ("2. a-1 divisible por factores primos de m", analisis["condicion2"]),
            ("3. Si m es múltiplo de 4, a-1 divisible por 4", analisis["condicion3"]),
        ]
        for descripcion, cumple in tabla:
            print("{}: {}".format(descripcion, "CUMPLE" if cumple else "NO CUMPLE"))

        print("\n" + analisis["conclusion"])
        if analisis["periodo_teorico"] is not None:
            print("Período teórico completo = {:,} valores."
                  .format(analisis["periodo_teorico"]).replace(",", "."))
        print("En esta práctica solo se generan y analizan 10.000 valores.")

    # ------------------------------------------------------------------
    # Gráfica con Matplotlib (se muestra y se guarda en resultados/)
    # ------------------------------------------------------------------
    def generar_grafica(self, u_python, u_java, ruta_imagen):
        import matplotlib.pyplot as plt

        n = range(len(u_python))
        plt.figure(figsize=(12, 6))
        plt.plot(n, u_python, ".", markersize=2.5, label="Python", color="tab:blue")
        plt.plot(range(len(u_java)), u_java, ".", markersize=2.5,
                 label="Java", color="tab:orange", alpha=0.6)
        plt.title("Secuencia pseudoaleatoria generada mediante LCG")
        plt.xlabel("Número de observación n")
        plt.ylabel("Valor normalizado U(n)")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.savefig(ruta_imagen, dpi=150)
        plt.show()
        print("\nGráfica guardada en: {}".format(ruta_imagen))
