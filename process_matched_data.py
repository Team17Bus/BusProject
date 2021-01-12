import pandas as pd
from datetime import datetime, timedelta

debug_with_one_line_one_brigade = True
debug_line = 102
debug_brigade = 5  # conversion error in excel: 5.0 became 50 in arr dataFrame

historical_data = True # False if using online data
# TODO: make work for online arrivals / schedules

# goal: assign delay difference to edges between stops

pd.set_option("display.max_columns", None)

# import arrivals
arr = pd.read_csv("arrival_matches_01-09-2020_2130 (subset).csv", sep=';', header=0)

arr = arr[arr['scheduled_time'].notnull()]

# import schedule
sched = pd.read_csv("stop_times.txt", sep=",")

# split trip_id column into line - brigade
trip_id = sched['trip_id'].str.split('_', expand=True)
sched['line'] = trip_id.iloc[:, 0]
sched['brigade'] = trip_id.iloc[:, 1]
sched['start_time'] = trip_id.iloc[:, 3]

# get all combinations of line and brigade in arrivals:
# arr.groupby(by=['bus_line', 'bus_brigade']).size()

if debug_with_one_line_one_brigade:
    arr = arr.loc[(arr['bus_brigade'] == 50) & (arr['bus_line'] == debug_line)] # TODO: put 'debug_brigade' when excel error has been fixed
    sched = sched.loc[(sched['brigade'] == str(debug_brigade)) & (sched['line'] == str(debug_line))]


# add column with absolute delays
arr['arrival_time'] = arr['arrival_time'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S'))
arr['scheduled_time'] = arr['scheduled_time'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S'))

