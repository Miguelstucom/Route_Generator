import heapq
from grafo import obtener_grafo
from pedido import pedidos

# Obtener el grafo de las ciudades y distancias
grafo = obtener_grafo()

# Definir la capacidad de los vehículos (por ejemplo, la capacidad máxima de carga que puede llevar un vehículo)
CAPACIDAD_VEHICULO = 3000  # Ejemplo de capacidad, ajusta según tus necesidades


# Cálculo de los ahorros (savings) entre todas las combinaciones de pedidos
def calcular_ahorros():
    ahorros = []
    for i, pedido1 in enumerate(pedidos):
        for j, pedido2 in enumerate(pedidos):
            if i >= j:
                continue  # No consideramos los pedidos combinados consigo mismos
            origen1, destino1 = pedido1["origen"], pedido1["destino"]
            origen2, destino2 = pedido2["origen"], pedido2["destino"]

            # Verificar si los nodos están en el grafo antes de acceder a ellos
            if (
                origen1 not in grafo
                or destino1 not in grafo
                or origen2 not in grafo
                or destino2 not in grafo
            ):
                print(
                    f"Advertencia: Algunas ciudades no están en el grafo. Origen1: {origen1}, Destino1: {destino1}, Origen2: {origen2}, Destino2: {destino2}"
                )
                continue  # Saltar este par de pedidos si alguna ciudad no está en el grafo

            # Verificar si las conexiones necesarias existen
            if (
                destino1 not in grafo[origen1]
                or destino2 not in grafo[origen2]
                or origen2 not in grafo[origen1]
                or destino2 not in grafo[destino1]
            ):
                print(
                    f"No se encontró conexión válida entre las rutas {origen1}-{destino1} y {origen2}-{destino2}."
                )
                continue  # Saltar este par de pedidos si no hay conexiones válidas

            # Calcular el ahorro de juntar las rutas (utilizando la distancia en el grafo)
            ahorro = (
                grafo[origen1][destino1].get("weight", float("inf"))
                + grafo[origen2][destino2].get("weight", float("inf"))
                - grafo[origen1][origen2].get("weight", float("inf"))
                - grafo[destino1][destino2].get("weight", float("inf"))
            )
            if ahorro > 0:  # Solo consideramos los ahorros positivos
                ahorros.append((ahorro, i, j))

    # Ordenar los ahorros de mayor a menor
    ahorros.sort(reverse=True, key=lambda x: x[0])
    return ahorros


# Asignar pedidos a rutas iniciales (un vehículo por cada pedido)
def inicializar_rutas():
    rutas = []
    for pedido in pedidos:
        ruta = [pedido["origen"], pedido["destino"]]
        rutas.append(ruta)
    return rutas


# Implementación del algoritmo de Clarke-Wright
def clarke_wright():
    ahorros = calcular_ahorros()  # Calcular los ahorros entre los pedidos
    rutas = inicializar_rutas()  # Inicializar una ruta por pedido
    capacidades = [
        pedido["cantidad"] for pedido in pedidos
    ]  # Capacidades de los pedidos

    for ahorro, i, j in ahorros:
        ruta1 = rutas[i]
        ruta2 = rutas[j]

        # Verificar si podemos unir las rutas sin superar la capacidad del vehículo
        cantidad_total = capacidades[i] + capacidades[j]

        if cantidad_total <= CAPACIDAD_VEHICULO:
            # Si se puede combinar, unimos las rutas
            # Añadimos la segunda ruta al final de la primera
            rutas[i] = (
                ruta1 + ruta2[1:]
            )  # Unir las rutas, excluyendo el destino de la ruta1
            rutas[j] = []  # Marcamos la ruta j como vacía, ya que está fusionada

            # Actualizamos las capacidades
            capacidades[i] = cantidad_total
            capacidades[j] = 0  # La capacidad de la ruta j ya no existe

    # Filtrar rutas vacías y devolver las rutas finales
    rutas = [ruta for ruta in rutas if ruta]
    return rutas


# Función para imprimir las rutas finales
def mostrar_rutas_finales(rutas):
    for idx, ruta in enumerate(rutas):
        print(f"Ruta {idx + 1}: {' -> '.join(ruta)}")


# Función principal para procesar los pedidos con el algoritmo de Clarke-Wright
def procesar_pedidos():
    rutas_finales = clarke_wright()
    mostrar_rutas_finales(rutas_finales)


if __name__ == "__main__":
    procesar_pedidos()
