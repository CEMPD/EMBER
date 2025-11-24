#!/usr/bin/env python

import sys
import pandas as pd

usecols = ['event_id','type','area','county','date_time']
dtype = {'id': str, 'event_id': str, 'event_name': str, 'county': str, 'date_time': str}
loc = pd.read_csv(sys.argv[1], usecols=usecols, dtype=dtype)
print(sum(loc['area'].fillna(0)))
loc['month'] = loc['date_time'].str[4:6]
usecols = ['id','event_name','sources']
eve = pd.read_csv(sys.argv[2], usecols=usecols, dtype=dtype)
eve.rename(columns={'id': 'event_id'}, inplace=True)
eve.drop_duplicates('event_id', inplace=True)
idx = ['event_id','county','month','type']
for col in idx:
    loc[col] = loc[col].fillna('')
loc = loc[idx+['area',]].groupby(idx, as_index=False).sum()
loc = pd.merge(loc, eve, on='event_id', how='left')
loc['state_province'] = loc['county'].str[:3]
fn = '/proj/ie/proj/GSA-EMBER/BlueSky/from_EPA/ember_package/sf2/exports/summaries/flat_costcy_07dec2021.csv'
usecols = ['region_cd','country','stabbr']
dtype = {'region_cd': str}
costcy = pd.read_csv(fn, usecols=usecols, dtype=dtype)
costcy['state_province'] = costcy['region_cd'].str[:3]
loc = pd.merge(loc, costcy.drop_duplicates('state_province'), on='state_province')
print(sum(loc['area'].fillna(0)))
loc.to_csv(sys.argv[3], index=False)
