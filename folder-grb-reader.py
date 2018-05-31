import requests
import psycopg2
import datetime,time
import os
import pandas as pd
import numpy as np
import math
import sys
from grb import gribReader

ICE_DATA_LOCATION =  'testdata/'
MIN_LAT = 64

def connect():
    try:
        connect_str = "dbname='iceml' user='iceml' host='localhost' password='WinterNavigation'"
        conn = psycopg2.connect(connect_str)
        return conn
    except Exception as e:
        print("Db connection failed")
        print(e)

def timeString(timeStamp):
    return timeStamp.replace(tzinfo=datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]+'Z'

def geographyPoint(lon, lat):
    return "ST_GeogFromText('SRID=4326;POINT({} {})')".format(lon, lat)

def getWeatherfiles():
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT name FROM weatherfile ORDER BY name;")
    return cur.fetchall()

def writeFile(conn, cursor, filename):
    sql = "insert into weatherfile (name, loadtime) values ('{}', current_timestamp)".format(filename)
    cursor.execute(sql)
    conn.commit()

def writeIceData(conn, cursor, grb):
    results = []
    for index, row in grb.iterrows():
        results.append(writeFeature(row, cursor))

    writeCount = sum(results)
    conn.commit()
    print("Wrote positions: handled={} wrote={}".format(len(grb), writeCount))


def writeFeature(feature, cursor):
    timeStamp = feature["timestamp"]
    lon = feature["lon"]
    lat = feature["lat"]
    concentration = feature["concentration(%)"]
    speed = feature["speed(m/s)"]
    direction = feature["direction(deg)"]
    thickness = feature["thickness(m)"]
    if lat >= MIN_LAT:
        sql = """INSERT INTO ice (timestamp, location, concentration, speed, direction, thickness)
                  VALUES ('{}', {}, {}, {}, {}, {})
                  ON conflict ON CONSTRAINT ice_pkey DO UPDATE 
                  SET concentration = EXCLUDED.concentration, speed = EXCLUDED.speed, direction = EXCLUDED.direction, thickness = EXCLUDED.thickness
                  """.format(timeString(timeStamp), geographyPoint(lon,lat), nanToNull(concentration), nanToNull(speed), nanToNull(direction), nanToNull(thickness))
        cursor.execute(sql)
        return (True)
    else:
        return (False)

def nanToNull(value):
    if math.isnan(value):
        return 'null'
    return value

conn = connect()
cursor = conn.cursor()

fileTuples = getWeatherfiles()
files = list(map(lambda x: ''.join(x), fileTuples))
grbs =  list(filter(lambda x: x.endswith(".grb") or x.endswith(".grb2"), os.listdir(ICE_DATA_LOCATION)))

for filename in grbs:
    if(filename not in files):
        try:
            grb = gribReader.parse_grib(ICE_DATA_LOCATION+filename, forecastAgeLimit=8, minLat=MIN_LAT)
            writeIceData(conn, cursor, grb)
            writeFile(conn, cursor, filename)
            print("Processed file={}".format(filename))
        except ValueError:
            print("Error while processing file:", sys.exc_info()[0])
    else:
        print("File {} already read.".format(filename))