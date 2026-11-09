package ec.edu.feirnnr.lcg.core;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

/**
 * Pruebas de la prueba Chi-cuadrado con secuencias conocidas,
 * independientes de la biblioteca estadística.
 */
class ChiSquareTestTest {

    private final ChiSquareTest test = new ChiSquareTest();

    private static double[] perfectamenteUniforme(int k, int perBin) {
        double[] values = new double[k * perBin];
        int index = 0;
        for (int i = 0; i < k; i++) {
            double center = (i + 0.5) / k;
            for (int j = 0; j < perBin; j++) {
                values[index++] = center;
            }
        }
        return values;
    }

    @Test
    void chiCuadradoCeroParaUniformidadPerfecta() {
        int k = 10;
        int perBin = 10;
        TestResult result = test.execute(perfectamenteUniforme(k, perBin), 0.05, k);
        assertEquals(0.0, result.statistic, 1e-12);
        assertEquals(k * perBin, result.sampleSize);
        assertEquals(9, result.degreesFreedom);
        assertEquals(k, result.observed.size());
        long observedSum = result.observed.stream().mapToLong(Long::longValue).sum();
        assertEquals(result.sampleSize, observedSum);
        double expectedSum = result.expected.stream().mapToDouble(Double::doubleValue).sum();
        assertEquals(result.sampleSize, expectedSum, 1e-9);
        assertEquals(1.0, result.pValue, 1e-9);
        assertFalse(result.rejectH0);
        result.validateConsistency();
    }

    @Test
    void casoExtremoConocido() {
        // Todos los valores en el primer intervalo: χ² = 9·(0−10)²/10 + (100−10)²/10 = 900.
        double[] values = new double[100];
        java.util.Arrays.fill(values, 0.05);
        TestResult result = test.execute(values, 0.05, 10);
        assertEquals(900.0, result.statistic, 1e-9);
        assertEquals(0.0, result.pValue, 1e-12);
        assertTrue(result.rejectH0);
        assertEquals(100L, result.observed.get(0));
        assertEquals(0L, result.observed.get(1));
    }

    @Test
    void gradosDeLibertadSiguenAK() {
        TestResult result = test.execute(perfectamenteUniforme(5, 20), 0.05, 5);
        assertEquals(4, result.degreesFreedom);
    }

    @Test
    void frecuenciaEsperadaMenorQueCincoEsRechazada() {
        double[] values = new double[40];
        java.util.Arrays.fill(values, 0.5);
        assertThrows(IllegalArgumentException.class, () -> test.execute(values, 0.05, 10));
    }

    @Test
    void secuenciaVaciaEsRechazada() {
        assertThrows(IllegalArgumentException.class, () -> test.execute(new double[0], 0.05, 10));
    }

    @Test
    void valorPEnRangoYDecisionCoherente() {
        TestResult result = test.execute(perfectamenteUniforme(10, 50), 0.05, 10);
        assertTrue(result.pValue >= 0.0 && result.pValue <= 1.0);
        assertEquals(result.pValue < result.alpha, result.rejectH0);
    }
}
