import pandas as pd
import datetime
from schedule_matching_online import match_schedule2
import sys

debug = True


def convert_dtype(x):
    if not x:
        return ''
    try:
        return float(x)
    except:
        return ''


info = sys.argv[1].split(',')

file = info[0]
today = info[1]+' '
start = info[2]

#file = '8-9dec'
#stop = '8-9dec'
#today = '2020_12_09'+' '
#start = 0

dir_schedule_today = 'BusProject/online_data/stop_times'+file+'.csv'
#dir_schedule_today = 'online_data/stop_times' + stop + '.csv'

today = today+' '

dir_arrivals = 'BusProject/online_data/arrival_estimations_'+file+'.csv'
dir_matches = 'BusProject/online_data/arrival_matches'+file+start+'.csv'
#dir_arrivals = 'online_data/arrival_estimations_' + file + '.csv'
#dir_matches = 'online_data/arrival_matches_'+file+'a.csv'

data_stop_times = pd.read_csv(dir_schedule_today, sep=',',
                              names=['lines','bus_brigade','arrival_time','stop_id','stop_sequence'],
                              dtype={'lines':str, 'arrival_time':str ,'stop_id':str,})

data_stop_times['arrival_time'] = pd.to_datetime(today + data_stop_times['arrival_time'],
                                                 format='%Y_%m_%d %H:%M:%S')

if debug: print(data_stop_times.head())

# load arrivals
online_arrivals = pd.read_csv(dir_arrivals, ',',
                              names=['bus_line', 'bus_brigade', 'bus_id', 'stop_zespol', 'stop_slupek', 'location',
                                     'arrival_time', 'scheduled_time'],
                              dtype={'bus_line': str, 'stop_zespol': str, 'stop_slupek':str},
                              converters={'bus_brigade': convert_dtype}, index_col=False
                              )

#online_arrivals['stop_zespol'] = online_arrivals['stop_zespol'].astype(str)
#online_arrivals['stop_zespol'] = online_arrivals['stop_zespol'].astype(str)

online_arrivals = online_arrivals[online_arrivals['scheduled_time'].isnull()]

print(online_arrivals.info())

online_arrivals['stop_id'] = online_arrivals['stop_zespol'].astype(str)+'_'+online_arrivals['stop_slupek'].astype(str)
#online_arrivals['stop_id'] = online_arrivals[['stop_zespol','stop_slupek']].agg('_'.join,axis=1)
online_arrivals['arrival_time'] = pd.to_datetime(online_arrivals['arrival_time'], format='%Y-%m-%d %H:%M:%S')
online_arrivals['stop_seq'] = ""

print(online_arrivals.iloc[100])

# select only the arrivals between 5:00 and 23:00 of today
min_str = today + ' 04:59:59'
max_str = today + ' 23:00:00'

min = datetime.datetime.strptime(min_str, '%Y_%m_%d %H:%M:%S')
max = datetime.datetime.strptime(max_str, '%Y_%m_%d %H:%M:%S')

online_arrivals = online_arrivals[online_arrivals['arrival_time']<max]
online_arrivals = online_arrivals[online_arrivals['arrival_time']>min]

#online_arrivals = online_arrivals[online_arrivals['bus_line'] == "123"]
#online_arrivals = online_arrivals[online_arrivals['bus_brigade'] == 5.0]

online_arrivals = online_arrivals.sort_values(by='arrival_time',ascending=True)

print(online_arrivals.head())
print(data_stop_times.head())

match_schedule2(data_stop_times, online_arrivals, dir_matches, int(start))
online_arrivals = online_arrivals.dropna(subset=['scheduled_time'])
online_arrivals.to_csv(dir_matches, ';', index=False)

if debug: print(online_arrivals.head())
