#!/usr/bin/env python3
# Add FIPS geo tag by location to HMS

from datetime import datetime, timedelta
import numpy as np
import sys
import os.path
import multiprocessing as mp
import pandas as pd
from osgeo import ogr
import argparse

def main():   
    parser = argparse.ArgumentParser(description="Apply FIPS code to HMS Fire Points TXT files for a given date range.")
    parser.add_argument("inpath",  type=str, help="Path to HSM raw input files")
    parser.add_argument("outpath", type=str, help="Path for output files")
    parser.add_argument("fips_shape_path", type=str, help="Path for input fips shapefile")
    parser.add_argument("start_date", type=str, help="Start date in YYYYMMDD format")
    parser.add_argument("end_date", type=str, help="End date in YYYYMMDD format")
    
    args = parser.parse_args()
    
    inpath   = args.inpath          # sys.argv[1]
    outpath  = args.outpath         # sys.argv[2]
    fipspath = args.fips_shape_path # sys.argv[3] 
    if not os.path.exists(fipspath):
        print(f"❌ Input FIPS shapefile not found at {fipspath}")
        return
    
    # Convert input dates to datetime objects
    try:
        start_date = datetime.strptime(args.start_date, "%Y%m%d")
        end_date = datetime.strptime(args.end_date, "%Y%m%d")
    except ValueError:
        print("❌ Invalid date format! Please use YYYYMMDD.")
        return
    
    # Validate that start date is before end date
    if start_date > end_date:
        print("❌ Error: Start date must be before or equal to end date.")
        return
    dates = [date.strftime('%Y%m%d') for date in pd.date_range(start=start_date, end=end_date)]
    
    hms_year = Hms(inpath, outpath, fipspath)
    
    # Parallel processing
    # Issues when a large number of procs are specified. It works with 8, doesn't work with 32.
    procs = 8
    pool = mp.Pool(procs)
    res = pool.map(hms_year.get_fips, np.array_split(dates, procs))
    pool.close()
    pool.join()
    print('COMPLETE')

class na_shape:
    '''
    Simple point-in-polygon check to return a FIPS
    '''    
    def __init__(self,shape_file,field_name='GEOID'):
        driver = ogr.GetDriverByName('ESRI Shapefile')
        self.field_name = field_name
        self.shp = driver.Open(shape_file)
        self.layer = self.shp.GetLayer()

    def get_loc(self, lon, lat):
        '''
        Get the FIPS for the lat/lon
        '''
        pt = ogr.Geometry(ogr.wkbPoint)
        pt.SetPoint_2D(0, lon, lat)
        self.layer.SetSpatialFilter(pt)
        idx = self.layer.GetLayerDefn().GetFieldIndex(self.field_name)
        feat = self.layer.GetNextFeature()
        if feat:
            return '%0.6d' %int(feat.GetFieldAsString(idx))
        else:
            return 'OOB'

class Hms():
    def __init__(self, inpath, outpath, fips_shape_path):
        self.inpath   = inpath
        self.outpath  = outpath
        self.fipspath = fips_shape_path 

    def get_fips(self, dates):
        '''
        Get the FIPS from a dataframe
        '''
        geo_id = na_shape(shape_file=self.fipspath)
        for day in dates:
            fn = os.path.join(self.inpath, 'hms%s.txt' %day)
            if os.path.exists(fn):
                df = self.load_hms(fn)
                h_len = len(df) 
                df['fips'] = df[['Lon','Lat']].apply(lambda row: geo_id.get_loc(*row), axis=1)
                if len(df) != h_len:
                    print('WARNING: Change in size for hms%s.txt' %day)
                fn = os.path.join(self.outpath, 'hms%s.txt' %day)
                print('Writing %s: %s records' %(fn, len(df)))
                df.to_csv(fn, index=False)
            else:
                print('WARNING: Missing %s' %fn)

    def load_hms(self, fn):
        '''
        load the HMS file into a more standard format
        '''
        dtype = {'YearDay': str, 'Time': str, 'Ecosys': str}
        df = pd.read_csv(fn, dtype=dtype, skipinitialspace=True)
        idx = df['Lat'] > 24.5
        df = df[idx].copy()
        print('Loading %s: %s records' %(fn, len(df)), flush=True)
        return df

if __name__ == '__main__':
    main()
