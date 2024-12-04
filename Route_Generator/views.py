import pandas as pd
import folium
import networkx as nx
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from django.http import HttpResponse
from django.shortcuts import render
from datetime import date
from .models import Pedido, Ciudad, Conexion
from .utils import agrupar_pedidos, calcular_ruta_optima, filtrar_pedidos_validos
from .utils import (
    calcular_ruta_mas_corta,
    agrupar_pedidos,
    verificar_restricciones_tiempo,
    optimizar_camiones,
    algoritmo_genetico,
)
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from datetime import timedelta
from django.shortcuts import render
from django.http import HttpResponse


def main_view(request):
    return render(request, "Route_Generator/index.html")


def precargar_distancias(conexiones_file):
    """Precalcula las distancias entre todas las ciudades usando Dijkstra."""
    conexiones_data = pd.read_csv(conexiones_file)
    G = nx.Graph()

    for _, row in conexiones_data.iterrows():
        capital1 = row["Capital_1"].strip()
        capital2 = row["Capital_2"].strip()
        peso = float(row["Peso"])
        G.add_edge(capital1, capital2, weight=peso)

    ciudades = list(G.nodes())
    distancias = {ciudad: {} for ciudad in ciudades}

    for ciudad in ciudades:
        paths = nx.single_source_dijkstra_path_length(G, ciudad, weight="weight")
        for destino, distancia in paths.items():
            distancias[ciudad][destino] = distancia

    return distancias


from datetime import timedelta


def optimizar_reparto(request):
    pedidos = Pedido.objects.all()
    conexiones_file = "Route_Generator/static/csv/conexion.csv"
    capacidad_camion = 50
    distancias = precargar_distancias(conexiones_file)
    velocidad_media = 120

    for key, value in distancias.items():
        if "peso" in value:
            value["peso"] /= velocidad_media  # Convertir distancias a tiempo (horas)

    # Parámetros para el reagrupamiento
    max_reintentos = 10  # Limite de intentos de reagrupación
    reintento = 0

    while reintento < max_reintentos:
        mejor_solucion = optimizar_camiones(pedidos, capacidad_camion, distancias)

        fecha_limite_minima = None
        fecha_disponible_maxima = None

        for camion in mejor_solucion:
            for pedido in camion:
                fecha_limite = Pedido.fecha_limite_entrega(pedido)
                fecha_envio = Pedido.fecha_disponible(pedido)

                if fecha_limite_minima is None or fecha_limite < fecha_limite_minima:
                    fecha_limite_minima = fecha_limite

                if fecha_disponible_maxima is None or fecha_envio > fecha_disponible_maxima:
                    fecha_disponible_maxima = fecha_envio

        rutas_por_camion = []
        camiones_con_indices = []
        rutas_viables = True
        viabilidad_rutas = []  # Lista para almacenar la viabilidad de las rutas
        tiempos_rutas = []  # Lista para almacenar los tiempos estimados de las rutas

        for camion_idx, camion in enumerate(mejor_solucion, start=1):
            destinos = (
                    ["Mataró"]
                    + [pedido.ciudad_destino.nombre for pedido in camion]
                    + ["Mataró"]
            )

            # Generar la ruta del camión
            ruta_completa = []
            tiempo_total = 0  # Tiempo total de la ruta en horas
            for i in range(len(destinos) - 1):
                origen = destinos[i]
                destino = destinos[i + 1]

                try:
                    ruta_segmento = calcular_ruta_mas_corta(
                        origen,
                        destino,
                        conexiones_file,
                        fecha_disponible_maxima,
                        fecha_limite_minima,
                    )
                    ruta_completa.extend(ruta_segmento[:-1])  # Evitar duplicados

                    # Calcular el tiempo de este segmento y acumularlo
                    distancia_segmento = distancias.get((origen, destino), {}).get("peso", 0)
                    tiempo_segmento = distancia_segmento / velocidad_media  # Tiempo en horas
                    tiempo_total += tiempo_segmento

                except ValueError:
                    rutas_viables = False  # Marcar que la ruta no es viable
                    viabilidad_rutas.append({
                        "camion_idx": camion_idx,
                        "origen": origen,
                        "destino": destino,
                        "mensaje": "Ruta no viable"
                    })
                    break

            if not rutas_viables:
                break  # Detener el procesamiento y reintentar

            ruta_completa.append("Mataró")
            rutas_por_camion.append(ruta_completa)
            camiones_con_indices.append(
                {"indice": camion_idx, "camion": camion, "ruta": ruta_completa}
            )

            # **Aquí corregimos la definición de tiempo_limite**
            # Asegúrate de que las fechas son objetos de tipo `datetime`
            if fecha_limite_minima is not None and fecha_disponible_maxima is not None:
                # Calcular la diferencia entre las fechas en horas
                tiempo_restante = fecha_limite_minima - fecha_disponible_maxima
                if tiempo_restante < timedelta(0):  # Si la diferencia es negativa
                    tiempo_limite = 0
                else:
                    tiempo_limite = tiempo_restante.total_seconds() / 3600  # Convertir a horas
            else:
                tiempo_limite = float('inf')  # Si no hay fecha límite, asignar un valor infinito

            # Guardamos el tiempo de la ruta
            tiempos_rutas.append({
                "camion_idx": camion_idx,
                "tiempo_estimado": tiempo_total,
                "tiempo_limite": tiempo_limite,
                "tiempo_previsto": fecha_disponible_maxima,
                "mensaje": "Ruta dentro del límite" if tiempo_total <= tiempo_limite else "Ruta excede el límite"
            })

        if rutas_viables:
            # Si todas las rutas son viables, renderizar y salir del bucle
            return render(
                request,
                "Route_Generator/reparto.html",
                {
                    "camiones_con_indices": camiones_con_indices,
                    "viabilidad_rutas": viabilidad_rutas,  # Añadir la viabilidad de las rutas
                    "tiempos_rutas": tiempos_rutas  # Añadir los tiempos de las rutas
                },
            )

        # Incrementar el contador de reintentos si alguna ruta no fue viable
        reintento += 1

    # Si no se encuentra una solución tras los reintentos, devolver un mensaje de error
    return render(
        request,
        "Route_Generator/error.html",
        {
            "mensaje": "No se pudo encontrar una solución viable después de varios intentos de reagrupación.",
        },
    )


