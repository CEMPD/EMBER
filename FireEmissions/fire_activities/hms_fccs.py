#!/usr/bin/env python
# Add FCCS to HMS detects
# The "FutureWarning: '+init=<authority>:<code>' syntax is deprecated. '<authority>:<code>' is the preferred initialization method." warnings can be ignored

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
    
    parser = argparse.ArgumentParser(description="Splitting HSM over U.S. to cropland and wildland")
    parser.add_argument("inpath",  type=str, help="Path to HSM input files with FIPS codes")
    parser.add_argument("outpath", type=str, help="Path for output files")
    parser.add_argument("fccmap_path", type=str, help="Path for U.S. FCC fuelbed netcdf file")
    parser.add_argument("fccxref_path", type=str, help="Path for FCC Fuelbed mapping file")
    parser.add_argument("cdlxref_path", type=str, help="Path for CDL mapping file")
    parser.add_argument("costcy_path", type=str, help="Path for COSTCY file")
    parser.add_argument("hms_label", type=str, help="Label for output files")
    parser.add_argument("start_date", type=str, help="Start date in YYYYMMDD format")
    parser.add_argument("end_date", type=str, help="End date in YYYYMMDD format")
    
    args       = parser.parse_args()
    inpath     = args.inpath          # sys.argv[1]
    outpath    = args.outpath         # sys.argv[2]
    fccflbd    = args.fccmap_path     # sys.argv[3]
    
    if not os.path.exists(fccflbd):
        print(f"❌ Input FCC Fuelbed not found at {fccflbd}")
        return
    
    fccxref    = args.fccxref_path    # sys.argv[4]
    if not os.path.exists(fccxref):
        print(f"❌ Input fuel mapping not found at {fccxref}")
        return
    
    cdlxref    = args.cdlxref_path    # sys.argv[5]
    if not os.path.exists(cdlxref):
        print(f"❌ Input CDL mapping not found at {cdlxref}")
        return
    
    costcy     = args.costcy_path     # sys.argv[6]
    if not os.path.exists(costcy):
        print(f"❌ Input COSTCY not found at {costcy}")
        return
    
    hms_label  = args.hms_label       # sys.argv[7]
    
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
    
    #year = '2023'
    #fn = '/proj/ie/proj/GSA-EMBER/BlueSky/georgia_BSP/lf22_2022_120m_smartmode_fix.nc'
    grid = GridTools()
    fccs = FCCS(fccflbd)
    fccs.load_fccsxref(fccxref) # ('/nas/longleaf/home/tranhuy/proj/GSA-EMBER/BlueSky/from_EPA/ember_package/activity/hms/LF20_FCCS_220.csv')
    fccs.load_cdlxref(cdlxref)  # ('/nas/longleaf/home/tranhuy/proj/GSA-EMBER/BlueSky/from_EPA/ember_package/activity/hms/cdl_cover.csv')
    
    #inpath = f'/proj/ie/proj/GSA-EMBER/BlueSky/HMS/outputs/{year}'
    hms = HMS(inpath, outpath, costcy, hms_label) #'hms_%s' %year)
    # Load the HMS files
    for day in dates:
        print(f'{day}', flush=True)
        hms.proc_day(day, fccs, grid)
    print('Annual records: %s' %len(hms.annual))
    hms.annual.fccs = hms.annual.fccs.fillna(-9999).astype(float).astype(int)
    hms.label_annual_fccs(fccs)
    hms.label_states()
    print('Annual records: %s' %len(hms.annual))
    hms.write_tree_crops()
    hms.write_mw_crops()
    hms.write_grass()
    hms.write_cdlcrops()
    hms.write_wildland()
    hms.write_all()
    print('COMPLETE')


class GridTools:
    '''
    Cell centroid to lat/lon
    '''
    def __init__(self):
        #self.proj = Proj(proj='aea', lat_1=29.5, lat_2=45.5, lon_0=-96.,
        #  lat_0=23, R=6378137, units='m', x_0=0, y_0=0, no_defs=True)
        self.proj = Proj('epsg:5072')

    def xy(self, df):
        '''
        Apply inverse projection to get lat lon
        '''
        df = df[['Lon','Lat']].apply(lambda row: self.proj(*row), axis=1)
        return df

