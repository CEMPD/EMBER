#!/usr/bin/env python
# Concatenates fire_locations files from daily BSF output directories 
# Modified 5 Jun 2017 to handle flaming and smoldering SCCs J. Beidler

import sys
import os.path
from datetime import date, timedelta
import re
import pandas as pd



# Columns to keep  -- these need to match the BSF output column names in fire_locations
# Pollutants - also columns to keep, but in a separate list to easily add HAPs
polls = ['pm2.5','pm10','co','co2','ch4','nox','nh3','so2','voc']
#polls = ('pm25','pm10','co','co2','ch4','nox','nh3','so2','voc','hap_106423','hap_106990','hap_107028','hap_108383','hap_108883','hap_110543','hap_120127','hap_129000','hap_191242','hap_192972','hap_193395', \
#	'hap_195197','hap_198550','hap_203338','hap_206440','hap_207089','hap_218019','hap_2381217','hap_247','hap_248','hap_26914181','hap_463581','hap_50000','hap_50328','hap_56553','hap_71432','hap_74873', \
#        'hap_75070','hap_85018','hap_95476')

#####

def main():
    if len(sys.argv) != 5:
        sys.exit('./prog.py bsf_output_directory concat_output_emissions_file')
    
    in_dir   = sys.argv[1] # BSF output directory
    out_fn   = sys.argv[2] # formatted output file
    startDay = sys.argv[3] # e.g., '20230101', first day to include in YYYYMMDD format
    endDay   = sys.argv[4] # e.g., '20231031', last day to include in YYYYMMDD format
    
    print('WARNING: Check for duplicate fires by fips, scc, lat/lon, eventid, date_time, and area')
    curDate = date(int(startDay[:4]), int(startDay[4:6]), int(startDay[6:8]))
    endDate = date(int(endDay[:4]), int(endDay[4:6]), int(endDay[6:8]))
    df = pd.DataFrame()
    while curDate <= endDate:
        loc = pd.DataFrame()
        emis = pd.DataFrame()
        today = curDate.strftime('%Y%m%d')
        rx = read_loc(in_dir, today, 'rx')
        if not rx.empty:
            loc = pd.concat((loc, rx))
            emis = pd.concat((emis, read_emis(in_dir, today, 'rx')))
        wf = read_loc(in_dir, today, 'wf')
        if not wf.empty:
            loc = pd.concat((loc, wf))
            emis = pd.concat((emis, read_emis(in_dir, today, 'wf')))
        if loc.empty:
            pass
        else:
            #print(sum(loc['PM2.5'].fillna(0)))
            loc = pd.merge(loc, emis, on='id', how='left')
            df = pd.concat((df, loc))
            #print(sum(loc['PM2.5'].fillna(0)))
        curDate += timedelta(1)
    #print(sum(df['PM2.5'].fillna(0)))
    df = get_scc(df)
    # Use only the proper consumption phases 
    df.loc[df['scc'].str.endswith('2'), 'consumption_residual'] = 0
    df.loc[df['scc'].str.endswith('1'), ['consumption_flaming','consumption_smoldering']] = 0
    #print(sum(df['PM2.5'].fillna(0)))
    df.to_csv(out_fn, index=False)

def read_loc(in_dir, today, runtype):
    '''
    Read in the location information
    '''
    fn = os.path.join(in_dir, 'fire_locations_%s_%s.csv' %(today, runtype))
    use_cols = ['id','event_id','latitude','longitude','type','area','county',
      'consumption_flaming','consumption_smoldering','consumption_residual',
      'heat','fccs_number','fuelbed_fractions','event_name']
    dtype = {'county': str}
    try:
        df = pd.read_csv(fn, usecols=use_cols+polls, dtype=dtype)
    except FileNotFoundError:
        print('%s missing' %fn)
        return pd.DataFrame()
    print(fn)
    # Remove special characters from fire name
    '''
    sf = pd.read_csv('input/fire_locations_%s.csv' %today, usecols=['event_id','event_name'],
      dtype={'event_id': str, 'event_name': str})
    df = pd.merge(df, sf.drop_duplicates('event_id'), on='event_id', how='left')
    '''
    df['event_name'] = df['event_name'].astype(str).map(lambda x: re.sub(r',', '-', str(x)))
    df.insert(0, 'date', today)
    df.rename(columns={'county': 'fips'}, inplace=True)
    df['fips'] = df['fips'].str.zfill(5)
    for poll in polls:
        df.rename(columns={poll: poll.upper()}, inplace=True)
    return df

def read_emis(in_dir, today, runtype):
    '''
    Read in the emissions by phase
    Sum smoldering to  residual
    '''
    emis_polls = []
    for poll in polls:
        poll = poll.upper()
        if poll == 'NOX':
            poll = 'NOx'
        emis_polls.append(poll)    
    fn = os.path.join(in_dir, 'emissions_%s_%s.csv' %(today, runtype))
    use_cols = ['fire_id',]
    for phase in ('flame','smold','resid'):
        use_cols += ['%s_%s' %(pol, phase) for pol in emis_polls]
    try:
        df = pd.read_csv(fn, usecols=use_cols)
    except ValueError:
        return pd.DataFrame()
    except FileNotFoundError:
        print('Missing %s' %fn)
        return pd.DataFrame()
    df.rename(columns={'fire_id': 'id'}, inplace=True)
    df = df.groupby('id', as_index=False).sum()
    for pol in emis_polls:
        df['%s_flame' %pol] = df['%s_flame' %pol] + df['%s_smold' %pol]
        df['%s_smold' %pol] = df['%s_resid' %pol]
        df.drop('%s_resid' %pol, axis=1, inplace=True)
    df.rename(columns={'NOx_flame': 'NOX_flame', 'NOx_smold': 'NOX_smold'}, inplace=True)
    return df

def get_scc(df):
    '''
    Pivot out the flaming and smoldering into separate SCCs
    '''
    id_vars = ['date','id','event_id','latitude','longitude','type','area','fips',
      'consumption_flaming','consumption_smoldering','consumption_residual',
      'heat','fccs_number','fuelbed_fractions','event_name','scc']
    df['scc'] = '2811015000'
    df.loc[df['type'] == 'WF', 'scc'] = '2810001000'
    flame = df[id_vars + ['%s_flame' %pol.upper() for pol in polls]].copy()
    flame['scc'] = flame['scc'].str[:-1] + '2'
    smold = df[id_vars + ['%s_smold' %pol.upper() for pol in polls]].copy()
    smold['scc'] = smold['scc'].str[:-1] + '1'
    for pol in polls:
        pol = pol.upper()
        smold.rename(columns={'%s_smold' %pol: pol}, inplace=True)
        flame.rename(columns={'%s_flame' %pol: pol}, inplace=True)
    return pd.concat((flame, smold))


if __name__ == '__main__':
    main()




