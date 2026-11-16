package controlador;

import java.io.IOException;
import java.util.List;

import graficas.GeneradorGraficas;
import modelo.ExperimentoMonteCarlo;
import modelo.ResultadoExperimento;
import persistencia.GestorCSV;
import vista.Vista;

/**
 * Controlador: recibe las opciones del usuario y coordina el modelo,
 * la vista, la persistencia y la generación de gráficas.
 */
public class Controlador {

    private final Vista vista;
    private final ExperimentoMonteCarlo modelo = new ExperimentoMonteCarlo();
    private final GestorCSV gestorCSV = new GestorCSV();
    private final GeneradorGraficas generadorGraficas = new GeneradorGraficas();

    public Controlador(Vista vista) {
        this.vista = vista;
    }

    /** Ejecuta los cuatro experimentos, muestra la tabla y guarda el CSV. */
    public void ejecutarExperimentos() {
        List<ResultadoExperimento> resultados = modelo.ejecutarTodos();
        vista.mostrarTabla("METODO MONTE CARLO - JAVA", resultados);
        try {
            gestorCSV.guardar(resultados);
            vista.mostrarMensaje(
                    "Resultados guardados en: " + GestorCSV.ARCHIVO_RESULTADOS);
        } catch (IOException excepcion) {
            vista.mostrarError("No se pudieron guardar los resultados: "
                    + excepcion.getMessage());
        }
    }

    /** Muestra los resultados guardados anteriormente por Java. */
    public void mostrarResultados() {
        if (!GestorCSV.existe()) {
            vista.mostrarError("Aún no existen resultados de Java. "
                    + "Ejecute primero la opción 1.");
            return;
        }
        try {
            vista.mostrarTabla("RESULTADOS ANTERIORES - JAVA", gestorCSV.leer());
        } catch (IOException excepcion) {
            vista.mostrarError("No se pudieron leer los resultados: "
                    + excepcion.getMessage());
        }
    }

    /** Genera las tres gráficas individuales de Java desde el CSV guardado. */
    public void generarGraficas() {
        if (!GestorCSV.existe()) {
            vista.mostrarError("Aún no existen resultados de Java. "
                    + "Ejecute primero la opción 1.");
            return;
        }
        try {
            generadorGraficas.generarTodas(gestorCSV.leer());
            vista.mostrarMensaje("Gráficas generadas en: "
                    + GeneradorGraficas.CARPETA_GRAFICAS.toAbsolutePath());
        } catch (IOException excepcion) {
            vista.mostrarError("No se pudieron generar las gráficas: "
                    + excepcion.getMessage());
        }
    }
}
