import logging
import requests
import xmltodict
from datetime import datetime
#import pygrib

def getDownloadMetaData(apikey, timestep, datastep, forecastHoursToFuture, parameters, bbox):
    try:
        location_url = "http://data.fmi.fi/wfs?fmi-apikey={}&request=GetFeature&storedquery_id=fmi::forecast::helmi::grid&timestep={}&scalefactor=1000&datastep={}&endtime=after+{}+hours&parameters={}&bbox={}".format(apiKey, timestep, datastep, forecastHoursToFuture, parameters, bbox)
        print("GET: url=" + location_url)
        response = requests.get(url=location_url)
        data = response.content
        print("GET Result: code={}".format(response.status_code))
        return data
    except:
        logger.error("Error while fetching ice download metadata")

def getGrib(data):
    try:
        #print(data)
        doc = xmltodict.parse(data)
        downloadUrl = doc['wfs:FeatureCollection']['wfs:member'][0]['omso:GridSeriesObservation']['om:result']['gmlcov:RectifiedGridCoverage']['gml:rangeSet']['gml:File']['gml:fileReference']

        print("GET: url=" + downloadUrl)
        response = requests.get(url=downloadUrl)
        grib = response.content
        print("GET Result: code={}".format(response.status_code))

        return grib

        #print(doc['Time'])
    except:
        logger.error("Error while fetching ice grib")


logger = logging.getLogger()
logger.setLevel(logging.INFO)
parameters = "icespeed,icedirection"
apiKey = ""
forecastHoursToFuture = "6"
datastep = "4"
bbox = "17,60,25,65"
timestep = "180"

data = getDownloadMetaData(apiKey, timestep, datastep, forecastHoursToFuture, parameters, bbox)
grib = getGrib(data)
now = datetime.now()
date_var = now.strftime("%Y-%m-%dT%H-%M-%S")
with open("/Users/villehak/Work/iceML/ice-data/icedata_{}.grb2".format(date_var), mode='wb') as localfile:
	localfile.write(grib)
