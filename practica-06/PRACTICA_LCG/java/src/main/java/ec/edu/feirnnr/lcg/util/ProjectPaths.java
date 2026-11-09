package ec.edu.feirnnr.lcg.util;

import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

/**
 * Rutas canónicas del proyecto (capa de infraestructura).
 *
 * Localiza la raíz del proyecto (directorio que contiene python/ y java/)
 * subiendo desde el directorio de trabajo, de modo que los resultados se
 * guarden siempre en java/results/ independientemente de dónde se ejecute
 * el JAR. Si no se encuentra, se usa el directorio actual.
 */
public final class ProjectPaths {

    private static final Path ROOT = detectRoot();

    private ProjectPaths() {
    }

    private static Path detectRoot() {
        Path current = Paths.get("").toAbsolutePath().normalize();
        for (int i = 0; i < 6 && current != null; i++) {
            if (Files.isDirectory(current.resolve("python"))
                    && Files.isDirectory(current.resolve("java"))) {
                return current;
            }
            current = current.getParent();
        }
        return Paths.get("").toAbsolutePath().normalize();
    }

    public static Path root() {
        return ROOT;
    }

    public static Path javaResults() {
        return ROOT.resolve("java").resolve("results");
    }

    public static Path sequencesDir() {
        return javaResults().resolve("sequences");
    }

    public static Path graphsDir() {
        return javaResults().resolve("graphs");
    }

    public static Path reportsDir() {
        return javaResults().resolve("reports");
    }

    public static Path configPath() {
        return ROOT.resolve("java").resolve("config").resolve("parameters.json");
    }

    public static Path comparisonDir() {
        return ROOT.resolve("results");
    }
}
