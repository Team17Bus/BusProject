import pandas as pd
import sys

date = sys.argv[1]

dir_final = 'BusProject/online_data/arrival_matches' + date + '.csv'


dir_0 = 'BusProject/online_data/arrival_matches' + date + '0.csv'
dir_1 = 'BusProject/online_data/arrival_matches' + date + '50.csv'
dir_2 = 'BusProject/online_data/arrival_matches' + date + '100.csv'
dir_3 = 'BusProject/online_data/arrival_matches' + date + '150.csv'
dir_4 = 'BusProject/online_data/arrival_matches' + date + '200.csv'
dir_5 = 'BusProject/online_data/arrival_matches' + date + '250.csv'

directories = [dir_1, dir_2, dir_3, dir_4, dir_5]

match_df = pd.read_csv(dir_0, sep=";")
    # match_df = match_df.dropna(subset=['stop_seq'])

for d in directories:
    add_df = pd.read_csv(d, sep=";")
    add_df = add_df.dropna(subset=['scheduled_time'])
    match_df = pd.concat([match_df, add_df])
    print(add_df.size)
    print(match_df.size)

match_df.to_csv(dir_final, sep=';', index=False)
