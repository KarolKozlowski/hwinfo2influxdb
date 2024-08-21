"""
HWiNFO to influxDB 2
Revision 1.10 21/08/2024

## Python Dependancies
pip install influxdb_client

## Other Depenendencices
Remote Sensor Monitor
https://www.hwinfo.com/forum/threads/introducing-remote-sensor-monitor-a-restful-web-server.1025/

HWiNFO PRO
You must have HWiNFO pro - as the normal HWiNFO only gives shared memory support for 12 hrs and then resets.
This is not an issue but it means that you have to constantly enable it every 12hrs and restart the Remote Sensor Monitor below.

"""

import os
import sys
import time
import datetime
import requests

from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client.client.exceptions import InfluxDBError
from simplejson.errors import JSONDecodeError


def check_env_var(variable, default=None):
    """Function verifying presence of env variables."""
    if variable in os.environ:
        return_val = os.environ[variable]
    else:
        if default:
            return_val = default
        else:
            print(datetime.datetime.now(), f"Environment variable {variable} missing.")

    return return_val

# InfluxDB Database Details
token = check_env_var('INFLUX_TOKEN')
org = check_env_var('INFLUX_ORG')
bucket = check_env_var('INFLUX_BUCKET')
db_url = check_env_var('INFLUX_URL')

# Variables of PC
sample_time = int(check_env_var('SAMPLE_TIME', 30))
poll_ip = check_env_var('HWINFO_API')
device_id = check_env_var('DEVICE_NAME')

def init():
    """Function checking availability of data server."""
    try:
        hwinfo = requests.get(poll_ip, timeout=10)
        status_code = hwinfo.status_code
        print(datetime.datetime.now(), f"Remote Sensor Monitor is reachable (HTTP:{status_code}).")
    except requests.ConnectionError:
        print(datetime.datetime.now(), "Unable to conact Remote Sensor Moniter web server. Check both Remote Sensor Moniter and HWiNFO are running.")
        sys.exit()


def poll(retry_time):
    """Function polling data server."""

    poll_start = time.monotonic()

    while start + retry_time > time.monotonic():
        try:
            hwinfo_web_data = requests.get(poll_ip, timeout=10)
        except requests.ConnectionError:
            print(datetime.datetime.now(), " Error! Unable to conact Remote Sensor Moniter web server. Check both Remote Sensor Moniter and HWiNFO are running.")
            sys.exit()

        try:
            data = hwinfo_web_data.json()
            return data
        except AssertionError as error:
            print(datetime.datetime.now(), error)
            sys.exit()
        except JSONDecodeError as error:
            polling_time = time.monotonic() - poll_start
            print(datetime.datetime.now(), f"Could not fetch data (polling time: {polling_time:.2f}/{retry_time}): ", error)
            time.sleep(2)
            continue

    return None

def process_data(api, data):
    """Function processing polled data."""
    for measurement in data:
        sensorclass = measurement['SensorClass']
        sensorname = measurement['SensorName']
        sensorvalue = measurement['SensorValue']

        # Sanitize sensor class
        sensorclass = sensorclass.replace(" ", "_")

        # Sanitize sensor values
        sensorvalue = sensorvalue.replace(',', '.')

        # Sanitize sensor names
        sensorname = sensorname.replace(",", r"\,")
        sensorname = sensorname.replace(" ", "_")

        #parse to format accepted by influxDB
        influxdata = str(device_id+",Measurement=" + sensorclass+" "+str(sensorname)+"="+str(sensorvalue))

        #Write to influxDB
        try:
            api.write(bucket, org, influxdata)
        except InfluxDBError as err:
            print(datetime.datetime.now(), " Error! Could not write to database:", err)
            print(f"Sensor name: `{sensorname}`")
            print(f"Sensor value: `{sensorvalue}`")
            return
    print(datetime.datetime.now(), "Successfully posted data to server.")


print(datetime.datetime.now(), "starting....")

init()

client = InfluxDBClient(url=db_url, token=token)
write_api = client.write_api(write_options=SYNCHRONOUS)

while True:
    start = time.monotonic()

    poll_retry_time = sample_time - 2
    poll_data = poll(poll_retry_time)

    if poll_data:
        process_data(write_api, poll_data)
    else:
        print(datetime.datetime.now(), "Data could not be processed (missing).")
    stop = time.monotonic()

    processing_time = stop - start
    wait_time = sample_time - processing_time

    if sample_time > processing_time:
        print(datetime.datetime.now(), f"Processing completed in {processing_time:.2f}s, waiting for: {wait_time:.2f}s.")
        time.sleep(sample_time - processing_time)
    else:
        print(datetime.datetime.now(), "Processing took longer than sample timing.")
