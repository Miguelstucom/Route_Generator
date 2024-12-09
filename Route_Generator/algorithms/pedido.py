# pedido.py

# Definición de pedidos con orígenes y destinos
pedidos = [
    {
        "id": 1,
        "origen": "Mataró",
        "destino": "Barcelona",  # Cambiado a una ciudad del grafo
        "producto": "Producto A",
        "cantidad": 1000,
        "fecha_entrega": "2024-11-25",
    },
    {
        "id": 2,
        "origen": "Mataró",
        "destino": "Tarragona",  # Cambiado a una ciudad del grafo
        "producto": "Producto B",
        "cantidad": 1500,
        "fecha_entrega": "2024-11-26",
    },
    {
        "id": 3,
        "origen": "Mataró",
        "destino": "Girona",  # Cambiado a una ciudad del grafo
        "producto": "Producto C",
        "cantidad": 1200,
        "fecha_entrega": "2024-11-27",
    },
    {
        "id": 4,
        "origen": "Mataró",
        "destino": "Lleida",  # Cambiado a una ciudad del grafo
        "producto": "Producto D",
        "cantidad": 900,
        "fecha_entrega": "2024-11-28",
    },
    {
        "id": 5,
        "origen": "Mataró",
        "destino": "Reus",  # Cambiado a una ciudad del grafo
        "producto": "Producto E",
        "cantidad": 1100,
        "fecha_entrega": "2024-11-29",
    },
]


# Mostrar los pedidos
def mostrar_pedidos():
    for pedido in pedidos:
        print(f"Pedido ID: {pedido['id']}")
        print(f"Origen: {pedido['origen']}")
        print(f"Destino: {pedido['destino']}")
        print(f"Producto: {pedido['producto']}")
        print(f"Cantidad: {pedido['cantidad']}")
        print(f"Fecha de entrega: {pedido['fecha_entrega']}")
        print("-" * 30)
