package ec.edu.feirnnr.lcg.services;

import ec.edu.feirnnr.lcg.config.AppConfig;
import ec.edu.feirnnr.lcg.config.GeneratorParameters;
import ec.edu.feirnnr.lcg.config.StatisticalParameters;
import ec.edu.feirnnr.lcg.core.ChiSquareTest;
import ec.edu.feirnnr.lcg.core.KolmogorovSmirnovTest;
import ec.edu.feirnnr.lcg.core.LCG;
import ec.edu.feirnnr.lcg.core.TestResult;
import ec.edu.feirnnr.lcg.util.Ansi;
import ec.edu.feirnnr.lcg.util.JsonUtil;
import ec.edu.feirnnr.lcg.util.ProjectPaths;
import ec.edu.feirnnr.lcg.visualization.ChartService;

import java.io.IOException;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Locale;
import java.util.NoSuchElementException;
import java.util.Scanner;

/**
 * Menús interactivos de la implementación Java (capa de presentación).
 *
 * Mantiene la independencia de Java: no requiere Python. Reutiliza los
 * servicios de ejecución/exportación y las estrategias estadísticas.
 */
public final class MenuService {

    private final Ansi ui = Ansi.get();
    private final Scanner scanner = new Scanner(System.in);
    private final ExecutionService execution = new ExecutionService();
    private final ChartService charts = new ChartService();
    private final String[] args;

    private AppConfig config;
    private ExecutionService.Generation generation;
    private TestResult lastChi;
    private TestResult lastKs;

    public MenuService(AppConfig config, String[] args) {
        this.config = config;
        this.args = args;
    }

    // ------------------------------------------------------------------ #
    // Ciclo principal
    // ------------------------------------------------------------------ #
    public void run() {
        ui.printBanner("SISTEMA DE SIMULACIÓN ESTADÍSTICA — JAVA",
                "GENERADOR PSEUDOALEATORIO LCG Y PRUEBAS DE UNIFORMIDAD");
        while (true) {
            String option;
            try {
                option = mainMenu();
            } catch (NoSuchElementException endOfInput) {
                ui.printWarning("Entrada estándar cerrada. Saliendo.");
                return;
            }
            switch (option) {
                case "0" -> {
                    ui.printSuccess("Gracias por usar la implementación Java. ¡Hasta pronto!");
                    return;
                }
                case "1" -> executionLoop();
                case "2" -> configureParameters();
                case "3" -> showInformation();
                default -> ui.printError("Opción inválida.");
            }
        }
    }

    private String mainMenu() {
        System.out.println();
        table("MENÚ PRINCIPAL", List.of("Opción", "Acción"), List.of(
                List.of("[1]", "Ejecutar implementación Java (menú de ejecución)"),
                List.of("[2]", "Configurar parámetros del generador"),
                List.of("[3]", "Consultar información de la práctica"),
                List.of("[0]", "Salir del programa")
        ), new boolean[]{false, false});
        return readOption("Seleccione una opción", "0", "1", "2", "3");
    }

    private void executionLoop() {
        while (true) {
            String option;
            try {
                option = executionMenu();
            } catch (NoSuchElementException endOfInput) {
                return;
            }
            switch (option) {
                case "0" -> {
                    return;
                }
                case "1" -> generateAction();
                case "2" -> chiSquareAction();
                case "3" -> ksAction();
                case "4" -> fullAction();
                default -> ui.printError("Opción inválida.");
            }
        }
    }

    private String executionMenu() {
        ui.printSection("MENÚ DE EJECUCIÓN — JAVA");
        table("", List.of("Opción", "Acción"), List.of(
                List.of("[1]", "Generar números pseudoaleatorios (LCG)"),
                List.of("[2]", "Ejecutar prueba Chi-cuadrado"),
                List.of("[3]", "Ejecutar prueba Kolmogorov-Smirnov"),
                List.of("[4]", "Ejecutar proceso completo (pruebas + gráficas + reporte)"),
                List.of("[0]", "Regresar al menú principal")
        ), new boolean[]{false, false});
        showConfig();
        return readOption("Seleccione una opción", "0", "1", "2", "3", "4");
    }

