from utils import *
from descripcion_contaminantes import *
import numpy as np
import pandas as pd
import geopandas as gpd
import streamlit as st
import matplotlib.pyplot as plt
import glob, os
import time
import plotly.express as px
import math
from PIL import Image
import plotly.graph_objects as go


def main():
    #_max_width_() jugamos con el ancho

#     st.empty()
#     '''
#     # Explorador de calidad del aire :earth_africa:
#     Una herramienta para ayudar a visualizar los resultados del estudio de calidad del aire al año 2050 realizado por el CR2.
#     '''
#     st.markdown('---')    
    st.sidebar.markdown('''# Explorador de calidad del aire :earth_africa:''',)
    st.sidebar.markdown('''##### Una herramienta para ayudar a visualizar los resultados del estudio de calidad del aire al año 2050 realizado por el CR2.''')
    
    
    #Menu para seleccionar qué hacemos
    menu_principal()
    # LOGOS 
    plot_logo_cr2()
    plot_logo_spike()


    
def menu_principal(): 
    titulo_opcion = st.empty()
    st.sidebar.markdown('---')
    st.sidebar.markdown('**Seleccionamos un menú**')
    app_mode = st.sidebar.radio("Disponemos de dos visualizaciones",
                                ["Vista general de emisiones","Vista de contaminantes y variables socioeconomicas",], 
                                index=0, key='seleccion_principal')
#     st.sidebar.markdown('---')
    if app_mode == "Vista general de emisiones":
        '''## Vista general de emisiones'''
        vista_general_contaminantes()

    elif app_mode == "Vista de contaminantes y variables socioeconomicas":
        '''## Vista de contaminantes y variables socioeconomicas'''
        vista_contaminantes_socioeconomicas()    
        

    
    
def vista_contaminantes_socioeconomicas():
    
    lista_contaminantes = get_lista_contaminantes()
    lista_variables_socio = ['personas','pueblo_indigena', 'inmigrantes']
    diccionario_regiones = load_diccionario_regiones()
    lista_regiones = list(diccionario_regiones.values())
    st.sidebar.markdown('**Escogemos una región**')
    region = st.sidebar.selectbox('todas las regiones o una en particular',
                                  ['Todas las regiones', 'Todas las comunas'] + lista_regiones,
                                  index=0)
    
    st.sidebar.markdown('**Seleccionamos una variable a analizar**')
    barras = st.sidebar.selectbox('Qué variable describimos en barras?',
                                  lista_variables_socio+lista_contaminantes,
                                  index=3)
    st.sidebar.markdown('**Seleccionamos una segunda variable a analizar**')
    circulos = st.sidebar.selectbox('Qué variable describimos en círculos?',
                                    lista_variables_socio+lista_contaminantes,
                                   index=0)

    st.sidebar.markdown('---')
    cambiamos_params = st.sidebar.checkbox('Cambiar parámetros del mapa')
    if cambiamos_params:
        radio_circulos = st.sidebar.slider('Radio círculos', 
                                           min_value=1, max_value=100, 
                                           value=10, step=10, 
                                           key='radio_circulos')
        altura_barras = st.sidebar.slider('Altura barras',  
                                           min_value=1, max_value=20, 
                                           value=5, step=1,
                                           key='altura_barras')
    else:
        radio_circulos = 10
        altura_barras = 5
    
    if region == 'Todas las regiones':
        plot_barras_circulos(barras, circulos,
                             altura_barras=altura_barras, 
                             radio_circulos=radio_circulos)
        graficamos_barras_dobles(barras, circulos,)
    
    else:
        plot_barras_circulos_regional(region, barras, circulos, 
                                      altura_barras=altura_barras, 
                                      radio_circulos=radio_circulos)
        graficamos_barras_dobles_regional(region, barras, circulos, )
        
    
def vista_general_contaminantes():
    
    lista_contaminantes = get_lista_contaminantes()
    diccionario_regiones = load_diccionario_regiones()
    lista_regiones = list(diccionario_regiones.values())
    st.sidebar.markdown('**Escogemos una región**')
    region = st.sidebar.selectbox('Todas las regiones o una en particular', ['Todas las regiones'] + lista_regiones, index=0)
    
    st.sidebar.markdown('**Escogemos un contaminante a explorar**')
    emision = st.sidebar.selectbox('', lista_contaminantes,)

    # Añadimos la descripción del contaminante
    get_descripcion(emision)
    
    st.markdown(body=generate_html(
            tag="hcontaminantes",
            text=f"A continuación se representa una simulación de la evolución de concentración de {emision} a lo largo del día para las regiones ubicadas entre Coquimbo y Aysen <br>",
            font_size="15px"
        ),
        unsafe_allow_html=True,)
    

    if region == 'Todas las regiones':
        #Graficamos mapa de chule
        graficar_mapa_chile(emision)
        # Graficos de series de tiempo 
        '''## Series de tiempo'''
        st.markdown(body=generate_html(
                tag="hseries",
                text=f"Para cada comuna se muestra la evolución a lo largo del día de de la concentración atmosférica <br>",
                font_size="20px"
                ), unsafe_allow_html=True)
        contaminantes_agrupados_region = load_contaminantes_agrupados_region()
        plotear_series_tiempo_region(contaminantes_agrupados_region, emision)

        
    else:
        #Graficamos mapa de chule
        graficar_mapa_region(region, emision)
        # Graficos de series de tiempo
        '''## Series de tiempo'''
        st.markdown(body=generate_html(
                tag="hseries",
                text=f"Para cada región se muestra la evolución a lo largo del día de de la concentración atmosférica <br>",
                font_size="20px"
            ), unsafe_allow_html=True)
        contaminantes_agrupados_comuna = load_contaminantes_agrupados_comuna()
        plotear_series_tiempo_comuna(contaminantes_agrupados_comuna, region=region,  emision=emision)
    
  
    

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

main()













## SANDBOX



#==========================================================    
## USANDO ARCHIVOS LOCALES PARA PODER HACER QUERYS
#==========================================================    
#df_emisiones = gpd.read_file("/Users/pipe/Documents/Spike/CR2/calidad_aire_2050_cr2/datos_git/json_consolidado.geojson")

# if region_option == 'todo chile':
#     df_to_plot = df_emisiones.copy()
# else:
#     df_to_plot = df_emisiones.query('codregion==@region_option').copy()

# df_to_plot = json.loads(df_to_plot.to_json())



