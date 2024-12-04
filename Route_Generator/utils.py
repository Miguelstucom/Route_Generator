import networkx as nx
from datetime import datetime, timedelta
import pandas as pd
from tqdm import tqdm
import networkx as nx
import pandas as pd
from itertools import permutations

from datetime import date

import random

def inicializar_poblacion(pedidos, capacidad_camion, num_individuos):
    """Crea una población inicial aleatoria."""
    poblacion = []
    for _ in range(num_individuos):
        individuo = []
        pedidos_aleatorios = random.sample(list(pedidos), len(pedidos))
        camion_actual = []
        peso_actual = 0

        for pedido in pedidos_aleatorios:
            if peso_actual + pedido.cantidad <= capacidad_camion:
                camion_actual.append(pedido)
                peso_actual += pedido.cantidad
            else:
                individuo.append(camion_actual)
                camion_actual = [pedido]
                peso_actual = pedido.cantidad

        if camion_actual:
            individuo.append(camion_actual)

        poblacion.append(individuo)

    return poblacion


def calcular_aptitud(individuo, distancias, origen="Mataró"):
    """Calcula la aptitud de un individuo basado en el costo total."""
    costo_total = 0

    for camion in individuo:
        if not camion:
            continue

        if isinstance(camion, list):
            destinos = [origen] + [pedido.ciudad_destino.nombre for pedido in camion] + [origen]
        elif hasattr(camion, "ciudad_destino"):
            destinos = [origen, camion.ciudad_destino.nombre, origen]
        else:
            raise TypeError(f"El objeto {camion} no es válido para calcular distancias")

        distancia_total = sum(
            distancias[destinos[i]][destinos[i + 1]] for i in range(len(destinos) - 1)
        )
        costo_total += distancia_total * 0.5

    return costo_total


