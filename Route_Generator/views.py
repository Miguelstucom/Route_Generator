import pandas as pd
import folium
import networkx as nx
from django.shortcuts import render
from folium.plugins import MarkerCluster
from django.shortcuts import render
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
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


def generar_mapa(camion_idx, ruta, coordinates, grafo, ciudades_destino, user_location=None):
    mapa = folium.Map(location=[40.4637, -3.7492], zoom_start=6, max_zoom=12, min_zoom=6)

    for i, ciudad in enumerate(ruta):
        if ciudad in coordinates:
            lat, lon = coordinates[ciudad]
            color = "red" if ciudad in ciudades_destino else "blue"
            folium.Marker(
                location=[lat, lon],
                popup=f"{ciudad}",
                tooltip=f"Punto {i + 1}",
                icon=folium.Icon(color=color)
            ).add_to(mapa)

    for i in range(len(ruta) - 1):
        ciudad1 = ruta[i]
        ciudad2 = ruta[i + 1]
        if ciudad1 in coordinates and ciudad2 in coordinates:
            coord1 = coordinates[ciudad1]
            coord2 = coordinates[ciudad2]
            folium.PolyLine(
                locations=[coord1, coord2],
                color="blue",
                weight=2.5,
                opacity=1
            ).add_to(mapa)

    if user_location:
        camion_icon = folium.CustomIcon(
            icon_image="Route_Generator/static/icons/camion.png",
            icon_size=(50, 50)
        )
        folium.Marker(
            location=user_location,
            popup="Tu ubicación",
            tooltip="Tu ubicación",
            icon=camion_icon
        ).add_to(mapa)

    return mapa._repr_html_()


