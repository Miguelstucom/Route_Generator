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
    #Validamos los nodos
    if not isinstance(origen, str):
        raise TypeError(f"El nodo origen debe ser una cadena, pero es {type(origen)}.")
    if not isinstance(destino, str):
        raise TypeError(
            f"El nodo destino debe ser una cadena, pero es {type(destino)}."
        )
    # Lectura de datos de conexiones desde un archivo CSV
    velocidad_media = velocidad
    conexiones_data = pd.read_csv(conexiones_file)

    # Creación de un grafo con NetworkX
    G = nx.Graph()
    for _, row in conexiones_data.iterrows():
        capital1 = str(row["Capital_1"]).strip()
        capital2 = str(row["Capital_2"]).strip()
        peso = float(row["Peso"])
        G.add_edge(capital1, capital2, weight=peso)

    # Verificación de la existencia de los nodos en el grafo
    if origen not in G.nodes:
        raise ValueError(f"El nodo origen '{origen}' no existe en el grafo.")
    if destino not in G.nodes:
        raise ValueError(f"El nodo destino '{destino}' no existe en el grafo.")

    # Verificación de la existencia de un camino entre origen y destino
    if not nx.has_path(G, origen, destino):
        raise ValueError(f"No hay conexión entre '{origen}' y '{destino}'.")

    # Cálculo de la ruta más corta usando Dijkstra
    try:
        ruta = nx.shortest_path(G, source=origen, target=destino, weight="weight")
    except nx.NetworkXNoPath:
        raise ValueError(
            f"No se pudo calcular una ruta entre '{origen}' y '{destino}'."
        )

    # Cálculo del peso total de la ruta
    peso_total = 0.0
    for i in range(len(ruta) - 1):
        nodo_actual = ruta[i]
        nodo_siguiente = ruta[i + 1]
        peso_total += G[nodo_actual][nodo_siguiente]["weight"]

    # Cálculo del tiempo estimado de entrega
    tiempo_en_horas = peso_total / velocidad_media
    tiempo_total_estimado = fecha_envio + timedelta(hours=tiempo_en_horas)

    # Verificación contra la fecha límite de entrega
    if tiempo_total_estimado > fecha_limite:
        raise ValueError(
            f"La ruta más corta excede el tiempo de caducidad. "
            f"Tiempo estimado: {tiempo_en_horas} horas, fecha límite: {fecha_limite}."
        )

    return ruta


def agrupar_pedidos(pedidos, capacidad_camion, distancias, punto_inicial="Mataró", randomize=True):
    if randomize:
        # Si randomize es True, introducimos el factor aleatorio
        pedidos = sorted(
            pedidos,
            key=lambda p: distancias[punto_inicial][p.ciudad_destino.nombre] * (1 + random.random() * 0.1)
        )
    else:
        # Si no queremos aleatoriedad (primer intento), ordenamos sin factor aleatorio
        pedidos = sorted(
            pedidos,
            key=lambda p: distancias[punto_inicial][p.ciudad_destino.nombre]
        )

    print("Pedidos ordenados inicialmente:", [(p.id, p.ciudad_destino.nombre) for p in pedidos])

    camiones = []

    while pedidos:
        camion_actual = []
        peso_actual = 0

        pedido_base = pedidos.pop(0)
        camion_actual.append(pedido_base)
        peso_actual += pedido_base.cantidad

        print(f"\n[Inicio Camión] Pedido base ID:{pedido_base.id}, destino: {pedido_base.ciudad_destino.nombre}")

        while pedidos:
            if randomize:
                proximos = sorted(
                    pedidos,
                    key=lambda p: distancias[camion_actual[-1].ciudad_destino.nombre][p.ciudad_destino.nombre] * (1 + random.random() * 0.1)
                )
            else:
                proximos = sorted(
                    pedidos,
                    key=lambda p: distancias[camion_actual[-1].ciudad_destino.nombre][p.ciudad_destino.nombre]
                )

            print("Próximos candidatos:", [(p.id, p.ciudad_destino.nombre) for p in proximos])

            agregado = False
            for pedido in proximos:
                if peso_actual + pedido.cantidad <= capacidad_camion:
                    camion_actual.append(pedido)
                    peso_actual += pedido.cantidad
                    pedidos.remove(pedido)
                    print(f"Añadido pedido ID:{pedido.id}, destino:{pedido.ciudad_destino.nombre}")
                    agregado = True
                    break

            if not agregado:  # No se encontró ninguno que encaje
                break

        print("[Fin Camión]:", [(p.id, p.ciudad_destino.nombre) for p in camion_actual])
        camiones.append(camion_actual)

    return camiones

def optimizar_camiones(pedidos, capacidad_camion, distancia, intento=1):
    randomize = (intento > 1)
    print("\n" + "="*50)
    print(f"==== Intento número: {intento} ====")
    print("="*50 + "\n")
    return agrupar_pedidos(pedidos, capacidad_camion, distancia, randomize=randomize)