    // ------------------------------------------------------------------ #
    // Acciones
    // ------------------------------------------------------------------ #
    private void generateAction() {
        try {
            generation = execution.generateOnly(ExecutionService.adapt(config));
            ui.printSuccess(String.format(Locale.US, "Secuencia generada: N = %d en %.2f ms",
                    generation.states().length, generation.seconds() * 1000.0));
            showPreview();
            showSequenceStats();
            List<Path> paths = ExportService.exportSequence(
                    ProjectPaths.sequencesDir(), "secuencia_n" + config.generator().n(),
                    generation.states(), generation.uniforms());
            printPaths(paths, "Secuencias exportadas");
        } catch (IllegalArgumentException | IOException exc) {
            ui.printError(exc.getMessage());
        }
    }

    private void chiSquareAction() {
        ui.printSection("PRUEBA CHI-CUADRADO — JAVA");
        try {
            ensureGeneration();
            ChiSquareTest test = new ChiSquareTest();
            long start = System.nanoTime();
            lastChi = test.execute(generation.uniforms(), config.statistical().alpha(),
                    config.statistical().intervals());
            double seconds = (System.nanoTime() - start) / 1e9;

            showChiFrequencyTable(lastChi);
            showSummary(lastChi);
            ui.printSuccess(String.format(Locale.US, "Tiempo de cálculo: %.2f ms",
                    seconds * 1000.0));
            ExportService.exportFrequencies(ProjectPaths.reportsDir(),
                    "frecuencias_chi_square_java_n" + lastChi.sampleSize, lastChi);
        } catch (IllegalArgumentException | IOException exc) {
            ui.printError(exc.getMessage());
        }
    }

    private void ksAction() {
        ui.printSection("PRUEBA KOLMOGOROV-SMIRNOV — JAVA");
        try {
            ensureGeneration();
            KolmogorovSmirnovTest test = new KolmogorovSmirnovTest();
            long start = System.nanoTime();
            lastKs = test.execute(generation.uniforms(), config.statistical().alpha(),
                    config.statistical().intervals());
            double seconds = (System.nanoTime() - start) / 1e9;
            showSummary(lastKs);
            ui.printSuccess(String.format(Locale.US, "Tiempo de cálculo: %.2f ms",
                    seconds * 1000.0));
        } catch (IllegalArgumentException exc) {
            ui.printError(exc.getMessage());
        }
    }

    private void fullAction() {
        ui.printSection("PROCESO COMPLETO — JAVA");
        try {
            ExecutionService.Pipeline pipeline = execution.runMeasured(
                    ExecutionService.adapt(config), config.repetitions());
            generation = new ExecutionService.Generation(
                    pipeline.states(), pipeline.uniforms(),
                    pipeline.seconds("generation"));
            lastChi = pipeline.chi();
            lastKs = pipeline.ks();
            showPreview();
            showChiFrequencyTable(lastChi);
            showFullSummary(pipeline);

            List<Path> paths = new ArrayList<>();
            paths.addAll(ExportService.exportSequence(ProjectPaths.sequencesDir(),
                    "secuencia_n" + config.generator().n(),
                    pipeline.states(), pipeline.uniforms()));
            paths.add(ExportService.exportFrequencies(ProjectPaths.reportsDir(),
                    "frecuencias_chi_square_java_n" + pipeline.chi().sampleSize,
                    pipeline.chi()));
            paths.addAll(charts.exportAll(ProjectPaths.graphsDir(),
                    "lcg_java_n" + config.generator().n(),
                    pipeline.uniforms(), config.statistical().intervals()));
            paths.add(ExportService.exportResultsJson(ProjectPaths.reportsDir(),
                    "resultados_java", execution.headlessPayload(
                            ExecutionService.adapt(config), pipeline)));
            printPaths(paths, "Archivos generados");
        } catch (IllegalArgumentException | IOException exc) {
            ui.printError(exc.getMessage());
        }
    }

    private void ensureGeneration() {
        if (generation == null) {
            generation = execution.generateOnly(ExecutionService.adapt(config));
            ui.printWarning("Secuencia generada automáticamente antes de la prueba.");
        }
    }

