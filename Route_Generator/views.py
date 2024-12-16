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
from datetime import datetime
from .models import Pedido, Ciudad, Conexion
from .utils import (
    calcular_ruta_mas_corta,
    agrupar_pedidos,
    verificar_restricciones_tiempo,
    optimizar_camiones,
)
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from datetime import timedelta
from django.shortcuts import render
from django.http import HttpResponse


def main_view(request):
    return render(request, "Route_Generator/index.html")


def precargar_distancias(conexiones_file):
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

    pedidos = Pedido.objects.all()

    for i, ciudad in enumerate(ruta):
        if ciudad in coordinates:
            lat, lon = coordinates[ciudad]

            if ciudad == "Mataró":
                color = "green"
            elif ciudad in ciudades_destino:
                color = "red"
            else:
                color = "blue"

            if color == "red":
                numero_ciudad_destino = ciudades_destino.index(ciudad) + 1
                repeticiones = ciudades_destino.count(ciudad)
                numero_ciudad_destino_str = f"{numero_ciudad_destino}+" if repeticiones > 1 else f"{numero_ciudad_destino}"

                pedidos_ids = pedidos.filter(ciudad_destino__nombre=ciudad).values_list('id', flat=True)
                pedidos_ids_str = ", ".join(map(str, pedidos_ids))

                folium.Marker(
                    location=[lat, lon],
                    popup=f"{ciudad}",
                    tooltip=f"Pedidos: {pedidos_ids_str}",
                    icon=folium.DivIcon(
                        html=f"""
                        <div style="
                            background-color: white;
                            border: 2px solid red;
                            border-radius: 50%;
                            color: red;
                            font-size: 12px;
                            height: 25px;
                            width: 25px;
                            text-align: center;
                            line-height: 25px;">
                            {numero_ciudad_destino_str}
                        </div>
                        """
                    )
                ).add_to(mapa)
            else:
                border_color = "green" if color == "green" else "blue"
                font_color = "green" if color == "green" else "blue"
                folium.Marker(
                    location=[lat, lon],
                    popup=f"{ciudad}",
                    tooltip=f"Punto {i + 1} - {ciudad}",
                    icon=folium.DivIcon(
                        html=f"""
                        <div style="
                            background-color: white;
                            border: 2px solid {border_color};
                            border-radius: 50%;
                            color: {font_color};
                            font-size: 12px;
                            height: 15px;
                            width: 15px;
                            text-align: center;
                            line-height: 25px;">
                        </div>
                        """
                    )
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

from datetime import datetime, timedelta

def optimizar_reparto(request):
    if request.method == "POST":
        velocidad = float(request.POST.get("velocidad", 80))
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
        distancias = precargar_distancias(conexiones_file)
        pedidos = Pedido.objects.all()

        total_precio = 0
        total_kilometros = 0
        camiones_con_indices = []
        pedidos_no_entregables = []

        mejor_solucion = optimizar_camiones(pedidos, capacidad_camion, distancias)

        for camion_idx, camion in enumerate(mejor_solucion, start=1):
            destinos = ["Mataró"] + [p.ciudad_destino.nombre for p in camion] + ["Mataró"]
            ruta_completa = []
            tiempo_total = 0.0
            distancia_camion = 0
            rutas_viables = True
            precio_camion = sum(p.cantidad * p.producto.precio_venta for p in camion)

            for i in range(len(destinos) - 1):
                origen = destinos[i]
                destino = destinos[i + 1]
                try:
                    ruta_segmento = calcular_ruta_mas_corta(
                        origen,
                        destino,
                        conexiones_file,
                        datetime.now(),
                        datetime.max,
                        velocidad
                    )
                    ruta_completa.extend(ruta_segmento[:-1])
                    distancia_segmento = distancias.get(origen, {}).get(destino, 0)
                    distancia_camion += distancia_segmento
                    tiempo_total += distancia_segmento / velocidad
                except ValueError:
                    rutas_viables = False
                    break

            if not rutas_viables:
                break

            bloques_8h = int(tiempo_total // 8)
            tiempo_descanso = bloques_8h * 16
            tiempo_con_descanso = tiempo_total + tiempo_descanso
            fecha_entrega = datetime.now() + timedelta(hours=tiempo_con_descanso)

            fecha_limite = min(
                (datetime.now() + timedelta(days=p.producto.caducidad)).date() for p in camion
            )

            for pedido in camion:
                fecha_caducidad = datetime.now() + timedelta(days=pedido.producto.caducidad)
                distancia_individual = distancias.get("Mataró", {}).get(pedido.ciudad_destino.nombre, 0)

                tiempo_con_descanso_individual = calcular_tiempo_con_descansos(distancia_individual, velocidad)
                fecha_entrega_estimada = datetime.now() + timedelta(hours=tiempo_con_descanso_individual)

                if fecha_entrega_estimada.date() > fecha_caducidad.date():
                    pedidos_no_entregables.append({
                        "pedido_id": pedido.id,
                        "camion_id": camion_idx,
                        "ciudad_destino": pedido.ciudad_destino.nombre,
                        "fecha_entrega": fecha_entrega_estimada.date(),
                        "fecha_caducidad": fecha_caducidad.date(),
                    })

            coste_trayecto = distancia_camion * coste_medio
            total_precio += precio_camion
            total_kilometros += distancia_camion
            mapa_html = generar_mapa(
                camion_idx,
                ruta_completa + ["Mataró"],
                coordinates,
                None,
                [p.ciudad_destino.nombre for p in camion],
                user_location,
            )

            camiones_con_indices.append({
                "indice": camion_idx,
                "camion": camion,
                "ruta": ruta_completa + ["Mataró"],
                "distancia_camion": distancia_camion,
                "precio_camion": round(precio_camion, 2),
                "coste_trayecto": round(coste_trayecto, 2),
                "tiempo_sin_descanso": format_horas_minutos(tiempo_total),
                "tiempo_de_descanso": format_horas_minutos(tiempo_descanso),
                "tiempo_con_descanso": format_horas_minutos(tiempo_con_descanso),
                "fecha_limite": fecha_limite,
                "mapa": mapa_html,
                "fecha_entrega": fecha_entrega.date(),
            })

        if pedidos_no_entregables:
            return render(request, "Route_Generator/reparto.html", {
                "mensaje_error": "Algunos pedidos no se pueden entregar a tiempo.",
                "pedidos_no_entregables": pedidos_no_entregables,
            })

        # Calcular totales generales
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

    return render(request, "Route_Generator/reparto.html")



def calcular_tiempo_con_descansos(distancia, velocidad):
    tiempo_total = distancia / velocidad
    bloques_8h = int(tiempo_total // 8)
    tiempo_descanso = bloques_8h * 16
    tiempo_con_descanso = tiempo_total + tiempo_descanso
    return tiempo_con_descanso



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
