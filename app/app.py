from utils import *
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import datetime
from PIL import Image    

def main():
    st.beta_set_page_config(page_title='Explorador de calidad del aire',
                           page_icon=':earth-americas:')
    width_pagina = 1100
    max_width_(width_pagina)
    st.markdown('''<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=UA-177375442-1"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'UA-177375442-1');
</script>''',  unsafe_allow_html=True,)
    
    plot_logo_pagina()
    texto('''Una herramienta para visualizar resultados adicionales del Informe a las Naciones "El aire que respiramos: pasado, presente y futuro. Contaminación atmosférica por MP2,5 en el centro y sur de Chile"''', 15, sidebar=True)
    
 
    titulo_opcion = st.empty()
    st.sidebar.subheader('Seleccionamos un menú')

    menu = ["1. Vista general","2. Series de tiempo", "3. Mapas", "4. Comparación escenarios"]
    app_mode = st.sidebar.radio("", menu, index=0, key='seleccion_principal')
    width_figuras = 1000
    if app_mode==menu[0]:
        texto("Emisiones y Concentraciones de MP<sub>2,5</sub>", nfont=30)
        vista_general(width_figuras=width_figuras)

    elif app_mode==menu[1]:
        texto("Series de tiempo", nfont=30)
        series_de_tiempo(width_figuras=width_figuras)
        
    elif app_mode==menu[2]:
        texto("Mapas de concentración y emisión de MP<sub>2,5</sub>", 30)
        mapas(width_figuras=width_figuras)
        
    elif app_mode==menu[3]:
        texto("Comparación entre escenarios de emisión y concentración de MP<sub>2,5</sub>", 30)
        escenarios(width_figuras=width_figuras)
        

    

    # LOGOS 
    plot_logo_cr2()
    plot_logo_spike()

    
    
# 1. VISTA GENERAL
def vista_general(width_figuras = 1000):
    texto(' ')
    texto('''La informacion que se presenta en esta plataforma corresponde a salidas de un sistema de modelacion compuesto por el modelo meteorológico WRF y el modelo químico de transporte CHIMERE. Este sistema ha sido aplicado anteriormente con éxito para caracterizar la dispersión de la contaminación en Santiago y permite conocer la evolución de la calidad del aire en lugares donde no hay estaciones de monitoreo.
Los datos de concentracion de MP<sub>2,5</sub> en los distintos graficos corresponden al promedio del periodo 2015 a 2017 para los meses de mayo a agosto. Los flujos de emisión de MP<sub>2,5</sub> en tanto, corresponden a estimaciones del inventario de emisiones realizado por el CR2 para fines del informe a la nacion y está descrito en mayor detalle en el capítulo 2 del informe.''',
            nfont=15)
    
    st.markdown('---')
    st.sidebar.subheader('Dominio de interés')
    resolucion = get_resolucion(key='vista_general')
    escenario, escenario_escogido = get_escenario()
    opciones = ("Concentración versus emisión","Concentración versus número de habitantes","Emisión versus número de habitantes")
    vistas = st.sidebar.radio('Seleccionamos una vista',opciones)
#    st.sidebar.markdown('---')
#    width_figuras = st.sidebar.slider('ancho figuras', 0, 2000, 1000)
    
    
    if vistas==opciones[0]:
        variables = ['Concentración', 'Emisión', 'Número de habitantes']
    elif vistas==opciones[1]:
        variables = ['Concentración', 'Número de habitantes', 'Emisión']
    elif vistas==opciones[2]:
        variables = ['Emisión', 'Número de habitantes', 'Concentración']

    df = cargamos_datos_resumen(resolucion)
    
    texto("Concentración versus emisión de MP<sub>2,5</sub>", nfont=20,)
    ploteamos_barras(df, resolucion, variables, escenario = escenario, width_figuras=width_figuras)
    
    '''  
    
    '''

    st.markdown('---')

    texto("Dispersión del promedio invernal de MP<sub>2,5</sub>", nfont=20)
    plot_dispersion(df, resolucion, variables=variables, escenario=escenario, width_figuras=width_figuras)    
    
    st.markdown('---')
    st.subheader('Dispersión animada')
    bool_animacion = st.checkbox('Generar animación', False)
    if bool_animacion:
        animacion(resolucion=resolucion, width_figuras=width_figuras)
    
    


