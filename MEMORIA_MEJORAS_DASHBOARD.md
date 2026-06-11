# Memoria de Optimizaciones y Mejoras del Dashboard

Este documento registra las mejoras de diseño, usabilidad y correcciones en la lógica de datos implementadas el **10 de junio de 2026** en el Dashboard del Comité de Villas de Pachuquilla 5.

---

## 🛠️ Resumen de Mejoras Implementadas

### 1. Inmovilización y Estabilidad de la "Vista Tabla"
* **Solución de Transparencias:** Se detectó que la variable CSS `--surface` (utilizada como fondo de columnas y cabeceras fijas) no estaba definida para el modo oscuro en el archivo de estilos. Esto causaba un fondo transparente que hacía que las celdas móviles se traslaparan de manera ilegible por debajo de las celdas fijas al hacer scroll. Se definió `--surface: #151d30;` en `:root`.
* **Corrección del Scroll Vertical en Cabeceras:** Quitamos la propiedad pegajosa del elemento contenedor `thead` (que causaba un comportamiento errático entre navegadores) y la aplicamos directamente en las celdas `th`. Para evitar que el renglón de los meses se empalmara sobre el renglón de los años, fijamos una altura estricta de `28px` y definimos offsets individuales: la fila de Años se ancla en `top: 0` y la de Meses en `top: 28px`.
* **Prevención de Colapso de Columnas:** Se modificó la tabla para usar `width: max-content;` y `min-width: 100%;` en lugar de `width: 100%;`, asegurando que las columnas no se compriman. Se fijaron anchos estrictos para las columnas fijas (Villas en `70px` y Nombres en `180px`) y se elevó el `z-index: 30` en las esquinas de intersección.

### 2. Simplificación de la Navegación (Remoción de "Tabla Resumen")
* Eliminamos por completo la pestaña **"Tabla Resumen"** del HTML, CSS y JavaScript. 
* Esta pestaña resultaba redundante, ya que toda su información (Estatus de la villa, nombre de residente, controles del portón y conteo de meses pagados) y funciones (ver historial detallado de aportaciones) ya están incorporadas de forma visual en la **Vista Casas** (al hacer clic en cualquier tarjeta) y en la **Vista Tabla**.

### 3. Rediseño Completo de "Egresos" en Formato de Tarjetas
* **Cuadrícula de Tarjetas:** Reemplazamos la lista vertical simple de egresos por una cuadrícula moderna de tarjetas (`.expense-card`) responsiva con efecto hover e indicador visual superior.
* **Clasificación con Iconos Dinámicos:** Implementamos lógica en JavaScript para clasificar el egreso según su concepto y asignarle un icono representativo (ej. Foco para luz, Llave inglesa para mantenimiento/pintura, Llave/Candado para portón/controles, Escoba para limpieza, etc.).
* **Buscador en Tiempo Real:** Añadimos una barra de filtrado específica para egresos que permite buscar al instante gastos por concepto, fecha o monto.

### 4. Corrección de Datos e Históricos en `update_data.py`
* **Corrección de Filas Intercambiadas:** En la hoja de cálculo de Google Sheets, el orden de las filas varía a través del tiempo. En los meses recientes la descripción estaba en la Fila 38 y el monto en la Fila 39, mientras que en los meses de 2023 y 2024 el monto estaba en la Fila 39 y el concepto numérico en la Fila 40. Esto provocaba que los montos y descripciones se mostraran al revés.
* **Algoritmo Heurístico:** Se implementó una lógica de detección en [update_data.py](file:///Users/felipelopezsalazar/Library/Mobile%20Documents/com~apple~CloudDocs/Personal/Casa/Pachuquilla/comite_villas_dashboard/update_data.py) que lee las dos celdas y determina dinámicamente cuál es el monto (basado en la presencia de `$` o formato de número) y cuál la descripción.
* **Recuperación de Históricos de 2023 y 2024:** Gracias a la alineación correcta de celdas, el actualizador ahora recupera y muestra **10 egresos históricos** correspondientes al periodo 2023-2024 que antes eran completamente ignorados por el sistema al encontrarse la celda de montos vacía en la fila equivocada.

---

## 📂 Archivos Involucrados en el Proyecto

* 🌐 **[index.html](file:///Users/felipelopezsalazar/Library/Mobile%20Documents/com~apple~CloudDocs/Personal/Casa/Pachuquilla/comite_villas_dashboard/index.html)**: Estructura del panel, rediseño de estilos CSS pegajosos y de tarjetas de egresos, lógica de filtrado y visualización de datos.
* 🐍 **[update_data.py](file:///Users/felipelopezsalazar/Library/Mobile%20Documents/com~apple~CloudDocs/Personal/Casa/Pachuquilla/comite_villas_dashboard/update_data.py)**: Script actualizador que descarga los datos de Google Sheets, realiza la clasificación heurística de egresos y compila el fallback estático en el archivo HTML.
* 📦 **[comite_data.json](file:///Users/felipelopezsalazar/Library/Mobile%20Documents/com~apple~CloudDocs/Personal/Casa/Pachuquilla/comite_villas_dashboard/comite_data.json)**: Archivo JSON local que almacena la base de datos de respaldo en texto plano para el modo offline.
* ⚡ **[Sincronizar_y_Subir.command](file:///Users/felipelopezsalazar/Library/Mobile%20Documents/com~apple~CloudDocs/Personal/Casa/Pachuquilla/comite_villas_dashboard/Sincronizar_y_Subir.command)**: Ejecutable para macOS que realiza todo el proceso de descarga, actualización de fallbacks y despliegue a producción de forma automática en un solo clic.

---

*Documento archivado localmente para futuras consultas sobre la arquitectura del Dashboard.*