def seleccion(poblacion, distancias):
    """Selecciona los mejores individuos basados en la aptitud."""
    aptitudes = [(individuo, calcular_aptitud(individuo, distancias)) for individuo in poblacion]
    aptitudes.sort(key=lambda x: x[1])
    return [individuo for individuo, _ in aptitudes[:len(aptitudes) // 2]]


def cruzamiento(padre1, padre2):
    """Realiza cruzamiento entre dos individuos."""
    # Desanidar si están envueltos en una lista adicional
    if isinstance(padre1[0], list):
        padre1 = padre1[0]
    if isinstance(padre2[0], list):
        padre2 = padre2[0]

    if len(padre1) > 1 and len(padre2) > 1:
        punto_cruce = random.randint(1, len(padre1) - 1)
        hijo = padre1[:punto_cruce] + padre2[punto_cruce:]
        return hijo
    else:
        print("Error: los individuos no tienen longitud suficiente para el cruce.")
        return padre1  # O manejarlo de otra forma.


def mutacion(individuo, probabilidad_mutacion):
    """Realiza mutaciones en un individuo."""
    if random.random() < probabilidad_mutacion:
        i, j = random.sample(range(len(individuo)), 2)
        individuo[i], individuo[j] = individuo[j], individuo[i]
    return individuo

def algoritmo_genetico(pedidos, capacidad_camion, distancias, num_generaciones=100, num_individuos=50):
    """Implementa el algoritmo genético."""
    poblacion = inicializar_poblacion(pedidos, capacidad_camion, num_individuos)

    for _ in range(num_generaciones):
        poblacion = seleccion(poblacion, distancias)
        print("genetico")
        nueva_poblacion = []

        while len(nueva_poblacion) < num_individuos:
            padre1, padre2 = random.sample(poblacion, 2)
            hijo = cruzamiento(padre1, padre2)
            hijo = mutacion(hijo, 0.1)
            nueva_poblacion.append(hijo)

        poblacion = nueva_poblacion

    # Retorna el mejor individuo de la última generación
    mejor_individuo = min(poblacion, key=lambda ind: calcular_aptitud(ind, distancias))
    mejor_costo = calcular_aptitud(mejor_individuo, distancias)
    return mejor_individuo, mejor_costo



def filtrar_pedidos_validos(pedidos, fecha_actual):
    """Filtra los pedidos que pueden ser enviados en la fecha actual."""
    pedidos_validos = []
    for pedido in pedidos:
        if pedido.fecha_disponible() <= fecha_actual <= pedido.fecha_limite_entrega():
            pedidos_validos.append(pedido)
    return pedidos_validos

def calcular_ruta_optima(camion, conexiones_file, origen="Mataró"):
    """Encuentra la ruta óptima para el camión utilizando TSP."""
    conexiones_data = pd.read_csv(conexiones_file)

    # Construir el grafo
    G = nx.Graph()
    for _, row in conexiones_data.iterrows():
        G.add_edge(
            row["Capital_1"].strip(),
            row["Capital_2"].strip(),
            weight=float(row["Peso"])
        )

    # Lista de destinos incluyendo el origen
    destinos = [origen] + [pedido.ciudad_destino.nombre for pedido in camion]

    # Calcular todas las permutaciones de rutas posibles
    rutas_posibles = permutations(destinos)

    # Encontrar la ruta con menor distancia
    mejor_ruta = None
    menor_distancia = float('inf')

    for ruta in rutas_posibles:
        # Calcular la distancia de la ruta
        distancia = sum(
            nx.shortest_path_length(G, source=ruta[i], target=ruta[i+1], weight="weight")
            for i in range(len(ruta) - 1)
        )
        if distancia < menor_distancia:
            mejor_ruta = ruta
            menor_distancia = distancia

    return mejor_ruta, menor_distancia



def calcular_ruta_mas_corta(origen, destino, conexiones_file, fecha_envio, fecha_limite):
    """
    Calcula la ruta más corta usando NetworkX.

    :param origen: Nodo de origen (str).
    :param destino: Nodo de destino (str).
    :param conexiones_file: Ruta al archivo CSV con las conexiones.
    :return: Lista de nodos que forman la ruta más corta.
    """
    import pandas as pd
    import networkx as nx

    # Validar que origen y destino sean cadenas
    if not isinstance(origen, str):
        raise TypeError(f"El nodo origen debe ser una cadena, pero es {type(origen)}.")
    if not isinstance(destino, str):
        raise TypeError(f"El nodo destino debe ser una cadena, pero es {type(destino)}.")

    # Cargar las conexiones desde el archivo CSV
    conexiones_data = pd.read_csv("Route_Generator/static/csv/conexion.csv")

    # Construir el grafo
    G = nx.Graph()

    for i, row in conexiones_data.iterrows():
        capital1 = str(row["Capital_1"]).strip()  # Convertir a cadena y quitar espacios
        capital2 = str(row["Capital_2"]).strip()
        peso = float(row["Peso"])  # Asegurar que el peso es un número flotante

        # Añadir la arista al grafo
        G.add_edge(capital1, capital2, weight=peso)

    # Validar nodos en el grafo
    if origen not in G.nodes:
        raise ValueError(f"El nodo origen '{origen}' no existe en el grafo.")
    if destino not in G.nodes:
        raise ValueError(f"El nodo destino '{destino}' no existe en el grafo.")

    # Verificar si hay un camino entre los nodos
    if not nx.has_path(G, origen, destino):
        raise ValueError(f"No hay conexión entre '{origen}' y '{destino}'.")

    # Calcular y devolver la ruta más corta
    try:
        return nx.shortest_path(G, source=origen, target=destino, weight="weight")
    except nx.NetworkXNoPath:
        raise ValueError(f"No se pudo calcular una ruta entre '{origen}' y '{destino}'.")

    peso_total = 0
    for i in range(len(ruta) - 1):  # Recorrer nodos consecutivos en la ruta
        nodo_actual = ruta[i]
        nodo_siguiente = ruta[i + 1]
        peso_total += G[nodo_actual][nodo_siguiente]["weight"]  # Sumar peso de la arista

    # Verificar si la ruta excede el tiempo de caducidad
    tiempo_total_estimado = fecha_envio + timedelta(hours=peso_total)

    if tiempo_total_estimado > fecha_limite:
        raise ValueError(
            f"La ruta más corta excede el tiempo de caducidad. Peso total: {peso_total} horas, tiempo de caducidad: {fecha_limite}."
        )



def agrupar_pedidos(pedidos, capacidad_camion, distancias):
    """
    Agrupa pedidos en camiones considerando la capacidad del camión y la proximidad de los destinos.
    :param pedidos: Lista de pedidos.
    :param capacidad_camion: Capacidad máxima de cada camión.
    :param distancias: Diccionario de distancias entre ciudades {ciudad1: {ciudad2: distancia}}.
    :return: Lista de camiones (cada camión es una lista de pedidos).
    """
    pedidos = sorted(pedidos, key=lambda p: p.ciudad_destino.nombre)  # Ordenar por destino
    camiones = []

    while pedidos:
        camion_actual = []
        peso_actual = 0
        pedido_base = pedidos.pop(0)  # Toma el primer pedido como base
        camion_actual.append(pedido_base)
        peso_actual += pedido_base.cantidad

        proximos = sorted(
            pedidos,
            key=lambda p: distancias[pedido_base.ciudad_destino.nombre][p.ciudad_destino.nombre]
        )

        for pedido in proximos[:]:  # Iterar sobre una copia de la lista
            peso_pedido = pedido.cantidad
            if peso_actual + peso_pedido <= capacidad_camion:
                camion_actual.append(pedido)
                peso_actual += peso_pedido
                pedidos.remove(pedido)

        camiones.append(camion_actual)

    return camiones




def verificar_restricciones_tiempo(pedidos, productos):
    """Verifica que los pedidos cumplan con las restricciones de caducidad."""
    pedidos_validos = []
    for pedido in pedidos:
        producto = pedido.producto
        tiempo_restante = producto.caducidad - (datetime.now().date() - pedido.fecha_pedido).days
        if tiempo_restante > 0:
            pedidos_validos.append(pedido)
    return pedidos_validos


def optimizar_camiones(pedidos, capacidad_camion,distancia):
    """Usa un algoritmo genético para minimizar el número de camiones."""
    # Placeholder para implementar algoritmo genético.
    return agrupar_pedidos(pedidos, capacidad_camion,distancia)
