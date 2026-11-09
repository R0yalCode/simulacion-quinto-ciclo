package ec.edu.feirnnr.lcg.core;

import ec.edu.feirnnr.lcg.config.GeneratorParameters;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

/**
 * Pruebas unitarias del LCG en Java con casos conocidos y verificación
 * de identidad con la implementación Python (constantes compartidas).
 */
class LCGTest {

    @Test
    void cicloConocidoConParametrosPequenos() {
        // m=8, a=5, c=1, X0=1 → 6, 7, 4, 5, 2, 3, 0, 1 (periodo 8).
        LCG lcg = new LCG(new GeneratorParameters(1, 5, 1, 8, 8));
        assertArrayEquals(new long[]{6, 7, 4, 5, 2, 3, 0, 1}, lcg.generateStates());
    }

    @Test
    void parametrosPorDefectoCoincidenConPython() {
        // Constantes verificadas contra la implementación Python (misma secuencia).
        LCG lcg = new LCG(GeneratorParameters.defaults());
        long[] states = lcg.generateStates();
        assertEquals(1000, states.length);
        assertEquals(87628868L, states[0]);
        assertEquals(71072467L, states[1]);
        assertEquals(2332836374L, states[2]);
    }

    @Test
    void cantidadYIntervaloDeLaSecuencia() {
        GeneratorParameters params = new GeneratorParameters(12345, 1664525,
                1013904223L, 4294967296L, 500);
        LCG lcg = new LCG(params);
        long[] states = lcg.generateStates();
        double[] uniforms = lcg.toUniforms(states);
        assertEquals(500, states.length);
        assertEquals(500, uniforms.length);
        for (long state : states) {
            assertTrue(state >= 0 && state < params.modulus());
        }
        for (double uniform : uniforms) {
            assertTrue(uniform >= 0.0 && uniform < 1.0);
        }
    }

    @Test
    void uniformesIgualesAEstadoEntreModulo() {
        GeneratorParameters params = new GeneratorParameters(1, 5, 1, 8, 8);
        LCG lcg = new LCG(params);
        long[] states = lcg.generateStates();
        double[] uniforms = lcg.toUniforms(states);
        for (int i = 0; i < states.length; i++) {
            assertEquals(states[i] / 8.0, uniforms[i], 0.0);
        }
    }

    @Test
    void hashConocidoDeCiclo() {
        // SHA-256 de "6,7,4,5,2,3,0,1" calculado de forma independiente (Python).
        LCG lcg = new LCG(new GeneratorParameters(1, 5, 1, 8, 8));
        assertEquals("9e44f8dcd2ae42a74f1de1edd613705ff15cef0867e4bb194ef23267c434d546",
                LCG.sequenceHash(lcg.generateStates()));
    }

    @Test
    void parametrosInvalidosLanzanExcepcion() {
        assertThrows(IllegalArgumentException.class, () ->
                new GeneratorParameters(1, 5, 1, 8, 0).validate());
        assertThrows(IllegalArgumentException.class, () ->
                new GeneratorParameters(8, 5, 1, 8, 10).validate()); // semilla >= m
        assertThrows(IllegalArgumentException.class, () ->
                new GeneratorParameters(1, 5, 1, 1, 10).validate()); // m <= 1
        assertThrows(IllegalArgumentException.class, () ->
                new GeneratorParameters(1, -5, 1, 8, 10).validate());
    }

    @Test
    void multiplicacionSeguraConParametrosGrandes() {
        // Parámetros que desbordan long: el paso debe usar BigInteger y mantenerse exacto.
        GeneratorParameters params = new GeneratorParameters(
                1L, 3_037_000_493L, 1L, 4_294_967_291L, 5);
        LCG lcg = new LCG(params);
        long[] states = lcg.generateStates();
        assertEquals(5, states.length);
        // X1 = 3.037.000.493 * 1 + 1 = 3.037.000.494 < m.
        assertEquals(3_037_000_494L, states[0]);
        for (long state : states) {
            assertTrue(state >= 0 && state < params.modulus());
        }
    }
}
