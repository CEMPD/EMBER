#!/usr/bin/env python

import sys
import pandas as pd

def summary(df):
    df['fips'] = df['fips'].str[:2]
    cnt = df[['fips','NOX']].groupby('fips', as_index=False).count()
    cnt.rename(columns={'NOX': 'count'}, inplace=True)
    emis = df[['fips','area','PM2.5','CO','NOX']].groupby('fips', as_index=False).sum()
    df = pd.merge(cnt, emis, on='fips', how='outer')
    return df

fn = sys.argv[1]
out_fn = sys.argv[2]
dup_fn = sys.argv[3]
zer_fx = sys.argv[4]
df = pd.read_csv(fn, dtype={'date': str, 'fips': str, 'scc': str, 'event_name': str})
print(len(df), sum(df['NOX'].fillna(0)))
idx = df['fips'].astype(str).str.endswith('OOB')
print('Dropping %s OOB' %len(df[idx]))
df = df[~ idx].copy()
cols = list(df.columns)
df_t = summary(df.copy())
df_s = summary(df[df.duplicated(['scc','date','latitude','longitude'])].copy())
df[df.duplicated(['scc','date','latitude','longitude'])].to_csv('raw_dupes.csv', index=False)
tot = pd.merge(df_s, df_t, on='fips', how='outer', suffixes=['_d','_tot'])
tot = tot[tot['count_d'].notnull()].copy()
print('  - %s' %sum(tot['NOX_d'].fillna(0)))
tot.to_csv(dup_fn, index=False)
df.drop_duplicates(['fips','area','scc','date','latitude','longitude'], inplace=True)
print(len(df), sum(df['NOX'].fillna(0)))
# Drop entries with 0 emissions
df['sum'] = df[['PM10','NOX','CO','VOC']].sum(axis=1)
df[df['sum'] == 0].to_csv(zer_fx, index=False)
df = df[df['sum'] > 0].copy()
print(len(df), sum(df['NOX'].fillna(0)))
df.to_csv(out_fn, index=False, columns=cols)
