from utils import *
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import datetime
    

def main():
    
    st.sidebar.markdown('''# Explorador de calidad del aire :earth_africa:''',)
    st.sidebar.markdown('''##### Una herramienta para visualizar resultados adicionales del informe a la nacion sobre la calidad del aire.''')
    
    #Menu para seleccionar qué hacemos
    titulo_opcion = st.empty()
    st.sidebar.subheader('Seleccionamos un menú')

    menu = ["1. Vista general","2. Series de tiempo", "3. Mapas"]
    app_mode = st.sidebar.radio("", menu, index=0, key='seleccion_principal')
    
    if app_mode==menu[0]:
        texto("Emisiones y Concentraciones de MP<sub>2,5</sub>", nfont=30)
        vista_general()

    elif app_mode==menu[1]:
        texto("Series de tiempo", nfont=30)
        series_de_tiempo()
        
    elif app_mode==menu[2]:
        texto("Mapas de concentración y emisión de MP<sub>2,5</sub>", 30)
        mapas()
        
    width_pagina = st.sidebar.slider('seleccionamos un tamaño', 0, 2000, 1000)
    max_width_(width_pagina)
    

    # LOGOS 
    plot_logo_cr2()
    plot_logo_spike()

    
    
# 1. VISTA GENERAL
def vista_general():
    
    texto('''La información que se presenta en esta plataforma corresponde a salida de un sistema de modelación compuesto por el modelo meteorológico WRF y el modelo químico de transporte CHIMERE. Este sistema ha sido aplicado anteriormente con éxito para caracterizar la dispersión de la contaminación en Santiago y permite conocer la evolución de la calidad del aire en lugares donde no hay estaciones de monitoreo.
Los datos de concentracion de MP<sub>2,5</sub> en los distintos graficos corresponden al promedio del periodo 2015 a 2017 para los meses de mayo a agosto. Los flujos de emisión de MP<sub>2,5</sub> en tanto, corresponden a estimaciones del inventario de emisiones realizado por el CR2 para fines del informe a la nacion y está descrito en mayor detalle en el capítulo 2 del informe.''',
            nfont=15)
    
    st.markdown('---')
    st.sidebar.subheader('Dominio de interés')
    resolucion = get_resolucion(key='vista_general')
    opciones = ("Concentración vs emisión","Concentración vs número de habitantes","Emisión vs número de habitantes")
    vistas = st.sidebar.radio('Seleccionamos una vista',opciones)
    st.sidebar.markdown('---')
    width_figuras = st.sidebar.slider('ancho figuras', 0, 2000, 1000)
    
    
    if vistas==opciones[0]:
        variables = ['Concentración', 'Emisión']
    elif vistas==opciones[1]:
        variables = ['Concentración', 'número de habitantes']
    elif vistas==opciones[2]:
        variables = ['Emisión', 'número de habitantes']

    df = cargamos_datos_resumen(resolucion)
    texto("Concentracion versus emisión de MP<sub>2,5</sub>.", nfont=20,)
    ploteamos_barras(df, resolucion, variables, width_figuras=width_figuras)
    
    ''' '''
    ''' '''
    texto("Dispersión del promedio invernal de MP<sub>2,5</sub>.", nfont=20)
    plot_dispersion(df, resolucion, width_figuras=width_figuras)    
    
    


