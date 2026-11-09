package ec.edu.feirnnr.lcg.core;

import ec.edu.feirnnr.lcg.config.GeneratorParameters;

import java.math.BigInteger;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

/**
 * Generador congruencial lineal (LCG) — implementación manual.
 *
 * X(n+1) = (a · X(n) + c) mod m;   U(n) = X(n) / m.
 *
 * Aritmética en <code>long</code> verificada: la multiplicación
 * (a·X) y la suma (+c) se controlan con <code>Math.multiplyExact</code> y
 * <code>Math.addExact</code>; si los parámetros no caben en 64 bits se
 * recalcula el paso con <code>BigInteger</code>. Así, Python y Java
 * producen EXACTAMENTE la misma secuencia de estados enteros.
 *
 * Importante: con m = 2^32 y los parámetros por defecto
 * (a = 1664525, c = 1013904223) la multiplicación a·X < 7.2e15 y no hay
 * desbordamiento: el camino rápido (<code>long</code>) es suficiente.
 */
public final class LCG {

    private final GeneratorParameters params;

    public LCG(GeneratorParameters params) {
        if (params == null) {
            throw new IllegalArgumentException("Los parámetros del LCG no pueden ser nulos.");
        }
        params.validate();
        this.params = params;
    }

    /** Un paso de la recurrencia, seguro ante desbordamientos. */
    public long nextState(long state) {
        long modulus = params.modulus();
        long a = params.multiplier();
        long c = params.increment();

        long product;
        try {
            product = Math.multiplyExact(a, state);
        } catch (ArithmeticException overflow) {
            // Camino exacto con BigInteger (parámetros gigantes del usuario).
            return BigInteger.valueOf(a)
                    .multiply(BigInteger.valueOf(state))
                    .mod(BigInteger.valueOf(modulus))
                    .longValueExact();
        }
        try {
            return Math.addExact(product, c) % modulus;
        } catch (ArithmeticException overflow) {
            return BigInteger.valueOf(product)
                    .add(BigInteger.valueOf(c))
                    .mod(BigInteger.valueOf(modulus))
                    .longValueExact();
        }
    }

    /** Genera los n estados enteros X(1) … X(n) posteriores a la semilla. */
    public long[] generateStates() {
        params.validate();
        long n = params.n();
        if (n > Integer.MAX_VALUE) {
            throw new IllegalArgumentException(
                    "N excede el límite práctico de un arreglo Java (2^31−1).");
        }
        long[] states = new long[(int) n];
        long state = params.seed();
        for (int i = 0; i < states.length; i++) {
            state = nextState(state);
            states[i] = state;
        }
        return states;
    }

    /** Normalización U(i) = X(i) / m ∈ [0, 1). */
    public double[] toUniforms(long[] states) {
        double modulus = (double) params.modulus();
        double[] uniforms = new double[states.length];
        for (int i = 0; i < states.length; i++) {
            uniforms[i] = states[i] / modulus;
        }
        return uniforms;
    }

    public GeneratorParameters parameters() {
        return params;
    }

    /** Verifica que todos los valores normalizados estén en [0, 1). */
    public static void checkUnitInterval(double[] uniforms) {
        for (double u : uniforms) {
            if (u < 0.0 || u >= 1.0 || Double.isNaN(u)) {
                throw new IllegalStateException("Valor normalizado fuera de [0,1): " + u);
            }
        }
    }

    /**
     * Huella SHA-256 de la secuencia de enteros (decimales separados por comas),
     * idéntica al cálculo de python/core/lcg.py → permite comparar EXACTO.
     */
    public static String sequenceHash(long[] states) {
        StringBuilder sb = new StringBuilder(Math.max(16, states.length * 10));
        for (int i = 0; i < states.length; i++) {
            if (i > 0) {
                sb.append(',');
            }
            sb.append(states[i]);
        }
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] bytes = digest.digest(sb.toString().getBytes(StandardCharsets.US_ASCII));
            StringBuilder hex = new StringBuilder(bytes.length * 2);
            for (byte b : bytes) {
                hex.append(Character.forDigit((b >> 4) & 0xF, 16));
                hex.append(Character.forDigit(b & 0xF, 16));
            }
            return hex.toString();
        } catch (NoSuchAlgorithmException cause) {
            throw new IllegalStateException("SHA-256 no disponible en la JVM.", cause);
        }
    }
}
