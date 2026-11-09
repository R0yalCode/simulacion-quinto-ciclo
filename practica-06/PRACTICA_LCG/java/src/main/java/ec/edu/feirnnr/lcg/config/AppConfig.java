package ec.edu.feirnnr.lcg.config;

import java.util.ArrayList;
import java.util.List;

/**
 * Configuración completa de la aplicación (generador + estadística).
 * Es el equivalente exacto de python/config/AppConfig y comparte el
 * mismo JSON canónico que se intercambia entre Python y Java.
 */
public record AppConfig(GeneratorParameters generator,
                        StatisticalParameters statistical,
                        List<Long> comparisonSizes,
                        int repetitions) {

    public static AppConfig defaults() {
        return new AppConfig(
                GeneratorParameters.defaults(),
                StatisticalParameters.defaults(),
                new ArrayList<>(List.of(1000L, 10000L, 100000L, 1000000L)),
                3
        );
    }

    public void validate() {
        generator.validate();
        statistical.validate();
        if (comparisonSizes == null || comparisonSizes.isEmpty()) {
            throw new IllegalArgumentException(
                    "Debe existir al menos un tamaño N para la comparación.");
        }
        for (Long size : comparisonSizes) {
            if (size == null || size <= 0 || size > 20_000_000L) {
                throw new IllegalArgumentException(
                        "Los tamaños N del modo comparativo deben estar en (0, 20.000.000].");
            }
        }
        if (repetitions < 1 || repetitions > 10) {
            throw new IllegalArgumentException(
                    "Las repeticiones de medición deben estar en [1, 10].");
        }
    }

    /** Copia con otro valor de N (los records de params son inmutables). */
    public AppConfig withN(long n) {
        GeneratorParameters adapted = new GeneratorParameters(
                generator.seed(), generator.multiplier(), generator.increment(),
                generator.modulus(), n);
        return new AppConfig(adapted, statistical, comparisonSizes, repetitions);
    }

    @Override
    public String toString() {
        return "generador: " + generator + "; α = " + statistical.alpha()
                + "; intervalos = " + statistical.intervals()
                + "; tolerancia = " + statistical.tolerance()
                + "; repeticiones = " + repetitions;
    }
}
