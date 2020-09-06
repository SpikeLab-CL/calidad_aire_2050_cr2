import pandas as pd
import pandas_gbq
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pydeck as pdk

colores = [['rgb(31, 119, 180)', 'rgba(31, 119, 180, 0.2)'],
 ['rgb(255, 127, 14)', 'rgba(255, 127, 14, 0.2)'],
 ['rgb(44, 160, 44)', 'rgba(44, 160, 44, 0.2)'],
 ['rgb(214, 39, 40)', 'rgba(214, 39, 40, 0.2)'],
 ['rgb(148, 103, 189)', 'rgba(148, 103, 189, 0.2)'],
 ['rgb(140, 86, 75)', 'rgba(140, 86, 75, 0.2)'],
 ['rgb(227, 119, 194)', 'rgba(227, 119, 194, 0.2)'],
 ['rgb(127, 127, 127)', 'rgba(127, 127, 127, 0.2)'],
 ['rgb(188, 189, 34)', 'rgba(188, 189, 34, 0.2)'],
 ['rgb(23, 190, 207)', 'rgba(23, 190, 207, 0.2)']]

mapbox_key = 'pk.eyJ1IjoicGlwc2FsYXMiLCJhIjoiY2thZmliY2kyMDBtazJybzM2b2xwMnpmcSJ9.pvkr8G0WB8vQLWkOZFwonQ'

TEMPLATE = "plotly_white"

COLOR_MAP = {"default": "#262730",
             "pink": "#E22A5B",
             "purple": "#985FFF",}


#factor_escala_emisiones = 3600*4*10**6 AL FINAL ESCALÉ DESDE BQ



# 4. ESCENARIOS
def get_escenario():
    escenarios = {'Presente':'ref', 
                  'E. Regional (+ efecto rebote)': 'rebote',
                 'E. Comunal': 'comuna',
                 'E. Regional': 'comb'}
    escenario_escogido = st.sidebar.selectbox('Seleccionamos un escenario', list(escenarios.keys()))
    escenario = escenarios[escenario_escogido]
    return escenario, escenario_escogido



def plot_ciclo_diario_escenarios(df : pd.DataFrame, 
                                 resolucion : str, 
                                 tipo : str = 'concentracion', 
                                 width_figuras : float = 1000):
    
    
    _df, col_a_mirar = filtrar_escenario_por_resolucion(df, resolucion)
    _df = simplificar_nombre_region(_df)

    if tipo == 'concentracion':
        yaxis_title = 'Concentración promedio [μg/m³]'
    else:
         yaxis_title = 'Emisión acumulada [ton/día]'
        
    df_aux = _df.melt(id_vars=['hora', col_a_mirar], value_vars=[f'{tipo}_ref', f'{tipo}_comuna', f'{tipo}_comb', f'{tipo}_rebote'])
    df_aux.rename(columns={'variable':'Escenario'}, inplace=True)
    replace = {f'{tipo}_ref':'Presente', f'{tipo}_comuna':'E. Comunal', f'{tipo}_comb':'E. Regional', f'{tipo}_rebote':'E. Regional (+ efecto rebote)'}
    df_aux.replace(replace, inplace=True)
    df_aux.sort_values(by=['hora', 'Escenario'], inplace=True)
    regiones_a_plotear = df_aux[col_a_mirar].unique()
    fig = {}
    for region_a_mirar in regiones_a_plotear:
        
        key = f'{tipo}_{region_a_mirar}'
        fig[key] = px.line(df_aux.query(f'{col_a_mirar}=="{region_a_mirar}"'), x="hora", y="value", color="Escenario",
                      line_group="Escenario", hover_name="Escenario", title=f'Ciclo diario de {tipo} en {region_a_mirar}')

        fig[key].update_layout(height=400, width=width_figuras, template=TEMPLATE,
                          yaxis_title=yaxis_title,
                          xaxis_title='',
                          xaxis = dict(tickmode = 'array',
                                       tickvals = [0, 4, 8, 12, 16, 20],
                                       ticktext = ['0 hrs', '4 hrs', '8 hrs', '12 hrs', '16 hrs', '20 hrs']),
                          legend_title_text=col_a_mirar,)
        fig[key].update_layout(legend_title_text='Escenario',
                                          annotations=[dict(x=1.05,
                                          y=-0.05,
                                          showarrow=False,
                                          text="Hora local",
                                          xref="paper",
                                          yref="paper")],
                      autosize=False,
                      margin=dict(b=100)
                      )
        
                          
        #st.plotly_chart(fig[region_a_mirar])
    return fig

        
        
def cargamos_serie_escenario_ciclo_diario(resolucion='Todas las regiones'):
    if resolucion=='Todas las regiones':
        var_espacio = 'region'
        var_cruce = 'region'
    else:
        var_espacio = 'comuna, region'
        var_cruce = 'comuna'
    query = f'''
    WITH base_concentracion as(
        SELECT Time, {var_espacio}, 
        AVG(conc_ref) as conc_ref, AVG(conc_comuna) as conc_comuna, AVG(conc_comb) as conc_comb , AVG(conc_rebote) as conc_rebote
        FROM CR2.concentracion_escenarios_w_geo
        GROUP BY Time, {var_espacio}
    ),
    base_emision as(
        SELECT Time, {var_espacio}, 
        SUM(emi_ref) as emi_ref, SUM(emi_comuna) as emi_comuna, SUM(emi_comb) as emi_comb , SUM(emi_rebote) as emi_rebote
        FROM CR2.emision_escenarios_w_geo
        GROUP BY Time, {var_espacio}
    ),
    base_agrupada as(
    SELECT con.*, emi.* EXCEPT(Time, {var_espacio})
    FROM base_concentracion as con
    JOIN base_emision as emi
    ON con.Time = emi.Time AND con.{var_cruce} = emi.{var_cruce}
    WHERE con.region!="Región de Coquimbo" AND con.region!="Región de Magallanes y Antártica Chilena" 

    )
    SELECT EXTRACT(HOUR from Time) as hora, {var_espacio},
    AVG(conc_ref) as concentracion_ref, AVG(conc_comuna) as concentracion_comuna, AVG(conc_comb) as concentracion_comb , AVG(conc_rebote) as concentracion_rebote,
    AVG(emi_ref) as emision_ref, AVG(emi_comuna) as emision_comuna, AVG(emi_comb) as emision_comb , AVG(emi_rebote) as emision_rebote
    FROM base_agrupada
    GROUP BY hora, {var_espacio}
    ORDER BY hora ASC, {var_espacio}
    '''
    
#     df = pandas_gbq.read_gbq(query,
#                              project_id='spike-sandbox',
#                              use_bqstorage_api=True)
#     df.to_csv(f'./data/CE_datos_comparar_escenarios_ciclo_diario_{var_cruce}.csv', index=False)
    df = pd.read_csv(f'./data/CE_datos_comparar_escenarios_ciclo_diario_{var_cruce}.csv') 

    return df


