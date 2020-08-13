import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
TEMPLATE = "plotly_white"

def graficamos_barras_dobles_regional(region, barras, circulos):
    st.subheader('Podemos observar la información sin el componente geográfico. ')
    st.write('Notar que cada variable tiene un eje propio')
    base_path = '/Users/pipe/Documents/Spike/CR2/calidad_aire_2050_cr2'
    df_consolidado = pd.read_csv(f'{base_path}/datos_streamlit/emisiones_socioec_comunales.csv')
    diccionario_regiones = load_diccionario_regiones()
    df_consolidado['nom_region'] = df_consolidado['región'].replace(diccionario_regiones)
    if region != 'Todas las comunas':
        df_consolidado = df_consolidado.query('nom_region==@region')
    
    df_tobarplot = df_consolidado[['comuna', barras, circulos]].sort_values(by=barras, ascending=False)


    trace0 = go.Bar(x = df_tobarplot['comuna'], y=df_tobarplot[circulos], name=circulos)
    trace1 = go.Bar(x = df_tobarplot['comuna'], y=[0],showlegend=False,hoverinfo='none')
    trace2 = go.Bar(x = df_tobarplot['comuna'], y=[0], yaxis='y2',showlegend=False,hoverinfo='none') 
    trace3 = go.Bar(x = df_tobarplot['comuna'], y=df_tobarplot[barras], yaxis='y2', name=barras) 
    data = [trace0,trace1,trace2,trace3]
    
    layout = go.Layout(barmode='group',
                       legend=dict(x=0, y=1.1,orientation="h"),
                       yaxis=dict(title=circulos),
                       yaxis2=dict(title = barras,
                                   overlaying = 'y',
                                   side='right'),  template=TEMPLATE)
    fig = go.Figure(data=data, layout=layout, )
    st.write(fig)    
    
    

    
def graficamos_barras_dobles(barras, circulos):
    st.subheader('Podemos observar la información sin el componente geográfico. ')
    st.write('Notar que cada variable tiene un eje propio')
    base_path = '/Users/pipe/Documents/Spike/CR2/calidad_aire_2050_cr2'
    df_consolidado = pd.read_csv(f'{base_path}/datos_streamlit/emisiones_socioec_regionales.csv')
    
    df_tobarplot = df_consolidado[['región', barras, circulos]].sort_values(by=barras, ascending=False)
    diccionario_regiones = load_diccionario_regiones()
    df_tobarplot['region'] = df_tobarplot['región'].replace(diccionario_regiones)
    df_tobarplot = df_tobarplot.query('region in @diccionario_regiones.values()')

    trace0 = go.Bar(x = df_tobarplot['region'], y=df_tobarplot[circulos], name=circulos)
    trace1 = go.Bar(x = df_tobarplot['region'], y=[0],showlegend=False,hoverinfo='none')
    trace2 = go.Bar(x = df_tobarplot['region'], y=[0], yaxis='y2',showlegend=False,hoverinfo='none') 
    trace3 = go.Bar(x = df_tobarplot['region'], y=df_tobarplot[barras], yaxis='y2', name=barras) 
    data = [trace0,trace1,trace2,trace3]
    
    layout = go.Layout(barmode='group',
                       legend=dict(x=0, y=1.1,orientation="h"),
                       yaxis=dict(title=circulos),
                       yaxis2=dict(title = barras,
                                   overlaying = 'y',
                                   side='right'),  template=TEMPLATE)
    fig = go.Figure(data=data, layout=layout, )
    st.write(fig)
    
    
