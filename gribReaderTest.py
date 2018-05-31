import pandas as pd

from grb import gribReader
from ice import analysis

GRB_FILEPATH = 'jupiter/icedata_2018-03-21T00-44-30_next_6hours.grb2'
AIS_FILEPATH = 'jupiter/ais-observations-20180320-20180321.csv'

ices = gribReader.parse_grib(GRB_FILEPATH, forecastAgeLimit=1, minLat=60.5)
print('Parsed ice data. Top 10 rows:')
print(ices.head(10))

ais = pd.read_csv(AIS_FILEPATH)
ais = ais[(ais['timestamp'] > '2018-03-20 19:00:00') & (ais['timestamp'] < '2018-03-20 20:00:00')]

ais['concentration(%)'] = 'NaN'
ais['thickness(m)'] = 'NaN'
ais['speed(m/s)'] = 'NaN'
ais['direction(deg)'] = 'NaN'

for index, row in ais.head(10).iterrows():
    nearest = analysis.findNearestIcePoint('timestamp', 'lat', 'lon', row['timestamp'], row['lat'], row['lon'], ices, 1)
    if len(nearest) == 0:
        continue
    ais.loc[index, 'concentration(%)'] = nearest['concentration(%)']
    ais.loc[index, 'thickness(m)'] = nearest['thickness(m)']
    ais.loc[index, 'speed(m/s)'] = nearest['speed(m/s)']
    ais.loc[index, 'direction(deg)'] = nearest['direction(deg)']

print('Tagged ais data with ice forecast. Top 10 rows:')
print(ais.head(10))