#--------------
def plot_barras_escenarios(df : pd.DataFrame, 
                           tipo : str = 'concentracion',
                           resolucion : str = 'Todas las regiones',
                           width_figuras=1000):
    
    _df, col_a_mirar = filtrar_escenario_por_resolucion(df, resolucion)
    _df = simplificar_nombre_region(_df)
    _df.sort_values(by=f'{tipo}_ref', inplace=True, ascending=False)
    if tipo == 'concentracion':
        yaxis_title = 'Concentración promedio [μg/m³]'
        descripcion = '''Gráfico de barras que ilustra la concentración promedio diaria de MP<sub>2,5</sub> [μg/m<sup>3</sup>] por región/comuna de los meses de invierno (mayo-agosto) del período 2015 a 2017 simulados por el sistema de modelación WRF-CHIMERE para emisiones Presente y cada una de las trayectorias de emisiones (Comunal, Regional más efecto rebote y Regional)'''
        
    else:
        yaxis_title = 'Emisión promedio [ton/día]'
        descripcion = '''Gráfico de barras que ilustra la emisión acumulada diaria promedio de MP<sub>2,5</sub> [ton/día] por región/comuna para el caso Presente y las emisiones proyectadas para el año 2050 para cada uno de las trayectorias de emisiones (Comunal, Regional más efecto rebote y Regional)
'''
        
    x = _df[col_a_mirar]
    fig = go.Figure()
    escenarios = {f'{tipo}_ref':'Presente', f'{tipo}_comuna':'E. Comunal', f'{tipo}_rebote':'E. Regional (+ efecto rebote)', f'{tipo}_comb':'E. Regional'}
    nombre_colores = ['#AB63FA', '#636EFA', '#00CC96', '#EF553B']

    for escenario, color in zip(list(escenarios.keys()), nombre_colores):
        fig.add_trace(go.Bar(
            x=x,
            y=_df[escenario],
            name=escenarios[escenario],
            marker_color=color
        ))


    fig.update_layout(barmode='group', xaxis_tickangle=-45,
                     legend=dict(x=0, y=1.1,orientation="h"),
                       yaxis=dict(title=yaxis_title),)
    fig.update_layout(template=TEMPLATE)
    fig.update_layout(height=500, width=width_figuras,)
 
    st.plotly_chart(fig)
    texto(descripcion, 14, line_height=1, color='grey')


def filtrar_escenario_por_resolucion(df, resolucion):
    if resolucion == 'Todas las regiones':
        _df = df.copy()
        col_a_mirar = 'region'
        
    else:
        _df = df.query('region==@resolucion')
        col_a_mirar = 'comuna'
        
    col_referencia = [m for m in _df.columns if 'ref' in m]
    _df.sort_values(by=col_referencia, ascending=False, inplace=True)
    return _df, col_a_mirar

def cargamos_datos_comparacion_escenarios(resolucion):
    if resolucion=='Todas las regiones':
        var_espacio = 'region'
        var_cruce = 'region'
    else:
        var_espacio = 'comuna, region'
        var_cruce = 'comuna'

    query = f'''
        WITH  base_diaria_concentracion as(
            SELECT EXTRACT(DATE FROM Time) as date, {var_espacio}, 
            AVG(conc_ref) as conc_ref, AVG(conc_comuna) as conc_comuna, AVG(conc_comb) as conc_comb , AVG(conc_rebote) as conc_rebote
            FROM CR2.concentracion_escenarios_w_geo
            GROUP BY date, {var_espacio}
        ),
        base_diaria_emision as(
        SELECT EXTRACT(DATE FROM Time) as date, {var_espacio}, 
        SUM(emi_ref) as emi_ref, SUM(emi_comuna) as emi_comuna, SUM(emi_comb) as emi_comb , SUM(emi_rebote) as emi_rebote
        FROM CR2.emision_escenarios_w_geo
        GROUP BY date, {var_espacio}
        ),
        base_agrupada as(
        SELECT con.*, emi.* EXCEPT(date, {var_espacio})
        FROM base_diaria_concentracion as con
        JOIN base_diaria_emision as emi
        ON con.date = emi.date AND con.{var_cruce} = emi.{var_cruce}
        WHERE con.region!="Región de Coquimbo" AND con.region!="Región de Magallanes y Antártica Chilena" 
        ),
        base_final as(
        SELECT {var_espacio},
        AVG(conc_ref) as concentracion_ref, AVG(conc_comuna) as concentracion_comuna, AVG(conc_comb) as concentracion_comb , AVG(conc_rebote) as concentracion_rebote,
        AVG(emi_ref) as emision_ref, AVG(emi_comuna) as emision_comuna, AVG(emi_comb) as emision_comb , AVG(emi_rebote) as emision_rebote
        FROM base_agrupada
        GROUP BY {var_espacio}
        )
        SELECT * FROM base_final '''

#     df = pandas_gbq.read_gbq(query,
#                              project_id='spike-sandbox',
#                              use_bqstorage_api=True)
#     df.to_csv(f'./data/CE_datos_comparar_escenarios_{var_cruce}.csv', index=False)
    df = pd.read_csv(f'./data/CE_datos_comparar_escenarios_{var_cruce}.csv') 
    
    return df

# def filtrar_ciclo_escenario_por_resolucion(df, resolucion, temporal = 'hora'):
#     if resolucion == 'Todas las regiones':
#         _df = df.copy()
#     else:
#         _df = df.query('region==@resolucion')
        
#     _df = simplificar_nombre_region(_df)
#     return _df

def filtrar_espacial(df, resolucion):
    col_a_mirar = columna_a_mirar(resolucion)
    tipos = list(df[col_a_mirar].unique())
    if col_a_mirar == 'region':
        titulo = 'regiones'
    else:
        titulo = 'comunas'
    var_inicial = [f'Todas'] + tipos
    options = st.sidebar.multiselect(f'Filtramos {titulo}',
                                     var_inicial,
                                    default=['Todas'])
    return options
    
def filtrar_options(df, options, resolucion):
    col_a_mirar = columna_a_mirar(resolucion)
    if options==['Todas']:
        return df
    else:
        return df.query(f'{col_a_mirar} in {options}')


