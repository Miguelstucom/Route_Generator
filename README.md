# Route Generator

## Descripción del Proyecto
Route Generator es una herramienta desarrollada en Django que permite optimizar la logística de reparto de productos. Utiliza técnicas avanzadas como teoría de grafos y algoritmos genéticos para minimizar el número de camiones necesarios y optimizar las rutas, considerando factores como costos y tiempos de entrega. Este proyecto gestiona datos de productos, pedidos y distancias entre capitales de España.

## Características Principales
- Optimización de rutas de entrega.
- Cálculo de la cantidad óptima de camiones necesarios.
- Minimización de costos de transporte (0.5€ euros por kilómetro).
- Gestión de productos, tiempos de fabricación y fechas de caducidad.

## Requisitos del Sistema
- Python 3.10 o superior.
- Django.
- Tailwind CSS para el diseño de la interfaz.

## Instalación de paquetes
- py -m pip install django
- py -m pip install django-tailwind
- py -m pip install django_browser_reload
- py -m pip install pandas
- py -m pip install folium
- py -m pip install networkx
- py -m pip install reportlab
- py -m pip install tqdm

## Comandos para Iniciar el Proyecto
1. Importar los datos desde los archivos CSV a los modelos:
   ```bash
   python manage.py import_csv
   ```
2. Iniciar el servidor de Tailwind CSS para la gestión de estilos:
   ```bash
   python manage.py tailwind start
   ```
3. Ejecutar el servidor de desarrollo:
   ```bash
   python manage.py runserver
   ```
4. Visualizar la herramienta:
   ```bash
   #Entrar a tu navegador preferido
   http://127.0.0.1:8000/Route_Generator/optimizar-reparto/
   ```
5. (OPCIONAL) Visualizar mapa de conexiones:
   ```bash
   #Entrar a un mapa de conexiones para ver que provincias tienen conexión
   http://127.0.0.1:8000/Route_Generator/map/
   ```

## Estructura de Archivos
- `app/` - Contiene la lógica principal del proyecto.
- `static/` - Archivos estáticos como imágenes, CSS, CSV.
- `templates/` - Plantillas HTML del proyecto.

