package persistencia;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

import modelo.ResultadoExperimento;

/**
 * Capa de persistencia: escritura y lectura del CSV de resultados de Java.
 *
 * Se usa Locale.US para que los números decimales usen punto, de modo que
 * el archivo sea compatible con el programa Python.
 */
public class GestorCSV {

    public static final Path CARPETA_RESULTADOS = Paths.get("resultados");
    public static final Path ARCHIVO_RESULTADOS =
            CARPETA_RESULTADOS.resolve("resultados_java.csv");

    private static final String ENCABEZADO =
            "n,puntos_circulo,pi_estimado,error,tiempo_ms";

    /** Guarda la lista de resultados en el CSV. */
    public void guardar(List<ResultadoExperimento> resultados) throws IOException {
        Files.createDirectories(CARPETA_RESULTADOS);
        List<String> lineas = new ArrayList<>();
        lineas.add(ENCABEZADO);
        for (ResultadoExperimento r : resultados) {
            lineas.add(String.format(Locale.US, "%d,%d,%.10f,%.10f,%.3f",
                    r.getN(), r.getPuntosEnCirculo(), r.getPiEstimado(),
                    r.getError(), r.getTiempoMs()));
        }
        Files.write(ARCHIVO_RESULTADOS, lineas, StandardCharsets.UTF_8);
    }

    /** Lee el CSV de resultados y devuelve la lista de resultados. */
    public List<ResultadoExperimento> leer() throws IOException {
        List<ResultadoExperimento> resultados = new ArrayList<>();
        List<String> lineas = Files.readAllLines(ARCHIVO_RESULTADOS, StandardCharsets.UTF_8);
        for (int i = 1; i < lineas.size(); i++) { // la línea 0 es el encabezado
            String linea = lineas.get(i).trim();
            if (linea.isEmpty()) {
                continue;
            }
            String[] partes = linea.split(",");
            int n = Integer.parseInt(partes[0].trim());
            long puntos = Long.parseLong(partes[1].trim());
            double pi = Double.parseDouble(partes[2].trim());
            double error = Double.parseDouble(partes[3].trim());
            double tiempo = Double.parseDouble(partes[4].trim());
            resultados.add(new ResultadoExperimento(n, puntos, pi, error, tiempo));
        }
        return resultados;
    }

    /** Indica si el CSV de resultados ya existe. */
    public static boolean existe() {
        return Files.isRegularFile(ARCHIVO_RESULTADOS);
    }
}
