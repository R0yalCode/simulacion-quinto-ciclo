package ec.edu.feirnnr.lcg.services;

import ec.edu.feirnnr.lcg.config.GeneratorParameters;
import ec.edu.feirnnr.lcg.config.StatisticalParameters;
import ec.edu.feirnnr.lcg.core.ChiSquareTest;
import ec.edu.feirnnr.lcg.core.KolmogorovSmirnovTest;
import ec.edu.feirnnr.lcg.core.LCG;
import ec.edu.feirnnr.lcg.core.TestResult;
import ec.edu.feirnnr.lcg.util.JsonUtil;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * Servicio de ejecución (capa de aplicación) para Java.
 *
 * Pipeline completo con medición por partes independiente:
 * generación LCG, Chi-cuadrado y Kolmogorov-Smirnov, con
 * <code>System.nanoTime()</code>.
 *
 * Medición (sección 12 de la práctica): 1 ejecución de calentamiento NO
 * medida + <code>repetitions</code> repeticiones medidas; se informan los
 * promedios. Las gráficas y exportaciones NUNCA forman parte del tiempo
 * medido y la inicialización de la JVM queda fuera por construcción
 * (la medición ocurre dentro del proceso ya iniciado).
 */
public final class ExecutionService {

    public static final int WARMUP_DISCARDED = 1;
    private static final int EXTREMES = 20;

    /** Salida del pipeline: secuencia, resultados y tiempos promediados. */
    public record Pipeline(long[] states, double[] uniforms,
                           TestResult chi, TestResult ks,
                           Map<String, Object> timesSeconds) {
        public double seconds(String key) {
            return ((Number) timesSeconds().get(key)).doubleValue();
        }
    }

    /** Generación aislada (solo LCG), útil para el menú «generar números». */
    public record Generation(long[] states, double[] uniforms, double seconds) {
    }

    /** Genera la secuencia midiendo exclusivamente el LCG. */
    public Generation generateOnly(ParametersLike parameters) {
        LCG lcg = new LCG(parameters.generator());
        long t0 = System.nanoTime();
        long[] states = lcg.generateStates();
        double[] uniforms = lcg.toUniforms(states);
        double seconds = (System.nanoTime() - t0) / 1e9;
        LCG.checkUnitInterval(uniforms);
        return new Generation(states, uniforms, seconds);
    }

    /**
     * Pipeline medido: calentamiento (no medido) + repeticiones promediadas.
     * El resultado estadístico correspondiente a la última repetición es
     * determinista, por lo que es válido para el reporte y la comparación.
     */
    public Pipeline runMeasured(ParametersLike parameters, int repetitions) {
        int reps = Math.max(1, repetitions);
        runOnce(parameters); // calentamiento descartado de la medición

        double genSum = 0.0;
        double chiSum = 0.0;
        double ksSum = 0.0;
        long[] states = null;
        double[] uniforms = null;
        TestResult chiResult = null;
        TestResult ksResult = null;

        for (int rep = 0; rep < reps; rep++) {
            LCG lcg = new LCG(parameters.generator());
            long t0 = System.nanoTime();
            states = lcg.generateStates();
            uniforms = lcg.toUniforms(states);
            genSum += System.nanoTime() - t0;

            long t1 = System.nanoTime();
            chiResult = new ChiSquareTest().execute(
                    uniforms, parameters.statistical().alpha(),
                    parameters.statistical().intervals());
            chiSum += System.nanoTime() - t1;

            long t2 = System.nanoTime();
            ksResult = new KolmogorovSmirnovTest().execute(
                    uniforms, parameters.statistical().alpha(),
                    parameters.statistical().intervals());
            ksSum += System.nanoTime() - t2;
        }

        double gen = genSum / reps / 1e9;
        double chi = chiSum / reps / 1e9;
        double ks = ksSum / reps / 1e9;
        Map<String, Object> times = JsonUtil.mapOf(
                "generation", round9(gen),
                "chi_square", round9(chi),
                "ks", round9(ks),
                "total", round9(gen + chi + ks),
                "repetitions", reps,
                "warmup_discarded", WARMUP_DISCARDED
        );
        return new Pipeline(states, uniforms, chiResult, ksResult, times);
    }

    /** Una ejecución completa sin promediar (también usada como calentamiento). */
    private void runOnce(ParametersLike parameters) {
        LCG lcg = new LCG(parameters.generator());
        long[] states = lcg.generateStates();
        double[] uniforms = lcg.toUniforms(states);
        new ChiSquareTest().execute(uniforms,
                parameters.statistical().alpha(), parameters.statistical().intervals());
        new KolmogorovSmirnovTest().execute(uniforms,
                parameters.statistical().alpha(), parameters.statistical().intervals());
    }

