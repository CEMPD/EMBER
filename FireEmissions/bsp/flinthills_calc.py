#!/usr/bin/env python
# Converts the grass detects over the Flint Hills to an emissions inventory

import csv
import os.path, sys
import pandas as pd
import fauxioapi as io
from pyproj import Proj

def main():
    year     = sys.argv[1] #'2023'
    hms_fn   = sys.argv[2] #'/proj/ie/proj/GSA-EMBER/BlueSky/HMS/hms_split/hms_2023_fccscdl_grass_fh.csv' 
    fh_acres = sys.argv[3] #'ancillary/fh_2016_2024.csv'
    fh_fuel  = sys.argv[4] #'ancillary/sera_grass_efs_with_haps_march5_2021.csv'
    outdir   = sys.argv[5]
    print(hms_fn)
    ######################
    # Flint Hills scenario burn dates. These are marked at the top of the annual report
    #  distributed by Kansas State.
    # This is a tuple or list of the first and last dates for the burn season.
    #20210202_20210430,20210223_20210430,20220214_20220430,20230203_20230501
    fh_dates = (f'{year}0203',f'{year}0501')
    # Path to HMS grassland or Flint Hills grassland specific file for the year
    # At a minimum requires a header of:
    # Lon,Lat,county,YearDay
    #hms_fn = '/proj/ie/proj/GSA-EMBER/BlueSky/HMS/hms_split/hms_2023_fccscdl_grass_fh.csv'
    # Flint Hills annual acres burned by county
    #fh_acres = 'ancillary/fh_2016_2024.csv'
    # Flint Hills specific fuel loading
    #fh_fuel = 'ancillary/sera_grass_efs_with_haps_march5_2021.csv'
    # Gridded snow cover file
    #snowcover = f'snow/daily.metcro2d_snowcover.{year}.ncf'
    # Flatfile output prefix
    prefix = f'fh_{year}'
    ######
    #snow = SnowCover(snowcover)
    hms = get_hms(hms_fn)
    # Keep only the dates that fall within the scenario range
    hms = hms[hms.date_time.isin(pd.date_range(*fh_dates))].copy()
    #hms = snow.remove_snow(hms)
    # Merge in the adjust flint hills acres 
    hms = fh_scale(hms, fh_acres)
    hms['facility_id'] = 'FH' + hms.index.astype(str)
    fuel = get_fuel(fh_fuel)
    hms['CROP'] = 'SERA'
    hms = hms.merge(fuel, on='CROP', how='left')
    hms = fill_meta(hms)
    year = hms.calc_year.values[0]
    write_daily_ff10(hms.copy(), prefix, year, outdir)
    write_annual_ff10(hms, prefix, year, outdir)

def get_hms(fn):
    '''
    Get the HMS
    '''
    usecols  = ['Lon','Lat','YearDay','county']
    dtype = {'county': str, 'fips': str, 'YearDay': str}
    hms = pd.read_csv(fn, dtype=dtype)
    hms.rename(columns={'Lat': 'latitude', 'Lon': 'longitude'}, inplace=True)
    if 'county' not in list(hms.columns):
        hms['county'] = hms.fips
    hms.county = hms.county.astype(int).astype(str).str.zfill(5)
    hms['date_time'] = pd.to_datetime(hms['YearDay'], format='%Y%j')
    return hms[['latitude','longitude','date_time','YearDay','county']].copy()

def fill_meta(df):
    '''
    Fill the metadata for writing the Flat Files
    '''
    df.rename(columns={'county': 'region_cd'}, inplace=True)
    df['region_cd'] = df['region_cd'].astype(int).astype(str).str.zfill(5)
    df['value'] = df.acres * df.ef
    df['monthnum'] = df.date_time.dt.month.astype(str).str.zfill(2)
    df['day'] = df.date_time.dt.day.astype(str).str.zfill(2)
    df['calc_year'] = df.date_time.dt.year.astype(str)
    df['unit_id'] = df.calc_year
    df['facility_name'] = 'Flint Hills ' + df['region_cd'] + ' ' + df['YearDay']
    df['rel_point_id'] = df['monthnum'] + df['day'] 
    df['country_cd'] = 'US'
    df['process_id'] = 'FH'
    return df[df['value'].fillna(0) > 0]

