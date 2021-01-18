import pandas as pd
from datetime import datetime, time
import numpy as np
import sys

def edges_transform(filename, folder_in, folder_out):

    debug_with_one_line_one_brigade = False
    debug_line = 109
    debug_brigade = 50

    print_progress = True

    # TODO: make work for online arrivals / schedules
    # problem: no stop_seq --> should start over with delay diff if seq starts over, but not possible with online data...

    # goal 1: assign delay difference to edges between stops

    # result 1: delay_diff_dict
    # key: (line, brigade)
    # values: list of dataFrames, with
    #       stop_from_id  stop_from_loc stop_to_id  stop_to_loc delay_diff  stop_seq_diff  avg_delay_diff line brigade sched_date, sched_time
    #   as columns
    #   one dataFrame per run
    # see below (bottom) for sample output

    # goal 2: discretize data & normalize (according to szymanski et al)

    pd.set_option("display.max_columns", None)

    "filename ex: 2020_09_01.csv"

    date = filename.split('.')[0]
    print(date)

    # import arrivals
    if len(folder_in) == 0:
        arr = pd.read_csv(filename, sep=';', header=0)
    else:
        arr = pd.read_csv(folder_in + '/' + filename, sep=';', header=0)
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
    #arr['arrival_time'] = arr['arrival_time'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S.%f'))
    #arr['scheduled_time'] = arr['scheduled_time'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S'))
    arr['arrival_time'] = pd.to_datetime(arr['arrival_time'], format='%Y-%m-%d %H:%M:%S')
    arr['scheduled_time'] = pd.to_datetime(arr['scheduled_time'], format='%Y-%m-%d %H:%M:%S')

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

    num_combos = len(combos)

    for i in range(len(combos)):
        if print_progress:
            print(f'{i} / {num_combos}')
        line = combos.iloc[i]['bus_line']
        brigade = combos.iloc[i]['bus_brigade']

        sub_arr = arr.loc[(arr['bus_brigade'] == brigade) & (arr['bus_line'] == line)]

        if len(sub_arr) == 0:
            continue

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
              runs[r].iloc[i]['location'],
              runs[r].iloc[i + 1]['stop_id'],
              runs[r].iloc[i + 1]['location'],
              runs[r].iloc[i + 1]['relative_delay_sec'],
              runs[r].iloc[i + 1]['stop_seq_diff'],
              runs[r].iloc[i + 1]['relative_delay_sec'] / runs[r].iloc[i + 1]['stop_seq_diff'],
              runs[r].iloc[i + 1]['relative_delay_sec'] / runs[r].iloc[i + 1]['stop_seq_diff'] / 60.0,
              line,
              brigade,
              runs[r].iloc[i + 1]['scheduled_time'],
              runs[r].iloc[i + 1]['scheduled_time'].date(),
              runs[r].iloc[i + 1]['scheduled_time'].time()]
             for i in range(len(runs[r]) - 1)],
            columns=['stop_from_id', 'stop_from_loc', 'stop_to_id', 'stop_to_loc', 'delay_diff', 'stop_seq_diff', 'avg_delay_diff_sec', 'avg_delay_diff_min', 'line', 'brigade', 'sched_datetime', 'sched_date', 'sched_time'])
            for r in range(len(runs))]


    # concat all dataFrames
    df = pd.concat([delay_diff_dict[k][r] for k in delay_diff_dict for r in range(len(delay_diff_dict[k]))],
                   axis=0).reset_index(drop=True)

    df = df.drop(df[df['stop_seq_diff'] == 0].index)  # a very small number of rows have this

    df.to_csv(folder_out + '/' + 'delays_edges_' + filename, index=False)

    # ---------------------------------------------------------------------------------------------

# part 2 (discretization & normalization)

