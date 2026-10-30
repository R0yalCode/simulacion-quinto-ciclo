"""
Modelo: Lógica matemática del Generador Congruencial Lineal (LCG)
Fórmula:      X(n+1) = (a * X(n) + c) mod m
Normalización: U(n)   = X(n) / m
"""


class ModeloLCG:
    def __init__(self):
        # Parámetros iniciales obligatorios de la práctica
        self.a = 1664525
        self.c = 1013904223
        self.m = 4294967296          # 2^32
        self.semilla = 12345         # X0
        self.cantidad = 10000        # Cantidad de valores a generar

        # Secuencias generadas ([], []) para Python y Java
        self.x_python = []
        self.u_python = []
        self.x_java = []
        self.u_java = []
        self.java_disponible = False

    # ------------------------------------------------------------------
    # Generación de la secuencia con la fórmula LCG
    # ------------------------------------------------------------------
    def generar(self):
        """Genera la secuencia X(n) y su versión normalizada U(n)."""
        self.x_python = []
        self.u_python = []
        x = self.semilla
        for _ in range(self.cantidad):
            x = (self.a * x + self.c) % self.m
            self.x_python.append(x)
            self.u_python.append(x / self.m)
        return self.x_python, self.u_python

    def cambiar_semilla(self, nueva_semilla):
        """Actualiza la semilla (validada en el controlador)."""
        self.semilla = nueva_semilla

    # ------------------------------------------------------------------
    # Exportación a CSV (resultados de Python)
    # ------------------------------------------------------------------
    def exportar_csv(self, ruta):
        with open(ruta, "w", encoding="utf-8") as f:
            f.write("n,X(n),U(n)\n")
            for i in range(self.cantidad):
                u = "{:.10f}".format(self.u_python[i])
                f.write("{},{},{}\n".format(i, self.x_python[i], u))

    # ------------------------------------------------------------------
    # Comparación matemática de secuencias
    # ------------------------------------------------------------------
    def comparar_secuencias(self):
        """
        Compara X(n) de forma exacta y U(n) con tolerancia 1e-12.
        Devuelve un diccionario con el resumen de la comparación.
        """
        tolerancia = 1e-12
        n_py = len(self.x_python)
        n_jv = len(self.x_java)
        coincidencias = 0
        diferencias = []
        if n_py == n_jv:
            for i in range(n_py):
                x_ok = self.x_python[i] == self.x_java[i]
                u_ok = abs(self.u_python[i] - self.u_java[i]) <= tolerancia
                if x_ok and u_ok:
                    coincidencias += 1
                elif len(diferencias) < 5:
                    # Se guardan las primeras diferencias para mostrarlas
                    diferencias.append({
                        "n": i,
                        "x_py": self.x_python[i],
                        "x_jv": self.x_java[i],
                        "u_py": self.u_python[i],
                        "u_jv": self.u_java[i],
                    })
        total_dif = max(n_py, n_jv) - coincidencias
        return {
            "n_python": n_py,
            "n_java": n_jv,
            "coincidencias": coincidencias,
            "diferencias": total_dif,
            "ejemplos": diferencias,
        }

    # ------------------------------------------------------------------
    # Análisis del período mediante el teorema de Hull-Dobell
    # ------------------------------------------------------------------
    def factores_primos(self, n):
        """Devuelve los factores primos distintos de n."""
        factores = set()
        d = 2
        while d * d <= n:
            while n % d == 0:
                factores.add(d)
                n //= d
            d += 1
        if n > 1:
            factores.add(n)
        return factores

    def gcd(self, x, y):
        while y:
            x, y = y, x % y
        return x

    def analizar_periodo(self):
        """
        Comprueba las tres condiciones de Hull-Dobell.
        Se cumplen ->
        el generador tiene período completo m sobre Z_m.
        """
        m = self.m
        # Condición 1: c y m deben ser coprimos
        cond1 = self.gcd(self.c, m) == 1
        # Condición 2: a-1 divisible por todos los factores primos de m
        primos = self.factores_primos(m)
        cond2 = all((self.a - 1) % p == 0 for p in primos)
        # Condición 3: si m es divisible por 4, a-1 también
        cond3 = True
        if m % 4 == 0:
            cond3 = (self.a - 1) % 4 == 0

        if cond1 and cond2 and cond3:
            periodo_teorico = m   # Período completo
            conclusion = ("Se cumplen todas las condiciones de Hull-Dobell: "
                          "el generador tiene período completo m = {}"
                          .format(periodo_teorico))
        else:
            periodo_teorico = None
            conclusion = ("No se cumple el período completo: el período real "
                          "es menor que m.")
        return {
            "primos": sorted(primos),
            "condicion1": cond1,
            "condicion2": cond2,
            "condicion3": cond3,
            "periodo_teorico": periodo_teorico,
            "conclusion": conclusion,
        }
