import requests
from bs4 import BeautifulSoup
import re
from collections import Counter
from datetime import datetime
import webbrowser
import os
import plotly.graph_objs as go
from plotly.offline import plot


def obtener_resultados_euromillones(url):
    try:
        headers = {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            )
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        seccion_sorteos = soup.find('article', {'id': 'sorteosant'})

        if not seccion_sorteos:
            print("No se encontró la sección de sorteos")
            return []

        sorteos = seccion_sorteos.find_all('li', class_='blq')

        resultados = []

        for sorteo in sorteos:
            if 'numestre' in sorteo.get('class', []):
                continue

            try:
                fecha_tag = sorteo.find('h4')
                if fecha_tag:
                    fecha_texto = fecha_tag.get_text(strip=True)
                    fecha = re.search(r'- (.*)', fecha_texto)
                    fecha = fecha.group(1) if fecha else fecha_texto
                else:
                    fecha = "Desconocida"

                numeros_tags = sorteo.find_all('li', class_='numeros')
                numeros = [num.get_text(strip=True) for num in numeros_tags[:5]]

                estrellas_tags = sorteo.find_all('li', class_='estrellas')
                estrellas = [estrella.get_text(strip=True) for estrella in estrellas_tags[:2]]

                millon_tag = sorteo.find('li', class_='millon')
                codigo_millon = millon_tag.get_text(strip=True) if millon_tag else ''
                # Eliminar el texto "El Millón" del código
                codigo_millon = codigo_millon.replace('El Millón', '').strip()

                resultados.append({
                    'fecha': fecha,
                    'numeros': numeros,
                    'estrellas': estrellas,
                    'millon': codigo_millon
                })

            except Exception as e:
                print(f"Error procesando un sorteo: {str(e)}")
                continue

        return resultados

    except requests.exceptions.RequestException as e:
        print(f"Error al conectar con la URL: {str(e)}")
        return []
    except Exception as e:
        print(f"Error inesperado: {str(e)}")
        return []


def parsear_fecha(fecha_str):
    meses = {
        'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4, 'mayo': 5, 'junio': 6,
        'julio': 7, 'agosto': 8, 'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
    }
    try:
        partes = fecha_str.split()
        dia = int(partes[1])
        mes = meses[partes[3].lower()]
        año = int(partes[5])
        return datetime(año, mes, dia)
    except Exception:
        return None


def calcular_top3_por_posicion(resultados):
    # Para números y estrellas, por posición, contar apariciones
    pos_nums = [Counter() for _ in range(5)]
    pos_ests = [Counter() for _ in range(2)]

    for r in resultados:
        for i, num in enumerate(r['numeros']):
            pos_nums[i][num] += 1
        for i, est in enumerate(r['estrellas']):
            pos_ests[i][est] += 1

    top3_nums = [pos.most_common(3) for pos in pos_nums]
    top3_ests = [pos.most_common(3) for pos in pos_ests]

    return top3_nums, top3_ests


def generar_grafico_interactivo(resultados):
    freq_num_por_fecha = {}
    freq_est_por_fecha = {}
    fechas = []

    for res in resultados:
        fecha_dt = parsear_fecha(res['fecha'])
        if fecha_dt is None:
            continue
        fechas.append(fecha_dt)
        freq_num_por_fecha.setdefault(fecha_dt, Counter()).update(res['numeros'])
        freq_est_por_fecha.setdefault(fecha_dt, Counter()).update(res['estrellas'])

    fechas = sorted(set(fechas))

    numeros_posibles = [str(i) for i in range(1, 51)]
    estrellas_posibles = [str(i) for i in range(1, 13)]

    acumulado_num = {num: [] for num in numeros_posibles}
    acumulado_est = {est: [] for est in estrellas_posibles}

    cont_num = Counter()
    cont_est = Counter()

    for fecha in fechas:
        cont_num += freq_num_por_fecha.get(fecha, Counter())
        cont_est += freq_est_por_fecha.get(fecha, Counter())

        for num in numeros_posibles:
            acumulado_num[num].append(cont_num[num])
        for est in estrellas_posibles:
            acumulado_est[est].append(cont_est[est])

    trazas = []

    for num in numeros_posibles:
        trazas.append(go.Scatter(
            x=fechas,
            y=acumulado_num[num],
            mode='lines',
            name=f'Número {num}',
            visible='legendonly',
            line=dict(color='blue')
        ))

    for est in estrellas_posibles:
        trazas.append(go.Scatter(
            x=fechas,
            y=acumulado_est[est],
            mode='lines',
            name=f'Estrella {est}',
            visible='legendonly',
            line=dict(color='red', dash='dot')
        ))

    layout = go.Layout(
        title='Frecuencia acumulada de números y estrellas por fecha (Euromillones)',
        xaxis=dict(title='Fecha'),
        yaxis=dict(title='Frecuencia acumulada'),
        hovermode='x unified',
        legend=dict(title='Haz clic para mostrar/ocultar líneas')
    )

    fig = go.Figure(data=trazas, layout=layout)

    return fig.to_html(full_html=False, include_plotlyjs='cdn')