def optimizar_reparto(request):
    if request.method == "POST":
        velocidad = float(request.POST.get("velocidad", 120))
        coste_medio = float(request.POST.get("coste", 0.5))
        capacidad_camion = float(request.POST.get("capacidad", 50))

        user_lat = request.POST.get("user_lat", "").strip()
        user_lon = request.POST.get("user_lon", "").strip()
        user_location = None
        if user_lat and user_lon:
            try:
                user_location = (float(user_lat), float(user_lon))
            except ValueError:
                user_location = None

        csv_file = "Route_Generator/static/csv/csv.csv"
        data = pd.read_csv(csv_file)
        data["Latitud"] = data["Latitud"].str.replace(",", ".").astype(float)
        data["Longitud"] = data["Longitud"].str.replace(",", ".").astype(float)

        coordinates = {
            row["Capital"]: (row["Latitud"], row["Longitud"]) for _, row in data.iterrows()
        }

        conexiones_file = "Route_Generator/static/csv/conexion.csv"
        conexiones_data = pd.read_csv(conexiones_file)
        G = nx.Graph()
        for _, row in conexiones_data.iterrows():
            capital1, capital2, peso = row["Capital_1"], row["Capital_2"], row["Peso"]
            if capital1 in coordinates and capital2 in coordinates:
                G.add_edge(capital1, capital2, weight=peso)

        distancias = precargar_distancias(conexiones_file)
        pedidos = Pedido.objects.all()
        max_reintentos = 10
        reintento = 0

        total_precio = 0
        total_kilometros = 0
        camiones_con_indices = []

        while reintento < max_reintentos:
            mejor_solucion = optimizar_camiones(pedidos, capacidad_camion, distancias)

            fecha_limite_minima = None
            fecha_disponible_maxima = None

            for camion in mejor_solucion:
                for pedido in camion:
                    fecha_limite = pedido.fecha_limite_entrega()
                    fecha_envio = pedido.fecha_disponible()

                    if fecha_limite_minima is None or fecha_limite < fecha_limite_minima:
                        fecha_limite_minima = fecha_limite

                    if (
                        fecha_disponible_maxima is None
                        or fecha_envio > fecha_disponible_maxima
                    ):
                        fecha_disponible_maxima = fecha_envio

            rutas_viables = True
            rutas_por_camion = []
            viabilidad_rutas = []
            tiempos_rutas = []

            for camion_idx, camion in enumerate(mejor_solucion, start=1):
                fecha_limite_minima_camion = None
                fecha_disponible_maxima_camion = None

                for pedido in camion:
                    fecha_limite = pedido.fecha_limite_entrega()
                    fecha_envio = pedido.fecha_disponible()

                    if (
                        fecha_limite_minima_camion is None
                        or fecha_limite < fecha_limite_minima_camion
                    ):
                        fecha_limite_minima_camion = fecha_limite

                    if (
                        fecha_disponible_maxima_camion is None
                        or fecha_envio > fecha_disponible_maxima_camion
                    ):
                        fecha_disponible_maxima_camion = fecha_envio

                destinos = ["Mataró"] + [p.ciudad_destino.nombre for p in camion] + ["Mataró"]
                ruta_completa = []
                distancia_camion = 0
                tiempo_total = 0.0

                precio_camion = sum(p.cantidad * p.producto.precio_venta for p in camion)
                for i in range(len(destinos) - 1):
                    origen = destinos[i]
                    destino = destinos[i + 1]

                    try:
                        ruta_segmento = calcular_ruta_mas_corta(
                            origen,
                            destino,
                            conexiones_file,
                            fecha_disponible_maxima_camion,
                            fecha_limite_minima_camion,
                        )
                        ruta_completa.extend(ruta_segmento[:-1])
                        distancia_segmento = distancias.get(origen, {}).get(destino, 0)
                        distancia_camion += distancia_segmento
                        tiempo_total += distancia_segmento / velocidad
                    except ValueError:
                        rutas_viables = False
                        viabilidad_rutas.append(
                            {
                                "camion_idx": camion_idx,
                                "origen": origen,
                                "destino": destino,
                                "mensaje": "Ruta no viable",
                            }
                        )
                        break

                if not rutas_viables:
                    break

                ruta_completa.append("Mataró")
                bloques_8h = int(tiempo_total // 8)
                tiempo_de_descanso = bloques_8h * 16
                tiempo_con_descanso = tiempo_total + tiempo_de_descanso
                coste_trayecto = distancia_camion * coste_medio

                total_precio += precio_camion
                total_kilometros += distancia_camion

                mapa_html = generar_mapa(
                    camion_idx,
                    ruta_completa,
                    coordinates,
                    G,
                    [p.ciudad_destino.nombre for p in camion],
                    user_location,
                )

                camiones_con_indices.append({
                    "indice": camion_idx,
                    "camion": camion,
                    "ruta": ruta_completa,
                    "precio_camion": round(precio_camion, 2),
                    "distancia_camion": distancia_camion,
                    "coste_trayecto": round(coste_trayecto, 2),
                    "tiempo_sin_descanso": format_horas_minutos(tiempo_total),
                    "tiempo_de_descanso": format_horas_minutos(tiempo_de_descanso),
                    "tiempo_con_descanso": format_horas_minutos(tiempo_con_descanso),
                    "fecha_limite": fecha_disponible_maxima_camion,
                    "mapa": mapa_html,
                })

            if rutas_viables:
                tiempo_total_sin_descanso = total_kilometros / velocidad
                bloques_totales = tiempo_total_sin_descanso // 8
                tiempo_total_de_descanso = bloques_totales * 16
                tiempo_total_con_descanso = tiempo_total_sin_descanso + tiempo_total_de_descanso
                coste_reparto = total_kilometros * coste_medio

                return render(request, "Route_Generator/reparto.html", {
                    "camiones_con_indices": camiones_con_indices,
                    "total_precio": round(total_precio, 2),
                    "total_kilometros": total_kilometros,
                    "coste_reparto": round(coste_reparto, 2),
                    "tiempo_total_sin_descanso": format_horas_minutos(tiempo_total_sin_descanso),
                    "tiempo_total_de_descanso": format_horas_minutos(tiempo_total_de_descanso),
                    "tiempo_total_con_descanso": format_horas_minutos(tiempo_total_con_descanso),
                })

            reintento += 1

        return render(request, "Route_Generator/error.html", {
            "mensaje": "No se pudo encontrar una solución viable después de varios intentos.",
        })

    return render(request, "Route_Generator/reparto.html")




def format_horas_minutos(tiempo_horas):
    horas = int(tiempo_horas)
    minutos = round((tiempo_horas - horas) * 60)
    return f"{horas}h {minutos}m"




def calcular_tiempo_con_descanso(tiempo_horas):
    bloques_trabajo = tiempo_horas // 8
    tiempo_restante = tiempo_horas % 8
    descanso = bloques_trabajo * 8
    tiempo_total = bloques_trabajo * 8 + descanso + tiempo_restante

    tiempo_redondeado = round(tiempo_total, 2)

    horas = int(tiempo_redondeado)
    minutos = round((tiempo_redondeado - horas) * 60)

    return f"{horas}H {minutos}m"


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
        fila = conexiones_data[
            (conexiones_data["Capital_1"] == destino)
            & (conexiones_data["Capital_2"] == origen)
        ]
    if not fila.empty:
        return float(fila.iloc[0]["Peso"])
    else:
        raise ValueError(f"No se encontró conexión entre {origen} y {destino}.")