# 2. SERIES DE TIEMPO
def series_de_tiempo(width_figuras = 1000):   
    
    texto('''Los siguientes gráficos presentan series de tiempo de concentración promedio por región/comuna o emisión acumulada por región/comuna para intervalos de tiempo entre el 1 de Mayo  al 31 de Agosto. Cada serie de tiempo corresponde al promedio del período 2015 al 2017. El primer conjunto de gráficos permite examinar la serie de tiempo completa agrupado a nivel diario. En los ciclos diarios como en los cíclos semanales (el segundo y tercer conjunto de gráficos respectivamente), además del valor promedio se puede también ilustrar la desviación estandar de la variable presentada, esto es una medida de dispersión en torno a la media de la variable en cuestión. ''')
    
    st.sidebar.subheader('Dominio de interés')
    resolucion = get_resolucion(key='vista_general')

    escenario, escenario_escogido = get_escenario()
    ''' 
    
    '''
    #texto(''' 1. Serie completa''', 25)
    #hourly = st.checkbox('Resolución horaria', value=False)
    hourly = False

    df_serie_completa = cargamos_series_tiempo_completas(hourly=hourly, resolucion=resolucion)
    _df_serie_completa = filtrar_serie_daily_por_resolucion(df_serie_completa, resolucion)
    options = filtrar_espacial(_df_serie_completa,resolucion)
    if options==[]:
        st.sidebar.error('Lista vacía')


    #st.sidebar.markdown('---')
    st.sidebar.subheader('Ajustes gráficos')
    leyenda_h = True
    leyenda_arriba = False
    leyenda_sombreada = st.sidebar.checkbox('Incluimos dispersión sombreada', value=True)
    #st.markdown('---')
    #width_figuras = st.sidebar.slider('ancho figuras', 0, 2000, 1000)
    

    _df_serie_completa = filtrar_options(_df_serie_completa, options, resolucion)
    st.markdown('---')
    texto(f"Concentración de MP<sub>2,5</sub> para {escenario_escogido}", nfont=20)
    line_plot(_df_serie_completa, y='concentracion',
              resolucion=resolucion,
              escenario=escenario,
              leyenda_h=leyenda_h,
              hourly=hourly,
              leyenda_arriba=leyenda_arriba,
              width_figuras=width_figuras)
    texto(' ')
    texto(' ')
#     texto("Emisión de MP<sub>2,5</sub>", nfont=20,)
#     line_plot(_df_serie_completa, y='emision',
#               resolucion=resolucion,
#               leyenda_h=leyenda_h,
#               hourly=hourly,
#               leyenda_arriba=leyenda_arriba,
#               width_figuras=width_figuras)

    ''' 
    
    '''    
    st.markdown('---')
    texto(''' Ciclo diario''', 25)
    texto(' ')
    texto("El ciclo diario representa la evolución a lo largo de un dia de un parámetro (concentración o emisión). El valor de la variable en cada hora del ciclo corresponde al promedio de todas esas horas durante el período del 1 de Mayo al 31 de Agosto de los años 2015 al 2017. Además del ciclo diario promedio se ilustra tambien el área de una desviación estándar en torno al valor promedio (área achurada) que representa una medida de dispersión en torno a la media de la variable en cuestión.",)
    texto(' ')

    df_diario = cargamos_serie_24hrs(resolucion=resolucion) 
    _df_diario = filtrar_serie_daily_por_resolucion(df_diario, resolucion)
    _df_diario = filtrar_options(_df_diario, options, resolucion)


    texto(f"Concentración de MP<sub>2,5</sub>", nfont=20)
    plot_daily_curves(_df_diario,
                      resolucion,
                      tipo='concentracion',
                      escenario=escenario,
                      show_shade_fill=leyenda_sombreada,
                      leyenda_h=leyenda_h,
                      showlegend=True,
                      leyenda_arriba=leyenda_arriba,
                      width_figuras=width_figuras)
    texto(' ')
    texto(' ')

    texto("Emisión de MP<sub>2,5</sub>", nfont=20,)
    plot_daily_curves(_df_diario,
                      resolucion,
                      tipo='emision', 
                      escenario=escenario,
                      show_shade_fill=leyenda_sombreada,
                      leyenda_h=leyenda_h,
                      showlegend=True,
                      leyenda_arriba=leyenda_arriba,
                      width_figuras=width_figuras)

    ''' 
    
    '''   
