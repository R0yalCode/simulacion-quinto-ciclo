package ec.edu.feirnnr.lcg.core;

import java.util.List;

/**
 * Resultado estructurado de una prueba estadística.
 * Campos homólogos al protocolo Python (TestResult).
 */
public final class TestResult {

    public final String testName;
    public final long sampleSize;
    public final double statistic;
    public final double pValue;
    public final double alpha;
    public final boolean rejectH0;
    public final String decision;
    public final Integer degreesFreedom;   // null en KS
    public final List<Long> observed;      // null en KS
    public final List<Double> expected;    // null en KS
    public final java.util.Map<String, Object> details;

    public TestResult(String testName, long sampleSize, double statistic, double pValue,
                      double alpha, boolean rejectH0, String decision,
                      Integer degreesFreedom, List<Long> observed, List<Double> expected,
                     java.util.Map<String, Object> details) {
        this.testName = testName;
        this.sampleSize = sampleSize;
        this.statistic = statistic;
        this.pValue = pValue;
        this.alpha = alpha;
        this.rejectH0 = rejectH0;
        this.decision = decision;
        this.degreesFreedom = degreesFreedom;
        this.observed = observed;
        this.expected = expected;
        this.details = details;
    }

    /** Accesores estilo record (homogéneos con el resto del código). */
    public String testName() { return testName; }
    public long sampleSize() { return sampleSize; }
    public double statistic() { return statistic; }
    public double pValue() { return pValue; }
    public double alpha() { return alpha; }
    public boolean rejectH0() { return rejectH0; }
    public String decision() { return decision; }
    public Integer degreesFreedom() { return degreesFreedom; }
    public List<Long> observed() { return observed; }
    public List<Double> expected() { return expected; }
    public java.util.Map<String, Object> details() { return details; }

    /** Invariantes documentadas en la sección 15 de la práctica. */
    public void validateConsistency() {
        if (sampleSize < 0) {
            throw new IllegalStateException("El tamaño de muestra no puede ser negativo.");
        }
        if (pValue < 0.0 || pValue > 1.0) {
            throw new IllegalStateException("El valor p debe pertenecer a [0, 1].");
        }
        if (statistic < 0.0) {
            throw new IllegalStateException("El estadístico no puede ser negativo.");
        }
        if (rejectH0 != (pValue < alpha)) {
            throw new IllegalStateException("La decisión debe coherir con p < α.");
        }
        if (observed != null && observed.stream().mapToLong(Long::longValue).sum() != sampleSize) {
            throw new IllegalStateException("Las frecuencias observadas deben sumar N.");
        }
        if (observed != null && expected != null) {
            double sumExpected = expected.stream().mapToDouble(Double::doubleValue).sum();
            if (Math.abs(sumExpected - sampleSize) > 1e-9) {
                throw new IllegalStateException("Las frecuencias esperadas deben sumar N.");
            }
        }
    }
}