def get_fuel(fn):
    '''
    Get the fuel loading, ef, and combusion efficiency from the EF file
    '''
    dtype = {'SCC': str}
    df = pd.read_csv(fn, dtype=dtype)
    df = df[df.CROP == 'SERA'].copy()
    df.rename(columns={'SCC': 'scc', 'Fuel Loading': 'tons_acre', 'CC': 'ceff'}, inplace=True)
    df[['tons_acre','ceff']] = df[['tons_acre','ceff']].astype(float)
    # Calculate a heat flux EF 
    df['hflux'] = df.tons_acre * df.ceff * 8000 
    # Acresburned filler for inventory
    df['acresburned'] = 1
    df = pd.melt(df, 
      id_vars=['CROP','scc','Crop Type Num','Crop Type','tons_acre','ceff'],
      var_name='poll', value_name='ef')
    # lb/ton to ton/ton
    idx = df.poll.isin(['hflux','acresburned'])
    # Calc the EF in tons/acre
    df.loc[~ idx, 'ef'] = df.tons_acre * df.ceff * (df.loc[~ idx, 'ef'].astype(float) / 2000)
    df.poll = df.poll.apply(fix_poll)
    return df

def write_daily_ff10(day_df, prefix, year, outdir):
    '''
    Write out the daily FF10
    '''
    cols = ['region_cd','facility_id','unit_id','rel_point_id','scc','poll','monthnum','day',
      'process_id','country_cd']
    day_df = day_df[cols+['value',]].groupby(cols, as_index=False).sum()
    day_df['day'] = 'dayval' + day_df['day'].astype('i').astype(str)
    day_df = pd.pivot_table(day_df, values='value', index=cols, columns='day')
    day_df['monthtot'] = day_df.sum(axis=1)
    day_df.reset_index(inplace=True)
    day_df['monthnum'] = day_df['monthnum'].astype('i').astype(str)
    day_df.sort_values(['region_cd','facility_id','unit_id','scc','poll','monthnum'], inplace=True)
    out_cols = ('country_cd','region_cd','tribal_code','facility_id','unit_id','rel_point_id','process_id',
      'scc','poll','op_type_cd','calc_method','date_updated','monthnum','monthtot','dayval1','dayval2',
      'dayval3','dayval4','dayval5','dayval6','dayval7','dayval8','dayval9','dayval10','dayval11',
      'dayval12','dayval13','dayval14','dayval15','dayval16','dayval17','dayval18','dayval19',
      'dayval20','dayval21','dayval22','dayval23','dayval24','dayval25','dayval26','dayval27',
      'dayval28','dayval29','dayval30','dayval31','comment')
    for col in out_cols:
        if col not in list(day_df.columns):
            if col.startswith('dayval'):
                day_df[col] = 0
            else:
                day_df[col] = ''
    day_df[['dayval%s' %x for x in range(1,32)]] = day_df[['dayval%s' %x for x in range(1,32)]].fillna(0)
    print(sum(day_df.loc[day_df['poll'] == 'ACRESBURNED', 'monthtot'].fillna(0)))
    print('Unique daily fires written: %s' %day_df['facility_id'].drop_duplicates().shape[0], 
      flush=True)
    fn = os.path.join(outdir, 'ptday_{}_ff10.csv'.format(prefix))
    with open(fn, 'w') as daily:
        daily.write('#FORMAT=FF10_DAILY_POINT\n#COUNTRY=US\n#YEAR=%s\n' %year)
        day_df.to_csv(daily, index=False, columns=out_cols)

