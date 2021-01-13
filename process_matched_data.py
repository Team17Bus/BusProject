import pandas as pd
from datetime import datetime
import numpy as np
from collections import defaultdict

debug_with_one_line_one_brigade = False
debug_line = 109
debug_brigade = 50

historical_data = True  # False if using online data

# TODO: make work for online arrivals / schedules
# problem: no stop_seq --> should start over with delay diff if seq starts over, but not possible with online data...

# goal: assign delay difference to edges between stops

# result: delay_diff_dict
# key: (line, brigade)
# values: list of dataFrames, with
#       stop_from  stop_to  delay_diff  stop_seq_diff  avg_delay_diff
#   as columns
#   one dataFrame per run
# see below (bottom) for sample output

pd.set_option("display.max_columns", None)

if historical_data:

    # import arrivals
    arr = pd.read_csv("arrival_matches_01-09-2020_2130 (subset).csv", sep=';', header=0)
    arr = arr[arr['scheduled_time'].notnull()]

    """ Not necessary
    # import schedule
    sched = pd.read_csv("stop_times.txt", sep=",")

    # split trip_id column into line - brigade
    trip_id = sched['trip_id'].str.split('_', expand=True)
    sched['line'] = trip_id.iloc[:, 0]
    sched['brigade'] = trip_id.iloc[:, 1]
    sched['start_time'] = trip_id.iloc[:, 3]
    """

    # get all combinations of line and brigade in arrivals:
    arr.groupby(by=['bus_line', 'bus_brigade']).size()

    if debug_with_one_line_one_brigade:
        arr = arr.loc[(arr['bus_brigade'] == debug_brigade) & (arr['bus_line'] == debug_line)] # TODO: put 'debug_brigade' when excel error has been fixed
        #sched = sched.loc[(sched['brigade'] == str(debug_brigade)) & (sched['line'] == str(debug_line))]


    # add column with absolute delays
    arr['arrival_time'] = arr['arrival_time'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S'))
    arr['scheduled_time'] = arr['scheduled_time'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S'))
    arr['absolute_delay_sec'] = arr['arrival_time'] - arr['scheduled_time']
    arr['absolute_delay_sec'] = arr['absolute_delay_sec'].apply(lambda x: abs(x.total_seconds()))   # in seconds
    arr['absolute_delay_min'] = arr['absolute_delay_sec'] / 60                                      # in minutes
    arr = arr.round({'absolute_delay_sec': 0, 'absolute_delay_min': 2})

    # add column with relative delays and number of stops in between
    arr['relative_delay_sec'] = pd.Series([], dtype='float')
    arr['stop_seq_diff'] = pd.Series([], dtype='int')           # if stop is just after next one (ideal), this value is 1; if one stop is skipped, value is 2.

    if debug_with_one_line_one_brigade:
        arr = arr.reset_index(drop=True)
        begin_indices_debug = [0]

        prev_stop_seq = arr.iloc[0]['stop_seq']
        prev_delay = arr.iloc[0]['absolute_delay_sec']
        for i in range(1, len(arr)):
            curr_arr = arr.iloc[i]
            curr_stop_seq = curr_arr.loc['stop_seq']
            curr_delay = curr_arr.loc['absolute_delay_sec']
            if curr_stop_seq < prev_stop_seq:   # sequence starts over
                begin_indices_debug.append(i)
            else:
                stop_seq_diff = curr_stop_seq - prev_stop_seq
                arr.iloc[i, arr.columns.get_indexer(['stop_seq_diff'])] = stop_seq_diff
                arr.iloc[i, arr.columns.get_indexer(['relative_delay_sec'])] = curr_delay - prev_delay
            prev_stop_seq = curr_stop_seq
            prev_delay = curr_delay

        # split dataframe into seperate runs
        splits = begin_indices_debug + [len(arr)]
        all_runs = [arr.iloc[splits[n]:splits[n + 1]] for n in range(len(splits) - 1)]
        runs = [all_runs[i] for i in range(len(all_runs)) if len(all_runs[i]) > 1]

        # use list comprehension to come up with stop_from stop_to delay_diff stop_seq_diff avg_delay_diff for each run
        delay_diff_dict_debug = dict()
        k = (debug_line, debug_brigade)

        delay_diff_dict_debug[k] = [pd.DataFrame(
            [[runs[r].iloc[i]['stop_id'],
              runs[r].iloc[i+1]['stop_id'],
              runs[r].iloc[i+1]['relative_delay_sec'],
              runs[r].iloc[i+1]['stop_seq_diff'],
              runs[r].iloc[i+1]['relative_delay_sec']/runs[r].iloc[i+1]['stop_seq_diff']]
             for i in range(len(runs[r])-1)],
            columns=['stop_from', 'stop_to', 'delay_diff', 'stop_seq_diff', 'avg_delay_diff'])
            for r in range(len(runs))]


    combos = arr.loc[:, ['bus_line', 'bus_brigade']].drop_duplicates()
    delay_diff_dict = dict()   # stores: list of dataframes: stop_from stop_to delay_diff stop_seq_diff avg_delay_diff; (line, brigade) as keys
                                           # each dataframe corresponds to a run (complete stop sequence)
    for i in range(len(combos)):
        line = combos.iloc[i]['bus_line']
        brigade = combos.iloc[i]['bus_brigade']

        sub_arr = arr.loc[(arr['bus_brigade'] == brigade) & (arr['bus_line'] == line)]
        sub_arr = sub_arr.reset_index(drop=True)

        begin_indices = [0]

        prev_stop_seq = sub_arr.iloc[0]['stop_seq']
        prev_delay = sub_arr.iloc[0]['absolute_delay_sec']
        for i in range(1, len(sub_arr)):
            curr_arr = sub_arr.iloc[i]
            curr_stop_seq = curr_arr.loc['stop_seq']
            curr_delay = curr_arr.loc['absolute_delay_sec']
            if curr_stop_seq < prev_stop_seq:   # sequence starts over
                begin_indices.append(i)
            else:
                stop_seq_diff = curr_stop_seq - prev_stop_seq
                sub_arr.iloc[i, sub_arr.columns.get_indexer(['stop_seq_diff'])] = stop_seq_diff
                sub_arr.iloc[i, sub_arr.columns.get_indexer(['relative_delay_sec'])] = curr_delay - prev_delay
            prev_stop_seq = curr_stop_seq
            prev_delay = curr_delay

        # split dataframe into seperate runs
        splits = begin_indices + [len(sub_arr)]
        all_runs = [sub_arr.iloc[splits[n]:splits[n + 1]] for n in range(len(splits) - 1)]
        runs = [all_runs[i] for i in range(len(all_runs)) if len(all_runs[i]) > 1]

        # use list comprehension to come up with stop_from stop_to delay_diff stop_seq_diff avg_delay_diff for each run
        delay_diff_dict[(line, brigade)] = [pd.DataFrame(
            [[runs[r].iloc[i]['stop_id'],
              runs[r].iloc[i + 1]['stop_id'],
              runs[r].iloc[i + 1]['relative_delay_sec'],
              runs[r].iloc[i + 1]['stop_seq_diff'],
              runs[r].iloc[i + 1]['relative_delay_sec'] / runs[r].iloc[i + 1]['stop_seq_diff']]
             for i in range(len(runs[r]) - 1)],
            columns=['stop_from', 'stop_to', 'delay_diff', 'stop_seq_diff', 'avg_delay_diff'])
            for r in range(len(runs))]


""" example output of delay_diff_dict

(109, 30): 
  [   stop_from  stop_to  delay_diff  stop_seq_diff  avg_delay_diff
  0    5034_01  5033_01         2.0            1.0             2.0
  1    5033_01  5194_51        18.0            1.0            18.0
  2    5194_51  5032_51        65.0            1.0            65.0
  3    5032_51  5031_01       -70.0            1.0           -70.0
  4    5031_01  5030_01        -1.0            1.0            -1.0
  5    5030_01  5020_55       -13.0            1.0           -13.0
  6    5020_55  5019_51       104.0            1.0           104.0
  7    5019_51  5008_05       -48.0            1.0           -48.0
  8    5008_05  5044_51        22.0            2.0            11.0
  9    5044_51  5042_01        93.0            2.0            46.5
  10   5042_01  7088_01         4.0            4.0             1.0
  11   7088_01  7002_01        45.0            2.0            22.5
  12   7002_01  7013_05        44.0            2.0            22.0
  13   7013_05  7033_01       -11.0            1.0           -11.0
  14   7033_01  7040_04        -4.0            2.0            -2.0
  15   7040_04  7069_01        -3.0            2.0            -1.5
  16   7069_01  7070_01       -29.0            1.0           -29.0
  17   7070_01  7092_01        41.0            1.0            41.0
  18   7092_01  7077_01         8.0            1.0             8.0
  19   7077_01  7076_03       -20.0            2.0           -10.0
  20   7076_03  7076_07       100.0            1.0           100.0,   
  
  stop_from  stop_to  delay_diff  stop_seq_diff  avg_delay_diff
  0   7071_04  7069_04        81.0            2.0       40.500000
  1   7069_04  7033_02      -104.0            3.0      -34.666667],
 
 
 (106, 10): 
  [  stop_from  stop_to  delay_diff  stop_seq_diff  avg_delay_diff
  0   5038_02  5005_06       157.0            2.0            78.5
  1   5005_06  5026_04       -73.0            1.0           -73.0
  2   5026_04  5112_02        47.0            1.0            47.0
  3   5112_02  5067_07        14.0            1.0            14.0,    
  
  stop_from  stop_to  delay_diff  stop_seq_diff  avg_delay_diff
  0    5095_01  5037_01       -54.0            1.0      -54.000000
  1    5037_01  5193_01        44.0            1.0       44.000000
  2    5193_01  5036_01         8.0            1.0        8.000000
  3    5036_01  7087_01       -51.0            1.0      -51.000000
  4    7087_01  7025_03        35.0            1.0       35.000000
  5    7025_03  7015_03         5.0            1.0        5.000000
  6    7015_03  7028_01       -10.0            1.0      -10.000000
  7    7028_01  7044_01        99.0            1.0       99.000000
  8    7044_01  7043_03       -64.0            2.0      -32.000000
  9    7043_03  7062_02       -43.0            3.0      -14.333333
  10   7062_02  7061_02       198.0            1.0      198.000000],
 
 (102, 30): 
  [  stop_from  stop_to  delay_diff  stop_seq_diff  avg_delay_diff
  0   2109_02  2108_05        46.0            1.0            46.0
  1   2108_05  2108_04       266.0            1.0           266.0,    
  
  stop_from  stop_to  delay_diff  stop_seq_diff  avg_delay_diff
  0    2109_03  2111_01      -559.0            2.0          -279.5
  1    2111_01  2114_01       -18.0            2.0            -9.0
  2    2114_01  2115_01         2.0            1.0             2.0
  3    2115_01  2116_01         1.0            1.0             1.0
  4    2116_01  2006_05         5.0            1.0             5.0
  5    2006_05  2127_01        44.0            1.0            44.0
  6    2127_01  2133_01       -12.0            1.0           -12.0
  7    2133_01  2131_01       -39.0            3.0           -13.0
  8    2131_01  2399_02        21.0            1.0            21.0
  9    2399_02  1232_03         1.0            1.0             1.0
  10   1232_03  7079_04        97.0            1.0            97.0
  11   7079_04  7067_02       -52.0            2.0           -26.0
  12   7067_02  7043_04         1.0            2.0             0.5
  13   7043_04  7044_02       -31.0            2.0           -15.5
  14   7044_02  7028_02       -24.0            1.0           -24.0
  15   7028_02  7015_04        65.0            1.0            65.0
  16   7015_04  7025_02         5.0            1.0             5.0
  17   7025_02  7001_01        96.0            2.0            48.0,   
  
  stop_from  stop_to  delay_diff  stop_seq_diff  avg_delay_diff
  0   7001_02  7025_01        19.0            1.0            19.0
  1   7025_01  7015_03        -5.0            2.0            -2.5
  2   7015_03  7028_01        90.0            1.0            90.0
  3   7028_01  7044_01        14.0            1.0            14.0],
 
 
 (102, 20): 
 [  stop_from  stop_to  delay_diff  stop_seq_diff  avg_delay_diff
  0   2113_04  2112_02        -1.0            1.0            -1.0,   
  
  stop_from  stop_to  delay_diff  stop_seq_diff  avg_delay_diff
  0   2006_05  2127_01        35.0            1.0       35.000000
  1   2127_01  2132_01       -23.0            2.0      -11.500000
  2   2132_01  2131_01       -94.0            2.0      -47.000000
  3   2131_01  2399_02       112.0            1.0      112.000000
  4   2399_02  2399_01         0.0            1.0        0.000000
  5   2399_01  7067_02      -112.0            3.0      -37.333333
  6   7067_02  7043_04        56.0            2.0       28.000000
  7   7043_04  7044_02       -28.0            2.0      -14.000000
  8   7044_02  7028_02        -9.0            1.0       -9.000000],


"""

