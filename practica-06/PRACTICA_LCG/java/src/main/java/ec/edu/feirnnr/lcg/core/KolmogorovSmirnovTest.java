package ec.edu.feirnnr.lcg.core;

import org.apache.commons.math3.distribution.UniformRealDistribution;

import java.util.HashMap;
import java.util.Map;

/**
 * Prueba Kolmogorov-Smirnov de una muestra (implementación Strategy).
 *
 * Datos ordenados ascendentemente:
 *   D+ = max(i/N − U(i)),  D− = max(U(i) − (i−1)/N),  D = max(D+, D−)
 *
 * El estadístico D se calcula manualmente; el valor p se obtiene con
 * Apache Commons Math (KolmogorovSmirnovTest.kolmogorovSmirnovTest contra
 * UniformRealDistribution(0,1)), exacto para muestras pequeñas y
 * asintótico para grandes — la misma convención que scipy.stats.kstest.
 *
 * LIMITACIÓN DOCUMENTADA: con datos discretos (módulos pequeños) el valor
 * p pierde exactitud por empates; con m = 2^32 la malla es tan fina que
 * la aproximación es prácticamente exacta.
 */
public final class KolmogorovSmirnovTest implements StatisticalTest {

    @Override
    public String name() {
        return "Kolmogorov-Smirnov";
    }

    @Override
    public String shortName() {
        return "ks";
    }

    @Override
    public TestResult execute(double[] sequence, double alpha, int intervals) {
        int n = sequence == null ? 0 : sequence.length;
        if (n == 0) {
            throw new IllegalArgumentException(
                    "La secuencia está vacía: no es posible ejecutar Kolmogorov-Smirnov.");
        }
        // El cálculo trabaja sobre una copia ordenada; no muta la secuencia de origen.
        double[] ordered = new double[n];
        double dPlus = 0.0;
        double dMinus = 0.0;
        System.arraycopy(sequence, 0, ordered, 0, n);
        java.util.Arrays.sort(ordered);
        for (int i = 1; i <= n; i++) {
            double u = ordered[i - 1];
            if (u < 0.0 || u >= 1.0) {
                throw new IllegalArgumentException(
                        "Valor fuera de [0,1): no es una variable U(0,1) (" + u + ").");
            }
            dPlus = Math.max(dPlus, (double) i / n - u);
            dMinus = Math.max(dMinus, u - (double) (i - 1) / n);
        }
        double statistic = Math.max(dPlus, dMinus);

        org.apache.commons.math3.stat.inference.KolmogorovSmirnovTest commonsTest =
                new org.apache.commons.math3.stat.inference.KolmogorovSmirnovTest(
                        new org.apache.commons.math3.random.MersenneTwister(1L));
        UniformRealDistribution uniform = new UniformRealDistribution(0.0, 1.0);
        double pValue = commonsTest.kolmogorovSmirnovTest(uniform, ordered);
        double commonsStatistic = commonsTest.kolmogorovSmirnovStatistic(uniform, ordered);

        // Referencia asintótica clásica (diagnóstico; no es el valor p principal).
        double correction = Math.sqrt(n) + 0.12 + 0.11 / Math.sqrt(n);
        Map<String, Object> details = new HashMap<>();
        details.put("d_plus", dPlus);
        details.put("d_minus", dMinus);
        details.put("scipy_statistic", commonsStatistic);
        details.put("asymptotic_reference_p",
                asymptoticTail(statistic * correction));
        details.put("p_value_source",
                "Apache Commons Math KolmogorovSmirnovTest: exacto (n pequeño) / asintótico (n grande)");
        details.put("discrete_data_caveat",
                "Con módulos pequeños aparecen empates y el valor p es aproximado, no exacto.");

        StatisticalTest.Pair<Boolean, String> decision = decide(pValue, alpha);
        TestResult result = new TestResult(
                name(),
                n,
                statistic,
                pValue,
                alpha,
                decision.first(),
                decision.second(),
                null,
                null,
                null,
                details
        );
        result.validateConsistency();
        return result;
    }

    /**
     * Q(x) = 2·Σ_{k≥1} (−1)^(k−1) e^(−2 k² x²) — cola superior de la
     * distribución asintótica de Kolmogorov (referencia de diagnóstico).
     */
    static double asymptoticTail(double x) {
        if (x <= 0.0) {
            return 1.0;
        }
        double sum = 0.0;
        for (int k = 1; k <= 100; k++) {
            double term = Math.exp(-2.0 * k * k * x * x);
            sum += (k % 2 == 1) ? term : -term;
            if (term < 1e-16) {
                break;
            }
        }
        return Math.min(1.0, Math.max(0.0, 2.0 * sum));
    }
}
