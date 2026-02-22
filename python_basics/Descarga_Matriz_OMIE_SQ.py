# --------------------------------------------------------------
# DESCARGA AUTOMÁTICA DE PRECIOS CUARTOHORARIOS OMIE (marginalpdbc)
# --------------------------------------------------------------

# Importamos las librerías necesarias
import requests  # Para hacer peticiones HTTP
from bs4 import BeautifulSoup  # Para analizar el HTML del listado de ficheros
import pandas as pd  # Para manejar tablas de datos (DataFrame)
from datetime import datetime  # Para manejar fechas
import calendar  # Para obtener los días de cada mes
import urllib3  # Para gestionar advertencias SSL
from pathlib import Path  # Para manejar rutas de ficheros

# --------------------------------------------------------------
# CONFIGURACIÓN DE SESIÓN REQUESTS (SSL desactivado en entorno corp.)
# --------------------------------------------------------------

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  # Desactiva las advertencias SSL
session = requests.Session()  # Creamos una sesión de requests para reutilizar conexiones
session.verify = False  # Desactiva la verificación SSL (solo usar en entorno controlado)

# --------------------------------------------------------------
# Función para obtener la lista de ficheros publicados en OMIE
# --------------------------------------------------------------
def obtener_lista_ficheros(mes: int, año: int):
    base_url = "https://www.omie.es"
    lista_url = (
        "https://www.omie.es/es/file-access-list"
        "?dir=Precios+horarios+del+mercado+diario+en+Espa%C3%B1a"
        "&realdir=marginalpdbc"
    )

    r = session.get(lista_url)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    ficheros_por_dia = {}

    for a in soup.find_all("a"):
        href = a.get("href", "")
        texto = a.get_text().strip()

        # Coincidencias tipo marginalpdbc_YYYYMMDD.N
        if texto.startswith("marginalpdbc_") and texto.endswith(tuple([f".{i}" for i in range(1, 10)])):
            try:
                fecha_str, version = texto.replace("marginalpdbc_", "").split(".")
                fecha = datetime.strptime(fecha_str, "%Y%m%d")
                version = int(version)
            except Exception:
                continue

            if fecha.year == año and fecha.month == mes:
                # Guardamos solo la versión más reciente
                if fecha not in ficheros_por_dia or version > ficheros_por_dia[fecha][0]:
                    url_fichero = base_url + href
                    ficheros_por_dia[fecha] = (version, texto, url_fichero)

    # Convertimos a lista de tuplas [(fecha, nombre, url)]
    resultados = [(fecha, nombre, url) for fecha, (_, nombre, url) in sorted(ficheros_por_dia.items())]
    return resultados


# --------------------------------------------------------------
# Función para descargar un fichero diario y extraer precios cuartohorarios
# --------------------------------------------------------------
def descargar_precio(fila):
    """
    Descarga el fichero diario y extrae los 96 precios cuartohorarios de España.
    Confirmado por OMIE (octubre 2025): la última columna numérica de cada línea
    corresponde al precio marginal español (€/MWh).
    """
    fecha, nombre, url = fila  # Desempaquetamos la información del fichero
    r = session.get(url)  # Descargamos el fichero
    r.raise_for_status()  # Verificamos que no haya errores HTTP

    precios = []  # Lista para guardar los precios del día

    # Recorremos cada línea del fichero descargado
    for linea in r.text.strip().splitlines():
        linea = linea.strip().replace("\ufeff", "")  # Limpiamos caracteres extraños
        if not linea or not linea[0].isdigit():  # Si no empieza con número, no es línea de datos
            continue

        # Dividimos la línea por ';' y limpiamos espacios vacíos
        partes = [p.strip() for p in linea.split(";") if p.strip() != ""]
        if len(partes) < 5:
            continue  # Si no hay suficientes columnas, se ignora

        # Buscamos el último valor numérico (precio español)
        precio_es = None
        for campo in reversed(partes):
            try:
                precio_es = float(campo.replace(",", "."))  # Convertimos a float
                break
            except ValueError:
                continue

        # Si encontramos un precio válido, lo añadimos a la lista
        if precio_es is not None:
            precios.append(precio_es)

    # Comprobamos que haya 96 precios (96 cuartohoras)
    if len(precios) != 96:
        raise ValueError(
            f"{fecha.strftime('%Y-%m-%d')}: se obtuvieron {len(precios)} precios (esperado 96) desde {url}"
        )

    # Devolvemos la fecha y la lista de precios
    return fecha, precios

