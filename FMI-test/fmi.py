import logging
import requests
import xmltodict
from datetime import datetime
import time
from datetime import timedelta
#import pygrib

def getDownloadMetaData(apikey, timestep, datastep, forecastHoursToFuture, parameters, bbox):
    try:
    	now = datetime.now()
    	starttime = now.strftime("%Y-%m-%dT%H:00:00Z")
    	end = now + timedelta(hours=forecastHoursToFuture)
    	endtime = end.strftime("%Y-%m-%dT%H:00:00Z")
    	location_url = "http://data.fmi.fi/wfs?fmi-apikey={}&request=GetFeature&storedquery_id=fmi::forecast::helmi::grid&timestep={}&scalefactor=1000&datastep={}&starttime={}&endtime={}&parameters={}&bbox={}".format(apiKey, timestep, datastep, starttime, endtime, parameters, bbox)
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
        fileReferenceIndex = len(list(doc['wfs:FeatureCollection']['wfs:member']))-1
        downloadUrl = doc['wfs:FeatureCollection']['wfs:member'][fileReferenceIndex]['omso:GridSeriesObservation']['om:result']['gmlcov:RectifiedGridCoverage']['gml:rangeSet']['gml:File']['gml:fileReference']

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
parameters = "icespeed,icedirection,iceconcentration,icethickness,meanicethickness"
apiKey = ""
forecastHoursToFuture = 6
datastep = "2"
bbox = "16,57,30.3,66.5"
timestep = "60"
delay = 6*60*60

while True:
	data = getDownloadMetaData(apiKey, timestep, datastep, forecastHoursToFuture, parameters, bbox)
	grib = getGrib(data)
	now = datetime.now()
	date_var = now.strftime("%Y-%m-%dT%H-%M-%S")
	filepath = "/Users/villehak/Work/iceML/ice-data/icedata_{}_next_{}hours.grb2".format(date_var, forecastHoursToFuture)
	with open(filepath, mode='wb') as localfile:
		localfile.write(grib)
	print("Saved file. filepath={}".format(filepath))
	print("Waiting for {} hours".format(delay/60/60))
	time.sleep(6*60*60)
