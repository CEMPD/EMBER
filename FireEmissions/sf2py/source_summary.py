#!/usr/bin/env python

import sys
import pandas as pd

usecols = ['id','event_id','type','area','county','date_time']
dtype = {'id': str, 'event_id': str, 'event_name': str, 'county': str, 'date_time': str}
loc = pd.read_csv(sys.argv[1], usecols=usecols, dtype=dtype)
print(sum(loc['area'].fillna(0)))
fips = loc[['event_id','county','area']].copy()
fips['state_province'] = fips['county'].str.zfill(6).str[:3]
fips = fips.groupby(['event_id','state_province'], as_index=False).sum()
fips = fips.sort_values('area', ascending=False).drop_duplicates('event_id', keep='first')
sd = loc[['event_id','date_time']].sort_values('date_time', ascending=True).drop_duplicates('event_id', keep='first')
ed = loc[['event_id','date_time']].sort_values('date_time', ascending=False).drop_duplicates('event_id', keep='first')
loc.drop_duplicates('id', inplace=True)
usecols = ['id','event_name','sources']
eve = pd.read_csv(sys.argv[2], usecols=usecols, dtype=dtype)
eve.rename(columns={'id': 'event_id'}, inplace=True)
eve.drop_duplicates('event_id', inplace=True)
loc = loc[['event_id','type','area']].groupby(['event_id','type'], as_index=False).sum()
loc = pd.merge(loc, eve, on='event_id', how='left')
loc = pd.merge(loc, fips[['event_id','state_province']], on='event_id', how='left')
loc = pd.merge(loc, sd, on='event_id', how='left')
loc = pd.merge(loc, ed, on='event_id', how='left', suffixes=['_start','_end'])
fn = '/proj/ie/proj/GSA-EMBER/BlueSky/from_EPA/ember_package/sf2/exports/summaries/flat_costcy_07dec2021.csv'
usecols = ['region_cd','country','stabbr']
dtype = {'region_cd': str}
costcy = pd.read_csv(fn, usecols=usecols, dtype=dtype)
costcy['state_province'] = costcy['region_cd'].str[:3]
loc = pd.merge(loc, costcy.drop_duplicates('state_province'), on='state_province')
print(sum(loc['area'].fillna(0)))
loc.to_csv(sys.argv[3], index=False)
