"""Vista: menús, lectura de opciones y presentación de tablas en la terminal."""


class Vista:
    """Toda la interacción con el usuario se realiza desde esta clase."""

    def mostrar_menu(self):
        """Muestra el menú principal del programa Python."""
        print()
        print("=====================================")
        print("  METODO MONTE CARLO - MENU (PYTHON) ")
        print("=====================================")
        print("1. Ejecutar experimentos en Python")
        print("2. Mostrar resultados anteriores de Python")
        print("3. Generar gráficas de Python")
        print("4. Comparar resultados de Python y Java")
        print("5. Salir")

    def leer_opcion(self):
        """Lee la opción escrita por el usuario."""
        return input("Seleccione una opción: ").strip()

    def mostrar_mensaje(self, mensaje):
        """Muestra un mensaje informativo."""
        print(mensaje)

    def mostrar_error(self, mensaje):
        """Muestra un mensaje de error."""
        print(f"ERROR: {mensaje}")

    def mostrar_tabla(self, titulo, resultados):
        """Muestra la tabla de resultados de los experimentos."""
        print()
        print("=" * 38)
        print(f"{titulo:^38}")
        print("=" * 38)
        print()
        print(f"{'N':<14}{'PI ESTIMADO':<20}{'ERROR':<18}{'TIEMPO (ms)'}")
        print("-" * 70)
        for r in resultados:
            print(f"{r['n']:<14}{r['pi_estimado']:<20.6f}"
                  f"{r['error']:<18.6f}{r['tiempo_ms']:.3f}")
        print()

    def mostrar_tabla_comparacion(self, resultados_py, resultados_java):
        """Muestra las tablas comparativas de π/error y de tiempos."""
        print()
        print("=" * 60)
        print(f"{'COMPARACION PYTHON VS JAVA':^60}")
        print("=" * 60)
        print()
        print(f"{'N':<8}{'PI PYTHON':<13}{'PI JAVA':<13}"
              f"{'ERROR PY':<13}{'ERROR JAVA':<13}")
        print("-" * 60)
        for r_py, r_jv in zip(resultados_py, resultados_java):
            print(f"{r_py['n']:<8}{r_py['pi_estimado']:<13.6f}"
                  f"{r_jv['pi_estimado']:<13.6f}"
                  f"{r_py['error']:<13.6f}{r_jv['error']:.6f}")
        print()
        print(f"{'N':<8}{'TIEMPO PYTHON (ms)':<25}{'TIEMPO JAVA (ms)'}")
        print("-" * 50)
        for r_py, r_jv in zip(resultados_py, resultados_java):
            print(f"{r_py['n']:<8}{r_py['tiempo_ms']:<25.3f}{r_jv['tiempo_ms']:.3f}")
        print()

    def mostrar_conclusiones(self, lineas):
        """Muestra las conclusiones de la comparación."""
        print("CONCLUSIONES:")
        for linea in lineas:
            print(linea)
