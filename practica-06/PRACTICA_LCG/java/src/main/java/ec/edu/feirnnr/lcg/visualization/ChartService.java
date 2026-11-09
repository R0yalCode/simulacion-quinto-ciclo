package ec.edu.feirnnr.lcg.visualization;

import org.jfree.chart.ChartFactory;
import org.jfree.chart.ChartUtils;
import org.jfree.chart.JFreeChart;
import org.jfree.chart.plot.PlotOrientation;
import org.jfree.chart.plot.XYPlot;
import org.jfree.chart.renderer.xy.XYLineAndShapeRenderer;
import org.jfree.chart.renderer.xy.XYBarRenderer;
import org.jfree.chart.title.TextTitle;
import org.jfree.data.statistics.HistogramDataset;
import org.jfree.data.statistics.HistogramType;
import org.jfree.data.xy.XYSeries;
import org.jfree.data.xy.XYSeriesCollection;

import java.awt.BasicStroke;
import java.awt.Color;
import java.awt.Font;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

/**
 * Gráficas con JFreeChart (capa de visualización).
 *
 * Genera PNG en modo headless (sin abrir ventanas):
 * 1) ECDF empírica escalonada;
 * 2) CDF uniforme teórica (diagonal);
 * 3) comparación ECDF vs teórica (base de Kolmogorov-Smirnov);
 * 4) histograma de frecuencias con k intervalos.
 */
public final class ChartService {

    private static final int MAX_ECDF_POINTS = 2000;
    private static final int WIDTH = 900;
    private static final int HEIGHT = 540;
    private static final Color EMP_BLUE = new Color(21, 101, 192);
    private static final Color THEO_RED = new Color(198, 40, 40);
    private static final Color GRID = new Color(0xEE, 0xEE, 0xEE);

    /** Genera el conjunto mínimo de 4 gráficas de la práctica. */
    public List<Path> exportAll(Path graphsDir, String prefix,
                                double[] uniforms, int intervals) throws IOException {
        Files.createDirectories(graphsDir.toAbsolutePath());
        List<Path> paths = new ArrayList<>(4);
        paths.add(saveEcdf(graphsDir, prefix + "_ecdf_empirica_java.png", uniforms));
        paths.add(saveUniformCdf(graphsDir, prefix + "_cdf_uniforme_teorica_java.png"));
        paths.add(saveComparison(graphsDir, prefix + "_ecdf_vs_uniforme_java.png", uniforms));
        paths.add(saveHistogram(graphsDir, prefix + "_histograma_frecuencias_java.png",
                uniforms, intervals));
        return paths;
    }

    /** Índices de la muestra ordenada para trazar la ECDF (submuestreo si es enorme). */
    private static int[] ecdfIndices(int n) {
        if (n <= MAX_ECDF_POINTS) {
            int[] indices = new int[n];
            for (int i = 0; i < n; i++) {
                indices[i] = i;
            }
            return indices;
        }
        int[] indices = new int[MAX_ECDF_POINTS];
        for (int i = 0; i < MAX_ECDF_POINTS; i++) {
            indices[i] = (int) Math.round(
                    (double) i * (n - 1) / (MAX_ECDF_POINTS - 1));
        }
        return indices;
    }

    private static JFreeChart styledChart(String title, String xLabel, String yLabel,
                                          XYSeriesCollection dataset, boolean step) {
        JFreeChart chart = step
                ? ChartFactory.createXYStepChart(title, xLabel, yLabel, dataset,
                        PlotOrientation.VERTICAL, true, false, false)
                : ChartFactory.createXYLineChart(title, xLabel, yLabel, dataset,
                        PlotOrientation.VERTICAL, true, false, false);
        XYPlot plot = chart.getXYPlot();
        plot.setBackgroundPaint(Color.WHITE);
        plot.setDomainGridlinePaint(GRID);
        plot.setRangeGridlinePaint(GRID);
        if (plot.getRenderer() instanceof XYLineAndShapeRenderer renderer) {
            renderer.setDefaultShapesVisible(false);
            renderer.setSeriesStroke(0, new BasicStroke(2.2f));
            renderer.setSeriesPaint(0, EMP_BLUE);
            renderer.setSeriesStroke(1, new BasicStroke(1.8f));
            renderer.setSeriesPaint(1, THEO_RED);
        }
        chart.getTitle().setFont(new Font("SansSerif", Font.BOLD, 15));
        plot.getDomainAxis().setRange(0.0, 1.0);
        return chart;
    }

