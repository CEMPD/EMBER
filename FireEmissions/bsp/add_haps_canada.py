#!/usr/bin/env python
# Add HAP values to the loc file for CANADA

import sys
import pandas as pd

def main():
    print('FOR CANADA ONLY')
    dtype = {'date': str, 'id': str, 'scc': str, 'fips': str, 'fccs_number': str, 'VEG': str}
    df = pd.read_csv(sys.argv[1], dtype=dtype)
    cons = get_cons(df)
    print(len(df))
    # Read in the regionalized HAP factors (lb/ton consumed)
    haps =  pd.read_csv('/proj/ie/proj/GSA-EMBER/BlueSky/ember_2023/haps/hapfactors_2014_mt_form_adj.csv', dtype={'poll': str})
    # Read in the phased lead factors (mg Pb/kg consumed) by state and phase
    lead = get_lead('lead_factors_2020.txt')
    print(cons.head())
    cons['state'] = 'MT'
    # Calc the HAP emis -- use MT as the HAP state (upper MW and Rockies all have same HAPS)
    haps = pd.merge(cons, haps[haps['state'] == 'MT'], on='type', how='left')
    # Multiply HAP factor by tons fuel consumed and divide by 2000 to get tons
    haps['emis'] = haps['factor'] * haps['cons'] / 2000.
    # Calc the Lead emis -- also use MT
    lead = pd.merge(cons, lead, on='state', how='left')
    lead['emis'] = (lead['consumption_flaming'] * lead['flaming_pb']) + (lead['consumption_smoldering'] * lead['smolder_pb']) +\
      (lead['consumption_residual'] * lead['smolder_pb'])
    haps = pd.concat((haps[['id','scc','poll','emis']], lead[['id','scc','poll','emis']]))
    haps = haps.groupby(['id','scc','poll'], as_index=False).sum()
    haps = pd.pivot_table(haps, index=['id','scc'], values='emis', columns='poll', fill_value=0)
    haps.reset_index(inplace=True)
    df = pd.merge(df, haps, on=['id','scc'], how='inner')
    print(len(df))
    print(sum(df['463581']))
    df.columns = [col.lower() for col in list(df.columns)]
    df.to_csv(sys.argv[2], index=False)

def get_cons(df):
    '''
    Get the consumption values from the post-bsp file
    '''
    cons = df[['id','scc','area','type','fips','consumption_flaming','consumption_smoldering',
      'consumption_residual']].copy()
    cons['stfips'] = cons['fips'].str[:2]
    cons['cons'] = cons[['consumption_flaming','consumption_smoldering',
      'consumption_residual']].fillna(0).sum(axis=1)
    return cons

def get_lead(fn):
    '''
    Get the lead factors and adjust
    '''
    df = pd.read_csv(fn)
    df['poll'] = '7439921'
    df.rename(columns={'flaming_mgpb_kgconsume': 'flaming_pb', 'smoldering_mgpb_kgconsume': 'smolder_pb'}, 
      inplace=True)
    # convert mg/kg to tons/ton
    df['flaming_pb'] = df['flaming_pb'] * 1e-6
    df['smolder_pb'] = df['smolder_pb'] * 1e-6
    return df

if __name__ == '__main__':
    main()
