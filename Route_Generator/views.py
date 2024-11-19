import pandas as pd
import folium
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

    conexiones_file = "Route_Generator/static/csv/conexion.csv"
    conexiones_data = pd.read_csv(conexiones_file)

    for i, row in conexiones_data.iterrows():
        capital1 = row["Capital_1"]
        capital2 = row["Capital_2"]

        if capital1 in coordinates and capital2 in coordinates:
            coord1 = coordinates[capital1]
            coord2 = coordinates[capital2]

            folium.PolyLine(
                locations=[coord1, coord2],
                color="blue",
                weight=2.5,
                opacity=1
            ).add_to(mapa)

    map_path = "Route_Generator/static/mapas/mapa_espana.html"
    mapa.save(map_path)

    return render(request, 'Route_Generator/index.html', {'map_path': map_path})