def fh_scale(hms, fh):
    '''
    Scale the FH acres/detect to the seasonal county burns 
    header: region_cd,acres_[YYYY]
    '''
    year = hms.YearDay.values[0][:4]
    fharea = pd.read_csv(fh, usecols=['region_cd',f'acres_{year}'], 
      dtype={'region_cd': str}, comment='#')
    print('Acres In: %s' %sum(fharea[f'acres_{year}']), flush=True)
    hmscount = hms[['county','latitude']].groupby('county', as_index=False).count()
    hmscount.rename(columns={'latitude': 'cnt'}, inplace=True)
    fharea = fharea.merge(hmscount, left_on='region_cd', right_on='county', how='left')
    fharea['acres'] = fharea[f'acres_{year}'] / fharea.cnt
    hms = hms.merge(fharea[['county','acres']], on='county', how='left')
    return hms

def write_annual_ff10(day_df, prefix, year, outdir):
    '''
    Write out the annual FF10
    '''
    cols = ['region_cd','facility_id','unit_id','scc','poll','facility_name',
        'latitude','longitude','calc_year','rel_point_id','process_id','country_cd']
    ann_inv = day_df[cols+['value',]].groupby(cols, as_index=False).sum()
    ann_inv.rename(columns={'value': 'ann_value'}, inplace=True)
    ann_inv['region_cd'] = ann_inv['region_cd'].astype(int).astype(str).str.zfill(5)
    print('Unique annual fires read: %s' %ann_inv['facility_id'].drop_duplicates().shape[0])
    ann_inv['stkhgt'] = '1'
    ann_inv['stkdiam'] = '1'
    ann_inv['stktemp'] = '1'
    ann_inv['stkflow'] = '1'
    ann_inv['stkvel'] = '1'
    ann_inv['data_set_id'] = 'EPA_GRASSLAND_HMS'
    ann_inv.sort_values(['region_cd','facility_id','scc','poll'], inplace=True)
    print(sum(ann_inv.loc[ann_inv['poll'] == 'ACRESBURNED', 'ann_value'].fillna(0)))
    print('Unique annual fires written: %s' %ann_inv[['region_cd','facility_id']].drop_duplicates().shape[0])
    out_cols = ('country_cd','region_cd','tribal_code','facility_id','unit_id','rel_point_id','process_id',
      'agy_facility_id','agy_unit_id','agy_rel_point_id','agy_process_id','scc','poll','ann_value',
      'ann_pct_red','facility_name','erptype','stkhgt','stkdiam','stktemp','stkflow','stkvel','naics',
      'longitude','latitude','ll_datum','horiz_coll_mthd','design_capacity','design_capacity_units',
      'reg_codes','fac_source_type','unit_type_code','control_ids','control_measures','current_cost',
      'cumulative_cost','projection_factor','submitter_id','calc_method','data_set_id',
      'facil_category_code','oris_facility_code','oris_boiler_id','ipm_yn','calc_year','date_updated',
      'fug_height','fug_width_xdim','fug_length_ydim','fug_angle','zipcode','annual_avg_hours_per_year',
      'jan_value','feb_value','mar_value','apr_value','may_value','jun_value','jul_value','aug_value',
      'sep_value','oct_value','nov_value','dec_value','jan_pctred','feb_pctred','mar_pctred',
      'apr_pctred','may_pctred','jun_pctred','jul_pctred','aug_pctred','sep_pctred','oct_pctred',
      'nov_pctred','dec_pctred','comment')
    for col in out_cols:
        if col not in list(ann_inv.columns):
            ann_inv[col] = ''
    fn = os.path.join(outdir, 'ptinv_{}_ff10.csv'.format(prefix))
    with open(fn, 'w') as annual:
        annual.write('#FORMAT=FF10_POINT\n#COUNTRY=US\n#YEAR=%s\n' %year)
        ann_inv.to_csv(annual, index=False, columns=out_cols, quoting=csv.QUOTE_NONNUMERIC)