#     st.markdown('---')
#     texto(''' 3. Ciclo semanal''', 25)
#     texto("El ciclo semanal representa la evolución a lo largo de una semana de un parámetro (concentración o emisión). El valor de la variable en cada día del ciclo corresponde al promedio de todas esos días durante el periodo del 1 de Mayo al 31 de Agosto de los años 2015 al 2017. Además del ciclo semanal promedio se ilustra también el área de una desviación estándar en torno al valor promedio (área achurada) que representan una medida de dispersión en torno a la media de la variable en cuestión.")
#     texto(' ')
    
#     df_semanal = cargamos_serie_semanal(resolucion=resolucion)
#     _df_semanal = filtrar_serie_daily_por_resolucion(df_semanal, resolucion, temporal = 'day')
#     _df_semanal = filtrar_options(_df_semanal, options, resolucion)

#     if show_concentraciones:
#         texto(f"Concentración de MP<sub>2,5</sub>", nfont=20)
#         plot_weekly_curves(_df_semanal,
#                            resolucion=resolucion,
#                            tipo='concentracion',
#                            escenario=escenario,
#                            show_shade_fill=leyenda_sombreada,
#                            leyenda_h=leyenda_h,
#                            showlegend=True,
#                            leyenda_arriba=leyenda_arriba,
#                            width_figuras=width_figuras)
#     texto(' ')
#     texto(' ')
#     if show_emisiones:
#         texto("Emisión de MP<sub>2,5</sub>", nfont=20,)
#         plot_weekly_curves(_df_semanal,
#                            resolucion=resolucion,
#                            tipo='emision',
#                            escenario=escenario,
#                            show_shade_fill=leyenda_sombreada,
#                            showlegend=True,
#                            leyenda_h=leyenda_h,
#                            leyenda_arriba=leyenda_arriba,
#                            width_figuras=width_figuras)
   
# 3. MAPAS    
def mapas(width_figuras = 1000):
    texto(' ')
    texto('''La figura inferior ilustra simultáneamente la concentración y emisión mensual/invernal de MP<sub>2,5</sub> correspondiente al promedio del período 2015 al 2017. Mientras la concentracion se representa a través de un mapa de calor (colores rojos representan altas concentraciones, mientras que colores amarillos representan bajas concentraciones), las emisiones se representan por columnas verticales cuya altura es proporcional a las emisiones de dicha región/comuna.''',19)
    texto(' ')
    texto(' ')
    st.sidebar.subheader('Escenario de interés')
    escenario, escenario_escogido = get_escenario()
    agregaciones = {'Agrupación regional':'region', 'Agrupación comunal':'comuna'}
    resolucion_mapa = st.sidebar.selectbox('Agregando emisiones', list(agregaciones.keys()), index=0)
    
    st.sidebar.subheader('Período a graficar')
    mapa = ['Todo el período'] + [f"Promedio de {k}" for k in ['Mayo','Junio', 'Julio', 'Agosto']]
    modo_mapa = st.sidebar.radio("Seleccionamos un período para promediar", mapa, index=0, key='seleccion_principal')

    
    #width_figuras = st.sidebar.slider('ancho figuras', 0, 2000, 1000)

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

    #texto(f"Agregando desde {fecha_inicio} hasta {fecha_fin}",)
    df_mapa = cargamos_raster(resolucion = agregaciones[resolucion_mapa],
                              date_inicio=fecha_inicio,
                              date_fin=fecha_fin)
    plot_mapa(df_mapa,
              resolucion=agregaciones[resolucion_mapa],
              escenario=escenario,
              width_figuras=width_figuras)    

# 4. Escenarios

