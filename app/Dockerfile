FROM python:3.7

WORKDIR /root
RUN mkdir /root/app

COPY requirements.txt /root/app/requirements.txt
RUN pip install -r /root/app/requirements.txt

COPY app.py /root/app/app.py
COPY utils.py /root/app/utils.py
COPY run.sh /root/app/run.sh
COPY spike-sandbox-985f44341d26.json /root/app/spike-sandbox-985f44341d26.json

ENV GOOGLE_APPLICATION_CREDENTIALS /root/app/spike-sandbox-985f44341d26.json

EXPOSE 8080

CMD ["sh", "/root/app/run.sh"]