def guardar_todo_en_html(resultados, top3_nums, top3_ests, grafico_html, archivo_html):
    html = f"""
    <html>
    <head>
        <meta charset="utf-8" />
        <title>NainoMillones</title>
        <style>
            body {{ font-family: Arial, sans-serif; background: #f4f4f9; padding: 20px; }}
            h1, h2 {{ color: #333; }}
            table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
            th, td {{ border: 1px solid #ccc; padding: 8px; text-align: center; }}
            th {{ background: #007bff; color: white; }}
            tr:nth-child(even) {{ background: #e9ecef; }}
            .numero {{ color: blue; font-weight: bold; }}
            .estrella {{ color: red; font-weight: bold; }}
            .millon {{ color: green; font-weight: bold; }}
            .top-table {{ width: 50%; margin-bottom: 40px; }}
        </style>
    </head>
    <body>
        <h1>Resultados Euromillones</h1>
        

        <h2>Combinación ganadora en el último sorteo</h2>
        <p><strong>Fecha:</strong> {resultados[0]['fecha']}</p>
        <p><strong>Números:</strong> {" ".join(f'<span class="numero">{n}</span>' for n in resultados[0]["numeros"])}</p>
        <p><strong>Estrellas:</strong> {" ".join(f'<span class="estrella">{e}</span>' for e in resultados[0]["estrellas"])}</p>
        <p><strong>Código Millón:</strong> <span class="millon">{resultados[0]['millon']}</span></p>

        <h2>Resultados anteriores</h2>
        <table>
            <thead>
                <tr>
                    <th>Fecha</th>
                    <th>Números</th>
                    <th>Estrellas</th>
                    <th>Código Millón</th>
                </tr>
            </thead>
            <tbody>
    """
    for r in resultados[1:]:
        numeros_html = ' '.join(f'<span class="numero">{n}</span>' for n in r['numeros'])
        estrellas_html = ' '.join(f'<span class="estrella">{e}</span>' for e in r['estrellas'])
        millon_html = f'<span class="millon">{r["millon"]}</span>' if r["millon"] else ''
        html += f"<tr><td>{r['fecha']}</td><td>{numeros_html}</td><td>{estrellas_html}</td><td>{millon_html}</td></tr>"


    html += """
            </tbody>
        </table>

        <h2>Top 3 números por posición</h2>
        <table class="top-table">
            <thead>
                <tr><th>Posición</th><th>1º</th><th>2º</th><th>3º</th></tr>
            </thead>
            <tbody>
    """

    posiciones = ['1ª', '2ª', '3ª', '4ª', '5ª']
    for i, top_pos in enumerate(top3_nums):
        html += f"<tr><td>{posiciones[i]} posición</td>"
        for num, cnt in top_pos:
            html += f"<td><span class='numero'>{num}</span> ({cnt} veces)</td>"
        html += "</tr>"

    html += """
            </tbody>
        </table>

        <h2>Top 3 estrellas por posición</h2>
        <table class="top-table">
            <thead>
                <tr><th>Posición</th><th>1º</th><th>2º</th><th>3º</th></tr>
            </thead>
            <tbody>
    """

    posiciones_ests = ['1ª', '2ª']
    for i, top_pos in enumerate(top3_ests):
        html += f"<tr><td>{posiciones_ests[i]} posición</td>"
        for est, cnt in top_pos:
            html += f"<td><span class='estrella'>{est}</span> ({cnt} veces)</td>"
        html += "</tr>"

    html += """
            </tbody>
        </table>

        <h2>Gráfico interactivo de frecuencia acumulada</h2>
        {grafico_html}

    <h3>Datos obtenidos de <a href="https://www.euromillones.com.es/resultados-anteriores.html">Euromillones</a></h3>
    </body>
    </html>
    """.format(grafico_html=grafico_html)

    with open(archivo_html, 'w', encoding='utf-8') as f:
        f.write(html)


if __name__ == "__main__":
    url = "https://www.euromillones.com.es/resultados-anteriores.html"
    resultados = obtener_resultados_euromillones(url)

    if not resultados:
        print("No se encontraron resultados.")
        exit()

    top3_nums, top3_ests = calcular_top3_por_posicion(resultados)

    grafico_html = generar_grafico_interactivo(resultados)

    archivo_html = "euromillones_completo.html"
    guardar_todo_en_html(resultados, top3_nums, top3_ests, grafico_html, archivo_html)

    print(f"Archivo HTML generado: {archivo_html}")
    webbrowser.open('file://' + os.path.realpath(archivo_html))
