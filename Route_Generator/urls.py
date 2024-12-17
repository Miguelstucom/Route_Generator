from django.contrib import admin
from django.urls import include, path
from Route_Generator import views


urlpatterns = [
    path('optimizar-reparto/', views.optimizar_reparto, name='optimizar_reparto'),
    path('map/', views.mostrar_mapa, name='mostrar_mapa'),

]