'''
Size is 39083, 25384
Coordinate System is:
PROJCS["NAD_1983_Albers",
    GEOGCS["NAD83",
        DATUM["North_American_Datum_1983",
            SPHEROID["GRS 1980",6378137,298.2572221010002,
                AUTHORITY["EPSG","7019"]],
            AUTHORITY["EPSG","6269"]],
        PRIMEM["Greenwich",0],
        UNIT["degree",0.0174532925199433],
        AUTHORITY["EPSG","4269"]],
    PROJECTION["Albers_Conic_Equal_Area"],
    PARAMETER["standard_parallel_1",29.5],
    PARAMETER["standard_parallel_2",45.5],
    PARAMETER["latitude_of_center",23],
    PARAMETER["longitude_of_center",-96],
    PARAMETER["false_easting",0],
    PARAMETER["false_northing",0],
    UNIT["metre",1,
        AUTHORITY["EPSG","9001"]]]
Origin = (-2362395.000000000000000,3267405.000000000000000)
Pixel Size = (120.000000000000000,-120.000000000000000)
'''
class FCCS:
    '''
    '''

    def __init__(self, fn):
        with ncf.Dataset(fn) as f:
            self.fccs = f.variables['Band1'][:].ravel()
        # Resolution of FCCS raster in projection units (ie. meters)
        self.xres = 120
        self.yres = -120
        # X origin of FCCS raster in projection units 
        self.xorig = -2362395
        # Y origin of FCCS raster in projection units 
        self.yorig = 3267405
        self.ncols = 39083
        self.nrows = 25384
        #print(fccs.min(), fccs.max())

    def load_fccsxref(self, fn='LF20_FCCS_220.csv'):
        fccs = pd.read_csv(fn, usecols=['FCCS','FUELBED_NAME'], dtype={'FCCS': str})
        fccs.rename(columns={'FCCS': 'fccs', 'FUELBED_NAME': 'desc'}, inplace=True)
        self.fccsxref = fccs[fccs['fccs'].astype(int) < 1300].copy()
       
    # The CDL xref generally doesn't change, but check the rasters from time to time
    def load_cdlxref(self, fn='cdl_cover.csv'):
        cdl = pd.read_csv(fn, dtype={'fccs': str}, names=['fccs','desc'], skiprows=1)
        cdl['fccs'] = '9' + cdl['fccs'].astype(int).astype(str).str.zfill(3)
        self.cdlxref = cdl