def escenarios(width_figuras = 1000):
    texto(' ')
    texto('Las figuras en esta sección correponden a los resultados de las simulaciones realizadas usando las emisiones de diferentes escenarios que consideran distintas evoluciones de medidas de mitigación desde el presente hasta el año 2050. Los escenarios de proyeccion de emisiones considerados son Comunal, Regional y Regional más efecto rebote. Cada una de las simulaciones se realizaron con la misma meteorología (mayo a agosto de los años 2015 a 2017). La comparación entre los escenarios con el caso presente permite examinar el impacto de las medidas de mitigación incluídas en cada escenario, si se implementaran hoy. Así, los resultados permiten evaluar la eficiencia de estas medidas y su efecto en mejorar la calidad del aire.')
    texto(' ')
    st.sidebar.subheader('Dominio de interés')
    resolucion = get_resolucion(key='escenarios')
    df_ciclo_escenarios = cargamos_serie_escenario_ciclo_diario(resolucion=resolucion)
    df_ciclo_escenarios, _ = filtrar_escenario_por_resolucion(df_ciclo_escenarios, resolucion)
    options = filtrar_espacial(df_ciclo_escenarios,resolucion)
    df_barras_escenarios = cargamos_datos_comparacion_escenarios(resolucion)
    
    
    
    if options==[]:
        st.sidebar.error('Lista vacía')
    else:
        df_ciclo_escenarios_filtrado = filtrar_options(df_ciclo_escenarios, options, resolucion)
        df_barras_escenarios = filtrar_options(df_barras_escenarios, options, resolucion)
    st.sidebar.markdown('---')
    #width_figuras = st.sidebar.slider('ancho figuras', 0, 2000, 1000)
    
    
    
    
    texto('''Concentración promedio de MP<sub>2,5</sub> asociado a cada escenario''', 25)
    plot_barras_escenarios(df_barras_escenarios, 
                           tipo='concentracion',
                           resolucion=resolucion,
                           width_figuras=width_figuras)
    
    
    texto(' ')
    texto(' ')
    texto('''Emisiones de MP<sub>2,5</sub> asociadas a cada escenario''', 25)
    plot_barras_escenarios(df_barras_escenarios, 
                           tipo='emision',
                           resolucion=resolucion,
                           width_figuras=width_figuras)

    
    st.markdown('---')
    texto(' ')
    texto('Ciclo diario por escenario para:', 25)
    texto(' ')
    generamos_concentracion = st.checkbox('Concentración', value=False)
    generamos_emision = st.checkbox('Emisión', value=False)
    figuras_concentracion = plot_ciclo_diario_escenarios(df_ciclo_escenarios_filtrado,
                                           resolucion,
                                           tipo = 'concentracion',
                                           width_figuras=width_figuras)

    figuras_emision = plot_ciclo_diario_escenarios(df_ciclo_escenarios_filtrado,
                                           resolucion,
                                           tipo = 'emision',
                                           width_figuras=width_figuras)
    

    
    espacio_figuras = {}
    for fig in figuras_concentracion.keys():
        espacio_figuras[fig] = st.empty()
    for fig in figuras_emision.keys():
        espacio_figuras[fig] = st.empty()
        
    if generamos_concentracion:
        caption = '''Evolución diaria promedio de las emisiones acumulada de MP<sub>2,5</sub> por región/comuna. La línea continua indica el valor promedio para cada hora del día.''' 
        texto(caption, 16, line_height=1.1, color='grey')
        for fig in figuras_concentracion.keys():
            espacio_figuras[fig].plotly_chart(figuras_concentracion[fig])
        

    else:
        for fig in figuras_concentracion.keys():
            espacio_figuras[fig].empty()

        
    if generamos_emision:
        caption = '''Evolución diaria promedio de la concentración promedio de MP<sub>2,5</sub> por región/comuna. La línea continua indica el valor promedio para cada hora del día.''' 
        texto(caption, 16, line_height=1.1, color='grey')
        for fig in figuras_emision.keys():
            espacio_figuras[fig].plotly_chart(figuras_emision[fig])
        

    else:
        for fig in figuras_emision.keys():
            espacio_figuras[fig].empty()

    #select_block_container_style()
    

main()