    private static Path save(JFreeChart chart, Path path) throws IOException {
        ChartUtils.saveChartAsPNG(path.toFile(), chart, WIDTH, HEIGHT);
        return path;
    }

    /** 1) ECDF empírica escalonada: F(u) = i/m en la muestra ordenada. */
    public Path saveEcdf(Path graphsDir, String fileName, double[] uniforms) throws IOException {
        double[] ordered = uniforms.clone();
        Arrays.sort(ordered);
        int n = ordered.length;
        int[] indices = ecdfIndices(n);
        XYSeries series = new XYSeries("ECDF empírica F_N(u)");
        series.add(0.0, 0.0);
        for (int idx : indices) {
            series.add(Math.min(ordered[idx], 1.0), (double) (idx + 1) / n);
        }
        XYSeriesCollection dataset = new XYSeriesCollection();
        dataset.addSeries(series);
        JFreeChart chart = styledChart(
                "Distribución acumulada empírica (LCG) — Java", "u",
                "F(u) empírica", dataset, true);
        return save(chart, graphsDir.resolve(fileName));
    }

    /** 2) CDF uniforme teórica: F(u) = u en [0,1]. */
    public Path saveUniformCdf(Path graphsDir, String fileName) throws IOException {
        XYSeries series = new XYSeries("CDF teórica U(0,1)");
        series.add(0.0, 0.0);
        series.add(1.0, 1.0);
        XYSeriesCollection dataset = new XYSeriesCollection();
        dataset.addSeries(series);
        JFreeChart chart = styledChart(
                "Distribución acumulada uniforme teórica U(0,1) — Java", "u",
                "F(u) teórica", dataset, false);
        return save(chart, graphsDir.resolve(fileName));
    }

    /** 3) Comparación ECDF vs diagonal teórica, con anotación del estadístico D. */
    public Path saveComparison(Path graphsDir, String fileName, double[] uniforms)
            throws IOException {
        double[] ordered = uniforms.clone();
        Arrays.sort(ordered);
        int n = ordered.length;
        int[] indices = ecdfIndices(n);

        XYSeries empirical = new XYSeries("ECDF empírica F_N(u)");
        empirical.add(0.0, 0.0);
        for (int idx : indices) {
            empirical.add(Math.min(ordered[idx], 1.0), (double) (idx + 1) / n);
        }
        XYSeries theoretical = new XYSeries("CDF teórica U(0,1)");
        theoretical.add(0.0, 0.0);
        theoretical.add(1.0, 1.0);

        double dPlus = 0.0;
        double dMinus = 0.0;
        for (int i = 1; i <= n; i++) {
            double u = ordered[i - 1];
            dPlus = Math.max(dPlus, (double) i / n - u);
            dMinus = Math.max(dMinus, u - (double) (i - 1) / n);
        }
        double d = Math.max(dPlus, dMinus);

        XYSeriesCollection dataset = new XYSeriesCollection();
        dataset.addSeries(empirical);
        dataset.addSeries(theoretical);
        JFreeChart chart = styledChart(
                "Comparación ECDF vs CDF uniforme — Java", "u", "F(u)", dataset, true);
        chart.addSubtitle(new TextTitle(String.format(
                java.util.Locale.US, "D (Kolmogorov-Smirnov) = %.6f", d)));
        return save(chart, graphsDir.resolve(fileName));
    }

    /** 4) Histograma con k intervalos (frecuencias observadas). */
    public Path saveHistogram(Path graphsDir, String fileName, double[] uniforms,
                              int intervals) throws IOException {
        HistogramDataset dataset = new HistogramDataset();
        dataset.setType(HistogramType.FREQUENCY);
        dataset.addSeries("Frecuencia observada", uniforms, intervals, 0.0, 1.0);
        JFreeChart chart = ChartFactory.createHistogram(
                String.format("Histograma de frecuencias (%d intervalos) — Java", intervals),
                "Intervalo de u", "Frecuencia observada", dataset,
                PlotOrientation.VERTICAL, true, false, false);
        if (chart.getXYPlot().getRenderer() instanceof XYBarRenderer renderer) {
            renderer.setSeriesPaint(0, EMP_BLUE);
            renderer.setShadowVisible(false);
        }
        chart.getTitle().setFont(new Font("SansSerif", Font.BOLD, 15));
        return save(chart, graphsDir.resolve(fileName));
    }
}
