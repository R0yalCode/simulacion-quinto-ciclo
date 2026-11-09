package ec.edu.feirnnr.lcg.util;

/**
 * Utilidades ANSI para la presentación por terminal en Java.
 *
 * Detecta si la terminal admite secuencias ANSI (tty, VARIABLE no dumb,
 * sin NO_COLOR) y entrega helpers para títulos, secciones, tablas y
 * mensajes de estado. En modo headless (pipes) se desactivan los colores
 * para que la salida del coordinador sea limpia.
 */
public final class Ansi {

    public final boolean enabled;

    private static Ansi instance;

    private Ansi(boolean enabled) {
        this.enabled = enabled;
    }

    public static Ansi get() {
        if (instance == null) {
            instance = new Ansi(detect());
        }
        return instance;
    }

    /** Modo forzado (p. ej. pruebas que capturan la salida). */
    public static void force(boolean value) {
        instance = new Ansi(value);
    }

    private static boolean detect() {
        if (System.getenv("NO_COLOR") != null) {
            return false;
        }
        if (System.getenv("FORCE_COLOR") != null) {
            return true;
        }
        String term = System.getenv("TERM");
        if (term == null || term.equalsIgnoreCase("dumb")) {
            return false;
        }
        return System.console() != null;
    }

    public String wrap(String text, String code) {
        return enabled ? code + text + RESET : text;
    }

    public String bold(String text)    { return wrap(text, "\u001b[1m"); }
    public String cyan(String text)    { return wrap(text, "\u001b[1;36m"); }
    public String yellow(String text)  { return wrap(text, "\u001b[1;33m"); }
    public String green(String text)   { return wrap(text, "\u001b[1;32m"); }
    public String red(String text)     { return wrap(text, "\u001b[1;31m"); }
    public String dim(String text)     { return wrap(text, "\u001b[2m"); }

    public static final String RESET  = "\u001b[0m";

    /** Doble línea decorativa de la misma anchura que el título. */
    public void printBanner(String title, String subtitle) {
        System.out.println();
        String line = "=".repeat(Math.max(title.length(), subtitle.length()) + 8);
        System.out.println(cyan(line));
        System.out.println(cyan(title));
        System.out.println(cyan(subtitle));
        System.out.println(cyan(line));
    }

    public void printSection(String title) {
        System.out.println();
        System.out.println(cyan(String.format("---------- %s ----------", title)));
    }

    public void printSuccess(String message)  { System.out.println(green("✔ ") + message); }
    public void printWarning(String message)  { System.out.println(yellow("· ") + message); }
    public void printError(String message)    { System.out.println(red("✘ ") + message); }
}
