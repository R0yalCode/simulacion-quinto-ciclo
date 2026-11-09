package ec.edu.feirnnr.lcg.services;

import ec.edu.feirnnr.lcg.config.AppConfig;
import ec.edu.feirnnr.lcg.core.LCG;
import org.junit.jupiter.api.Test;

import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

/**
 * Pruebas del protocolo headless y de la medición por partes.
 * Verifican las invariantes que el coordinador de Python usa para comparar.
 */
class ExecutionServiceTest {

    private static AppConfig configN(long n, int repetitions) {
        AppConfig base = AppConfig.defaults();
        return new AppConfig(base.generator(), base.statistical(),
                base.comparisonSizes(), repetitions).withN(n);
    }

    @Test
    void protocoloContieneTodasLasClavesAcordadas() {
        AppConfig config = configN(250, 1);
        ExecutionService service = new ExecutionService();
        ExecutionService.Pipeline pipeline =
                service.runMeasured(ExecutionService.adapt(config), config.repetitions());
        Map<String, Object> payload = service.headlessPayload(
                ExecutionService.adapt(config), pipeline);

        for (String key : List.of("engine", "generator", "statistical", "sequence",
                "chi_square", "kolmogorov_smirnov", "times_seconds",
                "times_meta", "p_value_source")) {
            assertTrue(payload.containsKey(key), "Falta la clave " + key);
        }
        assertEquals("java", payload.get("engine"));

        @SuppressWarnings("unchecked")
        Map<String, Object> sequence = (Map<String, Object>) payload.get("sequence");
        assertEquals(250, ((Number) sequence.get("count")).intValue());
        assertEquals(LCG.sequenceHash(pipeline.states()), sequence.get("sha256"));
        assertEquals(20, ((List<?>) sequence.get("first_20_integers")).size());
        assertEquals(20, ((List<?>) sequence.get("last_20_integers")).size());
    }

    @Test
    void estadisticosDelProtocoloSonCoherentes() {
        AppConfig config = configN(500, 1);
        ExecutionService service = new ExecutionService();
        ExecutionService.Pipeline pipeline =
                service.runMeasured(ExecutionService.adapt(config), config.repetitions());
        Map<String, Object> payload = service.headlessPayload(
                ExecutionService.adapt(config), pipeline);

        @SuppressWarnings("unchecked")
        Map<String, Object> chi = (Map<String, Object>) payload.get("chi_square");
        long observedSum = ((List<?>) chi.get("observed")).stream()
                .mapToLong(value -> ((Number) value).longValue()).sum();
        assertEquals(500L, observedSum);
        double chiP = ((Number) chi.get("p_value")).doubleValue();
        assertTrue(chiP >= 0.0 && chiP <= 1.0);
        assertEquals(9, ((Number) chi.get("degrees_freedom")).intValue());

        @SuppressWarnings("unchecked")
        Map<String, Object> ks = (Map<String, Object>) payload.get("kolmogorov_smirnov");
        double dPlus = ((Number) ks.get("d_plus")).doubleValue();
        double dMinus = ((Number) ks.get("d_minus")).doubleValue();
        double d = ((Number) ks.get("statistic")).doubleValue();
        assertEquals(Math.max(dPlus, dMinus), d, 0.0);
        double ksP = ((Number) ks.get("p_value")).doubleValue();
        assertTrue(ksP >= 0.0 && ksP <= 1.0);
    }

    @Test
    void tiemposIncluyenLasCuatroMedidasYMetadatos() {
        AppConfig config = configN(200, 2);
        ExecutionService service = new ExecutionService();
        ExecutionService.Pipeline pipeline =
                service.runMeasured(ExecutionService.adapt(config), config.repetitions());
        Map<String, Object> payload = service.headlessPayload(
                ExecutionService.adapt(config), pipeline);

        @SuppressWarnings("unchecked")
        Map<String, Object> times = (Map<String, Object>) payload.get("times_seconds");
        for (String key : List.of("generation", "chi_square", "ks", "total")) {
            assertTrue(times.containsKey(key), "Falta el tiempo " + key);
            double seconds = ((Number) times.get(key)).doubleValue();
            assertTrue(seconds >= 0.0);
        }
        double sum = ((Number) times.get("generation")).doubleValue()
                + ((Number) times.get("chi_square")).doubleValue()
                + ((Number) times.get("ks")).doubleValue();
        assertEquals(sum, ((Number) times.get("total")).doubleValue(), 1e-8);

        @SuppressWarnings("unchecked")
        Map<String, Object> meta = (Map<String, Object>) payload.get("times_meta");
        assertEquals(2, ((Number) meta.get("repetitions")).intValue());
        assertEquals(ExecutionService.WARMUP_DISCARDED,
                ((Number) meta.get("warmup_discarded")).intValue());
    }

    @Test
    void laSecuenciaNoSeModificaEntreRepeticiones() {
        AppConfig config = configN(300, 3);
        ExecutionService service = new ExecutionService();
        ExecutionService.Pipeline first =
                service.runMeasured(ExecutionService.adapt(config), config.repetitions());
        ExecutionService.Pipeline second =
                service.runMeasured(ExecutionService.adapt(config), config.repetitions());
        assertEquals(LCG.sequenceHash(first.states()), LCG.sequenceHash(second.states()));
        assertEquals(first.chi().statistic(), second.chi().statistic(), 0.0);
        assertEquals(first.ks().statistic(), second.ks().statistic(), 0.0);
        assertFalse(first.uniforms().length == 0);
    }
}
