package ec.edu.feirnnr.lcg.core;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

/**
 * Pruebas de Kolmogorov-Smirnov con secuencias conocidas.
 */
class KolmogorovSmirnovTestTest {

    private final KolmogorovSmirnovTest test =
            new KolmogorovSmirnovTest();

    @Test
    void estadisticoConocidoParaDiagonal() {
        // U(i) = i/(n+1) ⇒ D+ = D− = 1/(n+1) ⇒ D = 1/(n+1).
        int n = 100;
        double[] values = new double[n];
        for (int i = 1; i <= n; i++) {
            values[i - 1] = (double) i / (n + 1);
        }
        TestResult result = test.execute(values, 0.05, 10);
        double expected = 1.0 / (n + 1);
        assertEquals(expected, result.statistic, 1e-9);
        assertEquals(expected, ((Number) result.details.get("d_plus")).doubleValue(), 1e-9);
        assertEquals(expected, ((Number) result.details.get("d_minus")).doubleValue(), 1e-9);
        assertTrue(result.pValue >= 0.0 && result.pValue <= 1.0);
        assertTrue(!result.rejectH0); // D pequeña ⇒ p alta
    }

    @Test
    void estadisticoDentroDelIntervaloUnidad() {
        int n = 500;
        double[] values = new double[n];
        for (int i = 0; i < n; i++) {
            values[i] = (i + 0.5) / n;
        }
        TestResult result = test.execute(values, 0.05, 10);
        assertTrue(result.statistic >= 0.0 && result.statistic <= 1.0);
        assertTrue(result.pValue >= 0.0 && result.pValue <= 1.0);
        assertEquals(result.pValue < result.alpha, result.rejectH0);
    }

    @Test
    void secuenciaVaciaEsRechazada() {
        assertThrows(IllegalArgumentException.class, () -> test.execute(new double[0], 0.05, 10));
    }

    @Test
    void valoresFueraDeRangoSonRechazados() {
        assertThrows(IllegalArgumentException.class,
                () -> test.execute(new double[]{0.5, 1.0}, 0.05, 10));
        assertThrows(IllegalArgumentException.class,
                () -> test.execute(new double[]{-0.1, 0.5}, 0.05, 10));
    }

    @Test
    void colaAsintoticaConocida() {
        assertEquals(1.0, KolmogorovSmirnovTest.asymptoticTail(0.0), 1e-12);
        // Aproximación clásica: Q(1.36) ≈ 0.05 (referencia de diagnóstico).
        assertEquals(0.05, KolmogorovSmirnovTest.asymptoticTail(1.36), 0.01);
    }
}
