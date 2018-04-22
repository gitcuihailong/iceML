import pandas as pd
import numpy.ma as ma
import datetime
import pygrib # import pygrib interface to grib_api
import math

DATE_FORMAT = '%Y-%m-%d %H:%M:%S.%f'
MIN_LAT = 60.5

def parse_grib(filepath, forecastAgeLimit):
    grb = pygrib.open(filepath)
    return grb_to_df(grb, forecastAgeLimit)

def grb_to_df(grb, forecastAgeLimit):
    grids = get_grids_from_grb(grb)
    ices = get_values_from_grids(grids, forecastAgeLimit)
    return pd.DataFrame(ices, columns=['timestamp', 'lat', 'lon', 'concentration(%)', 'thickness(m)', 'speed(m/s)', 'direction(deg)', 'forecast_age(h)'])

def get_values_from_grids(grids, forecastAgeLimit):
    ices = []
    for i in range(0, len(grids['thicknesses'])):
        lats, lons = grids['concentrations'][i].latlons()
        timestamp = grids['concentrations'][i].validDate
        analysisTime = grids['concentrations'][i].analDate
        hoursFromAnalysis = get_hours_between_dates(analysisTime ,timestamp)

        if hoursFromAnalysis > forecastAgeLimit:
                return ices

        concentrations = grids['concentrations'][i].values
        thicknesses = grids['thicknesses'][i].values
        speeds = grids['speeds'][i].values
        directions = grids['directions'][i].values

        if lats.size != lons.size != concentrations.size != thicknesses.size != speeds.size != directions.size:
            print('Grid sizes do not match')
            return
        for x in range(0, len(thicknesses)):
            for y in range(0, len(thicknesses[x])):
                conc = float(concentrations[x][y]) * 100
                thick = float(thicknesses[x][y])
                speed = float(speeds[x][y])
                dir = float(directions[x][y])
                lat = lats[x][y]
                lon = lons[x][y]

                if (lat > MIN_LAT) & atleastOneValid(conc, thick, speed, dir):
                    ices.append([timestamp, lat, lon, conc, thick, speed, dir, hoursFromAnalysis])
    return ices

def atleastOneValid(conc, thick, speed, dir):
    if not math.isnan(conc) & math.isnan(thick) & math.isnan(speed) & math.isnan(dir):
        return (conc > 0) | (thick > 0) | (speed > 0)
    return False

def get_hours_between_dates(date1, date2):
    diff = date2 - date1
    hours = diff.seconds / 3600
    return hours

def get_grids_from_grb(grb):
    grb.rewind()
    grids = {}
    grids['thicknesses'] = grb.select(name='Sea-ice thickness')
    grids['concentrations'] = grb.select(name='Sea-ice cover')
    grids['speeds'] = grb.select(name='Speed of ice drift')
    grids['directions'] = grb.select(name='Direction of ice drift')
    return grids