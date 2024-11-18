from django.contrib import admin
from django.urls import include, path
from Route_Generator import views


urlpatterns = [
    path('index/', views.main_view, name='ejemplo'),
    #
]