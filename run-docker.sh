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

# build latest docker timage
docker build . -t hwinfo2influxdb

# run it
docker run -it \
  -e INFLUX_TOKEN="${INFLUX_TOKEN}" \
  -e INFLUX_ORG="${INFLUX_ORG}" \
  -e INFLUX_BUCKET="${INFLUX_BUCKET}" \
  -e INFLUX_URL="${INFLUX_URL}" \
  -e SAMPLE_TIME=${SAMPLE_TIME} \
  -e HWINFO_API="${HWINFO_API}" \
  -e DEVICE_NAME="${DEVICE_NAME}" \
  hwinfo2influxdb