# 2. SERIES DE TIEMPO
def series_de_tiempo():   
    
    texto('''Los siguientes gráficos presentan series de tiempo de concentración promedio por región/comuna o emisión acumulada por región/comuna para intervalos de tiempo entre el 1º de Mayo  al 31 de Agosto. Cada serie de tiempo corresponde al promedio del período 2015 al 2017. El primer conjunto de gráficos permite examinar la serie de tiempo completa y existe la opcion de ilustrar los datos con datos horarios o diarios. En los ciclos diarios, el segundo conjunto de gráficos, además del valor promedio se puede también ilustrar la desviación estandar de la variable presentada, esto es una medida de dispersión en torno a la media de la variable en cuestión. ''')
    
    
    st.sidebar.subheader('Dominio de interés')
    resolucion = get_resolucion(key='vista_general')
    ''' 
    
    '''
    texto(''' 1. Serie completa''', 25)
    hourly = st.checkbox('Resolución horaria', value=False)

    df_serie_completa = cargamos_series_tiempo_completas(hourly=hourly, resolucion=resolucion)
    _df_serie_completa = filtrar_serie_daily_por_resolucion(df_serie_completa, resolucion)
    options = filtrar_espacial(_df_serie_completa,resolucion)
    if options==[]:
        st.sidebar.error('Lista vacía')
    show_concentraciones = st.sidebar.checkbox('Gráficos de concentraciones', value=True)
    show_emisiones = st.sidebar.checkbox('Gráficos de emisiones', value=False)
    
    st.sidebar.markdown('---')
    leyenda_h = st.sidebar.checkbox('Leyenda horizontal', value=True)
    leyenda_arriba = st.sidebar.checkbox('Leyenda arriba', value=True)
    leyenda_sombreada = st.sidebar.checkbox('Incluimos dispersión sombreada', value=True)
    #st.markdown('---')
    width_figuras = st.sidebar.slider('ancho figuras', 0, 2000, 1000)
    
    
    
   
    
    #_df = filtrar_usuario(_df,resolucion, espacio)
    _df_serie_completa = filtrar_options(_df_serie_completa, options, resolucion)
    if show_concentraciones:
        texto(f"Concentración de MP<sub>2,5</sub>", nfont=20)
        line_plot(_df_serie_completa, y='concentracion_pm25',
                  resolucion=resolucion,
                  leyenda_h=leyenda_h,
                  hourly=hourly,
                  leyenda_arriba=leyenda_arriba,
                  width_figuras=width_figuras)
        ''' 
        
        '''
    if show_emisiones:
        texto("Emisión de MP<sub>2,5</sub>", nfont=20,)
        line_plot(_df_serie_completa, y='emision_pm25',
                  resolucion=resolucion,
                  leyenda_h=leyenda_h,
                  hourly=hourly,
                  leyenda_arriba=leyenda_arriba,
                  width_figuras=width_figuras)

    ''' 
    
    '''    
    texto(''' 2. Ciclo diario''', 25)
    texto("El ciclo diario representa la evolución a lo largo de un dia de un parámetro (concentración o emisión). El valor de la variable en cada hora del ciclo corresponde al promedio de todas esas horas durante el periodo del 1 de Mayo al 31 de Agosto de los años 2015 al 2017. Ademas del ciclo diario promedio se ilustra tambien el área de una desviación estandar en torno al valor promedio (área achurada) y representa una medida de dispersión en torno a la media de la variable en cuestión.",)

    df_diario = cargamos_serie_24hrs(resolucion=resolucion) 
    _df_diario = filtrar_serie_daily_por_resolucion(df_diario, resolucion)
    _df_diario = filtrar_options(_df_diario, options, resolucion)

    if show_concentraciones:
        texto(f"Concentración de MP<sub>2,5</sub>", nfont=20)
        plot_daily_curves(_df_diario, resolucion, tipo='concentracion',
                          show_shade_fill=leyenda_sombreada,
                          leyenda_h=leyenda_h,
                          showlegend=True,
                          width_figuras=width_figuras)
    if show_emisiones:
        texto("Emisión de MP<sub>2,5</sub>", nfont=20,)
        plot_daily_curves(_df_diario, resolucion, tipo='emision',
                          show_shade_fill=leyenda_sombreada,
                          leyenda_h=leyenda_h,
                          showlegend=True,
                          width_figuras=width_figuras)

    ''' 
    
    '''   
    texto(''' 3. Ciclo semanal''', 25)
    texto("El ciclo semanal representa la evolución a lo largo de una semana de un parámetro (concentración o emisión) con datos horarios o promedios diarios. El valor de la variable en cada hora/día del ciclo corresponde al promedio de todas esas horas/días durante el periodo del 1 de Mayo al 31 de Agosto de los años 2015 al 2017. Además del ciclo semanal promedio se ilustra también el área de una desviación estandar en torno al valor promedio (área achurada) y representan una medida de dispersión en torno a la media de la variable en cuestión.")
    
    df_semanal = cargamos_serie_semanal(resolucion=resolucion)
    _df_semanal = filtrar_serie_daily_por_resolucion(df_semanal, resolucion, temporal = 'day')
    _df_semanal = filtrar_options(_df_semanal, options, resolucion)

    if show_concentraciones:
        texto(f"Concentración de MP<sub>2,5</sub>", nfont=20)
        plot_weekly_curves(_df_semanal, resolucion=resolucion, tipo='concentracion',
                           show_shade_fill=leyenda_sombreada,
                           leyenda_h=leyenda_h,
                           showlegend=True,
                           width_figuras=width_figuras)
    if show_emisiones:
        texto("Emisión de MP<sub>2,5</sub>", nfont=20,)
        plot_weekly_curves(_df_semanal, resolucion=resolucion, tipo='emision',
                           show_shade_fill=leyenda_sombreada,
                           showlegend=True,
                           leyenda_h=leyenda_h,
                           width_figuras=width_figuras)
  


    
# 3. MAPAS    
def mapas():
    
    texto('''La figura inferior ilustra simultaneamente la concentración y emisión mensual/invernal de MP2,5 correspondiente al promedio del periodo 2015 al 2017. Mientras la concentracion se representa a través de un mapa de calor (colores) las emisiones se representan por varas verticales cuya altura es proporcional a las emisiones de dicha comuna.''')

    st.sidebar.subheader('Período a graficar')
    mapa = ['Todo el período'] + [f"Promedio de {k}" for k in ['Mayo','Junio', 'Julio', 'Agosto']]
    modo_mapa = st.sidebar.radio("Seleccionamos un período para promediar", mapa, index=0, key='seleccion_principal')
    
    width_figuras = st.sidebar.slider('ancho figuras', 0, 2000, 1000)

    if modo_mapa == mapa[0]:
        fecha_inicio = '2015-05-01'
        fecha_fin = '2015-08-31'
    elif modo_mapa == mapa[1]:
        fecha_inicio = '2015-05-01'
        fecha_fin = '2015-05-31'
    elif modo_mapa == mapa[2]:
        fecha_inicio = '2015-06-01'
        fecha_fin = '2015-06-30'
    elif modo_mapa == mapa[3]:
        fecha_inicio = '2015-07-01'
        fecha_fin = '2015-07-31'
    elif modo_mapa == mapa[4]:
        fecha_inicio = '2015-08-01'
        fecha_fin = '2015-08-31'

        
    texto(f"Agregando desde {fecha_inicio} hasta {fecha_fin}",)
    df_mapa = cargamos_raster(fecha_inicio, fecha_fin)
    plot_mapa(df_mapa, width_figuras=width_figuras)    


main()