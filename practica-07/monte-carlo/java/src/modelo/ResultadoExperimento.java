package modelo;

/**
 * Resultado de un experimento Monte Carlo con un tamaño de muestra N.
 */
public class ResultadoExperimento {

    private final int n;
    private final long puntosEnCirculo;
    private final double piEstimado;
    private final double error;
    private final double tiempoMs;

    public ResultadoExperimento(int n, long puntosEnCirculo, double piEstimado,
                                double error, double tiempoMs) {
        this.n = n;
        this.puntosEnCirculo = puntosEnCirculo;
        this.piEstimado = piEstimado;
        this.error = error;
        this.tiempoMs = tiempoMs;
    }

    public int getN() {
        return n;
    }

    public long getPuntosEnCirculo() {
        return puntosEnCirculo;
    }

    public double getPiEstimado() {
        return piEstimado;
    }

    public double getError() {
        return error;
    }

    public double getTiempoMs() {
        return tiempoMs;
    }
}
