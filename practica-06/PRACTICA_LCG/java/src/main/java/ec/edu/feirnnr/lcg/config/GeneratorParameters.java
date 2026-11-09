package ec.edu.feirnnr.lcg.config;

/**
 * Parámetros del generador congruencial lineal (LCG).
 *
 * X(n+1) = (a · X(n) + c) mod m;  U(n) = X(n) / m.
 *
 * Valores por defecto idénticos a la implementación Python:
 * X0 = 12345, a = 1664525, c = 1013904223, m = 2^32.
 */
public record GeneratorParameters(long seed, long multiplier, long increment,
                                  long modulus, long n) {

    public static GeneratorParameters defaults() {
        return new GeneratorParameters(12345L, 1664525L, 1013904223L,
                4294967296L, 1000L);
    }

    /** Validación de parámetros LCG (objetivo: mismos números que Python). */
    public void validate() {
        if (modulus <= 1) {
            throw new IllegalArgumentException("El módulo (m) debe ser mayor o igual que 2.");
        }
        if (seed < 0 || seed >= modulus) {
            throw new IllegalArgumentException(
                    "La semilla debe estar en el rango [0, " + (modulus - 1) + "].");
        }
        if (multiplier < 0) {
            throw new IllegalArgumentException("El multiplicador (a) no puede ser negativo.");
        }
        if (increment < 0) {
            throw new IllegalArgumentException("El incremento (c) no puede ser negativo.");
        }
        if (n <= 0) {
            throw new IllegalArgumentException("La cantidad de números (N) debe ser mayor que cero.");
        }
        if (n > 20_000_000L) {
            throw new IllegalArgumentException(
                    "La cantidad de números (N) no puede exceder 20.000.000.");
        }
    }

    @Override
    public String toString() {
        return String.format(
                "X(n+1) = (%d · X(n) + %d) mod %d, X0 = %d, N = %d",
                multiplier, increment, modulus, seed, n);
    }
}