def discretize_normalize(df):
    # date_time_object.time()
    bins_timeofday = [time(x[0], x[1]) for x in [(5, 0), (7, 0), (9, 0), (16, 0), (18, 30), (22, 0)]]
    bins_delay_diff = [-60.0, -30.5, -20.5, -15.5, -10.5, -5.5, -4.5, -3.5, -2.5, -1.5, -0.5, 0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 10.5, 15.5, 20.5, 30.5, 60.0]

    delay_cut = pd.cut(df['avg_delay_diff_min'], bins=bins_delay_diff)
    delay_cut_counts = delay_cut.value_counts()
    delay_cats = delay_cut.cat.categories

    def timeofday_binning(t):
        bool_arr = t < np.array(bins_timeofday)
        true_arr = bool_arr.nonzero()[0]
        if len(true_arr) == 0:
           interval = (bins_timeofday[len(bins_timeofday) - 1], time(23, 59))
        else:
            index = true_arr[0]
            if index == 0:
                interval = (time(0, 0), bins_timeofday[index])
            else:
                interval = (bins_timeofday[index - 1], bins_timeofday[index])
        return interval

    timeofday_cut = df['sched_time'].apply(timeofday_binning).astype("category")
    timeofday_cut_counts = timeofday_cut.value_counts()
    timeofday_cats = timeofday_cut.cat.categories

    df['avg_delay_diff_bin'] = delay_cut
    df['timeofday_bin'] = timeofday_cut
    df['timeofday_bin_left'] = timeofday_cut.apply(lambda x: x[0])


    # get categories: timeofday_cut.cat.categories

    # create matrix (each entry is a bin) -- x-axis: timeofday, y-axis: delay diff
    bin_matrix = pd.crosstab(df['avg_delay_diff_bin'], df['timeofday_bin'])

    # normalize
    norm_matrix = pd.DataFrame([(bin_matrix.iloc[:, i] / sum(bin_matrix.iloc[:, i]) / len(timeofday_cats)) for i in range(len(timeofday_cats))]).transpose()
    # get timeofday name: norm_matrix[i].name


    # get datapoints belonging to certain bins:
    # df.loc[df['avg_delay_diff_bin'] == delay_cats[0]] --> data points with avg delay diff of (-60.0, -30.5]
    # for some reason this doesn't work with timeofday... so instead use just left value of the bin:
    # df.loc[df['timeofday_bin_left'] == timeofday_cats[0][0]]

    norm_matrix.to_csv('normalized_bin_counts.csv', index=False)
    df.to_csv('delays_edges_binned.csv', index=False)


    # -----------------------------------------------------------------------------------------
    """ RESULT 1: example output of delay_diff_dict
    
     ('123', 4.0): 
     [   stop_from_id           stop_from_loc stop_to_id             stop_to_loc  \
      0       2313_04  (52.221734, 21.092292)    2269_02  (52.221089, 21.096954)   
      1       2269_02  (52.221089, 21.096954)    2269_01  (52.221206, 21.097342)   
      2       2269_01  (52.221206, 21.097342)    2128_02  (52.226292, 21.100221)   
      3       2128_02  (52.226292, 21.100221)    2124_02  (52.230204, 21.095359)   
      4       2124_02  (52.230204, 21.095359)    2250_02  (52.232367, 21.096466)   
      5       2250_02  (52.232367, 21.096466)    2102_04  (52.236196, 21.098363)   
      6       2102_04  (52.236196, 21.098363)    2107_02  (52.238006, 21.099511)   
      7       2107_02  (52.238006, 21.099511)    2011_01   (52.24262, 21.101188)   
      8       2011_01   (52.24262, 21.101188)    2010_01  (52.244099, 21.094242)   
      9       2010_01  (52.244099, 21.094242)    2008_08  (52.245865, 21.084594)   
      10      2008_08  (52.245865, 21.084594)    2113_02  (52.250823, 21.084664)   
      11      2113_02  (52.250823, 21.084664)    2121_01  (52.252711, 21.082849)   
      
          delay_diff  stop_seq_diff  avg_delay_diff line  brigade  sched_date  \
      0        -18.0            1.0           -18.0  123      4.0  2020-09-01   
      1        664.0            1.0           664.0  123      4.0  2020-09-01   
      2       -665.0            1.0          -665.0  123      4.0  2020-09-01   
      3         -1.0            2.0            -0.5  123      4.0  2020-09-01   
      4         28.0            1.0            28.0  123      4.0  2020-09-01   
      5         15.0            1.0            15.0  123      4.0  2020-09-01   
      6         11.0            1.0            11.0  123      4.0  2020-09-01   
      7         49.0            2.0            24.5  123      4.0  2020-09-01   
      8         63.0            1.0            63.0  123      4.0  2020-09-01   
      9        -44.0            1.0           -44.0  123      4.0  2020-09-01   
      10        24.0            1.0            24.0  123      4.0  2020-09-01   
      11       -28.0            1.0           -28.0  123      4.0  2020-09-01   
      
         sched_time  
      0    22:07:00  
      1    22:24:00  
      2    22:10:00  
      3    22:12:00  
      4    22:12:00  
      5    22:14:00  
      6    22:15:00  
      7    22:17:00  
      8    22:18:00  
      9    22:20:00  
      10   22:22:00  
      11   22:23:00  ],
      
      
     ('239', 51.0): 
        [  stop_from_id           stop_from_loc stop_to_id             stop_to_loc  \
      0      3132_02   (52.15571, 21.033754)    3133_02  (52.151325, 21.026204)   
      1      3133_02  (52.151325, 21.026204)    3013_02    (52.15408, 21.01796)   
      2      3013_02    (52.15408, 21.01796)    3415_01   (52.14645, 21.015266)   
      3      3415_01   (52.14645, 21.015266)    3416_02  (52.144157, 21.010789)   
      4      3416_02  (52.144157, 21.010789)    3419_51  (52.142301, 21.006083)   
      
         delay_diff  stop_seq_diff  avg_delay_diff line  brigade  sched_date  \
      0       -95.0            2.0      -47.500000  239     51.0  2020-09-01   
      1       745.0            3.0      248.333333  239     51.0  2020-09-01   
      2      -715.0            1.0     -715.000000  239     51.0  2020-09-01   
      3        26.0            1.0       26.000000  239     51.0  2020-09-01   
      4         8.0            1.0        8.000000  239     51.0  2020-09-01   
      
        sched_time  
      0   22:13:00  
      1   22:27:00  
      2   22:17:00  
      3   22:18:00  
      4   22:19:00  ,   
      
      stop_from_id           stop_from_loc stop_to_id             stop_to_loc  \
      0      3416_01   (52.144273, 21.01131)    3413_01  (52.152459, 21.014953)   
      1      3413_01  (52.152459, 21.014953)    3130_01  (52.155819, 21.023741)   
      
         delay_diff  stop_seq_diff  avg_delay_diff line  brigade  sched_date  \
      0       657.0            4.0          164.25  239     51.0  2020-09-01   
      1      -638.0            2.0         -319.00  239     51.0  2020-09-01   
      
        sched_time  
      0   22:16:00  
      1   22:29:00  ],
      
      
      
    
    also: 'df' gives all dataFrames concatenated
    """