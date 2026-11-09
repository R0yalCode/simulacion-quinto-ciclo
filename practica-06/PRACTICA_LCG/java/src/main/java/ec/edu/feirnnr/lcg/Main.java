package ec.edu.feirnnr.lcg;

import ec.edu.feirnnr.lcg.config.AppConfig;
import ec.edu.feirnnr.lcg.services.ExecutionService;
import ec.edu.feirnnr.lcg.services.ExportService;
import ec.edu.feirnnr.lcg.services.MenuService;
import ec.edu.feirnnr.lcg.util.JsonUtil;
import ec.edu.feirnnr.lcg.util.ProjectPaths;
import ec.edu.feirnnr.lcg.visualization.ChartService;

import java.io.IOException;
import java.nio.file.Path;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * Punto de entrada de la implementación Java (independiente de Python).
 *
 * Modos:
 * - interactivo (menús propios);
 * - headless: protocolo JSON compartido con Python para el coordinador.
 *
 * Ejemplo headless (lo usa el coordinador de Python):
 *   java -jar lcg-simulator.jar --headless --config cfg.json --output out.json --n 1000
 */
public final class Main {

    public static void main(String[] args) {
        System.setProperty("java.awt.headless", "true");
        try {
            if (contains(args, "--headless")) {
                System.exit(headless(args));
            }
            AppConfig config = loadOrCreateConfig();
            new MenuService(config, args).run();
        } catch (IOException | IllegalArgumentException exc) {
            System.err.println("Error: " + exc.getMessage());
            System.exit(2);
        }
    }

    /* ------------------------------------------------------------------ */
    /* Modo headless (coordinador Python ↔ Java)                           */
    /* ------------------------------------------------------------------ */
    private static int headless(String[] args) throws IOException {
        try {
            AppConfig config = AppConfig.defaults();
            String configPath = valueOf(args, "--config");
            if (configPath != null) {
                config = ExportService.loadConfig(Path.of(configPath));
            } else if (java.nio.file.Files.exists(ProjectPaths.configPath())) {
                config = ExportService.loadConfig(ProjectPaths.configPath());
            }
            String nValue = valueOf(args, "--n");
            if (nValue != null) {
                config = config.withN(Long.parseLong(nValue));
            }
            String repsValue = valueOf(args, "--repetitions");
            if (repsValue != null) {
                config = new AppConfig(config.generator(), config.statistical(),
                        config.comparisonSizes(), Integer.parseInt(repsValue));
            }
            config.validate();

            String outputPath = valueOf(args, "--output");
            if (outputPath == null) {
                throw new IllegalArgumentException("Falta el argumento obligatorio --output.");
            }

            ExecutionService service = new ExecutionService();
            ExecutionService.Pipeline pipeline = service.runMeasured(
                    ExecutionService.adapt(config), config.repetitions());
            Map<String, Object> payload = service.headlessPayload(
                    ExecutionService.adapt(config), pipeline);

            Map<String, Object> result = new LinkedHashMap<>();
            result.put("status", "ok");
            result.put("engine", "java");
            result.put("parameters", JsonUtil.mapOf(
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
                    "repetitions", config.repetitions()));

            JsonUtil.writeFile(Path.of(outputPath), payload);
            if (!contains(args, "--no-plots")) {
                try {
                    new ChartService().exportAll(ProjectPaths.graphsDir(),
                            "lcg_java_n" + config.generator().n(),
                            pipeline.uniforms(), config.statistical().intervals());
                } catch (IOException chartError) {
                    System.err.println("[aviso] gráficas no generadas: " + chartError.getMessage());
                }
            }
            Map<String, Object> summary = new LinkedHashMap<>();
            summary.put("status", "ok");
            summary.put("engine", "java");
            summary.put("sequence_sha256", payload.get("sequence") instanceof Map<?, ?> seq
                    ? ((Map<?, ?>) seq).get("sha256") : null);
            System.out.println(JsonUtil.pretty(summary));
            return 0;
        } catch (IOException | IllegalArgumentException exc) {
            System.err.println(JsonUtil.pretty(JsonUtil.mapOf(
                    "status", "error", "message", String.valueOf(exc.getMessage()))));
            return 2;
        }
    }

    /* ------------------------------------------------------------------ */
    /* Modo interactivo                                                    */
    /* ------------------------------------------------------------------ */
    private static AppConfig loadOrCreateConfig() throws IOException {
        Path path = ProjectPaths.configPath();
        if (java.nio.file.Files.exists(path)) {
            try {
                return ExportService.loadConfig(path);
            } catch (IllegalArgumentException invalid) {
                System.err.println("[aviso] configuración inválida, se usan valores por "
                        + "defecto: " + invalid.getMessage());
                AppConfig config = AppConfig.defaults();
                ExportService.exportConfig(path, config);
                return config;
            }
        }
        AppConfig config = AppConfig.defaults();
        ExportService.exportConfig(path, config);
        return config;
    }

    /* ------------------------------------------------------------------ */
    /* Argumentos                                                          */
    /* ------------------------------------------------------------------ */
    private static boolean contains(String[] args, String flag) {
        for (String arg : args) {
            if (flag.equals(arg)) {
                return true;
            }
        }
        return false;
    }

    private static String valueOf(String[] args, String flag) {
        for (int i = 0; i < args.length - 1; i++) {
            if (flag.equals(args[i])) {
                return args[i + 1];
            }
        }
        return null;
    }
}
