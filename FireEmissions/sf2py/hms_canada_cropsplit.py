#!/usr/bin/env python
# Splits Canada crops from wildland and labels all detects

from datetime import datetime, timedelta
import os.path
import numpy as np
import sys
import multiprocessing as mp
import pandas as pd
from pyproj import Proj
import netCDF4 as ncf
import argparse

def main():
    parser = argparse.ArgumentParser(description="Splitting HSM over Canada to cropland and wildland")
    parser.add_argument("inpath",  type=str, help="Path to HSM input files with FIPS codes")
    parser.add_argument("outpath", type=str, help="Path for output files")
    parser.add_argument("fccmap_path", type=str, help="Path for Canada crop- and wildland landcover netcdf file")
    parser.add_argument("fuelxref_path", type=str, help="Path for Landcover and Fuel type mapping file")
    parser.add_argument("hms_label", type=str, help="Label for output files")
    parser.add_argument("start_date", type=str, help="Start date in YYYYMMDD format")
    parser.add_argument("end_date", type=str, help="End date in YYYYMMDD format")
    
    args       = parser.parse_args()
    inpath     = args.inpath          # sys.argv[1]
    outpath    = args.outpath         # sys.argv[2]
    fccpath    = args.fccmap_path     # sys.argv[3]
    if not os.path.exists(fccpath):
        print(f"❌ Input landcover not found at {fccpath}")
        return
    
    fxrefpath   = args.fuelxref_path   # sys.argv[4]
    if not os.path.exists(fxrefpath):
        print(f"❌ Input fuel mapping not found at {fxrefpath}")
        return
    
    hms_label  = args.hms_label       # sys.argv[5]
    
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
    
    
    grid = GridTools()
    #fn = '/work/MOD3APP/jbeidler/canada/fires/fbp/fbp_2011_250m_canada_fccsmap_crops_fix.nc'
    cover = Cover(fccpath)
    cover.load_coverxref(fxrefpath)
    #inpath = 'northamerica'
    
    hms = HMS(inpath, outpath, hms_label)
    # Issue with a large number of procs specified
    hms.procs = 4
    # Load the HMS files
    #for day in [x.strftime('%Y%m%d') for x in list(pd.date_range('%s0101' %year,'%s1031' %year))]:
    for day in dates:
        print(day, flush=True)
        hms.proc_day(day, cover, grid)
    ####
    hms.annual = hms.annual.merge(cover.coverxref, on='code', how='left')
    hms.write_crops()
    hms.write_wildland()
    hms.write_all()
    print('COMPLETE')

class GridTools:
    '''
    Cell centroid to lat/lon
    '''
    def __init__(self):
        '''
        self.proj = Proj(proj='lcc', lat_1=49, lat_2=77, lon_0=-95.,
          lat_0=49, R=6378137, units='m', x_0=0, y_0=0, no_defs=True)
        '''
        self.proj = Proj(proj='lcc', lat_1=50, lat_2=70, lon_0=-96.,
          lat_0=40, R=6378137, units='m', x_0=0, y_0=0, no_defs=True)

    def xy(self, df):
        '''
        Apply inverse projection to get lat lon
        '''
        df = df[['Lon','Lat']].apply(lambda row: self.proj(*row), axis=1)
        return df

class Cover:
    '''
    '''

    def __init__(self, fn):
        with ncf.Dataset(fn) as f:
            self.lc = f.variables['Band1'][:].ravel()
        '''
        # Resolution of Crops raster in projection units (ie. meters)
        self.res = 240
        # X origin of Crops raster in projection units 
        self.xorig = -2660910
        # Y origin of Crops raster in projection units 
        self.yorig = 2998848
#        self.yorig = -831312
        self.ncols = 24242
        self.nrows = 15959
        '''
        # Resolution of Crops raster in projection units (ie. meters)
        self.res = 250
        # X origin of Crops raster in projection units 
        self.xorig = -2697070
        # Y origin of Crops raster in projection units 
        self.yorig = 5036868
        self.ncols = 23723
        self.nrows = 19840
        #print(fccs.min(), fccs.max())

    def load_coverxref(self, fn='nfi_aci_fuel_xref.csv'):
        cover = pd.read_csv(fn, usecols=['Code','Label'], dtype={'Code': int})
        cover.rename(columns={'Code': 'code', 'Label': 'desc'}, inplace=True)
        self.coverxref = cover.copy()
       
class HMS:

    def __init__(self, inpath, outpath, label):
        self.procs = 4
        self.inpath  = inpath
        self.outpath = outpath
        self.annual  = pd.DataFrame()
        self.label   = label

    def get_hms(self, day):
        '''
        Load the HMS daily file
        '''
        fn = os.path.join(self.inpath, 'hms%s.txt' %day)
        if os.path.exists(fn):
            dtype = {'YearDay': str, 'Time': str, 'Satellite': str, 'fips': str, 'Ecosys': str}
            df = pd.read_csv(fn, dtype=dtype)
            df.rename(columns={'fips': 'county'}, inplace=True)
            df['gday'] = day
            df['Lon'] = df['Lon'].round(3)
            df['Lat'] = df['Lat'].round(3)
            # Drop detects as duplicates on the same day within the same rounded lat/lon
            df.drop_duplicates(['Lon','Lat'], inplace=True)
            #print(df[df['county'].str.startswith('1')])
            # Drop county outside of canada
            return df[(df['county'].str.startswith('1')) & (df['county'].str.endswith('000'))]
        else:
            return pd.DataFrame()

    def proc_day(self, day, cover, grid):
        '''
        Process an HMS day and append it to the annual file
        '''
        hms = self.get_hms(day)
        if len(hms) > 0:
            cols = list(hms.columns)
            pool = mp.Pool(self.procs)
            res = pool.map(grid.xy, np.array_split(hms, self.procs))
            pool.close()
            pool.join()
            locs = pd.DataFrame(pd.concat(res), columns=['xy',], index=hms.index)
            locs = pd.DataFrame(locs['xy'].values.tolist(), columns=['x','y'], index=locs.index)
            hms = pd.concat((hms, locs), axis=1)
            hms['col'] = np.floor((hms['x'] - cover.xorig)/cover.res).astype(int)
            hms['row'] = np.floor((hms['y'] - cover.yorig)/(-1 * cover.res)).astype(int)
            idx = (hms['col'] < 0) | (hms['row'] < 0) | (hms['row'] > cover.nrows) | (hms['col'] > cover.ncols)
            oob = hms[idx].copy()
            hms = hms[~ (idx)].copy()
            oob['code'] = -9999
            hms['cell'] = (hms['col'] + (hms['row'] * cover.ncols)).astype(int)
            hms['code'] = hms['cell'].apply(lambda cell: cover.lc[cell])
            cols.append('code')
            self.annual = pd.concat((self.annual, hms[cols], oob[cols]))

    def write_crops(self):
        '''
        Write the crops
        '''
        idx = (self.annual['code'].astype(int) >= 9120) & (self.annual['code'].astype(int) < 9200)
        self.annual[idx].to_csv(os.path.join(self.outpath,'%s_crops.csv' %self.label), index=False)

    def write_wildland(self):
        '''
        Write the wildland fires
        '''
        idx = (self.annual['code'].fillna(0).astype(int) < 9120) | (self.annual['code'].astype(int) >= 9200)
        self.annual[idx].to_csv(os.path.join(self.outpath,'%s_wildland.csv' %self.label), index=False)

    def write_all(self):
        '''
        Write all HMS detects
        '''
        self.annual.to_csv(os.path.join(self.outpath,'%s_all.csv' %self.label), index=False)

if __name__ == '__main__':
    main()
