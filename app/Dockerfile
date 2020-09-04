FROM python:3.7

WORKDIR /root
RUN mkdir /root/app

COPY requirements.txt /root/app/requirements.txt
RUN pip install -r /root/app/requirements.txt

COPY app.py /root/app/app.py
COPY utils.py /root/app/utils.py
COPY run.sh /root/app/run.sh
COPY spike-sandbox-985f44341d26.json /root/app/spike-sandbox-985f44341d26.json
COPY CE_datos_comparar_escenarios_ciclo_diario_comuna.csv /root/app/CE_datos_comparar_escenarios_ciclo_diario_comuna.csv
COPY CE_datos_comparar_escenarios_ciclo_diario_region.csv /root/app/CE_datos_comparar_escenarios_ciclo_diario_region.csv
COPY CE_datos_comparar_escenarios_comuna.csv /root/app/CE_datos_comparar_escenarios_comuna.csv
COPY CE_datos_comparar_escenarios_region.csv /root/app/CE_datos_comparar_escenarios_region.csv
COPY MP_mapa_agregacion_comuna_from_2015-05-01_to_2015-05-31.csv /root/app/MP_mapa_agregacion_comuna_from_2015-05-01_to_2015-05-31.csv
COPY MP_mapa_agregacion_comuna_from_2015-05-01_to_2015-08-31.csv /root/app/MP_mapa_agregacion_comuna_from_2015-05-01_to_2015-08-31.csv
COPY MP_mapa_agregacion_comuna_from_2015-06-01_to_2015-06-30.csv /root/app/MP_mapa_agregacion_comuna_from_2015-06-01_to_2015-06-30.csv
COPY MP_mapa_agregacion_comuna_from_2015-07-01_to_2015-07-31.csv /root/app/MP_mapa_agregacion_comuna_from_2015-07-01_to_2015-07-31.csv
COPY MP_mapa_agregacion_comuna_from_2015-08-01_to_2015-08-31.csv /root/app/MP_mapa_agregacion_comuna_from_2015-08-01_to_2015-08-31.csv
COPY MP_mapa_agregacion_region_from_2015-05-01_to_2015-05-31.csv /root/app/MP_mapa_agregacion_region_from_2015-05-01_to_2015-05-31.csv
COPY MP_mapa_agregacion_region_from_2015-05-01_to_2015-08-31.csv /root/app/MP_mapa_agregacion_region_from_2015-05-01_to_2015-08-31.csv
COPY MP_mapa_agregacion_region_from_2015-06-01_to_2015-06-30.csv /root/app/MP_mapa_agregacion_region_from_2015-06-01_to_2015-06-30.csv
COPY MP_mapa_agregacion_region_from_2015-07-01_to_2015-07-31.csv /root/app/MP_mapa_agregacion_region_from_2015-07-01_to_2015-07-31.csv
COPY MP_mapa_agregacion_region_from_2015-08-01_to_2015-08-31.csv /root/app/MP_mapa_agregacion_region_from_2015-08-01_to_2015-08-31.csv
COPY ST_series_ciclo_diario_comuna.csv /root/app/ST_series_ciclo_diario_comuna.csv
COPY ST_series_ciclo_diario_region.csv /root/app/ST_series_ciclo_diario_region.csv
COPY ST_series_ciclo_semanal_comuna.csv /root/app/ST_series_ciclo_semanal_comuna.csv
COPY ST_series_ciclo_semanal_region.csv /root/app/ST_series_ciclo_semanal_region.csv
COPY ST_series_completas_comuna.csv /root/app/ST_series_completas_comuna.csv
COPY ST_series_completas_region.csv /root/app/ST_series_completas_region.csv
COPY VG_datos_resumen_comuna.csv /root/app/VG_datos_resumen_comuna.csv
COPY VG_datos_resumen_region.csv /root/app/VG_datos_resumen_region.csv

ENV GOOGLE_APPLICATION_CREDENTIALS /root/app/spike-sandbox-985f44341d26.json

EXPOSE 8080

CMD ["sh", "/root/app/run.sh"]