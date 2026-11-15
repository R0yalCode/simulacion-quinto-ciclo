package vista;

import java.util.List;
import java.util.Locale;
import java.util.Scanner;

import modelo.ResultadoExperimento;

/**
 * Vista: menús, lectura de opciones y presentación de tablas en la terminal.
 */
public class Vista {

    private final Scanner scanner = new Scanner(System.in);

    /** Muestra el menú principal del programa Java. */
    public void mostrarMenu() {
        System.out.println();
        System.out.println("=====================================");
        System.out.println("   METODO MONTE CARLO - MENU (JAVA)  ");
        System.out.println("=====================================");
        System.out.println("1. Ejecutar experimentos en Java");
        System.out.println("2. Mostrar resultados anteriores de Java");
        System.out.println("3. Generar gráficas de Java");
        System.out.println("4. Salir");
    }

    /** Lee la opción escrita por el usuario. */
    public String leerOpcion() {
        System.out.print("Seleccione una opción: ");
        return scanner.nextLine().trim();
    }

    /** Muestra un mensaje informativo. */
    public void mostrarMensaje(String mensaje) {
        System.out.println(mensaje);
    }

    /** Muestra un mensaje de error. */
    public void mostrarError(String mensaje) {
        System.out.println("ERROR: " + mensaje);
    }

    /** Muestra la tabla de resultados con el formato de la práctica. */
    public void mostrarTabla(String titulo, List<ResultadoExperimento> resultados) {
        System.out.println();
        System.out.println("======================================");
        System.out.println(centrar(titulo, 38));
        System.out.println("======================================");
        System.out.println();
        System.out.printf(Locale.US, "%-14s%-20s%-18s%s%n",
                "N", "PI ESTIMADO", "ERROR", "TIEMPO (ms)");
        System.out.println("-".repeat(70));
        for (ResultadoExperimento r : resultados) {
            System.out.printf(Locale.US, "%-14d%-20.6f%-18.6f%.3f%n",
                    r.getN(), r.getPiEstimado(), r.getError(), r.getTiempoMs());
        }
        System.out.println();
    }

    /** Centra un texto dentro de un ancho fijo. */
    private String centrar(String texto, int ancho) {
        int espacios = Math.max(0, (ancho - texto.length()) / 2);
        return " ".repeat(espacios) + texto;
    }
}