# 3. MAPAS
@st.cache
def cargamos_raster(resolucion :str = 'region',
                    date_inicio : str = "2015-05-03", 
                    date_fin : str = "2015-05-04",):
    if resolucion=='region':
        var_cruce = 'region'
    else:
        var_cruce = 'comuna'
    
    query = f'''
    WITH  base_agrupada as(
        SELECT con.Time, con.lat, con.lon, con.{var_cruce},
                con.conc_ref, con.conc_comb, con.conc_comuna, con.conc_rebote, 
                emi.emi_ref, emi.emi_comb, emi.emi_comuna, emi.emi_rebote
        FROM CR2.concentracion_escenarios_w_geo as con
        JOIN CR2.emision_escenarios_w_geo as emi
            ON con.lat=emi.lat AND con.lon=emi.lon AND con.Time=emi.Time
        WHERE con.Time>='{date_inicio}' AND con.Time<'{date_fin}' 
        AND con.region!="Región de Coquimbo" AND con.region!="Región de Magallanes y Antártica Chilena" 
    )
    SELECT lat, lon, {var_cruce}, 
    AVG(conc_ref) as concentracion_ref, AVG(conc_comb) as concentracion_comb, AVG(conc_comuna) as concentracion_comuna, AVG(conc_rebote) as concentracion_rebote, 
    AVG(emi_ref) as emision_ref, AVG(emi_comb) as emision_comb, AVG(emi_comuna) as emision_comuna, AVG(emi_rebote) as emision_rebote
    FROM base_agrupada
    GROUP BY lat, lon, {var_cruce}
'''
    
#     df = pandas_gbq.read_gbq(query,
#                              project_id='spike-sandbox',
#                              use_bqstorage_api=True)
#     df.to_csv(f'./data/MP_mapa_agregacion_{var_cruce}_from_{date_inicio}_to_{date_fin}.csv', index=False)
    df = pd.read_csv(f'./data/MP_mapa_agregacion_{var_cruce}_from_{date_inicio}_to_{date_fin}.csv')

    return df


def plot_mapa(df : pd.DataFrame,
              resolucion : str = 'region',
              escenario : str = 'ref',
              width_figuras : float = 1000,
              pitch : float = 40,
              bearing : float = -90):
    
    columna_emision = f'emision_{escenario}'
    columna_concentracion = f'concentracion_{escenario}'
    emisiones_comunales = df.groupby(resolucion)[['lat','lon',columna_emision]]\
                            .agg({'lat':'mean', 'lon':'mean',columna_emision:'sum'}).reset_index()
    df2 = df[['lat','lon',columna_concentracion]].copy()
    emisiones_comunales[columna_emision] *= 1e3
    df2[columna_concentracion] *= 1e14
    
    if resolucion == 'region':
        elevation_scale = 200
        radius = 3500
    else:
        elevation_scale = 600
        radius = 2500
    
    emisiones = pdk.Layer("ColumnLayer",
                          id=columna_emision,
                          data=emisiones_comunales,
                          get_position=["lon", "lat"],
                          get_elevation=columna_emision,
                          elevation_scale=elevation_scale,
                          radius=radius,
                          get_fill_color=[columna_emision,0, columna_emision, 140],
                          getElevation = columna_emision,
                          pickable=True,
                          extruded=True,
                          auto_highlight=True,
                          lineWidthUnits='pixels')


    concentraciones = pdk.Layer("HeatmapLayer",
                             data=df2,
                             opacity=0.1,
                             get_position=["lon", "lat"],
                             aggregation='MEAN',
                             threshold=0.1,
                             get_weight=columna_concentracion,
                             pickable=True,)

    view_state = pdk.ViewState(longitude=-70,
                               latitude=-45,
                               zoom=4,
                               min_zoom=2,
                               max_zoom=7,
                               pitch=60,
                               bearing=35)

    st.pydeck_chart(pdk.Deck(layers=[emisiones, concentraciones],
                             initial_view_state=view_state,
                             map_style="mapbox://styles/mapbox/light-v9",
                             mapbox_key=mapbox_key,
                             height=1000, width=width_figuras))
    
    texto('''Mapa de concentración (colores) y emisión (barras) de MP<sub>2,5</sub>. Mientras la concentración [μg/m<sup>3</sup>] corresponde al promedio para el intervalo de tiempo, la emisión corresponde al valor acumulado (suma) para el mismo intervalo de tiempo [ton/periodo]''',14, line_height=1, color='grey')
    
    
    

# 2. SERIES DE TIEMPO
@st.cache
def cargamos_serie_semanal(resolucion = 'Todas las regiones'):
    if resolucion=='Todas las regiones':
        var_espacio = 'region'
        var_cruce = 'region'
    else:
        var_espacio = 'comuna, region'
        var_cruce = 'comuna'
    query = f'''
    WITH  base_comunal_concentracion as(
        SELECT EXTRACT(DATE FROM Time) as date, {var_espacio}, 
        AVG(conc_ref) as concentracion_ref, AVG(conc_comb) as concentracion_comb, AVG(conc_comuna) as concentracion_comuna, AVG(conc_rebote) as concentracion_rebote
        FROM CR2.concentracion_escenarios_w_geo
        GROUP BY date, {var_espacio}
    ),
    base_comunal_emision as(
        SELECT EXTRACT(DATE FROM Time) as date, {var_espacio},
        SUM(emi_ref) as emision_ref, SUM(emi_comb) as emision_comb, SUM(emi_comuna) as emision_comuna, SUM(emi_rebote) as emision_rebote,
        FROM CR2.emision_escenarios_w_geo
        GROUP BY date, {var_espacio}
    ),
    base_agrupada as(
        SELECT con.*, emi.* EXCEPT(date, {var_espacio})
        FROM base_comunal_concentracion as con
        JOIN base_comunal_emision as emi
            ON con.{var_cruce}=emi.{var_cruce} AND con.date=emi.date
        WHERE con.region!="Región de Magallanes y Antártica Chilena" AND con.region!="Región de Coquimbo"
    )
    SELECT EXTRACT(DAYOFWEEK from date) as day, {var_espacio},
    AVG(emision_ref) as avg_emision_ref, STDDEV(emision_ref) as stddev_emision_ref,
    AVG(emision_comb) as avg_emision_comb, STDDEV(emision_comb) as stddev_emision_comb,
    AVG(emision_comuna) as avg_emision_comuna, STDDEV(emision_comuna) as stddev_emision_comuna,
    AVG(emision_rebote) as avg_emision_rebote, STDDEV(emision_rebote) as stddev_emision_rebote,
    AVG(concentracion_ref) as avg_concentracion_ref, STDDEV(concentracion_ref) as stddev_concentracion_ref,
    AVG(concentracion_comb) as avg_concentracion_comb, STDDEV(concentracion_comb) as stddev_concentracion_comb,
    AVG(concentracion_comuna) as avg_concentracion_comuna, STDDEV(concentracion_comuna) as stddev_concentracion_comuna,
    AVG(concentracion_rebote) as avg_concentracion_rebote, STDDEV(concentracion_rebote) as stddev_concentracion_rebote,
    FROM base_agrupada
    GROUP BY day, {var_espacio}
    ORDER BY {var_espacio}
    '''
    #
#     df = pandas_gbq.read_gbq(query,
#                              project_id='spike-sandbox',
#                              use_bqstorage_api=True)
#     df.to_csv(f'./data/ST_series_ciclo_semanal_{var_cruce}.csv', index=False)

    df = pd.read_csv(f'./data/ST_series_ciclo_semanal_{var_cruce}.csv')

    return df