class HMS:

    def __init__(self, inpath, outpath, costcy, label):
        self.procs = 4 
        self.inpath = inpath
        self.outpath = outpath
        self.annual = pd.DataFrame()
        self.costcy = costcy
        self.label = label
        self._set_classes()

    def get_hms(self, day):
        '''
        Load the HMS daily file
        '''
        fn = os.path.join(self.inpath, 'hms%s.txt' %day)
        print(f'within HMS.get_hms; fn={fn}')
        if os.path.exists(fn):
            dtype = {'YearDay': str, 'Time': str, 'Satellite': str, 'fips': str, 'Ecosys': str}
            df = pd.read_csv(fn, dtype=dtype)
            print(df)
            df.columns = df.columns.str.strip()
            print(df.columns)
            df['gday'] = day
            df['Lon'] = df['Lon'].round(3)
            df['Lat'] = df['Lat'].round(3)
            # Drop detects as duplicates on the same day within the same rounded lat/lon
            df.drop_duplicates(['Lon','Lat'], inplace=True)
            df = df[df['fips'] != 'OOB'].copy()
            # Drop county outside of domain
            return df[(df['fips'] != '99999') & (df['fips'].astype(int) < 99999)]
        else:
            return pd.DataFrame()

    def proc_day(self, day, fccs, grid):
        '''
        Process an HMS day and append it to the annual file
        '''
        hms = self.get_hms(day)
        input_len = len(hms)
        if len(hms) > 0:
            cols = list(hms.columns)
            pool = mp.Pool(self.procs)
            res = pool.map(grid.xy, np.array_split(hms, self.procs))
            pool.close()
            pool.join()
            locs = pd.DataFrame(pd.concat(res), columns=['xy',], index=hms.index)
            locs = pd.DataFrame(locs['xy'].values.tolist(), columns=['x','y'], index=locs.index)
            hms = pd.concat((hms, locs), axis=1)
            hms['col'] = np.floor((hms['x'] - fccs.xorig)/fccs.xres).astype(int)
            hms['row'] = np.floor((hms['y'] - fccs.yorig)/fccs.yres).astype(int)
            hms['cell'] = (hms['col'] + (hms['row'] * fccs.ncols)).astype(int)
            idx = (hms.cell >= 0) & (hms.cell < len(fccs.fccs))
            oob = hms[~ idx].copy()
            oob['fccs'] = -9999
            hms = hms[idx].copy()
            hms['fccs'] = hms['cell'].apply(lambda cell: fccs.fccs[cell])
            cols.append('fccs')
            self.annual = pd.concat((self.annual, hms[cols], oob[cols]))
        print('\tI/O: %s -> %s' %(input_len, len(hms)+len(oob)))

    def label_annual_fccs(self, fccs):
        '''
        Label the FCCS codes
        '''
        xref = pd.concat((fccs.fccsxref, fccs.cdlxref))
        self.annual['fccs'] = self.annual['fccs'].astype(str)
        self.annual = self.annual.merge(xref, on='fccs', how='left') 

    def label_states(self):
        costcy = pd.read_csv(self.costcy, usecols=['region_cd','stabbr'], dtype={'region_cd': str})
        costcy.rename(columns={'region_cd': 'fips'}, inplace=True)
        self.annual = self.annual.merge(costcy, on='fips', how='left')

    def _set_classes(self):
        self.grass = ['9176','9037','1281','131','133','175','176','203','213','236','280','302','315',
          '318','336','41','415','417','420','435','436','437','442','443','445','453','506','514','519',
          '530','531','532','533','57','65','66','1283']
        # Corn and soy
        self.mw_crops = ['9001','9012','9013','9005','9254']
        self.mw_st = ['IA','IN','IL','MI','MO','MN','WI','OH','KS']
        self.tree_crops = ['9066','9067','9068','9069','9070','9071','9072','9074','9075','9076','9077','9204',
          '9211','9212','9217','9218','9220','9223','9242','1273','1274']
        # These are additional crops in FCCS that should be moved to the crops file
        self.fccs_crops = ['1201','1203','1223','1224','1230','1232','1244','1247','1261']

    def write_tree_crops(self):
        '''
        Write the tree crops
        '''
        idx = self.annual['fccs'].isin(self.tree_crops)
        self.annual[idx].to_csv(os.path.join(self.outpath,'%s_fccscdl_tree_crops.csv' %self.label), index=False)

    def write_mw_crops(self):
        '''
        Write the crops in the MW
        '''
        idx = (self.annual['stabbr'].isin(self.mw_st)) & (self.annual['fccs'].isin(self.mw_crops))
        self.annual.loc[idx, 'fccs'] = '8' + self.annual.loc[idx, 'fccs'].str[1:]
        idx = (self.annual['fccs'].astype(float) > 7999) & (self.annual['fccs'].astype(float) < 9000)
        self.annual[idx].to_csv(os.path.join(self.outpath,'%s_fccscdl_mwcrops.csv' %self.label), index=False)

    def write_grass(self):
        '''
        Write the grass FCCS or CDL types
        '''
        idx = self.annual['fccs'].isin(self.grass)
        self.annual[idx].to_csv(os.path.join(self.outpath,'%s_fccscdl_grass.csv' %self.label), index=False)

    def write_cdlcrops(self):
        '''
        Write the CDL crops outside the MW and not trees
        '''
        idx = ((self.annual['fccs'].astype(int) > 9000) | (self.annual['fccs'].isin(self.fccs_crops))) \
          & (~ self.annual['fccs'].isin(self.grass+self.tree_crops))
        self.annual[idx].to_csv(os.path.join(self.outpath,'%s_fccscdl_cdlcrops.csv' %self.label), index=False)

    def write_wildland(self):
        '''
        Write the wildland fires
        '''
        idx = (self.annual['fccs'].astype(int) < 8000) \
          & (~ self.annual['fccs'].isin(self.grass+self.tree_crops+self.fccs_crops))
        self.annual[idx].to_csv(os.path.join(self.outpath,'%s_fccscdl_wildland.csv' %self.label), index=False)

    def write_all(self):
        '''
        Write all HMS detects
        '''
        self.annual.to_csv(os.path.join(self.outpath,'%s_fccscdl_all.csv' %self.label), index=False)

if __name__ == '__main__':
    main()
