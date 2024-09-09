FROM python:3.12.6-alpine3.20

WORKDIR /usr/src/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY hwinfo2influxdb.py .

CMD [ "python", "-u", "hwinfo2influxdb.py" ]