def plot_weekly_curves(_df : pd.DataFrame,
                       resolucion = 'Todas las regiones',
                       tipo = 'emision', 
                       escenario : str = 'ref',
                       showlegend=True,
                       show_shade_fill=True,
                       leyenda_h=True,
                       leyenda_arriba=True,
                       width_figuras=1000):

    col_a_mirar = columna_a_mirar(resolucion)
    fig = go.Figure()
    x = list(_df.sort_values(by='day').day.unique())
    x_rev = x[::-1]

    y, y_upper, y_lower = {}, {}, {}
    k = 0
    columnas = [f'avg_{tipo}_{escenario}', f'stddev_{tipo}_{escenario}']
    if tipo == 'emision':
        
        yaxis_title = 'Emisión promedio [ton/día]'
        descripcion = '''Evolución semanal promedio de emisión de MP<sub>2,5</sub> por región/comuna. La linea continua indica el valor promedio y el área achurada (correspondiente a una desviación estandar) representa una medida de la dispersión en torno a este promedio.'''
        
    elif tipo == 'concentracion':
        yaxis_title = 'Concentración promedio [μg/m³]'
        descripcion = '''Evolución semanal promedio de la concentración de MP<sub>2,5</sub> por región/comuna. La linea continua indica el valor promedio y el área achurada (correspondiente a una desviación estandar) representa una medida de la dispersión en torno a este promedio.'''
    
    for comuna in _df[col_a_mirar].unique():
        
        if col_a_mirar == 'comuna':
            aux = _df.query('comuna==@comuna').copy()
        else:
            aux = _df.query('region==@comuna').copy()
        y[comuna] = list(aux[columnas[0]].values)
        y_upper[comuna] = list(y[comuna] + aux[columnas[1]].values)
        y_lower[comuna] = list(y[comuna] - aux[columnas[1]].values)
        y_lower[comuna] = y_lower[comuna][::-1]

        color = colores[k%len(colores)]
        k+=1
        if show_shade_fill:
            fig.add_trace(go.Scatter(x=x+x_rev,
                                    y=y_upper[comuna]+y_lower[comuna],
                                    fill='toself',
                                    fillcolor=f'{color[1]}',
                                    line_color=f'rgba(255,255,255,0)',
                                    showlegend=showlegend,
                                    name=comuna,
                                    ))

        fig.add_trace(go.Scatter(x=x, y=y[comuna],
                                line_color=f'{color[0]}',
                                name=comuna,
                                ))


    fig.update_traces(mode='lines')
    fig.update_layout(height=600, width=width_figuras,
                      yaxis=dict(title=yaxis_title),
                      xaxis = dict(tickmode = 'array',
                                   tickvals = [1,2,3,4,5,6,7],
                                   ticktext = ['Lunes','Martes','Miércoles','Jueves','Viernes','Sábado','Domingo']),
                      legend_title_text=col_a_mirar,
                      template=TEMPLATE)
    
    set_leyenda(fig, leyenda_h, leyenda_arriba)
    fig.update_layout(legend_title_text=' ')
    st.plotly_chart(fig)
    texto(descripcion,14, line_height=1, color='grey')



@st.cache
def cargamos_serie_24hrs(resolucion='Todas las regiones'):
    if resolucion=='Todas las regiones':
        var_espacio = 'region'
        var_cruce = 'region'
    else:
        var_espacio = 'comuna, region'
        var_cruce = 'comuna'
    query = f'''
    WITH  base_comunal_concentracion as(
        SELECT Time, {var_espacio}, 
        AVG(conc_ref) as concentracion_ref, AVG(conc_comb) as concentracion_comb, AVG(conc_comuna) as concentracion_comuna, AVG(conc_rebote) as concentracion_rebote
        FROM CR2.concentracion_escenarios_w_geo
        GROUP BY Time, {var_espacio}
    ),
    base_comunal_emision as(
        SELECT Time, {var_espacio},  
        SUM(emi_ref) as emision_ref, SUM(emi_comb) as emision_comb, SUM(emi_comuna) as emision_comuna, SUM(emi_rebote) as emision_rebote,
        FROM CR2.emision_escenarios_w_geo
        GROUP BY Time, {var_espacio}
    ),
    base_agrupada as(
        SELECT con.*, emi.* EXCEPT(Time, {var_espacio})
        FROM base_comunal_concentracion as con
        JOIN base_comunal_emision as emi
            ON con.{var_cruce}=emi.{var_cruce} AND con.Time=emi.Time
        WHERE con.region!="Región de Magallanes y Antártica Chilena" AND con.region!="Región de Coquimbo"
    )
    SELECT EXTRACT(HOUR from Time) as hora, {var_espacio},
    AVG(emision_ref) as avg_emision_ref, STDDEV(emision_ref) as stddev_emision_ref,
    AVG(emision_comb) as avg_emision_comb, STDDEV(emision_comb) as stddev_emision_comb,
    AVG(emision_comuna) as avg_emision_comuna, STDDEV(emision_comuna) as stddev_emision_comuna,
    AVG(emision_rebote) as avg_emision_rebote, STDDEV(emision_rebote) as stddev_emision_rebote,
    AVG(concentracion_ref) as avg_concentracion_ref, STDDEV(concentracion_ref) as stddev_concentracion_ref,
    AVG(concentracion_comb) as avg_concentracion_comb, STDDEV(concentracion_comb) as stddev_concentracion_comb,
    AVG(concentracion_comuna) as avg_concentracion_comuna, STDDEV(concentracion_comuna) as stddev_concentracion_comuna,
    AVG(concentracion_rebote) as avg_concentracion_rebote, STDDEV(concentracion_rebote) as stddev_concentracion_rebote,
    FROM base_agrupada
    GROUP BY hora, {var_espacio}
    ORDER BY hora ASC, {var_espacio}
    '''
    
#     df = pandas_gbq.read_gbq(query,
#                              project_id='spike-sandbox',
#                              use_bqstorage_api=True)
#     df.to_csv(f'./data/ST_series_ciclo_diario_{var_cruce}.csv', index=False)

    df = pd.read_csv(f'./data/ST_series_ciclo_diario_{var_cruce}.csv')
    return df

def filtrar_serie_daily_por_resolucion(df, resolucion, temporal = 'hora'):
    if resolucion == 'Todas las regiones':
        _df = df.copy()
    else:
        _df = df.query('region==@resolucion')
        
    _df = simplificar_nombre_region(_df)
    return _df

def columna_a_mirar(resolucion):
    if resolucion == 'Todas las regiones':
        col_a_mirar = 'region'        
    else:
        col_a_mirar = 'comuna'
    return col_a_mirar



