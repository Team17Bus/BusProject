import pandas as pd
import sys

date = sys.argv[1]

dir_final = 'BusProject/arrival_matches_asb/'+date+'.csv'

dir_0 = 'BusProject/arrival_matches_asb/'+date+'0.csv'
dir_1 = 'BusProject/arrival_matches_asb/'+date+'50.csv'
dir_2 = 'BusProject/arrival_matches_asb/'+date+'100.csv'
dir_3 = 'BusProject/arrival_matches_asb/'+date+'150.csv'
dir_4 = 'BusProject/arrival_matches_asb/'+date+'200.csv'
dir_5 = 'BusProject/arrival_matches_asb/'+date+'250.csv'

directories = [dir_1,dir_2,dir_3,dir_4,dir_5]

match_df = pd.read_csv(dir_0, sep=";")
match_df = match_df.dropna(subset=['stop_seq'])

for d in directories:
    add_df = pd.read_csv(d, sep=";")
    add_df = add_df.dropna(subset=['stop_seq'])
    match_df.append(add_df)

match_df.to_csv(dir_final,sep=';',index=False)