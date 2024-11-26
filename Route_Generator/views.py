import pandas as pd
import folium
import networkx as nx
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from xhtml2pdf import pisa
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

    if request.method == 'POST':
        ciudad_origen = 'Mataró'
        ciudad_destino = request.POST.get('ciudad_destino', None)

        if ciudad_origen and ciudad_destino:
            ruta, distancia = obtener_ruta_mas_corta(ciudad_origen, ciudad_destino)
            if ruta:
                html_content = render_to_string('Route_Generator/pdf.html', {
                    'ciudad_origen': ciudad_origen,
                    'ciudad_destino': ciudad_destino,
                    'ruta': ruta,
                    'distancia': distancia
                })

                response = HttpResponse(content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="ruta_{ciudad_origen}_{ciudad_destino}.pdf"'

                pisa_status = pisa.CreatePDF(html_content, dest=response)

                if pisa_status.err:
                    return HttpResponse(f"Error al generar el PDF: {pisa_status.err}")

                return response
            else:
                mensaje = f"No hay ruta disponible entre {ciudad_origen} y {ciudad_destino}."
                return render(request, 'Route_Generator/index.html', {'mensaje': mensaje})
        else:
            mensaje = "Por favor, ingrese dos ciudades para calcular la ruta."
            return render(request, 'Route_Generator/index.html', {'mensaje': mensaje})

    map_path = "Route_Generator/static/mapas/mapa_espana.html"
    mapa.save(map_path)

    return render(request, 'Route_Generator/index.html', {'map_path': map_path})
