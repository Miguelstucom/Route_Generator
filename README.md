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

## Estructura de Archivos
- `app/` - Contiene la lógica principal del proyecto.
- `static/` - Archivos estáticos como imágenes, CSS, CSV.
- `templates/` - Plantillas HTML del proyecto.

