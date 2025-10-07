#!/usr/bin/env python
# Convert the BSP loc file to FF10s

import sys
import csv
import os.path
from datetime import datetime
import numpy as np
import pandas as pd

def main():
    loc_name = sys.argv[1]
    prefix = sys.argv[2]
    workdir = sys.argv[3]
    ######################
    loc_df = get_loc_data(loc_name)
    caps = ['ACRESBURNED','HFLUX','PM2_5','PM10','NOX','SO2','NH3','CO','VOC','CO2','CH4']
    write_daily_ff10(loc_df[loc_df['poll'].isin(caps)].copy(), prefix, workdir)
    write_annual_ff10(loc_df[loc_df['poll'].isin(caps)], prefix, workdir)
    # Check for HAPS
    if len(loc_df[~ loc_df['poll'].str.upper().isin(caps)]) > 0:
        prefix += '_haps'
        write_daily_ff10(loc_df[~ loc_df['poll'].isin(caps)].copy(), prefix, workdir)
        write_annual_ff10(loc_df[~ loc_df['poll'].isin(caps)], prefix, workdir)

def get_loc_data(loc_name):
    '''
    Read in the aggregate location data
    '''
    key_cols = ['date','id','event_id','event_name','latitude','longitude','fips','scc','fccs_number','type']
    idx = key_cols + ['consumption_smoldering','consumption_residual','consumption_flaming']
    dtype={'fips': str, 'scc': str, 'date': str}
    loc_df = pd.read_csv(loc_name, dtype=dtype)
    loc_df.columns = [col.lower() for col in loc_df.columns]
    loc_df.rename(columns={'pm2.5': 'pm2_5', 'heat': 'hflux', 'area': 'acresburned'}, inplace=True)
    print('Dropping %s duplicate records' %len(loc_df[loc_df[['date','latitude','longitude','scc']].duplicated()]))
    loc_df.drop_duplicates(['date','latitude','longitude','scc'], inplace=True)
    print(sum(loc_df['nox'].fillna(0)))
    loc_df['fccs_number'] = loc_df['fccs_number'].fillna(0).astype('i')
    loc_df.drop(['consumption_smoldering','consumption_residual','consumption_flaming',
      'fuelbed_fractions'], axis=1, inplace=True)
    loc_df = pd.melt(loc_df, id_vars=key_cols, value_name='value', var_name='poll')
    loc_df = loc_df[loc_df['value'].fillna(0) > 0].copy()
    loc_df.rename(columns={'id': 'unit_id','event_id': 'facility_id','event_name': 'facility_name',
        'fips': 'region_cd', 'fccs_number': 'process_id'}, inplace=True)
    loc_df['month'] = loc_df['date'].str[4:6]
    loc_df['day'] = loc_df['date'].str[6:8]
    loc_df['calc_year'] = loc_df['date'].str[:4]
    loc_df.drop('date',axis=1,inplace=True)
    loc_df['poll'] = loc_df['poll'].apply(fix_poll)
    # Set HFLUX to 1000 BTU to force in ground layer for smoldering SCC/residual emissions
    loc_df.loc[(loc_df['poll'] == 'HFLUX') & (loc_df['scc'].str.endswith('1')), 'value'] = 1000.
    meta = loc_df[['month','day','facility_id','facility_name','region_cd','unit_id','latitude',
      'longitude','scc','calc_year','process_id']].drop_duplicates()
    loc_df = loc_df[['unit_id','scc','poll','value']].groupby(['unit_id','scc','poll'], as_index=False).sum()
    print(loc_df[loc_df['value'].isnull()])
    loc_df = pd.merge(loc_df, meta, on=['unit_id','scc'], how='left')
    loc_df['rel_point_id'] = loc_df['month'] + loc_df['day']
    loc_df.to_csv('loc_df.csv', index=False)
    loc_df['value'] = loc_df['value'].fillna(0).astype(float).round(6)
    loc_df.region_cd = loc_df.region_cd.astype(int).astype(str).str.zfill(6)
    
    #regioncd = str(loc_df.region_cd.values[0]) # Huy Tran 20250507: This original code may cause issue when a US region_cd is at position [0]
    ## To fix the issue, sort loc_df by reion_cd in descending order so that a CA region_cd will jump to top
    regioncd  = loc_df.sort_values(by='region_cd', ascending=False).region_cd.values[0]
    #print(regioncd)
    if regioncd[0] == '1':
        loc_df['country_cd'] = 'CA'
        print('Selecting CA only from %s fires' %len(loc_df))
        loc_df = loc_df[loc_df.region_cd.str.startswith('1')].copy()
    else:
        loc_df['country_cd'] = 'US'
        print('Selecting US only from %s fires' %len(loc_df))
        loc_df = loc_df[~ loc_df.region_cd.str.startswith('1')].copy()
    loc_df.region_cd = loc_df.region_cd.str[-5:]
    #print(len(loc_df))
    print('%s fires extracted' %len(loc_df))
    return loc_df

