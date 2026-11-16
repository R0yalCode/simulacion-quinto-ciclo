package modelo;

import java.util.ArrayList;
import java.util.List;

/**
 * Modelo: lógica del método Monte Carlo para aproximar el valor de π.
 */
public class ExperimentoMonteCarlo {

    /** Tamaños de muestra obligatorios de la práctica. */
    public static final int[] TAMANOS = {1_000, 10_000, 100_000, 1_000_000};

    /** Semilla común de ambos lenguajes. */
    public static final long SEMILLA = LCG.SEMILLA;

    /**
     * Ejecuta el experimento con n puntos y devuelve el resultado.
     *
     * El tiempo medido corresponde únicamente al experimento (generación de
     * puntos y conteo), no a la lectura ni escritura de archivos.
     */
    public ResultadoExperimento ejecutar(int n) {
        LCG lcg = new LCG(SEMILLA);
        long puntosEnCirculo = 0;

        long inicio = System.nanoTime();
        for (int i = 0; i < n; i++) {
            double x = lcg.siguiente();
            double y = lcg.siguiente();
            if (x * x + y * y <= 1.0) {
                puntosEnCirculo++;
            }
        }
        long fin = System.nanoTime();

        double piEstimado = 4.0 * puntosEnCirculo / n;
        double error = Math.abs(Math.PI - piEstimado);
        double tiempoMs = (fin - inicio) / 1_000_000.0;
        return new ResultadoExperimento(n, puntosEnCirculo, piEstimado, error, tiempoMs);
    }

    /** Ejecuta los cuatro experimentos obligatorios. */
    public List<ResultadoExperimento> ejecutarTodos() {
        List<ResultadoExperimento> resultados = new ArrayList<>();
        for (int n : TAMANOS) {
            resultados.add(ejecutar(n));
        }
        return resultados;
    }
}
