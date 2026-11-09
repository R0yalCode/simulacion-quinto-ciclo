package ec.edu.feirnnr.lcg.config;

/**
 * Parámetros estadísticos compartidos por las pruebas de uniformidad:
 * nivel de significancia α, número de intervalos de Chi-cuadrado y la
 * tolerancia comparativa entre bibliotecas (Python ↔ Java).
 */
public record StatisticalParameters(double alpha, int intervals, double tolerance) {

    public static StatisticalParameters defaults() {
        return new StatisticalParameters(0.05, 10, 1e-4);
    }

    public void validate() {
        if (alpha <= 0.0 || alpha >= 1.0) {
            throw new IllegalArgumentException("El nivel de significancia (α) debe estar en (0, 1).");
        }
        if (intervals < 2 || intervals > 1000) {
            throw new IllegalArgumentException("El número de intervalos debe estar en [2, 1000].");
        }
        if (tolerance <= 0.0) {
            throw new IllegalArgumentException("La tolerancia comparativa debe ser mayor que cero.");
        }
    }
}