    /** Protocolo JSON headless compartido con Python (intercambio por subprocess). */
    public Map<String, Object> headlessPayload(ParametersLike parameters, Pipeline pipeline) {
        long[] states = pipeline.states();
        double[] uniforms = pipeline.uniforms();
        long n = states.length;

        long[] firstInts = Arrays.copyOfRange(states, 0, (int) Math.min(EXTREMES, n));
        long[] lastInts = Arrays.copyOfRange(states, (int) Math.max(0, n - EXTREMES), states.length);
        List<Object> firstTs = new ArrayList<>(EXTREMES);
        List<Object> lastTs = new ArrayList<>(EXTREMES);
        for (long v : firstInts) {
            firstTs.add(v);
        }
        for (long v : lastInts) {
            lastTs.add(v);
        }
        List<Object> firstUs = new ArrayList<>(EXTREMES);
        List<Object> lastUs = new ArrayList<>(EXTREMES);
        int firstCount = firstInts.length;
        for (int i = 0; i < firstCount; i++) {
            firstUs.add(round(uniforms[i]));
        }
        int lastStart = (int) Math.max(0, n - EXTREMES);
        for (int i = lastStart; i < n; i++) {
            lastUs.add(round(uniforms[i]));
        }

        TestResult chi = pipeline.chi();
        TestResult ks = pipeline.ks();

        GeneratorParameters g = parameters.generator();
        StatisticalParameters s = parameters.statistical();

        Map<String, Object> payload = new LinkedHashMap<>();
        payload.put("engine", "java");
        payload.put("generator", JsonUtil.mapOf(
                "seed", g.seed(), "multiplier", g.multiplier(),
                "increment", g.increment(), "modulus", g.modulus(), "n", g.n()));
        payload.put("statistical", JsonUtil.mapOf(
                "alpha", s.alpha(), "intervals", s.intervals(), "tolerance", s.tolerance()));
        payload.put("sequence", JsonUtil.mapOf(
                "count", n,
                "sha256", LCG.sequenceHash(states),
                "first_20_integers", firstTs,
                "last_20_integers", lastTs,
                "first_20_uniforms", firstUs,
                "last_20_uniforms", lastUs));
        payload.put("chi_square", JsonUtil.mapOf(
                "statistic", chi.statistic(),
                "p_value", chi.pValue(),
                "degrees_freedom", chi.degreesFreedom(),
                "observed", chi.observed(),
                "expected", chi.expected(),
                "reject_h0", chi.rejectH0()));
        payload.put("kolmogorov_smirnov", JsonUtil.mapOf(
                "statistic", ks.statistic(),
                "p_value", ks.pValue(),
                "d_plus", ((Number) ks.details().get("d_plus")).doubleValue(),
                "d_minus", ((Number) ks.details().get("d_minus")).doubleValue(),
                "reject_h0", ks.rejectH0()));
        Map<String, Object> times = new LinkedHashMap<>();
        for (Map.Entry<String, Object> entry : pipeline.timesSeconds().entrySet()) {
            if ("repetitions".equals(entry.getKey())
                    || "warmup_discarded".equals(entry.getKey())) {
                continue; // metadatos: van en times_meta, no son tiempos
            }
            if (entry.getValue() instanceof Number number) {
                times.put(entry.getKey(), round9(number.doubleValue()));
            } else {
                times.put(entry.getKey(), entry.getValue());
            }
        }
        payload.put("times_seconds", times);
        payload.put("times_meta", JsonUtil.mapOf(
                "repetitions", pipeline.timesSeconds().get("repetitions"),
                "warmup_discarded", pipeline.timesSeconds().get("warmup_discarded")));
        payload.put("p_value_source", JsonUtil.mapOf(
                "chi_square", "Apache Commons Math: 1 − ChiSquaredDistribution(gl).cumulativeProbability(χ²)",
                "kolmogorov_smirnov",
                "Apache Commons Math KolmogorovSmirnovTest: exacto/asintótico (compatible con scipy)"));
        return payload;
    }

    private static double round9(double value) {
        return Math.round(value * 1e9) / 1e9;
    }

    private static Double round(double value) {
        return Math.round(value * 1e12) / 1e12;
    }

    /** Contrato funcional mínimo (evita acoplar el servicio a records concretos). */
    public interface ParametersLike {
        GeneratorParameters generator();

        StatisticalParameters statistical();
    }

    /** Adaptador de ec.edu.feirnnr.lcg.config.AppConfig al contrato interior. */
    public static ParametersLike adapt(ec.edu.feirnnr.lcg.config.AppConfig config) {
        return new ParametersLike() {
            @Override
            public GeneratorParameters generator() {
                return config.generator();
            }

            @Override
            public StatisticalParameters statistical() {
                return config.statistical();
            }
        };
    }
}
