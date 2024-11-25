import pandas as pd
import folium
import networkx as nx
from django.shortcuts import render
def main_view(request):
    return render(request, 'Route_Generator/index.html')


def mostrar_mapa(request):
    csv_file = "Route_Generator/static/csv/csv.csv"
    data = pd.read_csv(csv_file)

    data["Latitud"] = data["Latitud"].str.replace(",", ".").astype(float)
    data["Longitud"] = data["Longitud"].str.replace(",", ".").astype(float)

    mapa = folium.Map(location=[40.4637, -3.7492], zoom_start=6)

    coordinates = {}
    for i, row in data.iterrows():
        coordinates[row['Capital']] = (row['Latitud'], row['Longitud'])

    for i, row in data.iterrows():
        folium.Marker(
            location=[row["Latitud"], row["Longitud"]],
            popup=f"{row['Capital']} - {row['Provincia']}"
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
                locations=[coord1, coord2],
                color="blue",
                weight=2.5,
                opacity=1
            ).add_to(mapa)

    def obtener_ruta_mas_corta(ciudad1, ciudad2):
        try:
            ruta = nx.shortest_path(G, source=ciudad1, target=ciudad2, weight='weight')
            distancia = nx.shortest_path_length(G, source=ciudad1, target=ciudad2, weight='weight')
            return ruta, distancia
        except nx.NetworkXNoPath:
            return None, None

    mensaje = ""
    if request.method == 'POST':
        ciudad_origen = 'Mataró'
        ciudad_destino = request.POST.get('ciudad_destino', None)

        if ciudad_origen and ciudad_destino:
            ruta, distancia = obtener_ruta_mas_corta(ciudad_origen, ciudad_destino)
            if ruta:
                mensaje = f"La ruta más corta entre {ciudad_origen} y {ciudad_destino} es: {ruta}"
                for i in range(len(ruta) - 1):
                    capital1 = ruta[i]
                    capital2 = ruta[i + 1]
                    coord1 = coordinates[capital1]
                    coord2 = coordinates[capital2]

                    folium.PolyLine(
                        locations=[coord1, coord2],
                        color="red",
                        weight=4,
                        opacity=1
                    ).add_to(mapa)

                    folium.Marker(
                        location=coord1,
                        popup=f"{capital1} en la ruta",
                        icon=folium.Icon(color="red", icon="info-sign")
                    ).add_to(mapa)

                folium.Marker(
                    location=coordinates[ruta[-1]],
                    popup=f"{ruta[-1]} - Destino",
                    icon=folium.Icon(color="red", icon="info-sign")
                ).add_to(mapa)
            else:
                mensaje = f"No hay ruta disponible entre {ciudad_origen} y {ciudad_destino}."
        else:
            mensaje = "Por favor, ingrese dos ciudades para calcular la ruta."

    map_path = "Route_Generator/static/mapas/mapa_espana.html"
    mapa.save(map_path)

    return render(request, 'Route_Generator/index.html', {'map_path': map_path, 'mensaje': mensaje})