def plot_barras_circulos_regional(region : 'str' = 'Los Ríos', 
                                  barras : 'str' = 'CO', 
                                  circulos : 'str' = 'personas',
                                  altura_barras = 5, radio_circulos = 10):
                         

    st.markdown(f'''A continuación se muestra en barras verticales el valor de **{barras}** y en círculos se presenta **{circulos}**''')
    
    base_path = '/Users/pipe/Documents/Spike/CR2/calidad_aire_2050_cr2'
    df_consolidado = pd.read_csv(f'{base_path}/datos_streamlit/emisiones_socioec_comunales.csv')
    centroide_regiones = pd.read_csv(f'{base_path}/datos_streamlit/centroide_regiones.csv')

    diccionario_regiones = load_diccionario_regiones()    
    centroide_regiones['nom_region'] = centroide_regiones['región'].replace(diccionario_regiones)
    df_consolidado['nom_region'] = df_consolidado['región'].replace(diccionario_regiones) 
    
    if region!='Todas las comunas':
        df_consolidado = df_consolidado.query('nom_region==@region')
        centroide_regiones = centroide_regiones.query('nom_region==@region')
    df_consolidado.rename(columns={'centroide_y':'lat', 'centroide_x':'lon'}, inplace=True)
    
    # Generamos los radios y las alturas de las columnas
    df_consolidado['radio_'+circulos] = radio_circulos*pd.cut(df_consolidado[circulos], bins=5, labels=False) + 1
    
    # QUEDA PENDIENTE MEJORAR UNA FORMA DE SAMPLEAR PUNTOS PROPORCIONAL AL VALOR.
    cols = ['lat','lon',barras]
    maximo = df_consolidado[cols][barras].mean()
    df_alturas = df_consolidado[cols].reindex(df_consolidado[cols].index.repeat(10*altura_barras*df_consolidado[cols][barras]/maximo))

    
    st.deck_gl_chart(
     viewport={
         'latitude': centroide_regiones.centroide_y.values[-1],
         'longitude': centroide_regiones.centroide_x.values[-1],
         'zoom': 6,
         'pitch': 50,
     },
     layers=[
         {
         'type': 'HexagonLayer',
         'data': df_alturas,
         'radius': 5000,
         'elevationScale': 300,
         'elevationRange': [0, altura_barras*200],
         'pickable': True,
         'extruded': True,
     }, {
         'type': 'ScatterplotLayer',
         'data': df_consolidado,
         'radiusScale':1000,
         'getRadius': 'radio_'+circulos,
     }])

def plot_barras_circulos(barras : 'str' = 'CO', 
                         circulos : 'str' = 'personas',
                         altura_barras = 5, radio_circulos = 10):
                         

        
    st.markdown(f'''A continuación se muestra en barras verticales el valor de **{barras}** y en círculos se presenta **{circulos}**''')
    
    base_path = '/Users/pipe/Documents/Spike/CR2'
    df_consolidado = pd.read_csv(f'{base_path}/calidad_aire_2050_cr2/datos_git/emisiones_socioec_consolidado_regional.csv')
    df_consolidado.rename(columns={'centroide_y':'lat', 'centroide_x':'lon'}, inplace=True)
    # Generamos los radios y las alturas de las columnas
    df_consolidado['radio_'+circulos] = radio_circulos*pd.cut(df_consolidado[circulos], bins=5, labels=False) + 1
    
    # QUEDA PENDIENTE MEJORAR UNA FORMA DE SAMPLEAR PUNTOS PROPORCIONAL AL VALOR.
    cols = ['lat','lon',barras]
    maximo = df_consolidado[cols][barras].mean()
    df_alturas = df_consolidado[cols].reindex(df_consolidado[cols].index.repeat(10*altura_barras*df_consolidado[cols][barras]/maximo))

       
    st.deck_gl_chart(
     viewport={
         'latitude': -38,
         'longitude': -72,
         'zoom': 5,
         'pitch': 50,
     },
     layers=[
         {
         'type': 'HexagonLayer',
         'data': df_alturas,
         'radius': 10000,
         'elevationScale': 300,
         'elevationRange': [0, altura_barras*200],
         'pickable': True,
         'extruded': True,
     }, {
         'type': 'ScatterplotLayer',
         'data': df_consolidado,
         'radiusScale':1000,
         'getRadius': 'radio_'+circulos,
     }])

    



