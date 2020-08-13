import pandas as pd
import numpy as np
import streamlit as st
from utils import *

def get_descripciones():
    
    descripciones = {
        'CO': """El monóxido de carbono, también denominado óxido de carbono (II), gas carbonoso y anhídrido carbonoso (los dos últimos cada vez más en desuso), cuya fórmula química es CO, es un gas incoloro y altamente tóxico. Puede causar la muerte cuando se respira en niveles elevados. Se produce por la combustión deficiente de sustancias como gas, gasolina, queroseno, carbón, petróleo, tabaco o madera. Las chimeneas, las calderas, los calentadores de agua o calefactores y los aparatos domésticos que queman combustible, como las estufas u hornillas de la cocina o los calentadores a queroseno, también pueden producirlo si no están funcionando bien. Los vehículos con el motor encendido también lo despiden3​4​. Grandes cantidades de CO se forman como subproducto durante los procesos oxidativos para la producción de productos químicos, lo que hace necesaria la purificación de los gases residuales. Por otro lado, se están realizando considerables esfuerzos de investigación para desarrollar nuevos procesos5​ y catalizadores para la maximización de la producción del producto útil. También se puede encontrar en las atmósferas de las estrellas de carbono.""",
                     
        'NH3': """El amoníaco, amoniaco, azano, espíritu de Hartshorn, trihidruro de nitrógeno o gas de amonio es un compuesto químico de nitrógeno con la fórmula química NH3. Es un gas incoloro con un característico olor repulsivo. El amoníaco contribuye significativamente a las necesidades nutricionales de los organismos terrestres por ser un precursor de fertilizantes. Directa o indirectamente, el amoníaco es también un elemento importante para la síntesis de muchos fármacos y es usado en diversos productos comerciales de limpieza. Pese a su gran uso, el amoníaco es cáustico y peligroso. La producción industrial del amoníaco en 2012 fue de 198 000 000 toneladas, lo que equivale a un 35 % de incremento con respecto al año 2006, con 146 500 000 toneladas. 
El NH3 hierve a los -33.34 ℃ a una presión de una atmósfera, esto ayuda a que pueda conservarse en estado líquido, bajo presión a temperaturas bajas. Sin embargo, a temperaturas mayores a 405.5 K (temperatura crítica) ningún aumento en la presión producirá la condensación de este gas. Si la presión aumenta por encima del valor crítico de 111.5 atm, cualquier aumento por encima de este valor aumenta la compresión de las moléculas del gas, pero no se forma una fase líquida definida. El amoníaco casero o hidróxido de amonio (NH4OH), es una solución de NH3 en agua. La concentración de dicha solución es medida en unidades de la Escala Baumé, con 26 grados baumé (cerca del 30 % por peso de amoníaco) como concentración típica del producto comercial.""",
        
        'NO': """El óxido de nitrógeno (II), óxido nítrico o monóxido de nitrógeno (NO). Es un gas incoloro y soluble en agua, presente en pequeñas cantidades en los mamíferos. Está también extendido por el aire siendo producido en automóviles y plantas de energía.
No debe confundirse con el óxido nitroso (N2O), con el dióxido de nitrógeno (NO2) o con cualquiera del resto de los óxidos de nitrógeno existentes.
Es una molécula altamente inestable en el aire ya que se oxida rápidamente en presencia de oxígeno convirtiéndose en dióxido de nitrógeno. Por esta razón se le considera también como un radical libre.
""",
        
        'NO2': """El dióxido de nitrógeno u óxido de nitrógeno (IV) (NO2), es un compuesto químico formado por los elementos nitrógeno y oxígeno, uno de los principales contaminantes entre los varios óxidos de nitrógeno.
El dióxido de nitrógeno es de color marrón-amarillento. Se forma como subproducto en los procesos de combustión a altas temperaturas, como en los vehículos motorizados y las plantas eléctricas. Por ello es un contaminante frecuente en zonas urbanas.
Es un gas tóxico, irritante y precursor de la formación de partículas de nitrato. Estas llevan a la producción de ácido y elevados niveles de PM-2.5 en el ambiente. Afecta principalmente al sistema respiratorio.""",
        
        'NOX': """El término (NxOy) se aplica a varios compuestos químicos binarios gaseosos formados por la combinación de oxígeno y nitrógeno. El proceso de formación más habitual de estos compuestos inorgánicos es la combustión a altas temperaturas, proceso en el cual habitualmente el aire es el comburente.
        El monóxido de nitrógeno es un gas a temperatura ambiente de olor dulce penetrante, fácilmente oxidable a dióxido de nitrógeno. Mientras que el dióxido de nitrógeno tiene un fuerte olor desagradable. El dióxido de nitrógeno es un líquido a temperatura ambiente, pero se transforma en un gas pardo-rojizo a temperaturas sobre los 21 °C.
El nitrógeno diatómico gaseoso al estar formado por un enlace triple, es muy poco reactivo, pero en las combustiones llevadas a cabo a altas temperaturas, el nitrógeno logra reaccionar con el oxígeno (que es muy reactivo) formando diversos tipos de óxidos de nitrógeno.
Los óxidos de nitrógeno son liberados al aire desde los tubos de escape de vehículos motorizados (sobre todo diésel y de mezcla pobre), de la combustión del carbón, petróleo o gas natural, y durante procesos tales como la soldadura por arco, galvanoplastia, grabado de metales y detonación de dinamita. También son producidos comercialmente al hacer reaccionar el ácido nítrico con metales o con celulosa.
Los óxidos de nitrógeno también se generan en la naturaleza, siendo las causas más frecuentes los incendios forestales, la actividad volcánica y la descomposición bacteriana de determinados nitratos.""",
        
        'O3': """El ozono (O3) es una sustancia cuya molécula está compuesta por tres átomos de oxígeno, formada al disociarse los dos átomos que componen el gas oxígeno. Cada átomo de oxígeno liberado se une a otra molécula de oxígeno gaseoso (O2), formando moléculas de ozono (O3).
A temperatura y presión ambientales, el ozono es un gas que desprende olores fuertes (similar al de los mariscos en estado de descomposición avanzado) y generalmente sin coloración, pero en grandes concentraciones puede volverse ligeramente azulado. Si se respira en grandes cantidades puede provocar una irritación en los ojos o la garganta, la cual suele pasar después de respirar aire fresco y rico en oxígeno durante algunos minutos.""",
        
        'PM10': """Se denomina PM10 (del inglés Particulate Matter) a pequeñas partículas sólidas o líquidas de polvo, cenizas, hollín, partículas metálicas, cemento o polen, dispersas en la atmósfera, y cuyo diámetro aerodinámico es menor que 10 µm (1 micrómetro corresponde la milésima parte de 1 milímetro). Están formadas principalmente por compuestos inorgánicos como silicatos y aluminatos, metales pesados entre otros, y material orgánico asociado a partículas de carbono (hollín).
La contaminación atmosférica por material particulado es la alteración de la composición natural de la atmósfera como consecuencia de la entrada en suspensión de partículas, ya sea por causas naturales o por la acción del hombre (causas antropogénicas).""",
        
         'PM25': """Se denomina PM25 (del inglés Particulate Matter) a pequeñas partículas dispersas en la atmósfera, y cuyo diámetro aerodinámico es menor que 2.5 µm (1 micrómetro corresponde la milésima parte de 1 milímetro).""",
        
        'SO2': """El dióxido de azufre, u óxido de azufre (IV), es un óxido cuya fórmula molecular es SO2. Es un gas incoloro con un característico olor irritante. Se trata de una sustancia reductora que, con el tiempo, el contacto con el aire y la humedad, se convierte en trióxido de azufre. La velocidad de esta reacción en condiciones normales es baja.
En agua se disuelve formando una disolución ácida. Puede ser concebido como el anhidruro de un hipotético ácido sulfuroso (H2SO3). Esto —en analogía a lo que pasa con el ácido carbónico— es inestable en disoluciones ácidas pero forma sales, los sulfitos y hidrogenosulfitos.
El dióxido de azufre es el principal causante de la lluvia ácida ya que en la atmósfera es transformado en ácido sulfúrico.
Es liberado en muchos procesos de combustión ya que los combustibles como el carbón, el petróleo, el diésel o el gas natural contienen ciertas cantidades de compuestos azufrados. Por estas razones se intenta eliminar estos compuestos antes de su combustión por ejemplo mediante la hidrodesulfuración en los derivados del petróleo o con lavados del gas natural haciéndolo más "dulce"."""}   

    return descripciones
                    
def get_descripcion(emision):
    descripciones = get_descripciones()
    return  st.sidebar.markdown(
        body=generate_html(
            text=descripciones[emision] +' Fuente Wikipedia',
            color="gray",
            font_size="12px",
        ),
        unsafe_allow_html=True,
    )

    
    