from django.db import models
from datetime import timedelta

#Generamos los modelos que usamos durante la ejecucion

class Ciudad(models.Model):
    nombre = models.CharField(max_length=100)
    provincia = models.CharField(max_length=100)
    latitud = models.FloatField()
    longitud = models.FloatField()

    def __str__(self):
        return self.nombre


class Conexion(models.Model):
    ciudad_origen = models.ForeignKey(Ciudad, related_name="conexiones_origen", on_delete=models.CASCADE)
    ciudad_destino = models.ForeignKey(Ciudad, related_name="conexiones_destino", on_delete=models.CASCADE)
    peso = models.FloatField()  # Distancia en km

    def __str__(self):
        return f"{self.ciudad_origen} -> {self.ciudad_destino}"


class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    precio_venta = models.FloatField()
    tiempo_fabricacion = models.PositiveIntegerField()  # Días
    caducidad = models.PositiveIntegerField()  # Días

    def __str__(self):
        return self.nombre


class Pedido(models.Model):
    fecha_pedido = models.DateField()
    cliente_id = models.PositiveIntegerField()
    cantidad = models.PositiveIntegerField()
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    ciudad_destino = models.ForeignKey(Ciudad, on_delete=models.CASCADE)

    def fecha_disponible(self):
        """Fecha en la que el producto estará listo para ser enviado."""
        return self.fecha_pedido + timedelta(days=self.producto.tiempo_fabricacion)

    def fecha_limite_entrega(self):
        """Fecha límite para entregar el pedido antes de la caducidad."""
        return self.fecha_disponible() + timedelta(days=self.producto.caducidad)

    def __str__(self):
        return f"Pedido {self.id} - Cliente {self.cliente_id}"
