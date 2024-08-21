#!/bin/bash

# InfluxDB configuration
export INFLUX_TOKEN="XXX_INFLUX_TOKEN_XXX"
export INFLUX_ORG="example.org"
export INFLUX_BUCKET="hwinfo"
export INFLUX_URL="https://influxdb.example.org"

# PC configuration
export SAMPLE_TIME=30 # in seconds
export HWINFO_API="http://hwinfo.example.org:55555"
export DEVICE_NAME="hwinfo-host"

python3 hwinfo2influxdb.py