# --------------------------------------------------------------
# Construir matriz mensual y escribir fichero con formato idéntico (sin columna Media)
# --------------------------------------------------------------
def construir_matriz_con_listado(mes: int, año: int, salida="matriz.txt"):
    # Obtenemos la lista de ficheros disponibles en OMIE para el mes
    fich_list = obtener_lista_ficheros(mes, año)
    
    # Creamos un diccionario {fecha: (nombre, url)} para acceso rápido
    perms = {fecha: (nombre, url) for fecha, nombre, url in fich_list}
    
    # Obtenemos el número de días del mes
    dias_mes = calendar.monthrange(año, mes)[1]

    # Nombres cortos de los días de la semana en español
    dias_sem = ["L", "M", "X", "J", "V", "S", "D"]

    matriz = []  # Lista donde se guardará la matriz mensual completa

    # Recorremos todos los días del mes
    for d in range(1, dias_mes + 1):
        fecha = datetime(año, mes, d)  # Construimos el objeto fecha
        etiqueta = f"{dias_sem[fecha.weekday()]} {fecha.day:02d}"  # Ejemplo: "L 01"
        
        # Si el fichero existe en OMIE, lo descargamos
        if fecha in perms:
            nombre, url = perms[fecha]
            try:
                _, precios = descargar_precio((fecha, nombre, url))  # Descargamos precios
                print(f"Descargado {fecha.strftime('%Y-%m-%d')}: {len(precios)} precios")
            except Exception as e:
                print("⚠️ Error descarga/parseo día", fecha.strftime("%Y-%m-%d"), ":", e)
                precios = [None] * 96  # Si hay error, dejamos el día vacío
        else:
            print("⚠️ No hay fichero para día", fecha.strftime("%Y-%m-%d"))
            precios = [None] * 96  # Día sin fichero -> todo vacío

        # Añadimos la fila del día: [Etiqueta + precios]
        matriz.append([etiqueta] + precios)

    # Definimos los nombres de las columnas: Día + 1..96
    cols = ["Día"] + [str(i) for i in range(1, 97)]

    # Creamos el DataFrame con pandas
    df = pd.DataFrame(matriz, columns=cols)

    # Calculamos las medias por columna (para la fila "Total")
    medias_columnas = df.iloc[:, 1:97].mean(skipna=True)  # Serie con 96 valores

    # Lista de nombres de los meses en español
    meses_es = [
        "", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]
    mes_nombre = meses_es[mes]  # Nombre del mes actual

    # ----------------------------------------------------------
    # Escritura del fichero de salida con formato OMIE
    # ----------------------------------------------------------
    with open(salida, "w", encoding="utf-8") as f:
        # Escribimos cabecera (idéntica a la oficial, con 5 ';' al final)
        header_line = (
            f"OMIE - Mercado de electricidad;"
            f"Fecha Emisión :{datetime.now().strftime('%d/%m/%Y - %H:%M')};; "
            f"{mes_nombre} {año};Precio del mercado diario español (EUR/MWh);;;;;\n\n"
        )
        f.write(header_line)

        # Escribimos la fila de nombres de columnas (con ';' final)
        header_cols = ["Día"] + [str(i) for i in range(1, 97)]
        f.write(";".join(header_cols) + ";\n")

        # Línea "Tramos :" (idéntica al formato OMIE)
        f.write("Tramos :;149;7,82;47,06\n")

        # Escribimos cada fila de datos
        for _, row in df.iterrows():
            salida_campos = []  # Lista temporal para construir la línea
            for c in header_cols:
                v = row[c]
                if pd.isna(v) or v is None:
                    salida_campos.append("")  # Campo vacío
                else:
                    if isinstance(v, str):
                        salida_campos.append(v)  # Día (texto)
                    else:
                        salida_campos.append(f"{v:.2f}".replace(".", ","))  # Número con coma decimal
            f.write(";".join(salida_campos) + ";\n")  # Añadimos ';' final

        f.write("\n")  # Línea vacía antes del total

        # Escribimos la fila "Total " con las medias de cada tramo
        tot_line = ["Total "]
        for val in medias_columnas:
            if pd.isna(val):
                tot_line.append("")  # Dejar vacío si no hay datos
            else:
                tot_line.append(f"{val:.2f}".replace(".", ","))  # Formatear número
        f.write(";".join(tot_line) + ";\n")

        # Línea final de separación con muchos ';'
        f.write(";" * 98 + "\n")

    # Mensaje de confirmación
    print("✅ Fichero generado correctamente:", salida)


# --------------------------------------------------------------
# EJECUCIÓN PRINCIPAL (ejemplo de uso)
# --------------------------------------------------------------

from pathlib import Path

if __name__ == "__main__":
    # Pedimos el mes y el año por consola
    mes_elegido = int(input("Mes de precios a descargar (1-12): "))
    año_elegido = int(input("Año de precios a descargar (por ejemplo 2025): "))

    # Carpeta de descargas por defecto
    carpeta_descargas = Path.home() / "Downloads"

    # Pedimos al usuario una ruta personalizada
    ruta_usuario = input(
        f"Introduce la ruta donde guardar el archivo (Enter para usar {carpeta_descargas}): "
    ).strip()

    # Si el usuario no escribe nada, usamos la carpeta de descargas
    if ruta_usuario:
        ruta_salida = Path(ruta_usuario) / f"OMIE_QH_{año_elegido}{mes_elegido:02d}.txt"
    else:
        ruta_salida = carpeta_descargas / f"OMIE_QH_{año_elegido}{mes_elegido:02d}.txt"

    # Mostramos la ruta final
    print(f"\nEl archivo se guardará en:\n{ruta_salida}\n")

    # Ejecutamos la descarga
    construir_matriz_con_listado(mes_elegido, año_elegido, salida=ruta_salida)