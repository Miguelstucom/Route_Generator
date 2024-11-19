import heapq
from grafo import obtener_grafo
from pedido import pedidos  # Importar los pedidos


def dijkstra(origen, destino):
    grafo = obtener_grafo()  # Obtener el grafo

    # Verificar si el destino está en el grafo
    if destino not in grafo:
        print(f"El destino {destino} no está en el grafo.")
        return [], float("inf")

    distancias = {nodo: float("inf") for nodo in grafo}  # Inicializar distancias
    distancias[origen] = 0  # La distancia al origen es 0
    ruta_previa = {nodo: None for nodo in grafo}  # Inicializar rutas previas

    cola_prioridad = [(0, origen)]  # Cola de prioridad para el algoritmo

    while cola_prioridad:
        # Obtener el nodo con la distancia más pequeña
        (distancia_actual, nodo_actual) = heapq.heappop(cola_prioridad)

        # Si llegamos al destino, terminamos
        if nodo_actual == destino:
            break

        # Recorremos los vecinos del nodo actual
        for vecino, datos_conexion in grafo[nodo_actual].items():
            peso = datos_conexion.get(
                "weight", float("inf")
            )  # Obtener el peso de la conexión
            nueva_distancia = distancia_actual + peso  # Calcular nueva distancia

            # Si la nueva distancia es mejor, actualizamos la distancia y la ruta
            if nueva_distancia < distancias[vecino]:
                distancias[vecino] = nueva_distancia
                ruta_previa[vecino] = nodo_actual
                heapq.heappush(cola_prioridad, (nueva_distancia, vecino))

    # Verificar si el destino es alcanzable
    if distancias[destino] == float("inf"):
        print(
            f"No se puede entregar el pedido. No hay ruta disponible de {origen} a {destino}."
        )
        return [], float("inf")

    # Reconstruir la ruta desde el destino hasta el origen
    ruta = []
    nodo = destino
    while nodo is not None:
        ruta.append(nodo)
        nodo = ruta_previa[nodo]

    return (
        ruta[::-1],  # Retornar la ruta invertida
        distancias[destino],  # El costo total
    )


# Ejemplo de uso con los pedidos
def procesar_pedidos():
    for pedido in pedidos:
        origen = pedido["origen"]
        destino = pedido["destino"]
        ruta, costo = dijkstra(origen, destino)
        print(f"Pedido ID: {pedido['id']}")
        if ruta:
            print(f"Ruta más corta de {origen} a {destino}: {ruta} con costo {costo}")
        else:
            print(
                f"No se puede entregar el pedido. No hay ruta disponible de {origen} a {destino}."
            )
        print("-" * 30)


if __name__ == "__main__":
    procesar_pedidos()