def plot_daily_curves(_df : pd.DataFrame,
                      resolucion = 'Todas las regiones',
                      tipo : str = 'emision',
                      escenario : str = 'ref',
                      show_shade_fill=True,
                      showlegend=True,
                      leyenda_h=True,
                      leyenda_arriba=True,
                      width_figuras=1000):
    col_a_mirar = columna_a_mirar(resolucion)
    fig = go.Figure()
    x = list(_df.hora.unique())
    x_rev = x[::-1]
    y, y_upper, y_lower = {}, {}, {}
    k = 0 #parche para ir cambiando de color
    columnas = [f'avg_{tipo}_{escenario}', f'stddev_{tipo}_{escenario}']
    if tipo == 'emision':
        yaxis_title = 'Emisión promedio [ton/hr]' 
        descripcion = '''Evolución diaria promedio de emisión de MP<sub/>2,5</sub> por región/comuna. La linea continua indica el valor promedio y el área achurada (correspondiente a una desviación estándar) representa una medida de la dispersión en torno a este promedio.'''

    elif tipo == 'concentracion':
        yaxis_title = 'Concentración promedio de PM25 [μg/m³]'
        descripcion = '''Evolución diaria promedio de la concentración de MP<sub/>2,5</sub> por región/comuna. La linea continua indica el valor promedio y el área achurada (correspondiente a una desviación estándar) representa una medida de la dispersión en torno a este promedio.'''
    for comuna in _df[col_a_mirar].unique():
        
        if col_a_mirar == 'comuna':
            aux = _df.query('comuna==@comuna').copy()
        else:
            aux = _df.query('region==@comuna').copy()
            
        y[comuna] = list(aux[columnas[0]].values)
        y_upper[comuna] = list(y[comuna] + 1*aux[columnas[1]].values)
        y_lower[comuna] = list(y[comuna] - 1*aux[columnas[1]].values)
        y_lower[comuna] = y_lower[comuna][::-1]

        color = colores[k%len(colores)] #truquini
        k+=1
        if show_shade_fill:
            fig.add_trace(go.Scatter(x=x+x_rev,
                                    y=y_upper[comuna]+y_lower[comuna],
                                    fill='toself',
                                    fillcolor=f'{color[1]}',
                                    line_color=f'rgba(255,255,255,0)',#borde blanqueli
                                    showlegend=showlegend,
                                    name=comuna,
                                    ))

        fig.add_trace(go.Scatter(x=x, y=y[comuna],
                                line_color=f'{color[0]}',
                                name=comuna,
                                ))


    fig.update_traces(mode='lines')
    fig.update_layout(height=600, width=width_figuras,
                      yaxis_title=yaxis_title,
                      xaxis = dict(tickmode = 'array',
                                   tickvals = [0, 4, 8, 12, 16, 20],
                                   ticktext = ['0 hrs', '4 hrs', '8 hrs', '12 hrs', '16 hrs', '20 hrs']),
                      legend_title_text=' ',
                      template=TEMPLATE,
                      annotations=[dict(x=1,
                                      y=-0.05,
                                      showarrow=False,
                                      text="Hora local",
                                      xref="paper",
                                      yref="paper")],
                      autosize=False,
                      margin=dict(b=100)
                      )
    set_leyenda(fig, leyenda_h, leyenda_arriba)
    st.plotly_chart(fig)
    
    texto(descripcion,14, line_height=1, color='grey')




@st.cache
def cargamos_series_tiempo_completas(hourly=False, resolucion='Todas las regiones'):
    var_tiempo = ''
        
    if resolucion=='Todas las regiones':
        var_espacio = 'region'
        var_cruce = 'region'
    else:
        var_espacio = 'comuna, region'
        var_cruce = 'comuna'
    query = f'''
            WITH base_concentracion as(
                SELECT {var_espacio}, EXTRACT(DATE FROM Time) as date, 
                AVG(conc_ref) as concentracion_ref, AVG(conc_comb) as concentracion_comb, AVG(conc_comuna) as concentracion_comuna, AVG(conc_rebote) as concentracion_rebote
                FROM CR2.concentracion_escenarios_w_geo
                GROUP BY {var_espacio}, EXTRACT(DATE FROM Time)
            ),
            base_emision as (
                SELECT {var_espacio},EXTRACT(DATE FROM Time) as date,
                SUM(emi_ref) as emision_ref, SUM(emi_comb) as emision_comb, SUM(emi_comuna) as emision_comuna, SUM(emi_rebote) as emision_rebote,
                FROM CR2.emision_escenarios_w_geo
                GROUP BY {var_espacio}, EXTRACT(DATE FROM Time)
            )
            SELECT con.*, emi.* EXCEPT(date, {var_espacio})
            FROM
            base_concentracion as con
            JOIN
            base_emision as emi
                ON con.{var_cruce}=emi.{var_cruce} AND con.date=emi.date
            WHERE con.region!="Región de Magallanes y Antártica Chilena" AND con.region!="Región de Coquimbo"
            '''

#     df = pandas_gbq.read_gbq(query,
#                              project_id='spike-sandbox',
#                              use_bqstorage_api=True)
#     df.to_csv(f'./data/ST_series_completas_{var_cruce}.csv', index=False)

    df = pd.read_csv(f'./data/ST_series_completas_{var_cruce}.csv')
    return df



def line_plot(_df, y='concentracion', escenario = 'ref',
              resolucion='Todas las regiones', 
              leyenda_h=True, 
              hourly=False, 
              leyenda_arriba=True,
              width_figuras=1000):
    
    
    #_df, col_a_mirar = filtrar_serie_tiempo_por_resolucion(df, resolucion, hourly=hourly)
    col_a_mirar = columna_a_mirar(resolucion)
    if not hourly:
        sort_time = 'date'
    else:
        sort_time = 'Time'
            
    if y == 'concentracion':
        ylabel = 'Concentración [μg/m³]'
        descripcion = '''Serie de tiempo de concentración promedio diaria/horaria [μg/m<sup>3</sup>] por región/comuna. El valor promedio de cada día/hora corresponde al promedio de ese dia/hora de los años 2015 a 2017 simulados por el sistema de modelacion WRF-CHIMERE.'''
    else:
        ylabel = 'Emisión [ton/hr]'
        descripcion = '''Serie de tiempo de emisión acumulada diaria/horaria [ton/dia o ton/hr] por región/comuna. El valor promedio de cada día/hora corresponde al promedio de ese dia/hora de los años 2015 a 2017 simulados por el sistema de modelacion WRF-CHIMERE.'''

    yaxis = f'{y}_{escenario}'
    fig = px.line(_df.sort_values(by=sort_time),
                  x=sort_time,
                  y=yaxis, 
                  line_group=col_a_mirar,
                  color=col_a_mirar,
                  hover_name=col_a_mirar)

        
    fig.update_layout(height=500,
                      width=width_figuras,
                      xaxis_title="", 
                      yaxis_title=ylabel,
                      template=TEMPLATE,
                     legend_title_text=' ')
    
    set_leyenda(fig, leyenda_h, leyenda_arriba)
    st.plotly_chart(fig)
    texto(descripcion, nfont=14, line_height=1, color='grey')
    
    
