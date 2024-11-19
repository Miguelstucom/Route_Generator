import grafo
import pedido
import dijkstra
import clarke_wright


def mostrar_menu():
    print("\n----- Menú -----")
    print("1. Mostrar Pedidos")
    print("2. Ver Grafo")
    print("3. Calcular con Dijkstra")
    print("4. Calcular con Clarke Wright")
    print("5. Cerrar Programa")


def main():
    while True:
        mostrar_menu()
        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            pedido.mostrar_pedidos()  # Llamar a la función de mostrar pedidos de pedido.py
        elif opcion == "2":
            grafo.mostrar_grafo()  # Llamar a la función para mostrar el grafo desde grafo.py
        elif opcion == "3":
            dijkstra.procesar_pedidos()  # Llamar a la función de procesar pedidos en dijkstra.py
        elif opcion == "4":
            clarke_wright.procesar_pedidos()  # Llamar a la función de procesar pedidos en clarke_weight.py
        elif opcion == "5":
            print("Cerrando el programa...")
            break
        else:
            print("Opción no válida. Por favor, intente de nuevo.")


if __name__ == "__main__":
    main()
