import networkx as nx
import matplotlib.pyplot as plt

# Lista de ciudades de Cataluña
ciudades = [
    "Barcelona",
    "Tarragona",
    "Lleida",
    "Girona",
    "Manresa",
    "Terrassa",
    "Sabadell",
    "Mataró",
    "Reus",
    "L'Hospitalet de Llobregat",
    "Badalona",
    "Granollers",
    "Vic",
    "Igualada",
    "Vilanova i la Geltrú",
    "Vilafranca del Penedès",
    "Blanes",
    "Figueres",
    "La Seu d'Urgell",
]

# Crear el grafo
G = nx.Graph()

# Añadir nodos al grafo
for ciudad in ciudades:
    G.add_node(ciudad)

# Conexiones entre ciudades con tiempos de viaje (en minutos)
conexiones = [
    ("Barcelona", "Tarragona", 60),
    ("Barcelona", "Lleida", 90),
    ("Barcelona", "Girona", 75),
    ("Barcelona", "Manresa", 60),
    ("Barcelona", "Terrassa", 30),
    ("Barcelona", "Sabadell", 25),
    ("Barcelona", "Mataró", 30),
    ("Barcelona", "L'Hospitalet de Llobregat", 15),
    ("Barcelona", "Badalona", 20),
    ("Tarragona", "Reus", 15),
    ("Tarragona", "Vilanova i la Geltrú", 45),
    ("Tarragona", "Vilafranca del Penedès", 30),
    ("Girona", "Blanes", 40),
    ("Girona", "Figueres", 35),
    ("Girona", "La Seu d'Urgell", 120),
    ("Lleida", "La Seu d'Urgell", 90),
    ("Manresa", "Igualada", 40),
    ("Terrassa", "Sabadell", 15),
    ("Granollers", "Vic", 45),
    ("Granollers", "Mataró", 35),
]

# Añadir las conexiones al grafo
for ciudad1, ciudad2, tiempo in conexiones:
    G.add_edge(ciudad1, ciudad2, weight=tiempo)


# Función para mostrar el grafo
def mostrar_grafo():
    plt.figure(figsize=(14, 14))
    pos = nx.spring_layout(G, seed=42)
    nx.draw(
        G,
        pos,
        with_labels=True,
        node_size=500,
        font_size=8,
        node_color="lightblue",
        edge_color="gray",
    )
    labels = nx.get_edge_attributes(G, "weight")
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels, font_size=7)

    plt.title("Grafo de Ciudades de Cataluña con Tiempos de Viaje")
    plt.show()


# Función para obtener el grafo (para importarlo desde otros archivos)
def obtener_grafo():
    return G
