package ec.edu.feirnnr.lcg.services;

import ec.edu.feirnnr.lcg.util.JsonUtil;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

/**
 * Exportación de resultados (capa de infraestructura).
 *
 * CSV (secuencias y frecuencias), JSON (resultados y configuración) y
 * nombres con marca de tiempo para no sobrescribir corridas anteriores.
 */
public final class ExportService {

    private static final DateTimeFormatter STAMP = DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss");

    /** Nombre con fecha/hora: prefijo_20261106_093012.ext. */
    public static String timestamped(String prefix, String ext) {
        return prefix + "_" + LocalDateTime.now().format(STAMP) + "." + ext;
    }

    public static Path writeCsv(Path path, List<String> header,
                                List<List<Object>> rows) throws IOException {
        Files.createDirectories(path.toAbsolutePath().getParent());
        StringBuilder sb = new StringBuilder();
        sb.append(String.join(",", header)).append('\n');
        for (List<Object> row : rows) {
            StringBuilder line = new StringBuilder();
            for (int i = 0; i < row.size(); i++) {
                if (i > 0) {
                    line.append(',');
                }
                line.append(normalizeCsvCell(row.get(i)));
            }
            sb.append(line).append('\n');
        }
        Files.writeString(path, sb.toString(), StandardCharsets.UTF_8,
                StandardOpenOption.CREATE, StandardOpenOption.TRUNCATE_EXISTING);
        return path;
    }

    private static String normalizeCsvCell(Object value) {
        if (value == null) {
            return "";
        }
        String text = String.valueOf(value);
        if (text.contains(",") || text.contains("\n") || text.contains("\"")) {
            return '"' + text.replace("\"", "\"\"") + '"';
        }
        return text;
    }

    /** CSV de secuencia completa (enteros y normalizados). */
    public static List<Path> exportSequence(Path outDir, String prefix,
                                           long[] states, double[] uniforms) throws IOException {
        List<Path> paths = new ArrayList<>();
        List<List<Object>> intRows = new ArrayList<>(states.length);
        List<List<Object>> dblRows = new ArrayList<>(states.length);
        for (int i = 0; i < states.length; i++) {
            intRows.add(List.of((long) (i + 1), states[i]));
            dblRows.add(List.of((long) (i + 1),
                    String.format(java.util.Locale.US, "%.12f", uniforms[i])));
        }
        paths.add(writeCsv(outDir.resolve(timestamped(prefix + "_enteros_java", "csv")),
                List.of("i", "X(n)"), intRows));
        paths.add(writeCsv(outDir.resolve(timestamped(prefix + "_normalizada_java", "csv")),
                List.of("i", "U(n)"), dblRows));
        return paths;
    }

    /** CSV de frecuencias Chi-cuadrado (intervalo, observada, esperada, contribución). */
    public static Path exportFrequencies(Path outDir, String prefix,
                                        ec.edu.feirnnr.lcg.core.TestResult chi) throws IOException {
        List<String> labels = detailList(chi, "interval_labels");
        List<Double> contributions = (List<Double>) chi.details().get("contributions");
        List<List<Object>> rows = new ArrayList<>(labels.size());
        for (int i = 0; i < labels.size(); i++) {
            rows.add(List.of(labels.get(i), chi.observed().get(i),
                    chi.expected().get(i), contributions.get(i)));
        }
        return writeCsv(outDir.resolve(timestamped(prefix, "csv")),
                List.of("intervalo", "observada", "esperada", "contribucion"), rows);
    }

    @SuppressWarnings("unchecked")
    private static List<String> detailList(ec.edu.feirnnr.lcg.core.TestResult result, String key) {
        return (List<String>) result.details().get(key);
    }

    /** JSON estructurado de resultados del pipeline completo. */
    public static Path exportResultsJson(Path outDir, String prefix,
                                         Map<String, Object> payload) throws IOException {
        Path path = outDir.resolve(timestamped(prefix, "json"));
        JsonUtil.writeFile(path, payload);
        return path;
    }

    /** Exporta la configuración activa (equivalente a parameters.json de Python). */
    public static Path exportConfig(Path path,
                                   ec.edu.feirnnr.lcg.config.AppConfig config) throws IOException {
        Map<String, Object> payload = JsonUtil.mapOf(
                "generator", JsonUtil.mapOf(
                        "seed", config.generator().seed(),
                        "multiplier", config.generator().multiplier(),
                        "increment", config.generator().increment(),
                        "modulus", config.generator().modulus(),
                        "n", config.generator().n()),
                "statistical", JsonUtil.mapOf(
                        "alpha", config.statistical().alpha(),
                        "intervals", config.statistical().intervals(),
                        "tolerance", config.statistical().tolerance()),
                "comparison_sizes", config.comparisonSizes(),
                "repetitions", config.repetitions());
        JsonUtil.writeFile(path, payload);
        return path;
    }

    /** Lee la configuración JSON (protocolo compartido) con validación. */
    public static ec.edu.feirnnr.lcg.config.AppConfig loadConfig(Path path) throws IOException {
        Map<String, Object> root = JsonUtil.readFile(path);
        return fromMap(root);
    }

    public static ec.edu.feirnnr.lcg.config.AppConfig fromMap(Map<String, Object> root) {
        @SuppressWarnings("unchecked")
        Map<String, Object> generator = asMap(root.get("generator"));
        @SuppressWarnings("unchecked")
        Map<String, Object> statistical = asMap(root.get("statistical"));
        if (generator == null || statistical == null) {
            throw new IllegalArgumentException(
                    "Configuración inválida: faltan bloques generator/statistical.");
        }
        ec.edu.feirnnr.lcg.config.GeneratorParameters generatorParameters =
                new ec.edu.feirnnr.lcg.config.GeneratorParameters(
                        asLong(generator.get("seed"), 12345),
                        asLong(generator.get("multiplier"), 1664525),
                        asLong(generator.get("increment"), 1013904223),
                        asLong(generator.get("modulus"), 4294967296L),
                        asLong(generator.get("n"), 1000));
        ec.edu.feirnnr.lcg.config.StatisticalParameters statisticalParameters =
                new ec.edu.feirnnr.lcg.config.StatisticalParameters(
                        asDouble(statistical.get("alpha"), 0.05),
                        (int) asLong(statistical.get("intervals"), 10),
                        asDouble(statistical.get("tolerance"), 1e-4));
        List<Long> sizes = new ArrayList<>();
        Object rawSizes = root.get("comparison_sizes");
        if (rawSizes instanceof List<?> list) {
            for (Object item : list) {
                sizes.add(asLong(item, 0));
            }
        }
        int repetitions = (int) asLong(root.get("repetitions"), 3);
        ec.edu.feirnnr.lcg.config.AppConfig config = new ec.edu.feirnnr.lcg.config.AppConfig(
                generatorParameters, statisticalParameters, sizes, repetitions);
        config.validate();
        return config;
    }

    @SuppressWarnings("unchecked")
    private static Map<String, Object> asMap(Object value) {
        return (Map<String, Object>) value;
    }

    private static long asLong(Object value, long fallback) {
        if (value == null) {
            return fallback;
        }
        if (value instanceof Number number) {
            return number.longValue();
        }
        return Long.parseLong(String.valueOf(value));
    }

    private static double asDouble(Object value, double fallback) {
        if (value == null) {
            return fallback;
        }
        if (value instanceof Number number) {
            return number.doubleValue();
        }
        return Double.parseDouble(String.valueOf(value));
    }
}