def graficar_mapa_region(region, emision):
    base_path_github = 'https://raw.githubusercontent.com/SpikeLab-CL/calidad_aire_2050_cr2/master/figuras_streamlit'
    #Graficamos el mapa de chile
    diccionario_regiones = load_diccionario_regiones()
    diccionario_inverso = {k[1]:k[0] for k in diccionario_regiones.items()}
    region_number = diccionario_inverso[region]
    st.markdown(
        "<br>"
        '<div style="text-align: center;">'
        f'<img src="{base_path_github}/mapa_regional/gifs/gif_reg_{region_number}_{emision}.gif" width=400>'
        " </img>"
        "</a> </div>",
        unsafe_allow_html=True,
    )

def graficar_mapa_chile(emision):
    base_path_github = 'https://raw.githubusercontent.com/SpikeLab-CL/calidad_aire_2050_cr2/master/figuras_streamlit'
    #Graficamos el mapa de chile
    st.markdown(
        "<br>"
        '<div style="text-align: center;">'
        f'<img src="{base_path_github}/mapa_chile/gifs/gif_chile_{emision}.gif" width=400>'
        " </img>"
        "</a> </div>",
        unsafe_allow_html=True,
    )


@st.cache
def load_contaminantes_agrupados_region():
    return pd.read_csv('/Users/pipe/Documents/Spike/CR2/calidad_aire_2050_cr2/datos_serie_tiempos/series_tiempo_por_region.csv')
@st.cache
def load_contaminantes_agrupados_comuna():
    return pd.read_csv('/Users/pipe/Documents/Spike/CR2/calidad_aire_2050_cr2/datos_serie_tiempos/series_tiempo_por_comuna.csv')

def plotear_series_tiempo_comuna(df : pd.DataFrame, emision : str, region : str):
    df_emision = df.copy()
    diccionario_regiones = load_diccionario_regiones()
    diccionario_inverso = {k[1]:k[0] for k in diccionario_regiones.items()}
    region_number = diccionario_inverso[region]
    df_emision = df_emision.query('región==@region_number')[[m for m in df_emision.columns if m.startswith(f'{emision}_')] + ['comuna']].copy()
    
    comunas_disponibles = list(df_emision.comuna.unique())
    comunas_to_plot = st.multiselect('Seleccionamos comunas', ['Todas las comunas']+comunas_disponibles,
                                    default='Todas las comunas')
    if comunas_to_plot==[]:
        st.error('Seleccionar al menos una comuna')
    elif 'Todas las comunas' not in comunas_to_plot:
        df_emision = df_emision.query('comuna in @comunas_to_plot')
    if len(comunas_to_plot)>=1:
        df_emision = pd.melt(df_emision, id_vars=['comuna'])
        df_emision['time'] = df_emision.variable.apply(lambda x: x.split('_')[-1])
    
        fig = px.line(df_emision, x="time", y="value",
                      line_group="comuna", color='comuna', hover_name='comuna',
                      width=1000, height=500, template=TEMPLATE)
        fig.update_layout(xaxis_title="",yaxis_title=f"Concentración de {emision}[?] en la región {region}")
        _set_legends(fig)
        st.write(fig)



