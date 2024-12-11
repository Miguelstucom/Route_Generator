import networkx as nx
from datetime import datetime, timedelta
import pandas as pd
from tqdm import tqdm
from datetime import timedelta
from datetime import date
import random

def calcular_ruta_mas_corta(
    origen, destino, conexiones_file, fecha_envio, fecha_limite,velocidad
):

    if not isinstance(origen, str):
        raise TypeError(f"El nodo origen debe ser una cadena, pero es {type(origen)}.")
    if not isinstance(destino, str):
        raise TypeError(
            f"El nodo destino debe ser una cadena, pero es {type(destino)}."
        )

    velocidad_media = velocidad
    conexiones_data = pd.read_csv(conexiones_file)

    G = nx.Graph()
    for _, row in conexiones_data.iterrows():
        capital1 = str(row["Capital_1"]).strip()
        capital2 = str(row["Capital_2"]).strip()
        peso = float(row["Peso"])
        G.add_edge(capital1, capital2, weight=peso)

    if origen not in G.nodes:
        raise ValueError(f"El nodo origen '{origen}' no existe en el grafo.")
    if destino not in G.nodes:
        raise ValueError(f"El nodo destino '{destino}' no existe en el grafo.")

    if not nx.has_path(G, origen, destino):
        raise ValueError(f"No hay conexión entre '{origen}' y '{destino}'.")

    try:
        ruta = nx.shortest_path(G, source=origen, target=destino, weight="weight")
    except nx.NetworkXNoPath:
        raise ValueError(
            f"No se pudo calcular una ruta entre '{origen}' y '{destino}'."
        )

    peso_total = 0.0
    for i in range(len(ruta) - 1):
        nodo_actual = ruta[i]
        nodo_siguiente = ruta[i + 1]
        peso_total += G[nodo_actual][nodo_siguiente]["weight"]

    tiempo_en_horas = peso_total / velocidad_media
    tiempo_total_estimado = fecha_envio + timedelta(hours=tiempo_en_horas)

    if tiempo_total_estimado > fecha_limite:
        raise ValueError(
            f"La ruta más corta excede el tiempo de caducidad. "
            f"Tiempo estimado: {tiempo_en_horas} horas, fecha límite: {fecha_limite}."
        )

    return ruta


def agrupar_pedidos(pedidos, capacidad_camion, distancias, punto_inicial="Mataró"):
    pedidos = sorted(
        pedidos,
        key=lambda p: distancias[punto_inicial][p.ciudad_destino.nombre]
    )
    camiones = []

    while pedidos:
        camion_actual = []
        peso_actual = 0

        pedido_base = pedidos.pop(0)
        camion_actual.append(pedido_base)
        peso_actual += pedido_base.cantidad

        while pedidos:
            proximos = sorted(
                pedidos,
                key=lambda p: distancias[camion_actual[-1].ciudad_destino.nombre][p.ciudad_destino.nombre]
            )

            for pedido in proximos:
                if peso_actual + pedido.cantidad <= capacidad_camion:
                    camion_actual.append(pedido)
                    peso_actual += pedido.cantidad
                    pedidos.remove(pedido)
                    break
            else:
                break

        camiones.append(camion_actual)

    return camiones





def verificar_restricciones_tiempo(pedidos, productos):
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
    return agrupar_pedidos(pedidos, capacidad_camion,distancia)
