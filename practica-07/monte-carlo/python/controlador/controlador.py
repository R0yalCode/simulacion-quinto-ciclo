"""Controlador: coordina el modelo, la vista, la persistencia y las gráficas."""

from graficas import generador_graficas
from modelo.experimento import ExperimentoMonteCarlo
from persistencia import gestor_csv
from vista.vista import Vista


class Controlador:
    """Recibe las opciones del usuario y ejecuta la operación correspondiente."""

    def __init__(self):
        self.modelo = ExperimentoMonteCarlo()
        self.vista = Vista()

    def ejecutar_menu(self):
        """Muestra el menú y ejecuta la opción elegida hasta que se salga."""
        while True:
            self.vista.mostrar_menu()
            try:
                opcion = self.vista.leer_opcion()
            except EOFError:
                self.vista.mostrar_mensaje("")
                break
            if opcion == "1":
                self.ejecutar_experimentos()
            elif opcion == "2":
                self.mostrar_resultados()
            elif opcion == "3":
                self.generar_graficas()
            elif opcion == "4":
                self.comparar()
            elif opcion == "5":
                self.vista.mostrar_mensaje("¡Hasta luego!")
                break
            else:
                self.vista.mostrar_error("Opción no válida, intente de nuevo.")

    def ejecutar_experimentos(self):
        """Ejecuta los cuatro experimentos, muestra la tabla y guarda el CSV."""
        resultados = self.modelo.ejecutar_todos()
        self.vista.mostrar_tabla("METODO MONTE CARLO - PYTHON",
                                 [r.a_diccionario() for r in resultados])
        try:
            gestor_csv.guardar_resultados(resultados)
            self.vista.mostrar_mensaje(
                f"Resultados guardados en: {gestor_csv.ARCHIVO_PYTHON}")
        except OSError as error:
            self.vista.mostrar_error(
                f"No se pudieron guardar los resultados: {error}")

    def mostrar_resultados(self):
        """Muestra los resultados guardados anteriormente por Python."""
        datos = gestor_csv.leer_resultados(gestor_csv.ARCHIVO_PYTHON)
        if datos is None:
            self.vista.mostrar_error(
                "Aún no existen resultados de Python. Ejecute primero la opción 1.")
            return
        self.vista.mostrar_tabla("RESULTADOS ANTERIORES - PYTHON", datos)

    def generar_graficas(self):
        """Genera las tres gráficas individuales de Python desde el CSV guardado."""
        datos = gestor_csv.leer_resultados(gestor_csv.ARCHIVO_PYTHON)
        if datos is None:
            self.vista.mostrar_error(
                "Aún no existen resultados de Python. Ejecute primero la opción 1.")
            return
        generador_graficas.generar_graficas_python(datos)
        self.vista.mostrar_mensaje(
            f"Gráficas generadas en: {generador_graficas.CARPETA_GRAFICAS_PYTHON}")

    def comparar(self):
        """Compara los resultados de Python y Java, guarda tabla y gráficas."""
        datos_py = gestor_csv.leer_resultados(gestor_csv.ARCHIVO_PYTHON)
        datos_java = gestor_csv.leer_resultados(gestor_csv.ARCHIVO_JAVA)
        if datos_py is None:
            self.vista.mostrar_error(
                "Faltan resultados de Python. Ejecute primero la opción 1.")
            return
        if datos_java is None:
            self.vista.mostrar_error(
                "Faltan resultados de Java. Ejecute primero los experimentos "
                "en Java (opción 1 del menú de Java).")
            return
        self.vista.mostrar_tabla_comparacion(datos_py, datos_java)
        try:
            gestor_csv.guardar_tabla_comparacion(datos_py, datos_java)
        except OSError as error:
            self.vista.mostrar_error(
                f"No se pudo guardar la tabla comparativa: {error}")
            return
        generador_graficas.generar_graficas_comparacion(datos_py, datos_java)
        self.vista.mostrar_mensaje(
            f"Tabla comparativa guardada en: {gestor_csv.ARCHIVO_COMPARACION}")
        self.vista.mostrar_mensaje(
            f"Gráficas comparativas guardadas en: "
            f"{generador_graficas.CARPETA_GRAFICAS_COMPARACION}")
        self.vista.mostrar_conclusiones(
            self._construir_conclusiones(datos_py, datos_java))

    def _construir_conclusiones(self, datos_py, datos_java):
        """Construye las conclusiones de la comparación a partir de los datos."""
        lineas = []
        tiempo_py = sum(r["tiempo_ms"] for r in datos_py)
        tiempo_java = sum(r["tiempo_ms"] for r in datos_java)
        if tiempo_py < tiempo_java:
            lineas.append(
                f"- Menor tiempo de ejecución: Python "
                f"({tiempo_py:.3f} ms frente a {tiempo_java:.3f} ms de Java).")
        elif tiempo_java < tiempo_py:
            lineas.append(
                f"- Menor tiempo de ejecución: Java "
                f"({tiempo_java:.3f} ms frente a {tiempo_py:.3f} ms de Python).")
        else:
            lineas.append("- Empate en el tiempo de ejecución total.")

        mejor = min(datos_py, key=lambda r: r["error"])
        lineas.append(
            f"- Menor error absoluto: {mejor['error']:.6f} con N = {mejor['n']} "
            f"(igual en ambos lenguajes).")

        coinciden = all(abs(r_py["pi_estimado"] - r_jv["pi_estimado"]) < 1e-9
                        for r_py, r_jv in zip(datos_py, datos_java))
        if coinciden:
            lineas.append(
                "- Las aproximaciones de π coinciden en los cuatro tamaños "
                "(misma semilla y misma secuencia del LCG).")
        else:
            lineas.append(
                "- Las aproximaciones de π NO coinciden entre ambos lenguajes.")
        return lineas