def set_leyenda(fig, leyenda_h, leyenda_arriba):
    if leyenda_h:
        fig.layout.update(legend_orientation="h")
    if leyenda_h and leyenda_arriba:
        fig.layout.update(legend=dict(x=-0.1, y=1.2))
    elif leyenda_h and not leyenda_arriba:
        fig.layout.update(legend=dict(x=-0.1, y=-0.1))

    
def get_resolucion(key : str = 'resolucion'):    
    lista_regiones = ['Todas las regiones',
                      'Región de Valparaíso',
                      'Región Metropolitana de Santiago',
                      "Región del Libertador Bernardo O'Higgins",
                      'Región del Maule', 
                      'Región de Ñuble',
                      'Región del Biobío',
                      'Región de La Araucanía',
                      'Región de Los Ríos',
                      'Región de Los Lagos', 
                      'Región de Aysén del Gral.Ibañez del Campo']
        
    resolucion = st.sidebar.selectbox('Seleccione la/las región/es de interés',
                                      lista_regiones,
                                      key=key)
    
    if resolucion == 'Región del Biobío':
        resolucion = 'Región del Bío-Bío'
    return resolucion




# 1. VISTA GENERAL
def plot_dispersion(df : pd.DataFrame,
                    resolucion : str = 'Todas las regiones',
                    variables : list = ['Concentración','Emisión', 'Número de habitantes'],
                    escenario : str = 'ref',
                    width_figuras : int = 1000,
                    log_scale : bool = False):
    
    _df = df.copy()
    x = variables[1]
    y = variables[0]
    variables_rango = {'Concentración' : 'concentracion','Emisión' : 'emision', 'Número de habitantes':'Número de habitantes'}
    
    _df['Concentración'] = _df[f'concentracion_{escenario}']
    _df['Emisión'] = _df[f'emision_{escenario}']
    _df, col_a_mirar = filtrar_por_resolucion(_df, resolucion)
    max_x = 1.1*_df[[m for m in _df.columns if variables_rango[x] in m]].max().max()
    max_y = 1.1*_df[[m for m in _df.columns if variables_rango[y] in m]].max().max()
    _df['Logaritmo número de habitantes'] = np.round(np.log(_df['Número de habitantes']),2)
    _df['Emisión'] = np.round(_df['Emisión'],2)
    _df['Concentración'] = np.round(_df['Concentración'],2)
    if variables[2]=='Número de habitantes':
        color = 'Logaritmo número de habitantes'
    else:
        color = variables[2]
    _df['size'] = 8
   
    hover_data = {k:':.2f' for k in variables}
    axis_labels = {'Concentración':'Concentración [μg/m³]',
                   'Emisión':'Emisión [ton/día]',
                   'Número de habitantes':'Número de habitantes'}
    

    fig = px.scatter(_df, x=x, y=y,
                     color=color, 
                     size=color,
                     hover_data=['Número de habitantes'],
                     hover_name=col_a_mirar,
                     range_x=[0,max_x],
                     range_y=[0,max_y])
    
    
    fig.update_layout(height=500, width=width_figuras,
                     xaxis_title=axis_labels[x],
                     yaxis_title=axis_labels[y],
                     template=TEMPLATE)
    set_leyenda(fig, leyenda_h=True, leyenda_arriba=True)
    st.plotly_chart(fig)
    descripcion = {'Concentración':'la concentración promedio diaria [μg/m<sup>3</sup>]',
                   'Emisión': 'la emisión acumulada diaria promedio [ton/día]',
                   'Número de habitantes':'el número de habitantes'}
    texto(f'''Gráfico de dispersión que ilustra {descripcion[y]} y {descripcion[x]} por región/comuna. El tamaño y color de cada círculo ilustran {descripcion[variables[2]]} por región/comuna. Tanto la emisión como la concentración representan la condición promedio invernal (mayo-agosto) del período 2015 a 2017 simulados por el sistema de modelación WRF-CHIMERE.''', 14, line_height=1, color='grey')



def ploteamos_barras(df, resolucion, variables=['Concentración','Emisión'], width_figuras=1000, escenario='ref'):
    _df = df.copy()
    _df['Concentración'] = _df[f'concentracion_{escenario}']
    _df['Emisión'] = _df[f'emision_{escenario}']
    _df, col_a_mirar = filtrar_por_resolucion(_df, resolucion)
    _df['Concentración'] = np.round(_df['Concentración'],1)
    _df['Emisión'] = np.round(_df['Emisión'],2)
    var1 = variables[0]
    var2 = variables[1]
    _df.sort_values(by=var1, ascending=False, inplace=True)
    ylabels = {'Concentración':'Concentración [μg/m³]',
              'Emisión':'Emisión [ton/día]',
              'Número de habitantes':'Número de habitantes'}
    
    colores_barras = {'Concentración':'rgb(250, 50, 50)',
              'Emisión':'rgb(128, 128, 128)',
              'Número de habitantes':'rgb(51, 190, 255)'}
    
    # ploteamos
    trace0 = go.Bar(x=_df[col_a_mirar] , y= _df[var1], name=var1 ,marker_color=colores_barras[var1]) 
    trace1 = go.Bar(x=_df[col_a_mirar] , y=[0],showlegend=False,hoverinfo='none' ,marker_color=colores_barras[var1])
    trace2 = go.Bar(x=_df[col_a_mirar] , y=[0], yaxis='y2',showlegend=False,hoverinfo='none', marker_color=colores_barras[var2]) 
    trace3 = go.Bar(x=_df[col_a_mirar] , y=_df[var2], yaxis='y2', name=var2, marker_color=colores_barras[var2])

    data = [trace0,trace1,trace2,trace3]
    
    layout = go.Layout(barmode='group',
                       legend=dict(x=0, y=1.1,orientation="h"),
                       yaxis=dict(title=ylabels[var1]),
                       yaxis2=dict(title = ylabels[var2],
                                   overlaying = 'y',
                                   side='right'))
    fig = go.Figure(data=data, layout=layout)
    fig.update_layout(template=TEMPLATE)
    fig.update_layout(height=500, width=width_figuras,)
    st.plotly_chart(fig)
    texto('''Gráfico de barras que ilustra la emisión acumulada diaria promedio [ton/día] y la concentración promedio diaria [μg/m<sup>3</sup>] por región/comuna. Ambos parámetros representan la condición promedio invernal (mayo-agosto) del período 2015 a 2017 simulados por el sistema de modelación WRF-CHIMERE.''',14, line_height=1, color='grey')
    

    