def write_daily_ff10(day_df, prefix, workdir):
    '''
    Write out the daily FF10
    '''
    day_df = day_df[['region_cd','facility_id','scc','poll','month','day','value',
      'unit_id','calc_year','rel_point_id','process_id','country_cd']].copy()
    year = day_df['calc_year'].values[0]
    day_df.drop('calc_year', axis=1, inplace=True)
    day_df['day'] = 'dayval' + day_df['day'].astype('i').astype(str)
    day_df = pd.pivot_table(day_df, values='value', index=['region_cd','facility_id','scc','poll',
        'month','unit_id','rel_point_id','process_id','country_cd'], columns='day')
    day_df['monthtot'] = day_df.sum(axis=1)
    day_df.reset_index(inplace=True)
    day_df['monthnum'] = day_df['month'].astype('i').astype(str)
    day_df.sort_values(['region_cd','facility_id','scc','poll','monthnum'], inplace=True)
    print(sum(day_df.loc[day_df['poll'] == 'NOX', 'monthtot']))
    print(day_df.columns)
    out_cols = ('country_cd','region_cd','tribal_code','facility_id','unit_id','rel_point_id','process_id',
      'scc','poll','op_type_cd','calc_method','date_updated','monthnum','monthtot','dayval1','dayval2',
      'dayval3','dayval4','dayval5','dayval6','dayval7','dayval8','dayval9','dayval10','dayval11',
      'dayval12','dayval13','dayval14','dayval15','dayval16','dayval17','dayval18','dayval19',
      'dayval20','dayval21','dayval22','dayval23','dayval24','dayval25','dayval26','dayval27',
      'dayval28','dayval29','dayval30','dayval31','comment')
    for col in out_cols:
        if col.startswith('dayval'):
            try:
                day_df[col].fillna(0, inplace=True)
            except Exception as e:
                print(f"Missing {e}. try to add one.")
                day_df[col] = 0
    print('Unique daily fires written: %s' %day_df[['facility_id','unit_id']].drop_duplicates().shape[0])
    for col in out_cols:
        if col not in list(day_df.columns):
            day_df[col] = ''
    if day_df.country_cd.values[0] == 'CA':
        country = 'CANADA'
    else:
        country = 'US'
    
    ## Write rx and wf separately
    wf_scc    = ['2810001001','2810001002']
    wf_day_df = day_df[day_df['scc'].astype(str).isin(wf_scc)].copy()
    rx_day_df = day_df[~day_df['scc'].astype(str).isin(wf_scc)].copy()
    
    rx = os.path.join(workdir, 'ptday_{}_rx_ff10.csv'.format(prefix))
    with open(rx, 'w') as daily:
        daily.write('#FORMAT=FF10_DAILY_POINT\n#COUNTRY=%s\n#YEAR=%s\n' %(country, year))
        rx_day_df.to_csv(daily, index=False, columns=out_cols)
        
    wf = os.path.join(workdir, 'ptday_{}_wf_ff10.csv'.format(prefix))
    with open(wf, 'w') as daily:
        daily.write('#FORMAT=FF10_DAILY_POINT\n#COUNTRY=%s\n#YEAR=%s\n' %(country, year))
        wf_day_df.to_csv(daily, index=False, columns=out_cols)        

def write_annual_ff10(day_df, prefix, workdir):
    '''
    Write out the annual FF10
    '''
    idx = ['region_cd','facility_id','scc','poll','facility_name','country_cd',
        'latitude','longitude','calc_year','unit_id','rel_point_id','process_id']
    ann_inv = day_df[idx+['value',]].copy()
    ann_inv[idx] = ann_inv[idx].fillna('')
    year = ann_inv['calc_year'].values[0]
    ann_inv = ann_inv.groupby(idx, as_index=False).sum()
    ann_inv.rename(columns={'value': 'ann_value'}, inplace=True)
    print('Unique annual fires read: %s' %ann_inv[['facility_id','unit_id']].drop_duplicates().shape[0])
    ann_inv['stkhgt'] = '1'
    ann_inv['stkdiam'] = '30'
    ann_inv['stktemp'] = '1'
    ann_inv['stkflow'] = '1'
    ann_inv['stkvel'] = '0.3'
    ann_inv['data_set_id'] = '%sEPAFIRE' %year
    ann_inv['latitude'] = ann_inv['latitude'].round(6)
    ann_inv['longitude'] = ann_inv['longitude'].round(6)
    ann_inv.sort_values(['region_cd','facility_id','unit_id','scc','poll'], inplace=True)
    print(sum(ann_inv.loc[ann_inv['poll'] == 'NOX', 'ann_value']))
    print('Unique annual fires written: %s' %ann_inv[['facility_id','unit_id']].drop_duplicates().shape[0])
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
    if ann_inv.country_cd.values[0] == 'CA':
        country = 'CANADA'
    else:
        country = 'US'
    
    ## Write rx and wf separately
    wf_scc    = ['2810001001','2810001002']
    wf_ann_inv = ann_inv[ann_inv['scc'].astype(str).isin(wf_scc)].copy()
    rx_ann_inv = ann_inv[~ann_inv['scc'].astype(str).isin(wf_scc)].copy()
    
    rx = os.path.join(workdir, 'ptinv_{}_rx_ff10.csv'.format(prefix))
    with open(rx, 'w') as annual:
        annual.write('#FORMAT=FF10_POINT\n#COUNTRY=%s\n#YEAR=%s\n' %(country, year))
        rx_ann_inv.to_csv(annual, index=False, columns=out_cols, quoting=csv.QUOTE_NONNUMERIC)
        
    wf = os.path.join(workdir, 'ptinv_{}_wf_ff10.csv'.format(prefix))
    with open(wf, 'w') as annual:
        annual.write('#FORMAT=FF10_POINT\n#COUNTRY=%s\n#YEAR=%s\n' %(country, year))
        wf_ann_inv.to_csv(annual, index=False, columns=out_cols, quoting=csv.QUOTE_NONNUMERIC)        

def fix_poll(poll):
    '''
    Rename specific pollutants to SMOKE inventory name
    '''
    poll = poll.upper()
    if poll == 'AREA':
        poll = 'ACRESBURNED'
    elif poll == 'HEAT':
        poll = 'HFLUX'
    elif poll == 'PM25':
        poll = 'PM2_5'
    elif poll.startswith('HAP'):
        poll = poll.split('_')[1]
    return poll

main()