class SnowCover:
    
    def __init__(self, snow):
        '''
        '''
        self._read_snow(snow)

    def _read_snow(self, snow):
        '''
        Read in the daily gridded snow cover I/O API netCDF
        '''
        griddesc = 'griddesc_lambertonly_25oct2022_v27.txt'
        with io.IODataset(snow) as f:
            self.grid = io.Grid(f.GDNAM.strip(), griddesc)
            self.arr = f['SNOCOV'][:]
        self.proj = Proj(self.grid.proj4())

    def _arr_to_df(self):
        '''
        convert from a 4D array to a dataframe of format
        julday,cell
        '''
        self.df = pd.DataFrame()
        for n in range(self.arr.shape[0]):
            day = pd.DataFrame(self.arr[n,0,:].ravel(), columns=['cover',])
            day['cell'] = day.index
            day['jday'] = n + 1
            self.df = pd.concat((self.df, day[day['cover'].fillna(0) > 0]))

    def _calc_cell(self, lon, lat):
        '''
        Calculate the row-major cell from lat/lon to merge with the raveled grid
        '''
        x, y = self.proj(lon, lat)
        return int((x-self.grid.XORIG) / self.grid.XCELL) +\
          (int((y-self.grid.YORIG) / self.grid.YCELL) * self.grid.NCOLS)

    def remove_snow(self, hms):
        '''
        Remove the lat/lon associated with snow cover on a given day
        (TSTEP[DAY], LAY[1], ROW, COL)
        '''
        self._arr_to_df()
        cols = list(hms.columns)
        hms['cell'] = hms[['longitude','latitude']].apply(lambda row: self._calc_cell(*row), axis=1)
        hms['jday'] = hms['date_time'].dt.dayofyear
        hms = hms.merge(self.df, on=['cell','jday'], how='left')
        idx = hms['cover'].notnull() 
        hms[idx].to_csv('hms_snow_drops.csv', index=False)
        print('%s/%s HMS detections dropped for snow cover' %(len(hms[idx]), len(hms)), flush=True)
        return hms.loc[~ idx, cols].copy()

def fix_poll(poll):
    '''
    Rename specific pollutants to SMOKE inventory name
    '''
    haps = {'butadiene13': '106990', 'acetaldehyde': '75070', 'acrolein': '107028', 'anthracene': '120127', 
      'benzoaanthracene': '56553', 'benzene': '71432', 'benzoafluoranthene': '203338', 'benzoapyrene': '50328',
      'benzocphenanthrene': '195197', 'benzoepyrene': '192972', 'benzoghiperylene': '191242', 'benzobfluoranthene': '56832736',
      'benzokfluoranthene': '207089', 'benzofluoranthenes': '56832736', 'carbonylsulfide': '463581',
      'chrysene': '218019', 'fluoranthene': '206440', 'formaldehyde': '50000', 'indeno123cdpyrene': '193395',
      'methylchloride': '74873', 'methylanthracene': '26914181', 'methylbenzopyrenes': '65357699',
      'methylchrysene': '41637905', 'methylpyrene': '2381217', 'nhexane': '110543', 'ompxylene': '1330207',
      'perylene': '168550', 'phenanthrene': '85018', 'pyrene': '129000', 'toluene': '108883',
      'ethylbenzene': '100414', 'isopropylbenzene': '98828', 'proprionaldehyde': '123386',
      'styrene': '100425', 'trimethylpentane224': '540841', 'xylenes': '1330207', 'cumene': '98828',
      'acenaphthene': '208968', 'acetamide': '60355', 'acetonitrile': '75058', 'acrylonitrile': '107131',
      'fluorene': '86737', 'hydrogencyanide': '74908', 'methanol': '67561', 'naphthalene': '91203',
      'nitrobenzene': '98953', 'phenol': '108952', 'vinylacetate': '108054', 'acenaphthylene': '208968'}
    if poll.startswith('HAP'):
        poll = poll.split('_')[1]
    for c in ('[',']','(',')','_','-'):
        poll = poll.replace(c,'')
    if poll in haps:
       poll = haps[poll]
    poll = poll.upper()
    if poll == 'PM25':
        poll = 'PM2_5'
    elif poll[-3:] == 'PRI':
        poll = poll[:-3] + '-PRI'
    return poll

if __name__ == '__main__':
    main()
