FROM python:3.12.5-alpine3.20

WORKDIR /usr/src/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY hwinfo2influxdb.py .

CMD [ "python", "hwinfo2influxdb.py" ]
