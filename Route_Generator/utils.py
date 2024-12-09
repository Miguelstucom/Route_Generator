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
            destinos = (
                [origen]
                + [pedido.ciudad_destino.nombre for pedido in camion]
                + [origen]
            )
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
    aptitudes = [(individuo, calcular_aptitud(individuo, distancias)) for individuo in poblacion]
    aptitudes.sort(key=lambda x: x[1])
    return [individuo for individuo, _ in aptitudes[: len(aptitudes) // 2]]


def cruzamiento(padre1, padre2):
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
        return padre1


def mutacion(individuo, probabilidad_mutacion):
    """Realiza mutaciones en un individuo."""
    if random.random() < probabilidad_mutacion:
        i, j = random.sample(range(len(individuo)), 2)
        individuo[i], individuo[j] = individuo[j], individuo[i]
    return individuo


def algoritmo_genetico(
    pedidos, capacidad_camion, distancias, num_generaciones=100, num_individuos=50
):
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

    mejor_individuo = min(poblacion, key=lambda ind: calcular_aptitud(ind, distancias))
    mejor_costo = calcular_aptitud(mejor_individuo, distancias)
    return mejor_individuo, mejor_costo


def filtrar_pedidos_validos(pedidos, fecha_actual):
    pedidos_validos = []
    for pedido in pedidos:
        if pedido.fecha_disponible() <= fecha_actual <= pedido.fecha_limite_entrega():
            pedidos_validos.append(pedido)
    return pedidos_validos


def calcular_ruta_optima(camion, conexiones_file, origen="Mataró"):
    conexiones_data = pd.read_csv(conexiones_file)

    G = nx.Graph()
    for _, row in conexiones_data.iterrows():
        G.add_edge(
            row["Capital_1"].strip(),
            row["Capital_2"].strip(),
            weight=float(row["Peso"]),
        )

    destinos = [origen] + [pedido.ciudad_destino.nombre for pedido in camion]

    rutas_posibles = permutations(destinos)

    mejor_ruta = None
    menor_distancia = float("inf")

    for ruta in rutas_posibles:
        distancia = sum(
            nx.shortest_path_length(
                G, source=ruta[i], target=ruta[i + 1], weight="weight"
            )
            for i in range(len(ruta) - 1)
        )
        if distancia < menor_distancia:
            mejor_ruta = ruta
            menor_distancia = distancia

    return mejor_ruta, menor_distancia



def calcular_ruta_mas_corta(
    origen, destino, conexiones_file, fecha_envio, fecha_limite
):
    """
    Calcula la ruta más corta usando NetworkX y verifica si cumple con el tiempo de caducidad.
    """
    import pandas as pd
    import networkx as nx
    from datetime import timedelta

    if not isinstance(origen, str):
        raise TypeError(f"El nodo origen debe ser una cadena, pero es {type(origen)}.")
    if not isinstance(destino, str):
        raise TypeError(
            f"El nodo destino debe ser una cadena, pero es {type(destino)}."
        )

    velocidad_media = 60.0
    conexiones_data = pd.read_csv(conexiones_file)

    # Construir el grafo
    G = nx.Graph()
    for _, row in conexiones_data.iterrows():
        capital1 = str(row["Capital_1"]).strip()
        capital2 = str(row["Capital_2"]).strip()
        peso = float(row["Peso"])
        G.add_edge(capital1, capital2, weight=peso)

    # Validar nodos en el grafo
    if origen not in G.nodes:
        raise ValueError(f"El nodo origen '{origen}' no existe en el grafo.")
    if destino not in G.nodes:
        raise ValueError(f"El nodo destino '{destino}' no existe en el grafo.")

    # Verificar si hay un camino entre los nodos
    if not nx.has_path(G, origen, destino):
        raise ValueError(f"No hay conexión entre '{origen}' y '{destino}'.")

    # Calcular la ruta más corta
    try:
        ruta = nx.shortest_path(G, source=origen, target=destino, weight="weight")
    except nx.NetworkXNoPath:
        raise ValueError(
            f"No se pudo calcular una ruta entre '{origen}' y '{destino}'."
        )

    # Calcular el peso total (distancia)
    peso_total = 0.0
    for i in range(len(ruta) - 1):
        nodo_actual = ruta[i]
        nodo_siguiente = ruta[i + 1]
        peso_total += G[nodo_actual][nodo_siguiente]["weight"]

    # Convertir distancia total a horas
    tiempo_en_horas = peso_total / velocidad_media
    tiempo_total_estimado = fecha_envio + timedelta(hours=tiempo_en_horas)

    # Verificar tiempo de caducidad
    if tiempo_total_estimado > fecha_limite:
        raise ValueError(
            f"La ruta más corta excede el tiempo de caducidad. "
            f"Tiempo estimado: {tiempo_en_horas} horas, fecha límite: {fecha_limite}."
        )

    # Si todo va bien, retornar la ruta
    return ruta



def agrupar_pedidos(pedidos, capacidad_camion, distancias):
    pedidos = sorted(pedidos, key=lambda p: p.ciudad_destino.nombre)
    camiones = []

    while pedidos:
        camion_actual = []
        peso_actual = 0
        pedido_base = pedidos.pop(0)
        camion_actual.append(pedido_base)
        peso_actual += pedido_base.cantidad

        proximos = sorted(
            pedidos,
            key=lambda p: distancias[pedido_base.ciudad_destino.nombre][p.ciudad_destino.nombre]
        )

        for pedido in proximos[:]:
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
        tiempo_restante = (
            producto.caducidad - (datetime.now().date() - pedido.fecha_pedido).days
        )
        if tiempo_restante > 0:
            pedidos_validos.append(pedido)
    return pedidos_validos


def optimizar_camiones(pedidos, capacidad_camion,distancia):
    """Usa un algoritmo genético para minimizar el número de camiones."""
    return agrupar_pedidos(pedidos, capacidad_camion,distancia)
