import csv
import pandas as pd
from django.core.management.base import BaseCommand
from Route_Generator.models import Ciudad, Conexion, Producto, Pedido
from datetime import datetime

class Command(BaseCommand):
    help = 'Importa datos desde CSV a los modelos, borrando datos previos'

    def handle(self, *args, **kwargs):
        self.borrar_datos_antiguos()
        self.importar_ciudades()
        self.importar_conexiones()
        self.importar_productos()
        self.importar_pedidos()

    def borrar_datos_antiguos(self):
        Pedido.objects.all().delete()
        self.stdout.write(self.style.WARNING('Pedidos eliminados.'))

        Conexion.objects.all().delete()
        self.stdout.write(self.style.WARNING('Conexiones eliminadas.'))

        Producto.objects.all().delete()
        self.stdout.write(self.style.WARNING('Productos eliminados.'))

        Ciudad.objects.all().delete()
        self.stdout.write(self.style.WARNING('Ciudades eliminadas.'))

    def importar_ciudades(self):
        with open('Route_Generator/static/csv/csv.csv', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                Ciudad.objects.get_or_create(
                    id=int(row["id"]),
                    nombre=row["Capital"],
                    provincia=row["Provincia"],
                    latitud=float(row["Latitud"].replace(",", ".")),
                    longitud=float(row["Longitud"].replace(",", "."))
                )
        self.stdout.write(self.style.SUCCESS('Ciudades importadas con éxito.'))

    def importar_conexiones(self):
        with open('Route_Generator/static/csv/conexion.csv', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            faltantes = set()
            for row in reader:
                try:
                    origen = Ciudad.objects.get(nombre=row["Capital_1"].strip())
                    destino = Ciudad.objects.get(nombre=row["Capital_2"].strip())
                    Conexion.objects.get_or_create(
                        ciudad_origen=origen,
                        ciudad_destino=destino,
                        peso=float(row["Peso"])
                    )
                except Ciudad.DoesNotExist as e:
                    faltantes.add(row["Capital_1"].strip())
                    faltantes.add(row["Capital_2"].strip())

            if faltantes:
                self.stdout.write(self.style.ERROR("Ciudades faltantes:"))
                for ciudad in faltantes:
                    self.stdout.write(f"- {ciudad}")
            else:
                self.stdout.write(self.style.SUCCESS("No hay ciudades faltantes."))

        self.stdout.write(self.style.SUCCESS('Conexiones importadas con éxito.'))

    def importar_productos(self):
        with open('Route_Generator/static/csv/productos_que_se_elaboran_1.csv', newline='',
                  encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                Producto.objects.update_or_create(
                    id=int(row["Identificador del producto"]),
                    defaults={
                        "nombre": row["Nombre"],
                        "precio_venta": float(row["Precio Venta"].replace(",", ".")),
                        "tiempo_fabricacion": int(row["Tiempo de fabricación (días)"]),
                        "caducidad": int(row["Caducidad desde su fabricación (días)"]),
                    }
                )
        self.stdout.write(self.style.SUCCESS('Productos importados con éxito.'))

    def importar_pedidos(self):
        with open('Route_Generator/static/csv/pedidos_actualizados.csv', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    producto = Producto.objects.get(id=int(row["id producto"]))
                except Producto.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(f"Producto con ID {row['id producto']} no encontrado. Pedido omitido."))
                    continue

                ciudad_id = int(row["Identificador cliente"])
                try:
                    ciudad_destino = Ciudad.objects.get(id=ciudad_id)
                except Ciudad.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f"Ciudad con ID {ciudad_id} no encontrada en la base de datos."))
                    continue

                Pedido.objects.get_or_create(
                    fecha_pedido=datetime.strptime(row["Fecha del pedido"], "%Y-%m-%d").date(),
                    cliente_id=int(row["Identificador cliente"]),
                    cantidad=int(row["Cantidad"]),
                    producto=producto,
                    ciudad_destino=ciudad_destino
                )
        self.stdout.write(self.style.SUCCESS('Pedidos importados con éxito.'))

