#!/usr/bin/env python
# Setup the UTC offset for the BSF input data

from datetime import datetime
import os.path
import sys
import pytz
import pandas as pd
from timezonefinder import TimezoneFinder
from zoneinfo import ZoneInfo
from osgeo import osr, ogr

tf = TimezoneFinder()

def main():
    startdate = sys.argv[1]   # 20180101
    enddate = sys.argv[2]     # 20181231
    inpath = sys.argv[3]      # /path/to/fire_locations_YYYYMMDD.csv
    oupath = sys.argv[4]
    dates = [datetime.strftime(x, '%Y%m%d') for x in list(pd.date_range(startdate, enddate))]
    dtype = {'id': str, 'event_id': str, 'date_time': str}
    geo_id = na_shape()
    for day in dates:
        fn = os.path.join(inpath, 'fire_locations_%s.csv' %day)
        df = pd.read_csv(fn, dtype=dtype)
        cols = list(df.columns)
        print(day)
        if len(df) > 0:
            df['county'] = df[['longitude','latitude']].apply(lambda row: geo_id.get_loc(*row), axis=1)
            df['country'] = 'us'
            df.loc[df['county'].str.zfill(6).str.startswith('1'), 'country'] = 'ca'
            if not df[df['county'] == 'UNK'].empty:
                print('Out of domain locations to be dropped:')
                print(df[df['county'] == 'UNK'])
            df['date_time'] = df[['date_time','longitude','latitude']].apply(lambda row: offset(*row), axis=1)
        for runtype in ('RX','WF'):
            fn = os.path.join(oupath, 'fire_locations_%s_utc_%s.csv' %(day, runtype.lower()))
            idx = (df['type'] == runtype) & (df['area'].fillna(0) > 0)
            df[idx].to_csv(fn, columns=cols+['county','country'], index=False)

class na_shape:
    def __init__(self, 
      shape_file='/proj/ie/proj/GSA-EMBER/BlueSky/from_EPA/ember_package/geospatial/northamerica_county_province_state_latlon.shp',
      field_name='GEOID'):
        driver = ogr.GetDriverByName('ESRI Shapefile')
        self.field_name = field_name
        self.shp = driver.Open(shape_file)
        self.layer = self.shp.GetLayer()

    def get_loc(self, lon, lat):
        pt = ogr.Geometry(ogr.wkbPoint)
        pt.SetPoint_2D(0, lon, lat)
        self.layer.SetSpatialFilter(pt)
        idx = self.layer.GetLayerDefn().GetFieldIndex(self.field_name)
        feat = self.layer.GetNextFeature()
        if feat:
            return '%0.6d' %int(feat.GetFieldAsString(idx))
        else:
            return 'OOB'

def offset(ds, lon, lat):
    '''
    Insert the tz offset
    '''
    dt = pd.to_datetime(ds).tz_localize(tz=ZoneInfo(tf.certain_timezone_at(lat=lat, lng=lon)))
    dt = datetime.strftime(dt, '%Y%m%d%H%M%z')
    return dt[:-2] + ':00'

if __name__ == '__main__':
    main()
