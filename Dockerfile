FROM python:3.9.19

WORKDIR /usr/src/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY hwinfo2influxdb.py .

CMD [ "python", "hwinfo2influxdb.py" ]
