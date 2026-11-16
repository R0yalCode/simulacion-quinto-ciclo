package graficas;

import java.awt.BasicStroke;
import java.awt.Color;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;

import org.jfree.chart.ChartFactory;
import org.jfree.chart.ChartUtils;
import org.jfree.chart.JFreeChart;
import org.jfree.chart.axis.LogAxis;
import org.jfree.chart.plot.PlotOrientation;
import org.jfree.chart.plot.XYPlot;
import org.jfree.chart.renderer.xy.XYLineAndShapeRenderer;
import org.jfree.data.xy.XYSeries;
import org.jfree.data.xy.XYSeriesCollection;

import modelo.ResultadoExperimento;

/**
 * Capa de gráficas: genera las imágenes PNG de los resultados de Java
 * utilizando la biblioteca JFreeChart.
 */
public class GeneradorGraficas {

    public static final Path CARPETA_GRAFICAS = Paths.get("graficas");

    private static final Color COLOR_SERIE = new Color(31, 119, 180);
    private static final Color COLOR_PI_REAL = new Color(214, 39, 40);

    /** Genera las tres gráficas individuales de Java. */
    public void generarTodas(List<ResultadoExperimento> resultados) throws IOException {
        Files.createDirectories(CARPETA_GRAFICAS);
        generarGraficaError(resultados);
        generarGraficaTiempo(resultados);
        generarGraficaPi(resultados);
    }

    /** Gráfica del error absoluto según el número de puntos (eje Y logarítmico). */
    private void generarGraficaError(List<ResultadoExperimento> resultados)
            throws IOException {
        XYSeries serie = new XYSeries("Error absoluto");
        for (ResultadoExperimento r : resultados) {
            serie.add(r.getN(), r.getError());
        }
        JFreeChart grafica = crearGrafica(
                "Error absoluto según el número de puntos - Java",
                "Error absoluto (escala logarítmica)", serie, true);
        guardar(grafica, "error_java.png");
    }

    /** Gráfica del tiempo de ejecución según el número de puntos. */
    private void generarGraficaTiempo(List<ResultadoExperimento> resultados)
            throws IOException {
        XYSeries serie = new XYSeries("Tiempo (ms)");
        for (ResultadoExperimento r : resultados) {
            serie.add(r.getN(), r.getTiempoMs());
        }
        JFreeChart grafica = crearGrafica(
                "Tiempo de ejecución según el número de puntos - Java",
                "Tiempo (ms)", serie, false);
        guardar(grafica, "tiempo_java.png");
    }

    /** Gráfica de la aproximación de π, con línea horizontal del valor real. */
    private void generarGraficaPi(List<ResultadoExperimento> resultados)
            throws IOException {
        XYSeries seriePi = new XYSeries("π estimado");
        for (ResultadoExperimento r : resultados) {
            seriePi.add(r.getN(), r.getPiEstimado());
        }
        XYSeries serieReal = new XYSeries("π real");
        double nMinimo = resultados.get(0).getN();
        double nMaximo = resultados.get(resultados.size() - 1).getN();
        serieReal.add(nMinimo, Math.PI);
        serieReal.add(nMaximo, Math.PI);

        XYSeriesCollection datos = new XYSeriesCollection();
        datos.addSeries(seriePi);
        datos.addSeries(serieReal);

        JFreeChart grafica = crearGraficaConDatos(
                "Aproximación de π según el número de puntos - Java",
                "Valor de π", datos, false);
        XYLineAndShapeRenderer renderer =
                (XYLineAndShapeRenderer) grafica.getXYPlot().getRenderer();
        renderer.setSeriesPaint(1, COLOR_PI_REAL);
        renderer.setSeriesStroke(1, new BasicStroke(1.8f));
        guardar(grafica, "pi_java.png");
    }

    /** Crea una gráfica XY a partir de una sola serie. */
    private JFreeChart crearGrafica(String titulo, String etiquetaY, XYSeries serie,
                                    boolean ejeYLogaritmico) {
        XYSeriesCollection datos = new XYSeriesCollection(serie);
        return crearGraficaConDatos(titulo, etiquetaY, datos, ejeYLogaritmico);
    }

    /** Crea una gráfica XY con eje X logarítmico, cuadrícula y marcadores. */
    private JFreeChart crearGraficaConDatos(String titulo, String etiquetaY,
                                            XYSeriesCollection datos,
                                            boolean ejeYLogaritmico) {
        JFreeChart grafica = ChartFactory.createXYLineChart(
                titulo,
                "Número de puntos (N)",
                etiquetaY,
                datos,
                PlotOrientation.VERTICAL,
                true,   // leyenda
                false,  // tooltips
                false); // urls
        grafica.setBackgroundPaint(Color.WHITE);

        XYPlot plot = grafica.getXYPlot();
        plot.setDomainAxis(new LogAxis("Número de puntos (N) - escala logarítmica"));
        if (ejeYLogaritmico) {
            plot.setRangeAxis(new LogAxis(etiquetaY));
        }
        plot.setDomainGridlinesVisible(true);
        plot.setRangeGridlinesVisible(true);

        XYLineAndShapeRenderer renderer = new XYLineAndShapeRenderer(true, true);
        renderer.setSeriesPaint(0, COLOR_SERIE);
        renderer.setSeriesStroke(0, new BasicStroke(2.0f));
        plot.setRenderer(renderer);
        return grafica;
    }

    /** Guarda la gráfica como PNG en la carpeta graficas/. */
    private void guardar(JFreeChart grafica, String nombreArchivo) throws IOException {
        Path destino = CARPETA_GRAFICAS.resolve(nombreArchivo);
        ChartUtils.saveChartAsPNG(destino.toFile(), grafica, 900, 600);
    }
}
