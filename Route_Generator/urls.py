from django.contrib import admin
from django.urls import include, path
from Route_Generator import views


urlpatterns = [
    path('index/', views.mostrar_mapa, name='ejemplo'),

    path('map/', views.mostrar_mapa, name='mostrar_mapa'),

]