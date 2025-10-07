#!/usr/bin/env python

import pandas as pd

fh_counties = ['20015','20017','20019','20031','20035','20049','20061','20073','20111','20115',
  '20017','20127','20139','20149','20161','20197','20205','20207','40071','40105','40113','40147']
fh_dates = [x.strftime('%Y%m%d') for x in list(pd.date_range('20210203','20230501'))]
fn = 'hms_2023_fccscdl_grass.csv'
dtype = {'YearDay': str, 'fips': str, 'gday': str, 'fccs': str, 'Ecosys': str, 'Time': str}
df = pd.read_csv(fn, dtype=dtype)
idx = ((df['gday'].isin(fh_dates)) & (df['fips'].astype(int).astype(str).str.zfill(5).isin(fh_counties)))
df[idx].to_csv('hms_2023_fccscdl_grass_fh.csv', index=False)
df[~ idx].to_csv('hms_2023_fccscdl_grass_nofh.csv', index=False)

