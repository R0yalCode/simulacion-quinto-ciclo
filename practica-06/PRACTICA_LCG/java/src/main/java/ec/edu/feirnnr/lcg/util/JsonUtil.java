package ec.edu.feirnnr.lcg.util;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.LinkedHashMap;
import java.util.Map;

/**
 * Wrapper Gson (capa de infraestructura) para el protocolo JSON compartido
 * con Python: lectura/escritura de configuraciones y de resultados headless.
 */
public final class JsonUtil {

    private static final Gson GSON = new GsonBuilder()
            .setPrettyPrinting()
            .disableHtmlEscaping()
            .create();

    private JsonUtil() {
    }

    /** Parsea un objeto JSON a un mapa ordenado de tipo seguro. */
    @SuppressWarnings("unchecked")
    public static Map<String, Object> parse(String json) {
        Map<String, Object> map = (Map<String, Object>) GSON.fromJson(json, LinkedHashMap.class);
        if (map == null) {
            throw new IllegalArgumentException("JSON vacío o inválido.");
        }
        return map;
    }

    public static Map<String, Object> readFile(Path path) throws IOException {
        if (!Files.exists(path)) {
            throw new IOException("No se encontró el archivo: " + path);
        }
        String content = Files.readString(path, StandardCharsets.UTF_8);
        try {
            return parse(content);
        } catch (RuntimeException cause) {
            throw new IOException("JSON inválido en " + path + ": " + cause.getMessage(), cause);
        }
    }

    public static void writeFile(Path path, Map<String, Object> content) throws IOException {
        Files.createDirectories(path.toAbsolutePath().getParent());
        Files.writeString(path, GSON.toJson(content), StandardCharsets.UTF_8);
    }

    public static String pretty(Map<String, Object> content) {
        return GSON.toJson(content);
    }

    /** Construye un LinkedHashMap con pares clave/valor (legible y ordenado). */
    public static LinkedHashMap<String, Object> mapOf(Object... pairs) {
        if (pairs.length % 2 != 0) {
            throw new IllegalArgumentException("mapOf espera pares clave/valor.");
        }
        LinkedHashMap<String, Object> map = new LinkedHashMap<>();
        for (int i = 0; i < pairs.length; i += 2) {
            map.put(String.valueOf(pairs[i]), pairs[i + 1]);
        }
        return map;
    }
}
