
from django.urls import path

from Route_Generator import views
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('Route_Generator/', include('Route_Generator.urls')),
    path("__reload__/", include("django_browser_reload.urls")),
]
