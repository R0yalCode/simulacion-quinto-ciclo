/*
 * Modelo Java: Generador Congruencial Lineal (LCG)
 * Fórmula:      X(n+1) = (a * X(n) + c) mod m
 * Normalización: U(n)  = (double) X(n) / m
 *
 * Se reciben los parámetros por línea de comandos:
 *   java GeneradorLCG <a> <c> <m> <semilla> <cantidad> <archivo_csv>
 */
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.Locale;

public class GeneradorLCG {

    private long a;
    private long c;
    private long m;
    private long semilla;
    private long cantidad;

    public GeneradorLCG(long a, long c, long m, long semilla, long cantidad) {
        this.a = a;
        this.c = c;
        this.m = m;
        this.semilla = semilla;
        this.cantidad = cantidad;
    }

    // Permite cambiar la semilla sin reconstruir el generador
    public void cambiarSemilla(long nuevaSemilla) {
        this.semilla = nuevaSemilla;
    }

    // Ejecuta el LCG y escribe el CSV con columnas: n, X(n), U(n)
    public void generar(String rutaCsv) throws IOException {
        PrintWriter pw = new PrintWriter(new FileWriter(rutaCsv));
        pw.println("n,X(n),U(n)");

        long x = semilla;
        for (long i = 0; i < cantidad; i++) {
            x = (a * x + c) % m;                    // Recurrencia LCG
            double u = (double) x / (double) m;     // Normalización
            pw.println(i + "," + x + "," + String.format(Locale.US, "%.15f", u));
        }
        pw.close();
    }

    public static void main(String[] args) {
        if (args.length < 6) {
            System.out.println("Uso: java GeneradorLCG <a> <c> <m> <semilla> <cantidad> <archivo_csv>");
            return;
        }
        try {
            long a = Long.parseLong(args[0]);
            long c = Long.parseLong(args[1]);
            long m = Long.parseLong(args[2]);
            long semilla = Long.parseLong(args[3]);
            long cantidad = Long.parseLong(args[4]);
            String rutaCsv = args[5];

            GeneradorLCG generador = new GeneradorLCG(a, c, m, semilla, cantidad);
            generador.generar(rutaCsv);
            System.out.println("Generadas " + cantidad + " observaciones en " + rutaCsv);
        } catch (NumberFormatException e) {
            System.out.println("Error: los parámetros numéricos no son válidos.");
        } catch (IOException e) {
            System.out.println("Error al escribir el archivo CSV: " + e.getMessage());
        }
    }
}