def simplificar_nombre_region(df):
    diccionario_regiones = {'Región de Coquimbo': 'Coquimbo' ,
                      'Región de Valparaíso': 'Valparaíso' ,
                      'Región Metropolitana de Santiago': 'Metropolitana' ,
                      "Región del Libertador Bernardo O'Higgins": "Lib B O'Higgins" ,
                      'Región del Maule': 'Maule', 
                      'Región de Ñuble': 'Ñuble' ,
                      'Región del Bío-Bío': 'Biobío' ,
                      'Región de La Araucanía': 'La Araucanía' ,
                      'Región de Los Ríos': 'Los Ríos' ,
                      'Región de Los Lagos': 'Los Lagos', 
                      'Región de Aysén del Gral.Ibañez del Campo': 'Aysén' ,
                      'Región de Magallanes y Antártica Chilena': 'Magallanes'}
    return df.replace(diccionario_regiones).copy()
    
def filtrar_por_resolucion(df, resolucion, sort=True):
    if resolucion == 'Todas las regiones':
        _df = df.copy()
        col_a_mirar = 'region'
        
    else:
        _df = df.query('region==@resolucion')
        col_a_mirar = 'comuna'
        
    _df = simplificar_nombre_region(_df)
    if sort:
        _df.sort_values(by='Concentración', inplace=True, ascending=False)
    return _df, col_a_mirar

@st.cache
def cargamos_datos_resumen(resolucion):
    if resolucion=='Todas las regiones':
        var_espacio = 'region'
        var_cruce = 'region'
    else:
        var_espacio = 'comuna, region'
        var_cruce = 'comuna'

    query = f'''
        WITH  base_concentracion as(
            SELECT EXTRACT(DATE FROM Time) as date, {var_espacio}, 
            AVG(conc_ref) as concentracion_ref, AVG(conc_comb) as concentracion_comb, AVG(conc_comuna) as concentracion_comuna, AVG(conc_rebote) as concentracion_rebote, 
            FROM CR2.concentracion_escenarios_w_geo
            GROUP BY EXTRACT(DATE FROM Time), {var_espacio}
        ),
        base_emision as(
            SELECT EXTRACT(DATE FROM Time) as date, {var_espacio}, 
            SUM(emi_ref) as emision_ref, SUM(emi_comb) as emision_comb, SUM(emi_comuna) as emision_comuna, SUM(emi_rebote) as emision_rebote,
            FROM CR2.emision_escenarios_w_geo
            GROUP BY EXTRACT(DATE FROM Time), {var_espacio}
        ),
        base_agrupada as(
            SELECT con.*, emi.emision_ref, emi.emision_comb, emi.emision_comuna, emi.emision_rebote
            FROM base_concentracion as con
            JOIN base_emision as emi
                ON con.{var_cruce}=emi.{var_cruce} AND con.date=emi.date
            WHERE con.region!="Región de Magallanes y Antártica Chilena" AND con.region!="Región de Coquimbo"
        ),
        base_agregada as(
        SELECT {var_espacio}, AVG(concentracion_ref) as concentracion_ref, AVG(concentracion_comb) as concentracion_comb, AVG(concentracion_comuna) as concentracion_comuna, AVG(concentracion_rebote) as concentracion_rebote, 
        AVG(emision_ref) as emision_ref, AVG(emision_comb) as emision_comb, AVG(emision_comuna) as emision_comuna, AVG(emision_rebote) as emision_rebote
        FROM base_agrupada
        GROUP BY {var_espacio}
        ),
        base_agrupada_habitantes as(
        SELECT {var_espacio}, SUM(personas) as personas
        FROM CR2.habitantes_por_comuna
        GROUP BY {var_espacio}
        ),
        base_final as(
        SELECT pm25.*, habitantes.* EXCEPT({var_espacio})
        FROM base_agregada as pm25
        JOIN base_agrupada_habitantes as habitantes
            ON pm25.{var_cruce}=habitantes.{var_cruce}
        )
        SELECT * FROM base_final'''

#     df = pandas_gbq.read_gbq(query,
#                              project_id='spike-sandbox',
#                              use_bqstorage_api=True)
#     df.rename(columns={'personas':'Número de habitantes', 
#                        'concentracion_pm25': 'Concentración',
#                         'emision_pm25':'Emisión'}, inplace=True)
#     df.to_csv(f'./data/VG_datos_resumen_{var_cruce}.csv', index=False)
    
    df = pd.read_csv(f'./data/VG_datos_resumen_{var_cruce}.csv')
    return df


def animacion(resolucion : str = 'Todas las regiones', escenario : str = 'ref', width_figuras : int = 1200):

    
    escenarios = {'ref': 'Presente', 
                   'rebote': 'E. Regional (+ efecto rebote)',
                  'comuna': 'E. Comunal',
                  'comb': 'E. Regional',}
    df_diario = cargamos_datos_resumen_diario_animacion(resolucion)
    df_diario, col_a_mirar = filtrar_por_resolucion(df_diario, resolucion, sort=False)
    df_aux = df_diario.copy()
    #df_aux = simplificar_nombre_region(df_aux)
    x = f'Emisión {escenarios[escenario]}'
    y = f'Concentración {escenarios[escenario]}'
    
    df_aux.rename(columns={f'emision_{escenario}' : x, f'concentracion_{escenario}' : y}, inplace=True)

    df_aux['día'] = df_aux['date'].apply(lambda x: x.dayofyear)
    df_aux['día'] = df_aux['día'] - df_aux['día'].min() + 1 
    df_aux.sort_values(by='día', inplace=True)
    
    df_aux['Logaritmo número de habitantes'] = np.round(np.log10(df_aux['Número de habitantes']),2)


    max_x = 1.1*df_aux[[m for m in df_aux.columns if 'Emisión' in m]].max().max()
    max_y = 1.1*df_aux[[m for m in df_aux.columns if 'Concentración' in m]].max().max()
    fig = px.scatter(df_aux,
                     x=x,
                     y=y,
                     animation_frame="día",
                     animation_group=col_a_mirar,
                     size='Logaritmo número de habitantes',
                     color=col_a_mirar,
                     hover_name=col_a_mirar,
                     hover_data=['Número de habitantes'],
                     range_x=[0,max_x],
                     range_y=[0,max_y])
        
    fig.update_layout(height=500,
                      width=width_figuras,
                      template=TEMPLATE,
                      annotations=[dict(x=1,
                                       y=-0.55,
                                       showarrow=False,
                                       text="31 de Agosto",
                                       xref="paper",
                                       yref="paper"),
                                   dict(x=0.1,
                                       y=-0.55,
                                       showarrow=False,
                                       text="1 de Mayo",
                                       xref="paper",
                                       yref="paper")])
    set_leyenda(fig, leyenda_h=True, leyenda_arriba=True)
    st.plotly_chart(fig)
    texto(''')Gráfico de dispersión que ilustra la concentración promedio diaria [μg/m³] y la emisión acumulada diaria promedio [ton/día] por región/comuna. El tamaño de cada círculo ilustra el número de habitantes por región/comuna. Tanto la emisión como la concentracion de cada día corresponden al pomedio de ese dia de los años 2015 al 2017. El número de habitantes de una región/comuna es informado al colocar el cursor sobre dicha región/comuna. La barra inferior permite ver la evolución de la dispersión para cada día entre el 1º de Mayo y el 31 de Agosto.''',14, line_height=1, color='grey')