    // ------------------------------------------------------------------ #
    // Configuración
    // ------------------------------------------------------------------ #
    private void configureParameters() {
        ui.printSection("CONFIGURACIÓN DE PARÁMETROS — JAVA");
        showConfig();
        System.out.println(ui.dim("Deje vacío para conservar el valor actual."));
        try {
            GeneratorParameters g = config.generator();
            StatisticalParameters s = config.statistical();
            GeneratorParameters newGenerator = new GeneratorParameters(
                    readLong("Semilla X0", g.seed()),
                    readLong("Multiplicador a", g.multiplier()),
                    readLong("Incremento c", g.increment()),
                    readLong("Módulo m", g.modulus()),
                    readLong("Cantidad de números N", g.n())
            );
            StatisticalParameters newStatistical = new StatisticalParameters(
                    readDouble("Nivel de significancia α", s.alpha()),
                    (int) readLong("Número de intervalos k", s.intervals()),
                    readDouble("Tolerancia comparativa", s.tolerance())
            );
            System.out.print("Tamaños N comparativos separados por espacios "
                    + "(actual: " + config.comparisonSizes() + "): ");
            String rawSizes = scanner.nextLine().trim();
            List<Long> sizes = config.comparisonSizes();
            if (!rawSizes.isEmpty()) {
                sizes = new ArrayList<>();
                for (String token : rawSizes.replace(",", " ").split("\\s+")) {
                    sizes.add(Long.parseLong(token));
                }
            }
            int repetitions = (int) readLong("Repeticiones para promediar tiempos",
                    config.repetitions());

            AppConfig candidate = new AppConfig(newGenerator, newStatistical, sizes, repetitions);
            candidate.validate();
            ExportService.exportConfig(ProjectPaths.configPath(), candidate);
            this.config = candidate;
            this.generation = null;
            ui.printSuccess("Configuración guardada en " + ProjectPaths.configPath());
        } catch (IllegalArgumentException | IOException exc) {
            ui.printError("Configuración no aplicada: " + exc.getMessage());
        }
    }

    private void showConfig() {
        GeneratorParameters g = config.generator();
        StatisticalParameters s = config.statistical();
        table("Configuración actual", List.of("Parámetro", "Valor"), List.of(
                List.of("Semilla X0", String.valueOf(g.seed())),
                List.of("Multiplicador a", String.valueOf(g.multiplier())),
                List.of("Incremento c", String.valueOf(g.increment())),
                List.of("Módulo m", String.valueOf(g.modulus())),
                List.of("Cantidad de números N", String.valueOf(g.n())),
                List.of("Nivel de significancia α", String.valueOf(s.alpha())),
                List.of("Número de intervalos k", String.valueOf(s.intervals())),
                List.of("Tolerancia comparativa", String.valueOf(s.tolerance())),
                List.of("Repeticiones para tiempos", String.valueOf(config.repetitions()))
        ), new boolean[]{false, false});
    }

    // ------------------------------------------------------------------ #
    // Información
    // ------------------------------------------------------------------ #
    private void showInformation() {
        ui.printSection("INFORMACIÓN DE LA PRÁCTICA");
        System.out.println(ui.cyan("Método congruencial lineal (LCG)"));
        System.out.println("  X(n+1) = (a·X(n) + c) mod m;  U(n) = X(n)/m.");
        System.out.println("  Por defecto: X0 = 12345, a = 1664525, c = 1013904223, m = 2^32.");
        System.out.println();
        System.out.println(ui.cyan("Hipótesis estadísticas (α = 0.05)"));
        System.out.println("  H0: los datos siguen una distribución Uniforme U(0,1).");
        System.out.println("  H1: los datos no siguen una distribución U(0,1).");
        System.out.println("  Criterio: si p ≥ α no se rechaza H0; si p < α se rechaza H0.");
        System.out.println();
        System.out.println(ui.cyan("Prueba Chi-cuadrado"));
        System.out.println("  10 intervalos en [0,1); Ei = N/10; gl = 9.");
        System.out.println("  χ² = Σ (Oi − Ei)² / Ei; valor p de la distribución χ².");
        System.out.println();
        System.out.println(ui.cyan("Prueba Kolmogorov-Smirnov"));
        System.out.println("  D+ = max(i/N − U(i)); D− = max(U(i) − (i−1)/N); D = max(D+, D−).");
        System.out.println("  Con datos discretos (módulos pequeños) el valor p es aproximado.");
    }

    // ------------------------------------------------------------------ #
    // Tablas y presentación
    // ------------------------------------------------------------------ #
    private void showPreview() {
        long[] states = generation.states();
        double[] uniforms = generation.uniforms();
        int count = Math.min(10, states.length);
        List<List<String>> rows = new ArrayList<>(count);
        for (int i = 0; i < count; i++) {
            rows.add(List.of(String.valueOf(i + 1), String.valueOf(states[i]),
                    String.format(Locale.US, "%.6f", uniforms[i]),
                    String.format(Locale.US, "%.10f", uniforms[i])));
        }
        table("Primeros números generados",
                List.of("i", "X(i) entero", "U(i) = X/m", "U(i) 10 decimales"),
                rows, new boolean[]{true, true, true, true});
    }

