#HWiNFO to influxDB 2
#Revision 1.00 28/04/2022

####Python Dependancies
#pip install influxdb_client

###Other Depenendencices
#Remote Sensor Monitor
#https://www.hwinfo.com/forum/threads/introducing-remote-sensor-monitor-a-restful-web-server.1025/

#HWiNFO PRO
#You must have HWiNFO pro - as the normal HWiNFO only gives shared memory support for 12 hrs and then resets.
#This is not an issue but it means that you have to constantly enable it every 12hrs and restart the Remote Sensor Monitor below.


####################################################################################################
# Import modules
####################################################################################################

import os
import requests
import time
from datetime import datetime
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from simplejson.errors import JSONDecodeError


####################################################################################################
# Variables to Set
####################################################################################################

def check_env_var(variable, default=None):
    if variable in os.environ:
        return os.environ[variable]
    else:
        if default:
            return default
        else:
            print(datetime.now(), "Environment variable {} missing.".format(variable))

# InfluxDB Database Details
token = check_env_var('INFLUX_TOKEN')
org = check_env_var('INFLUX_ORG')
bucket = check_env_var('INFLUX_BUCKET')
db_url = check_env_var('INFLUX_URL')

# Variables of PC
sample_time = int(check_env_var('SAMPLE_TIME', 30))
poll_ip = check_env_var('HWINFO_API')
device_id = check_env_var('DEVICE_NAME')

####################################################################################################
#Functions start here
####################################################################################################

#test html webserver is up
def init():
    try:
        hwinfo = requests.get(poll_ip)
        print(datetime.now(), "Remote Sensor Monitor is reachable")
    except:
        print(datetime.now(), "Unable to conact Remote Sensor Moniter web server. Check both Remote Sensor Moniter and HWiNFO are running.")
        exit()


#####Polling function
def poll(write_api, retries):
    for i in range(1, retries):
        try:
            hwinfo_web_data = requests.get(poll_ip)
        except:
            print(datetime.now(), " Error! Unable to conact Remote Sensor Moniter web server. Check both Remote Sensor Moniter and HWiNFO are running.")
            exit()

        try:
            data = hwinfo_web_data.json()
            return data
        except AssertionError as error:
            print(datetime.now(), error)
            exit()
        except JSONDecodeError as error:
            print(datetime.now(), "Could not fetch data (try: {}/{}): ".format(i, retries), error)
            time.sleep(1)
            continue

#########Process data
def process_data(write_api, data):
    for a in data:
        sensorclass = a['SensorClass']
        sensorname = a['SensorName']
        sensorvalue = a['SensorValue']

        # Sanitize sensor class
        sensorclass = sensorclass.replace(" ", "_")

        # Sanitize sensor values
        sensorvalue = sensorvalue.replace(',', '.')

        # Sanitize sensor names
        sensorname = sensorname.replace(",", "\,")
        sensorname = sensorname.replace(" ", "_")

        #parse to format accepted by influxDB
        influxdata = str(device_id+",Measurement=" + sensorclass+" "+str(sensorname)+"="+str(sensorvalue))

        #Write to influxDB
        try:
            write_api.write(bucket, org, influxdata)
        except Exception as err:
            print(datetime.now(), " Error! Could not write to database:", err)
            print("Sensor name: `{}`".format(sensorname))
            print("Sensor value: `{}`".format(sensorvalue))
            return
    print(datetime.now(), "Successfully posted data to server.")

####################################################################################################
# Main Script Starts here
####################################################################################################
print(datetime.now(), "starting....")

init()

client = InfluxDBClient(url=db_url, token=token)
write_api = client.write_api(write_options=SYNCHRONOUS)

while True:
    start = time.monotonic()

    retries = sample_time - 5
    data = poll(write_api, retries)

    if data:
        process_data(write_api, data)
    else:
        print(datetime.now(), "Data could not be processed (missing).")
    stop = time.monotonic()

    processing_time = stop - start

    if (sample_time > processing_time):
        print(datetime.now(), "Processing completed in {:.2f}s, waiting for: {:.2f}s.".format(processing_time, sample_time - processing_time))
        time.sleep(sample_time - processing_time)
    else:
        print(datetime.now(), "Processing took longer than sample timing.")