@st.cache
def cargamos_datos_resumen_diario_animacion(resolucion):
    if resolucion=='Todas las regiones':
        var_espacio = 'region'
        var_cruce = 'region'
    else:
        var_espacio = 'comuna, region'
        var_cruce = 'comuna'

    query = f'''
        WITH  base_concentracion as(
            SELECT EXTRACT(DATE FROM Time) as date, {var_espacio}, 
            AVG(conc_ref) as concentracion_ref, AVG(conc_comb) as concentracion_comb, AVG(conc_comuna) as concentracion_comuna, AVG(conc_rebote) as concentracion_rebote, 
            FROM CR2.concentracion_escenarios_w_geo
            GROUP BY EXTRACT(DATE FROM Time), {var_espacio}
        ),
        base_emision as(
            SELECT EXTRACT(DATE FROM Time) as date, {var_espacio}, 
            SUM(emi_ref) as emision_ref, SUM(emi_comb) as emision_comb, SUM(emi_comuna) as emision_comuna, SUM(emi_rebote) as emision_rebote,
            FROM CR2.emision_escenarios_w_geo
            GROUP BY EXTRACT(DATE FROM Time), {var_espacio}
        ),
        base_agrupada as(
            SELECT con.*, emi.emision_ref, emi.emision_comb, emi.emision_comuna, emi.emision_rebote
            FROM base_concentracion as con
            JOIN base_emision as emi
                ON con.{var_cruce}=emi.{var_cruce} AND con.date=emi.date
            WHERE con.region!="Región de Magallanes y Antártica Chilena" AND con.region!="Región de Coquimbo"
        ),
        base_agregada as(
        SELECT date, {var_espacio}, AVG(concentracion_ref) as concentracion_ref, AVG(concentracion_comb) as concentracion_comb, AVG(concentracion_comuna) as concentracion_comuna, AVG(concentracion_rebote) as concentracion_rebote, 
        AVG(emision_ref) as emision_ref, AVG(emision_comb) as emision_comb, AVG(emision_comuna) as emision_comuna, AVG(emision_rebote) as emision_rebote
        FROM base_agrupada
        GROUP BY date, {var_espacio}
        ),
        base_agrupada_habitantes as(
        SELECT {var_espacio}, SUM(personas) as personas
        FROM CR2.habitantes_por_comuna
        GROUP BY {var_espacio}
        ),
        base_final as(
        SELECT pm25.*, habitantes.* EXCEPT({var_espacio})
        FROM base_agregada as pm25
        JOIN base_agrupada_habitantes as habitantes
            ON pm25.{var_cruce}=habitantes.{var_cruce}
        )
        SELECT * FROM base_final'''

#     df = pandas_gbq.read_gbq(query,
#                              project_id='spike-sandbox',
#                              use_bqstorage_api=True)
#     df.rename(columns={'personas':'Número de habitantes', 
#                        'concentracion_pm25': 'Concentración',
#                         'emision_pm25':'Emisión'}, inplace=True)
#     df.to_csv(f'./data/VG_datos_animacion_{var_cruce}.cvs', index=False)
    
    df = pd.read_csv(f'./data/VG_datos_animacion_{var_cruce}.cvs')
    df['date'] = df['date'].apply(pd.to_datetime)
    return df

# LOGOS
def plot_logo_cr2():
    st.sidebar.markdown(
        "<br>"
        '<div style="text-align: center;">'
        '<a href="http://www.cr2.cl/"> '
        '<img src="https://raw.githubusercontent.com/SpikeLab-CL/calidad_aire_2050_cr2/master/logo/logo_CR2_plataforma.png" width=240>'
        " </img>"
        "</a> </div>",
        unsafe_allow_html=True,
    )
    
    
def plot_logo_spike():
    st.sidebar.markdown(
        "<br>"
        '<div style="text-align: center;">'
        '<a href="http://www.spikelab.xyz/"> '
        '<img src="https://raw.githubusercontent.com/SpikeLab-CL/calidad_aire_2050_cr2/master/logo/logo_con_caption.png" width=150>'
        " </img>"
        "</a> </div>",
        unsafe_allow_html=True,
    )
    
    

def texto(texto : str = 'holi',
          nfont : int = 16,
          color : str = 'black',
          line_height : float =None,
          sidebar: bool = False):
    
    if sidebar:
        st.sidebar.markdown(
                body=generate_html(
                    text=texto,
                    color=color,
                    font_size=f"{nfont}px",
                    line_height=line_height
                ),
                unsafe_allow_html=True,
                )
    else:
        st.markdown(
        body=generate_html(
            text=texto,
            color=color,
            font_size=f"{nfont}px",
            line_height=line_height
        ),
        unsafe_allow_html=True,
        )
    

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

def max_width_(width=1000):
    max_width_str = f"max-width: {width}px;"
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
def plot_logo_pagina():
    st.sidebar.markdown(
        "<br>"
        '<div style="text-align: center;">'
        '<a href="http://www.cr2.cl/"> '
        '<img src="https://raw.githubusercontent.com/SpikeLab-CL/calidad_aire_2050_cr2/master/logo/logo_plataforma.png" width=300>'
        " </img>"
        "</a> </div>",
        unsafe_allow_html=True,
    )

    
    
# def load_diccionario_regiones():
#     diccionario_regiones = {10:'Los Lagos',
#     11:'Aysen',
#     13:'Metropolitana',
#     14:'Los Ríos',
#     16:'Ñuble',
#     4:'Coquimbo',
#     5:'Valparaíso',
#     6:'Libertador BOhiggins',
#     7:'Maule',
#     8:'Biobío',
#     9:'Araucanía'}
#     return diccionario_regiones

# def ploteamos_datos_resumen_separados(df, resolucion, version=''):
#     st.markdown(f'**Gráficos de barra {version}**')    
#     _df, col_a_mirar = filtrar_por_resolucion(df, resolucion)
    
#     # ploteamos
#     fig = make_subplots(rows=2, cols=1,
#                         subplot_titles=("Concentraciones [?]", "Emisiones [?]",))
    
#     fig.add_trace(go.Bar(x=_df[col_a_mirar], y=_df.concentracion_pm25, name='concentración'),
#                   row=1, col=1)
#     fig.add_trace(go.Bar(x=_df[col_a_mirar], y=_df.emision_pm25, name='emisión',),
#                   row=2, col=1)
#     fig.update_layout(height=700, width=900,
#                       legend=dict(x=0, y=1.1,orientation="h"),
#                       template=TEMPLATE)
#     st.plotly_chart(fig, use_container_width=False)
    