    private void showSequenceStats() {
        long[] states = generation.states();
        double[] uniforms = generation.uniforms();
        double min = Arrays.stream(uniforms).min().orElse(Double.NaN);
        double max = Arrays.stream(uniforms).max().orElse(Double.NaN);
        double mean = Arrays.stream(uniforms).average().orElse(Double.NaN);
        table("Resumen de la secuencia", List.of("Serie", "Mínimo", "Media", "Máximo"),
                List.of(List.of("N = " + states.length,
                        String.format(Locale.US, "%.8f", min),
                        String.format(Locale.US, "%.8f", mean),
                        String.format(Locale.US, "%.8f", max))),
                new boolean[]{false, true, true, true});
    }

    private void showChiFrequencyTable(TestResult result) {
        @SuppressWarnings("unchecked")
        List<String> labels = (List<String>) result.details().get("interval_labels");
        @SuppressWarnings("unchecked")
        List<Double> contributions = (List<Double>) result.details().get("contributions");
        List<List<String>> rows = new ArrayList<>();
        for (int i = 0; i < labels.size(); i++) {
            rows.add(List.of("[" + labels.get(i) + "]",
                    String.valueOf(result.observed().get(i)),
                    String.format(Locale.US, "%.1f", result.expected().get(i)),
                    String.format(Locale.US, "%.4f", contributions.get(i))));
        }
        table("Tabla de frecuencias — Chi-cuadrado (N = " + result.sampleSize + ")",
                List.of("Intervalo", "Observada", "Esperada", "(Oi−Ei)²/Ei"),
                rows, new boolean[]{false, true, true, true});
    }

    private void showSummary(TestResult result) {
        List<List<String>> rows = new ArrayList<>();
        rows.add(List.of("Prueba", result.testName));
        if (result.degreesFreedom != null) {
            rows.add(List.of("Grados de libertad", String.valueOf(result.degreesFreedom)));
            rows.add(List.of("Estadístico Chi-cuadrado",
                    String.format(Locale.US, "%.6f", result.statistic)));
            rows.add(List.of("Valor p Chi-cuadrado",
                    String.format(Locale.US, "%.6f", result.pValue)));
        } else {
            rows.add(List.of("Estadístico D Kolmogorov-Smirnov",
                    String.format(Locale.US, "%.6f", result.statistic)));
            rows.add(List.of("Valor p Kolmogorov-Smirnov",
                    String.format(Locale.US, "%.6f", result.pValue)));
            rows.add(List.of("D+ / D−", String.format(Locale.US, "%.6f / %.6f",
                    ((Number) result.details.get("d_plus")).doubleValue(),
                    ((Number) result.details.get("d_minus")).doubleValue())));
        }
        rows.add(List.of("Cantidad de datos", String.valueOf(result.sampleSize)));
        rows.add(List.of("Nivel de significancia", String.valueOf(result.alpha)));
        rows.add(List.of("Decisión", result.rejectH0 ? "Se rechaza H0" : "No se rechaza H0"));
        table("Resumen estadístico — " + result.testName, List.of("Indicador", "Resultado"),
                rows, new boolean[]{false, false});
        String color = result.rejectH0 ? ui.red(result.decision) : ui.green(result.decision);
        System.out.println("\nInterpretación: " + color);
    }