def plotear_series_tiempo_region(df, emision):
    diccionario_regiones = load_diccionario_regiones()
    df_emision = df[[m for m in df.columns if m.startswith(f'{emision}_')] + ['región']].copy()
    regiones_disponibles = list(diccionario_regiones.values())
    df_emision['región'].replace(diccionario_regiones, inplace=True)
    regiones_to_plot = st.multiselect('Seleccionamos regiones', ['Todas las regiones']+regiones_disponibles,
                                    default='Todas las regiones')
    if regiones_to_plot==[]:
        st.error('Seleccionar al menos una región')
    elif 'Todas las regiones' not in regiones_to_plot:
        df_emision = df_emision.query('región in @regiones_to_plot')
    if len(regiones_to_plot)>=1:
    
        df_emision = pd.melt(df_emision, id_vars=['región'])
        df_emision['time'] = df_emision.variable.apply(lambda x: x.split('_')[-1])

        
        fig = px.line(df_emision, x="time", y="value", 
                      line_group="región", color='región', hover_name='región',
                       width=1000, height=500, template=TEMPLATE)
        fig.update_layout(xaxis_title="",yaxis_title=f"Concentración de {emision} [?]")
        _set_legends(fig)
        st.write(fig)

    
def _set_legends(fig):
    fig.layout.update(legend=dict(x=-0.1, y=1.2))
    fig.layout.update(legend_orientation="h")
    
    
def load_diccionario_regiones():
    diccionario_regiones = {10:'Los Lagos',
    11:'Aysen',
    13:'Metropolitana',
    14:'Los Ríos',
    16:'Ñuble',
    4:'Coquimbo',
    5:'Valparaíso',
    6:'Libertador BOhiggins',
    7:'Maule',
    8:'Biobío',
    9:'Araucanía'}
    return diccionario_regiones

def plot_logo_cr2():
    st.sidebar.markdown(
        "<br>"
        '<div style="text-align: center;">'
        '<a href="http://www.cr2.cl/"> '
        '<img src="https://raw.githubusercontent.com/SpikeLab-CL/calidad_aire_2050_cr2/master/logo/logo_CR2_negro.png" width=200>'
        " </img>"
        "</a> </div>",
        unsafe_allow_html=True,
    )
    
def plot_logo_spike():
     st.sidebar.markdown(
        "<br>"
        '<div style="text-align: center;">'
        '<a href="http://spikelab.xyz"> '
        '<img src="https://raw.githubusercontent.com/SpikeLab-CL/calidad_aire_2050_cr2/master/logo/logo-grey-transparent.png" width=128>'
        " </img>"
        "</a> </div>",
        unsafe_allow_html=True,
    )

_SUSCEPTIBLE_COLOR = "rgba(230,230,230,.4)"
_RECOVERED_COLOR = "rgba(180,200,180,.4)"

COLOR_MAP = {
    "default": "#262730",
    "pink": "#E22A5B",
    "purple": "#985FFF",
}
    

def generate_html(
    text,
    color=COLOR_MAP["default"],
    bold=False,
    font_family=None,
    font_size=None,
    line_height=None,
    tag="div",
):
    if bold:
        text = f"<strong>{text}</strong>"
    css_style = f"color:{color};"
    if font_family:
        css_style += f"font-family:{font_family};"
    if font_size:
        css_style += f"font-size:{font_size};"
    if line_height:
        css_style += f"line-height:{line_height};"

    return f"<{tag} style={css_style}>{text}</{tag}>"

def _max_width_():
    max_width_str = f"max-width: 2000px;"
    st.markdown(
        f"""
    <style>
    .reportview-container .main .block-container{{
        {max_width_str}
    }}
    </style>    
    """,
        unsafe_allow_html=True,
    )
    

def get_lista_contaminantes():

    lista_contaminantes = ['CO', 'NH3', 'NO', 'NO2', 'NOX',
     'O3','PM10', 'PM25',  'SO2',]    
    return lista_contaminantes



#EJEMPLO DE BUEN MARKDOWN
# days_since_text = """
#     [The New York Times] (https://www.nytimes.com/interactive/2020/03/21/upshot/coronavirus-deaths-by-country.html):
#     >The accompanying chart... allows you to follow the disease’s 
#     >progression by country. **It uses what’s called a logarithmic scale — exponential growth at 
#     >different rates will appear as straight lines of different steepness.** The steeper the line, 
#     >the higher the growth rate and the faster the total number of coronavirus deaths is doubling.
# """
