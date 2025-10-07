#!/usr/bin/env python

import pandas as pd
from datetime import datetime, timedelta
import os

#jday_range = range(2023091, 2023213)
jday_range = range(2024001, 2024366)
#dtype = {'DAY': str, 'TIME': str, 'GENVEG': str, 'LATI': str, 'LONGI': str}
tdf = pd.DataFrame()

def julian_to_gregorian(julian_date):
    year = int(str(julian_date)[:4])
    day_of_year = int(str(julian_date)[4:])
    return datetime(year, 1, 1) + timedelta(days=day_of_year - 1)

for day in jday_range:
    date = julian_to_gregorian(day).strftime('%Y%m%d')
    print(f"{day} => {date}")
    
    #fn = '2023/GLOB_SAPRC99_%s.txt' %str(day)
    fn = '2024/FINNv2.5.1_modvrs_nrt_SAPRC_%s.txt' %str(date)
    
    try:
        #df = pd.read_csv(fn, dtype=dtype, skipinitialspace=True, index_col=False)
        df = pd.read_csv(fn, dtype=object, skipinitialspace=True, index_col=False)
    
        #print(df.head())
        #print(df.columns)
    
        tdf = pd.concat((tdf, df[(df['LATI'].str.replace('D','E').astype(float) > 0) & (df['LONGI'].str.replace('D','E').astype(float) < 0)]))
    except Exception as e:
        print(e)
        continue
    
for col in list(tdf.columns):
    #if col not in ('DAY','TIME','GENVEG'):
    if col not in ('DAY','TIME','POLYID','FIREID','GENVEG'):
        tdf[col] = tdf[col].str.replace('D','E').astype(float)
#fn = 'finn25_na_2023_apr_jul.csv'
fn = 'finn25_na_2024_jan_dec.csv'
tdf.to_csv(fn, index=False)