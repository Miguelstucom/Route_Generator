from django.db import models

class Ciudad(models.Model):
    capital = models.CharField(max_length=100)
    provincia = models.CharField(max_length=100)
    latitud = models.FloatField()
    longitud = models.FloatField()

    def __str__(self):
        return self.capital
from django.db import models

# Create your models here.
