package ec.edu.feirnnr.lcg.services;

import ec.edu.feirnnr.lcg.config.AppConfig;
import ec.edu.feirnnr.lcg.config.GeneratorParameters;
import ec.edu.feirnnr.lcg.config.StatisticalParameters;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

/**
 * Pruebas de configuración y exportación: ida y vuelta del JSON compartido,
 * validaciones en español y CSV con escape correcto.
 */
class ExportServiceTest {

    @TempDir
    Path tempDir;

    @Test
    void configuracionIdaYVueltaConservaValores() throws IOException {
        AppConfig original = new AppConfig(
                new GeneratorParameters(7L, 1103515245L, 12345L, 2147483648L, 1234L),
                new StatisticalParameters(0.01, 8, 1e-6),
                List.of(500L, 5000L),
                2);
        Path path = tempDir.resolve("parameters.json");
        ExportService.exportConfig(path, original);

        AppConfig loaded = ExportService.loadConfig(path);
        assertEquals(original.generator(), loaded.generator());
        assertEquals(original.statistical(), loaded.statistical());
        assertEquals(original.comparisonSizes(), loaded.comparisonSizes());
        assertEquals(original.repetitions(), loaded.repetitions());
    }

    @Test
    void configuracionInvalidaEsRechazada() {
        AppConfig seedFueraDeRango = new AppConfig(
                new GeneratorParameters(10L, 5L, 1L, 10L, 100L),
                StatisticalParameters.defaults(),
                List.of(1000L), 1);
        assertThrows(IllegalArgumentException.class, seedFueraDeRango::validate);

        AppConfig sinTamanos = new AppConfig(
                GeneratorParameters.defaults(),
                StatisticalParameters.defaults(),
                List.of(), 1);
        assertThrows(IllegalArgumentException.class, sinTamanos::validate);

        AppConfig repeticionesInvalidas = new AppConfig(
                GeneratorParameters.defaults(),
                StatisticalParameters.defaults(),
                List.of(1000L), 0);
        assertThrows(IllegalArgumentException.class, repeticionesInvalidas::validate);
    }

    @Test
    void jsonIncompletoLanzaMensajeClaro() {
        IllegalArgumentException error = assertThrows(IllegalArgumentException.class,
                () -> ExportService.fromMap(java.util.Map.of("repetitions", 3)));
        assertTrue(error.getMessage().contains("generator/statistical"));
    }

    @Test
    void csvEscapaComasYComillas() throws IOException {
        Path path = tempDir.resolve("salida.csv");
        ExportService.writeCsv(path, List.of("a", "b"), List.of(
                List.of("simple", 1),
                List.of("con,coma", "con\"comilla")));
        String content = Files.readString(path, StandardCharsets.UTF_8);
        assertTrue(content.startsWith("a,b\n"));
        assertTrue(content.contains("\"con,coma\",\"con\"\"comilla\""));
    }

    @Test
    void exportacionDeSecuenciaGeneraDosArchivos() throws IOException {
        long[] states = {6, 7, 4, 5};
        double[] uniforms = {0.75, 0.875, 0.5, 0.625};
        List<Path> paths = ExportService.exportSequence(tempDir, "prueba", states, uniforms);
        assertEquals(2, paths.size());
        for (Path path : paths) {
            assertTrue(Files.exists(path));
            assertTrue(Files.readString(path, StandardCharsets.UTF_8).startsWith("i,"));
        }
        String enteros = Files.readString(paths.get(0), StandardCharsets.UTF_8);
        assertTrue(enteros.contains("1,6"));
        assertTrue(enteros.contains("4,5"));
    }
}
