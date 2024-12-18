from django.contrib import admin
from django.urls import include, path
from Route_Generator import views


urlpatterns = [
    #Ruta exacta del proyecto desde Route_Generator
    path('optimizar-reparto/', views.optimizar_reparto, name='optimizar_reparto'),

    #Ruta para un mapa que muestra todas las conexiones, para poder ver si alguna ciudad no está conectada directamente
    path('map/', views.mostrar_mapa, name='mostrar_mapa'),

]