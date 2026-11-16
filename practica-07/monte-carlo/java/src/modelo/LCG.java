package modelo;

/**
 * Generador congruencial lineal (LCG) compartido por Java y Python.
 *
 * Garantiza exactamente la misma secuencia de números pseudoaleatorios en
 * ambos lenguajes usando la misma semilla, el mismo multiplicador y el
 * mismo módulo.
 *
 * Fórmula:
 *   X(n+1) = (48271 * X(n)) mod 2147483647
 *   U(n)   = X(n) / 2147483647
 */
public class LCG {

    /** Semilla común de ambos lenguajes. */
    public static final long SEMILLA = 123456789L;
    /** Multiplicador común de ambos lenguajes. */
    public static final long MULTIPLICADOR = 48271L;
    /** Módulo común de ambos lenguajes. */
    public static final long MODULO = 2147483647L;

    private long estado;

    public LCG() {
        this(SEMILLA);
    }

    public LCG(long semilla) {
        this.estado = semilla;
    }

    /** Avanza el estado y devuelve el siguiente número U en [0, 1). */
    public double siguiente() {
        estado = (MULTIPLICADOR * estado) % MODULO;
        return (double) estado / (double) MODULO;
    }

    /** Restablece el estado del generador a la semilla indicada. */
    public void reiniciar(long semilla) {
        this.estado = semilla;
    }
}
