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

## Cambio de juego de pruebas
- Para poder cambiar el juego de pruebas, solamente tenemos que cambiar el csv de la función "importar_pedidos" en el archivo "Route_Generator/management/commands/import_csv.py" por cualquier otro de los juegos de pruebas en "Route_Generator/static/csv" 

## Archivos necesarios
- conexión.csv -> Todas las conexiones entre ciudades
- csv.csv -> Todas las ciudades y sus coordenadas
- productos_que_se_elaboran_1.csv -> productos y toda su información
- El resto de archivos son juegos de pruebas disponibles para el usuario, siendo test.csv, el ejemplo de clase

## Comandos para Iniciar el Proyecto - Desde la carpeta raíz, es decir, en la carpeta padre de Route_Generator
1. Importar los datos desde los archivos CSV a los modelos:
   ```bash
   python/py manage.py import_csv
   ```
2. Iniciar el servidor de Tailwind CSS para la gestión de estilos:
   ```bash
   python/py manage.py tailwind start
   ```
3. Ejecutar el servidor de desarrollo:
   ```bash
   python/py manage.py runserver --noreload
   ```
4. Visualizar la herramienta:
   ```bash
   #Entrar a tu navegador preferido
   http://127.0.0.1:8000/Route_Generator/optimizar-reparto/
   ```
5. (OPCIONAL) Visualizar mapa de conexiones:
   ```bash
   #Entrar a un mapa de conexiones para ver que provincias tienen conexión
   #Ya que hay ciudades no conectadas al no haber carreteras principales, con esto se puede mirar si una conexión no se ha puesto porque no existe
   http://127.0.0.1:8000/Route_Generator/map/
   ```

## Estructura de Archivos
- `app/` - Contiene la lógica principal del proyecto.
- `static/` - Archivos estáticos como imágenes, CSS, CSV.
- `templates/` - Plantillas HTML del proyecto.

