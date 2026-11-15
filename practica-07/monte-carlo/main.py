"""Lanzador principal de la práctica: Método Monte Carlo para aproximar π.

Punto de entrada único del proyecto: permite ejecutar la implementación en
Python, la de Java, comparar resultados y generar todas las gráficas sin
salir de la aplicación.

Ejecución:
    cd ~/Documentos/monte-carlo
    python3 main.py

Este archivo actúa únicamente como lanzador y coordinador general: no
contiene la lógica matemática ni duplica el código de las implementaciones.
La lógica de Python se reutiliza importando sus capas ya existentes y la de
Java se compila y ejecuta como proceso independiente desde su carpeta.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

# Rutas absolutas construidas a partir de la ubicación del proyecto.
PROYECTO = Path(__file__).resolve().parent
CARPETA_PYTHON = PROYECTO / "python"
CARPETA_JAVA = PROYECTO / "java"
ARCHIVO_MAIN_PYTHON = CARPETA_PYTHON / "main.py"
FUENTES_JAVA = CARPETA_JAVA / "src"
CARPETA_CLASES_JAVA = CARPETA_JAVA / "bin"
JAR_JFREECHART = CARPETA_JAVA / "lib" / "jfreechart-1.5.5.jar"
JDK_PREDETERMINADO = Path.home() / "tools" / "jdk-21.0.13+9"

# La carpeta python/ se añade a sys.path para reutilizar directamente sus
# capas ya implementadas (controlador, persistencia, graficas) sin duplicar
# código en el lanzador.
sys.path.insert(0, str(CARPETA_PYTHON))


def mostrar_menu():
    """Muestra el menú principal de la práctica."""
    print()
    print("=" * 48)
    print("          PRACTICA METODO MONTE CARLO")
    print("=" * 48)
    print()
    print("Seleccione la implementacion que desea ejecutar:")
    print()
    print("1. Ejecutar implementacion en Python.")
    print("2. Ejecutar implementacion en Java.")
    print("3. Comparar resultados de Python y Java.")
    print("4. Generar todas las graficas.")
    print("5. Salir.")
    print()


def ejecutar_python():
    """Ejecuta el programa Python dentro de su carpeta y regresa al menú principal."""
    try:
        resultado = subprocess.run(
            [sys.executable, str(ARCHIVO_MAIN_PYTHON)],
            cwd=CARPETA_PYTHON,
        )
    except OSError as error:
        print(f"ERROR: No se pudo ejecutar el programa Python: {error}")
        return
    if resultado.returncode != 0:
        print("ERROR: El programa Python terminó con errores.")


def _resolver_jdk():
    """Localiza el JDK: JAVA_HOME, la ruta predeterminada del equipo o el PATH.

    Devuelve una tupla (ruta_java, ruta_javac) o None si no hay JDK disponible.
    """
    candidatos = []
    java_home = os.environ.get("JAVA_HOME")
    if java_home:
        candidatos.append(Path(java_home))
    candidatos.append(JDK_PREDETERMINADO)
    for carpeta in candidatos:
        java_bin = carpeta / "bin" / "java"
        javac_bin = carpeta / "bin" / "javac"
        if java_bin.is_file() and javac_bin.is_file():
            return java_bin, javac_bin
    if shutil.which("java") and shutil.which("javac"):
        return Path(shutil.which("java")), Path(shutil.which("javac"))
    return None


def compilar_java():
    """Compila el programa Java con el JDK configurado.

    Devuelve True si la compilación fue exitosa; en caso contrario muestra
    un mensaje claro del problema.
    """
    jdk = _resolver_jdk()
    if jdk is None:
        print("ERROR: No se encontró el JDK de Java.")
        print("Instale un JDK (sudo apt install default-jdk) o configure JAVA_HOME,")
        print(f"por ejemplo: export JAVA_HOME={JDK_PREDETERMINADO}")
        return False
    if not JAR_JFREECHART.is_file():
        print(f"ERROR: No se encontró la biblioteca JFreeChart en: {JAR_JFREECHART}")
        return False
    fuentes = sorted(FUENTES_JAVA.rglob("*.java"))
    if not fuentes:
        print(f"ERROR: No se encontraron archivos fuente Java en: {FUENTES_JAVA}")
        return False

    _, javac = jdk
    CARPETA_CLASES_JAVA.mkdir(parents=True, exist_ok=True)
    print("Compilando el programa Java...")
    comando = [str(javac), "-encoding", "UTF-8",
               "-cp", str(JAR_JFREECHART),
               "-d", str(CARPETA_CLASES_JAVA)]
    comando.extend(str(fuente) for fuente in fuentes)
    try:
        resultado = subprocess.run(comando, cwd=CARPETA_JAVA)
    except OSError as error:
        print(f"ERROR: No se pudo invocar el compilador de Java: {error}")
        return False
    if resultado.returncode != 0:
        print("ERROR: La compilación de Java falló. Revise los mensajes anteriores.")
        return False
    return True


def _ejecutar_java(argumentos):
    """Ejecuta la clase Main de Java desde su carpeta con argumentos extra.

    Devuelve True si el programa terminó correctamente.
    """
    jdk = _resolver_jdk()
    if jdk is None:
        return False
    java_bin, _ = jdk
    classpath = f"{CARPETA_CLASES_JAVA}{os.pathsep}{JAR_JFREECHART}"
    entorno = dict(os.environ)
    entorno["JAVA_HOME"] = str(java_bin.parent.parent)
    entorno["PATH"] = f"{java_bin.parent}{os.pathsep}{entorno.get('PATH', '')}"
    comando = [str(java_bin), "-cp", classpath, "Main", *argumentos]
    try:
        resultado = subprocess.run(comando, cwd=CARPETA_JAVA, env=entorno)
    except OSError as error:
        print(f"ERROR: No se pudo ejecutar el programa Java: {error}")
        return False
    return resultado.returncode == 0


def ejecutar_java():
    """Compila y ejecuta el programa Java; al salir regresa al menú principal."""
    if not compilar_java():
        return
    if not _ejecutar_java([]):
        print("ERROR: El programa Java terminó con errores.")


def comparar():
    """Ejecuta la comparación reutilizando el controlador de Python."""
    try:
        from controlador.controlador import Controlador
    except ImportError as error:
        print("ERROR: No se pudieron cargar los módulos de Python.")
        print(f"Detalle: {error}")
        print("Si falta matplotlib, instálelo con: pip3 install --user matplotlib")
        return
    Controlador().comparar()


def generar_todas_las_graficas():
    """Genera las gráficas individuales y comparativas desde los CSV existentes.

    No ejecuta experimentos ni inventa resultados: si falta el CSV de un
    lenguaje, informa qué experimentos debe ejecutar el usuario primero.
    """
    try:
        from persistencia import gestor_csv
    except ImportError as error:
        print(f"ERROR: No se pudieron cargar los módulos de Python: {error}")
        return
    try:
        from graficas import generador_graficas
    except ImportError as error:
        generador_graficas = None
        print("AVISO: matplotlib no está disponible; no se podrán generar las "
              "gráficas de Python ni las comparativas.")
        print(f"Detalle: {error}")
        print("Instale matplotlib con: pip3 install --user matplotlib")

    datos_py = gestor_csv.leer_resultados(gestor_csv.ARCHIVO_PYTHON)
    datos_java = gestor_csv.leer_resultados(gestor_csv.ARCHIVO_JAVA)

    if datos_py is not None and generador_graficas is not None:
        generador_graficas.generar_graficas_python(datos_py)
        print(f"Gráficas de Python generadas en: "
              f"{generador_graficas.CARPETA_GRAFICAS_PYTHON}")
    elif datos_py is None:
        print(f"ERROR: No existen resultados de Python: {gestor_csv.ARCHIVO_PYTHON}")
        print("Ejecute primero los experimentos de Python: opción 1 de este menú, "
              "y luego la opción 1 del menú de Python.")

    if datos_java is not None:
        if compilar_java() and _ejecutar_java(["graficas"]):
            print(f"Gráficas de Java generadas en: {CARPETA_JAVA / 'graficas'}")
    else:
        print(f"ERROR: No existen resultados de Java: {gestor_csv.ARCHIVO_JAVA}")
        print("Ejecute primero los experimentos de Java: opción 2 de este menú, "
              "y luego la opción 1 del menú de Java.")

    if datos_py is not None and datos_java is not None:
        if generador_graficas is not None:
            generador_graficas.generar_graficas_comparacion(datos_py, datos_java)
            print(f"Gráficas comparativas generadas en: "
                  f"{generador_graficas.CARPETA_GRAFICAS_COMPARACION}")
    else:
        print("Para las gráficas comparativas se necesitan los resultados "
              "de ambos lenguajes.")


def _leer_opcion():
    """Lee una opción del descriptor de entrada byte a byte.

    Se lee carácter a carácter para no consumir (bufferizar) más entrada de
    la que corresponde, de modo que los datos restantes queden disponibles
    para los programas hijos (Python o Java) que heredan la entrada.

    Devuelve None cuando la entrada termina (EOF).
    """
    print("Seleccione una opcion: ", end="", flush=True)
    linea = bytearray()
    while True:
        try:
            byte = os.read(0, 1)
        except OSError:
            return None
        if not byte:  # EOF
            return linea.decode("utf-8", "replace").strip() or None
        if byte == b"\n":
            return linea.decode("utf-8", "replace").strip()
        if byte != b"\r":
            linea += byte


def main():
    """Muestra el menú principal y coordina las opciones hasta que se salga."""
    while True:
        mostrar_menu()
        opcion = _leer_opcion()
        if opcion is None:
            print()
            break
        if opcion == "1":
            ejecutar_python()
        elif opcion == "2":
            ejecutar_java()
        elif opcion == "3":
            comparar()
        elif opcion == "4":
            generar_todas_las_graficas()
        elif opcion == "5":
            print("¡Hasta luego!")
            break
        else:
            print("ERROR: Opción no válida, intente de nuevo.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print("Programa interrumpido. ¡Hasta luego!")
