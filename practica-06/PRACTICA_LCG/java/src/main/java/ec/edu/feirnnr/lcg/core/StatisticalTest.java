package ec.edu.feirnnr.lcg.core;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

/**
 * Contrato Strategy para las pruebas de uniformidad (patrón de diseño
 * aplicado en la práctica). Cada estrategia ejecuta su prueba sobre la
 * secuencia normalizada U(i) ∈ [0,1) y devuelve un TestResult.
 */
public interface StatisticalTest {

    String name();

    String shortName();

    /** Ejecuta la prueba y devuelve el resultado estructurado. */
    TestResult execute(double[] sequence, double alpha, int intervals);

    /** Criterio estándar: se rechaza H0 si p < α. */
    default Pair<Boolean, String> decide(double pValue, double alpha) {
        boolean reject = pValue < alpha;
        String decision;
        if (reject) {
            decision = String.format(
                    "Valor p = %.6f < α = %.2f: SE RECHAZA H0 (no hay evidencia de uniformidad).",
                    pValue, alpha);
        } else {
            decision = String.format(
                    "Valor p = %.6f ≥ α = %.2f: NO se rechaza H0 (la secuencia es compatible con U(0,1)).",
                    pValue, alpha);
        }
        return new Pair<>(reject, decision);
    }

    /** Par simple para el par decisión/mensaje. */
    record Pair<A, B>(A first, B second) {
    }

    /** Etiqueta de intervalo «a - b» con formato compacto (equivalente a Python). */
    static List<String> intervalLabels(int k) {
        double width = 1.0 / k;
        List<String> labels = new ArrayList<>(k);
        for (int i = 0; i < k; i++) {
            labels.add(String.format("%s - %s", trimDouble(i * width), trimDouble((i + 1) * width)));
        }
        return labels;
    }

    static String trimDouble(double value) {
        if (value == Math.rint(value) && value >= 1.0) {
            return String.format("%d", (long) value);
        }
        return String.format("%s", java.math.BigDecimal.valueOf(value)
                .stripTrailingZeros().toPlainString());
    }

    /** Envoltorio común para detalles adicionales. */
    static Map<String, Object> mapOf(Object... pairs) {
        return ec.edu.feirnnr.lcg.util.JsonUtil.mapOf(pairs);
    }
}