    private void showFullSummary(ExecutionService.Pipeline pipeline) {
        TestResult chi = pipeline.chi();
        TestResult ks = pipeline.ks();
        List<List<String>> rows = new ArrayList<>();
        rows.add(List.of("Cantidad de datos", String.valueOf(chi.sampleSize)));
        rows.add(List.of("Estadístico Chi-cuadrado",
                String.format(Locale.US, "%.6f", chi.statistic)));
        rows.add(List.of("Grados de libertad", String.valueOf(chi.degreesFreedom)));
        rows.add(List.of("Valor p Chi-cuadrado",
                String.format(Locale.US, "%.6f", chi.pValue)));
        rows.add(List.of("Estadístico KS", String.format(Locale.US, "%.6f", ks.statistic)));
        rows.add(List.of("Valor p KS", String.format(Locale.US, "%.6f", ks.pValue)));
        rows.add(List.of("Nivel de significancia", String.valueOf(chi.alpha)));
        rows.add(List.of("Tiempo generación LCG", millis(pipeline.seconds("generation"))));
        rows.add(List.of("Tiempo Chi-cuadrado", millis(pipeline.seconds("chi_square"))));
        rows.add(List.of("Tiempo Kolmogorov-Smirnov", millis(pipeline.seconds("ks"))));
        rows.add(List.of("Tiempo proceso estadístico", millis(pipeline.seconds("total"))));
        rows.add(List.of("Decisión Chi-cuadrado",
                chi.rejectH0 ? "Se rechaza H0" : "No se rechaza H0"));
        rows.add(List.of("Decisión KS", ks.rejectH0 ? "Se rechaza H0" : "No se rechaza H0"));
        table("Resumen del proceso completo — Java", List.of("Indicador", "Resultado"),
                rows, new boolean[]{false, false});
    }

    private static String millis(double seconds) {
        return String.format(Locale.US, "%.2f ms", seconds * 1000.0);
    }

    private void printPaths(List<Path> paths, String label) {
        if (paths.isEmpty()) {
            return;
        }
        List<List<String>> rows = new ArrayList<>();
        for (Path path : paths) {
            rows.add(List.of(path.toString()));
        }
        table(label, List.of("Archivo"), rows, new boolean[]{false});
    }

    /** Tabla ASCII simple con anchos calculados dinámicamente. */
    private void table(String title, List<String> headers, List<List<String>> rows,
                       boolean[] rightAlign) {
        if (!title.isEmpty()) {
            System.out.println();
            System.out.println(ui.cyan(title));
        }
        int columns = headers.size();
        int[] widths = new int[columns];
        for (int i = 0; i < columns; i++) {
            widths[i] = headers.get(i).length();
        }
        for (List<String> row : rows) {
            for (int i = 0; i < columns && i < row.size(); i++) {
                widths[i] = Math.max(widths[i], row.get(i).length());
            }
        }
        String separator = "-".repeat(Arrays.stream(widths).sum() + 3 * (columns - 1) + 2);
        System.out.println(separator);
        System.out.println(" " + formatRow(headers, widths, new boolean[columns]));
        System.out.println(separator);
        for (List<String> row : rows) {
            System.out.println(" " + formatRow(row, widths, rightAlign));
        }
        System.out.println(separator);
    }

    private static String formatRow(List<String> cells, int[] widths, boolean[] rightAlign) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < widths.length; i++) {
            String cell = i < cells.size() ? cells.get(i) : "";
            if (i > 0) {
                sb.append(" | ");
            }
            if (rightAlign.length > i && rightAlign[i]) {
                sb.append(String.format("%" + widths[i] + "s", cell));
            } else {
                sb.append(String.format("%-" + widths[i] + "s", cell));
            }
        }
        return sb.toString();
    }

    // ------------------------------------------------------------------ #
    // Lectura de entradas
    // ------------------------------------------------------------------ #
    private String readOption(String prompt, String... valid) {
        while (true) {
            System.out.print("\n" + ui.yellow(prompt) + ": ");
            String value = scanner.nextLine().trim();
            for (String option : valid) {
                if (option.equals(value)) {
                    return value;
                }
            }
            ui.printError("Opción inválida. Debe ser una de: " + String.join(", ", valid));
        }
    }

    private long readLong(String prompt, long defaultValue) {
        while (true) {
            System.out.print(ui.cyan(prompt) + " (enter = " + defaultValue + "): ");
            String raw = scanner.nextLine().trim();
            if (raw.isEmpty()) {
                return defaultValue;
            }
            try {
                return Long.parseLong(raw);
            } catch (NumberFormatException exc) {
                ui.printError("Debe escribir un número entero.");
            }
        }
    }

    private double readDouble(String prompt, double defaultValue) {
        while (true) {
            System.out.print(ui.cyan(prompt) + " (enter = " + defaultValue + "): ");
            String raw = scanner.nextLine().trim().replace(',', '.');
            if (raw.isEmpty()) {
                return defaultValue;
            }
            try {
                return Double.parseDouble(raw);
            } catch (NumberFormatException exc) {
                ui.printError("Debe escribir un número decimal (por ejemplo 0.05).");
            }
        }
    }
}