def mostrar_mapa(request):
    csv_file = "Route_Generator/static/csv/csv.csv"
    data = pd.read_csv(csv_file)

    data["Latitud"] = data["Latitud"].str.replace(",", ".").astype(float)
    data["Longitud"] = data["Longitud"].str.replace(",", ".").astype(float)

    mapa = folium.Map(location=[40.4637, -3.7492], zoom_start=6)

    coordinates = {}
    for i, row in data.iterrows():
        coordinates[row["Capital"]] = (row["Latitud"], row["Longitud"])

    for i, row in data.iterrows():
        folium.Marker(
            location=[row["Latitud"], row["Longitud"]],
            popup=f"{row['Capital']} - {row['Provincia']}",
        ).add_to(mapa)

    G = nx.Graph()

    conexiones_file = "Route_Generator/static/csv/conexion.csv"
    conexiones_data = pd.read_csv(conexiones_file)

    for i, row in conexiones_data.iterrows():
        capital1 = row["Capital_1"]
        capital2 = row["Capital_2"]
        peso = row["Peso"]

        if capital1 in coordinates and capital2 in coordinates:
            G.add_edge(capital1, capital2, weight=peso)

            coord1 = coordinates[capital1]
            coord2 = coordinates[capital2]

            folium.PolyLine(
                locations=[coord1, coord2], color="blue", weight=2.5, opacity=1
            ).add_to(mapa)

    def obtener_ruta_mas_corta(ciudad1, ciudad2):
        try:
            ruta = nx.shortest_path(G, source=ciudad1, target=ciudad2, weight="weight")
            distancia = nx.shortest_path_length(
                G, source=ciudad1, target=ciudad2, weight="weight"
            )
            return ruta, distancia
        except nx.NetworkXNoPath:
            return None, None

    if request.method == "POST":
        ciudad_origen = "Mataró"
        ciudad_destino = request.POST.get("ciudad_destino", None)

        if ciudad_origen and ciudad_destino:
            ruta, distancia = obtener_ruta_mas_corta(ciudad_origen, ciudad_destino)
            if ruta:
                html_content = render_to_string(
                    "Route_Generator/pdf.html",
                    {
                        "ciudad_origen": ciudad_origen,
                        "ciudad_destino": ciudad_destino,
                        "ruta": ruta,
                        "distancia": distancia,
                    },
                )

                response = HttpResponse(content_type="application/pdf")
                response["Content-Disposition"] = (
                    f'attachment; filename="ruta_{ciudad_origen}_{ciudad_destino}.pdf"'
                )

                pisa_status = pisa.CreatePDF(html_content, dest=response)

                if pisa_status.err:
                    return HttpResponse(f"Error al generar el PDF: {pisa_status.err}")

                return response
            else:
                mensaje = (
                    f"No hay ruta disponible entre {ciudad_origen} y {ciudad_destino}."
                )
                return render(
                    request, "Route_Generator/index.html", {"mensaje": mensaje}
                )
        else:
            mensaje = "Por favor, ingrese dos ciudades para calcular la ruta."
            return render(request, "Route_Generator/index.html", {"mensaje": mensaje})

    map_path = "Route_Generator/static/mapas/mapa_espana.html"
    mapa.save(map_path)

    return render(request, "Route_Generator/index.html", {"map_path": map_path})


def calcular_distancia(origen, destino, conexiones_file):
    """Devuelve la distancia entre dos ciudades."""
    conexiones_data = pd.read_csv(conexiones_file)
    fila = conexiones_data[
        (conexiones_data["Capital_1"] == origen)
        & (conexiones_data["Capital_2"] == destino)
    ]
    if fila.empty:
        # Si no se encuentra conexión directa, prueba en el otro sentido
        fila = conexiones_data[
            (conexiones_data["Capital_1"] == destino)
            & (conexiones_data["Capital_2"] == origen)
        ]
    if not fila.empty:
        return float(fila.iloc[0]["Peso"])
    else:
        raise ValueError(f"No se encontró conexión entre {origen} y {destino}.")
