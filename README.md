# 📊 NainoMillones Analyzer

NainoMillones es un pequeño proyecto en Python que permite obtener, procesar, analizar y visualizar los resultados históricos del sorteo del **Euromillones** desde la página oficial [euromillones.com.es](https://www.euromillones.com.es/resultados-anteriores.html).

> **Nota:** Este pequeño programa no garantiza que te toque el Euromillones. Es simplemente un ejercicio básico de Python para scrapear una web.

## 🚀 ¿Qué hace este programa?

1. **Web Scraping**  
   Extrae automáticamente los resultados anteriores del Euromillones, incluyendo:
   - Fecha del sorteo
   - Números ganadores
   - Estrellas ganadoras
   - Código del Millón

2. **Análisis Estadístico**  
   - Calcula los **top 3 números y estrellas más frecuentes** por posición en los sorteos analizados
   - Genera un **gráfico interactivo** con la frecuencia acumulada por fecha.

3. **Visualización HTML**  
   Genera un archivo `HTML` completo con:
   - El último resultado del sorteo
   - Un histórico de resultados
   - Tablas con estadísticas de frecuencia
   - Un gráfico interactivo con [Plotly](https://plotly.com)

---

## 🧰 Tecnologías utilizadas

- `Python 3.x`
- `requests` (scraping)
- `BeautifulSoup` (parsing HTML)
- `re`, `collections.Counter`, `datetime`
- `plotly` (visualización interactiva)
- `webbrowser`, `os`

---

## 🧠 Estructura del código

### `obtener_resultados_euromillones(url)`
Realiza scraping a la URL proporcionada y devuelve una lista de sorteos con sus datos.

### `parsear_fecha(fecha_str)`
Convierte la fecha en texto a objeto `datetime` para facilitar el ordenamiento y análisis.

### `calcular_top3_por_posicion(resultados)`
Devuelve los 3 números/estrellas más frecuentes en cada posición.

### `generar_grafico_interactivo(resultados)`
Genera una gráfica de líneas acumulativas con la frecuencia de aparición por fecha.

### `guardar_todo_en_html(...)`
Construye y guarda un archivo `.html` con todos los resultados y visualizaciones.

---

## Ejecutar el programa

Basta con clonar el repositorio y una vez dentro del repositorio ejecutar:

```bash
python3 run_app.py
```
...si utilizas Windows y tienes Python añadido a tu PATH el comando a ejecutar será:
```bash
python run_app.py
```

## 📄 Resultado generado

El programa crea un archivo llamado:

```bash
euromillones_completo.html
```