import datetime
import geopy.distance

DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

def filterByLocation(iceData, latField, lonField, lat, lon, km):
    # 0.01 is a rough estimate of one kilometer in lat in norhern latitudes
    # 0.02 is a rough estimate of one kilometer in lon in norhern longitudes
    iceData = iceData.loc[(iceData[latField] > (lat - km * 0.01)) & (iceData[latField] < (lat + km * 0.01))
                        & (iceData[lonField] > (lon - km * 0.02)) & (iceData[lonField] < (lon + km * 0.02))]
    return iceData

def filterByTime(points, timeField, time, hours):
    time = time.split(".")[0]
    d = datetime.datetime.strptime(time, DATE_FORMAT)
    starttime = d - datetime.timedelta(hours=hours)
    endtime = d + datetime.timedelta(hours=hours)
    return points.loc[(points[timeField] > starttime) & (points[timeField] < endtime)]

def findNearestIcePoint(timeField,latField, lonField, timestamp, lat, lon, iceData, hours):
    iceData = filterByLocation(iceData, latField, lonField, lat, lon, hours)
    iceData = filterByTime(iceData, timeField, timestamp, 20)
    return getclosest(latField, lonField, lat, lon, iceData)

def getclosest(latField, lonField, lat, lon, iceData):
    if len(iceData) == 0:
        return iceData

    coords_1 = (lat, lon)
    coords_2 = (iceData.head(1)[latField].iloc[0], iceData.head(1)[lonField].iloc[0])

    smallestDistance = geopy.distance.vincenty(coords_1, coords_2).km
    closestIndex = iceData.head(1).index[0]
    for index, row in iceData.iterrows():
        coords_2 = (row[latField], row[lonField])
        distance = geopy.distance.vincenty(coords_1, coords_2).km

        if distance < smallestDistance:
            smallestDistance = distance
            closestIndex = index

    return iceData.iloc(closestIndex)[0]
