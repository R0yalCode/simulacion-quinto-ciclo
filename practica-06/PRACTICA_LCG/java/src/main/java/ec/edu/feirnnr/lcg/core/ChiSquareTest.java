package ec.edu.feirnnr.lcg.core;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

/**
 * Prueba Chi-cuadrado de bondad de ajuste (implementación Strategy).
 *
 * Divide [0,1) en k intervalos semiabiertos [a, b), calcula
 * χ² = Σ (Oi − Ei)² / Ei con Ei = N/k y gl = k − 1. El valor p se obtiene
 * con Apache Commons Math (org.apache.commons.math3.distribution.
 * ChiSquaredDistribution): p = 1 − CDF(χ²; gl), cola superior exacta,
 * convención idéntica a scipy.stats.chi2.sf en Python.
 */
public final class ChiSquareTest implements StatisticalTest {

    @Override
    public String name() {
        return "Chi-cuadrado";
    }

    @Override
    public String shortName() {
        return "chi_square";
    }

    @Override
    public TestResult execute(double[] sequence, double alpha, int intervals) {
        if (sequence == null || sequence.length == 0) {
            throw new IllegalArgumentException(
                    "La secuencia está vacía: no es posible ejecutar Chi-cuadrado.");
        }
        if (intervals < 2) {
            throw new IllegalArgumentException("Se requieren al menos 2 intervalos.");
        }
        int k = intervals;
        long n = sequence.length;
        double expected = (double) n / k;
        if (expected < 5.0) {
            throw new IllegalArgumentException(String.format(
                    "La frecuencia esperada Ei = %.2f es menor que 5; aumente N o "
                    + "reduzca el número de intervalos.", expected));
        }

        long[] observed = new long[k];
        for (double u : sequence) {
            int index = (int) Math.floor(u * k);
            if (u < 0.0 || u >= 1.0 || index < 0 || index >= k) {
                throw new IllegalArgumentException(
                        "Valor fuera de [0,1): no se puede clasificar (" + u + ").");
            }
            observed[index]++;
        }

        double statistic = 0.0;
        List<Double> contributions = new ArrayList<>(k);
        for (int i = 0; i < k; i++) {
            double contribution = (observed[i] - expected) * (observed[i] - expected) / expected;
            contributions.add(contribution);
            statistic += contribution;
        }

        int degreesFreedom = k - 1;
        org.apache.commons.math3.distribution.ChiSquaredDistribution chiDist =
                new org.apache.commons.math3.distribution.ChiSquaredDistribution(degreesFreedom);
        if (Double.isNaN(statistic) || Double.isInfinite(statistic)) {
            throw new IllegalStateException("El estadístico χ² no es finito (¿parámetros inválidos?).");
        }
        // p = 1 − F(χ²; gl): cola superior, igual a scipy.stats.chi2.sf.
        // Nota: en Commons Math, probability(x) es la densidad; la CDF es
        // cumulativeProbability(x).
        double pValue = 1.0 - chiDist.cumulativeProbability(statistic);

        StatisticalTest.Pair<Boolean, String> decision = decide(pValue, alpha);
        TestResult result = new TestResult(
                name(),
                n,
                statistic,
                pValue,
                alpha,
                decision.first(),
                decision.second(),
                degreesFreedom,
                toLongList(observed),
                toDoubleList(k, expected),
                mapOf(
                        "expected_frequency", expected,
                        "interval_labels", intervalLabels(k),
                        "contributions", contributions,
                        "p_value_source", "Apache Commons Math: 1 − ChiSquaredDistribution(gl).cumulativeProbability(χ²)"
                )
        );
        result.validateConsistency();
        return result;
    }

    private static List<Long> toLongList(long[] values) {
        List<Long> list = new ArrayList<>(values.length);
        for (long v : values) {
            list.add(v);
        }
        return list;
    }

    private static List<Double> toDoubleList(int k, double value) {
        List<Double> list = new ArrayList<>(k);
        for (int i = 0; i < k; i++) {
            list.add(value);
        }
        return list;
    }

    /** Etiquetas de los k intervalos semiabiertos [a, b) sobre [0,1). */
    private static List<String> intervalLabels(int k) {
        List<String> labels = new ArrayList<>(k);
        for (int i = 0; i < k; i++) {
            double lower = (double) i / k;
            double upper = (double) (i + 1) / k;
            labels.add(String.format(java.util.Locale.US, "%.2f, %.2f", lower, upper));
        }
        return labels;
    }

    /** Mapa ordenado a partir de pares clave/valor alternados. */
    private static Map<String, Object> mapOf(Object... pairs) {
        Map<String, Object> map = new java.util.LinkedHashMap<>();
        for (int i = 0; i + 1 < pairs.length; i += 2) {
            map.put((String) pairs[i], pairs[i + 1]);
        }
        return map;
    }
}
