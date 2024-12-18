
from django.urls import path

from Route_Generator import views
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    #Path de las rutas del proyecto
    path('Route_Generator/', include('Route_Generator.urls')),

    path("__reload__/", include("django_browser_reload.urls")),

    path('map/', include('Route_Generator.urls')),

]
