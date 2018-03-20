import logging
import requests
import xmltodict

def getXmlData(apikey, timestep, datastep, forecastHoursToFuture, parameters, bbox):
	try:
		location_url = "http://data.fmi.fi/wfs?fmi-apikey={}&request=GetFeature&storedquery_id=fmi::forecast::helmi::surface::array&timestep={}&scalefactor=1000&datastep={}&endtime=after+{}+hours&parameters={}&bbox={}".format(apiKey, timestep, datastep, forecastHoursToFuture, parameters, bbox)
		print("GET: url=" + location_url)
		response = requests.get(url=location_url)
		data = response.content
		print("GET Result: code={}".format(response.status_code))
		return data
	except:
		logger.error("Error while fetching ice data")

def parseXmlData(data):
	try:
		#print(data)
		doc = xmltodict.parse(data)
		lonMin = float(doc['Products']['Grid']['@LonMin'])
		latMin = float(doc['Products']['Grid']['@LatMin'])
		lonMax = float(doc['Products']['Grid']['@LonMax'])
		latMax = float(doc['Products']['Grid']['@LatMax'])
		xDims = int(doc['Products']['Grid']['@GridXDim'])
		yDims = int(doc['Products']['Grid']['@GridYDim'])
		xStep = (lonMax - lonMin) / (xDims - 1)
		yStep = (latMax - latMin) / (yDims - 1)

		print(xDims*yDims)

		for product in doc['Products']['Product']['Time']:
			processGrid(latMin, lonMin, yStep, xStep, product)


		#print(doc['Time'])
	except:
		logger.error("Error while parsing ice xml")

def processGrid(startLat, startLon, yStep, xStep, data):
	try:
		grid = [int(x) for x in data['Data']['IntegerArray'].split()]
		time = data['@Time']
		scaleFactor = data['Data']['@ScalingFactor']
		nullValue = data['Data']['@NullValue']
		product = data['Data']['@Parameter']
		print("Grid size={}, product={}, time={}, scaleFactor={}, nullValue={}".format(len(grid), product, time, scaleFactor, nullValue))
		#print(grid)
	except:
		logger.error("Error while processing ice grid")

logger = logging.getLogger()
logger.setLevel(logging.INFO)
parameters = "icespeed,icedirection"
apiKey = "5761aae0-2f02-4c9c-b3c8-d2500c6f05cc"
forecastHoursToFuture = "6"
datastep = "4"
bbox = "17,60,22,63.9"
timestep = "180"

data = getXmlData(apiKey, timestep, datastep, forecastHoursToFuture, parameters, bbox)
parseXmlData(data)