import java.util.NoSuchElementException;

import controlador.Controlador;
import vista.Vista;

/**
 * Punto de entrada del programa Java de la práctica Monte Carlo.
 *
 * Ejecución (desde la carpeta java/):
 *   java -cp "bin:lib/jfreechart-1.5.5.jar" Main
 */
public class Main {

    public static void main(String[] args) {
        System.setProperty("java.awt.headless", "true");

        Vista vista = new Vista();
        Controlador controlador = new Controlador(vista);

        // Modo no interactivo usado por el lanzador principal de la raíz:
        // "graficas" genera las gráficas de Java desde el CSV guardado y termina.
        if (args.length > 0 && "graficas".equalsIgnoreCase(args[0])) {
            controlador.generarGraficas();
            return;
        }

        boolean salir = false;

        while (!salir) {
            vista.mostrarMenu();
            String opcion;
            try {
                opcion = vista.leerOpcion();
            } catch (NoSuchElementException excepcion) {
                break; // entrada terminada (por ejemplo, Ctrl+D)
            }
            switch (opcion) {
                case "1" -> controlador.ejecutarExperimentos();
                case "2" -> controlador.mostrarResultados();
                case "3" -> controlador.generarGraficas();
                case "4" -> {
                    vista.mostrarMensaje("¡Hasta luego!");
                    salir = true;
                }
                default -> vista.mostrarError("Opción no válida, intente de nuevo.");
            }
        }
    }
}
