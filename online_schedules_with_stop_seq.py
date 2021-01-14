import pandas as pd
import json

# GOAL: to put online schedules in format of schedules for historic data (including a stop sequence)

# RESULT: order_dict
# key: (line, brigade)                              -- e.g. ('123', '6')
# value: dataframe with time, stop_id, order        -- e.g.
""" 
    line brigade      time  stop_id  order
0    123       6  04:21:00  2008_08      0
1    123       6  04:23:00  2113_02      1
2    123       6  04:24:00  2121_01      2
3    123       6  04:25:00  2122_01      3
4    123       6  04:26:00  2123_01      4
..   ...     ...       ...      ...    ...
633  123       6  23:24:00  2122_01    633
634  123       6  23:25:00  2123_01    634
635  123       6  23:26:00  2413_03    635
636  123       6  23:27:00  2118_01    636
637  123       6  23:28:00  2119_01    637
[638 rows x 5 columns]
"""

# stop_sequence not possible, since we do not know where the bus starts / ends
# however, we could optionally detect loops


# NOTE: 23,342 out of 905,369 entries have times > 23:59:59 (e.g. 29:54:00). max is 29:56:00. --> dropped these...
# or better: use Jurriaan's method in main.py (replace 24 with 00, 25 with 01 etc) and move to the next day

debug_small_dataset = False
debug_only_1_line_and_brigade = False
export_to_csv = True

pd.set_option("display.max_columns", None)

with open('online_data/timetable_per_line_and_stop_16dec.json', 'r') as f:
    data = json.load(f)

if debug_small_dataset:
    keys = list(data.keys())
    delete_keys = keys[100:]
    for k in delete_keys:
        del data[k]

first_key = list(data.keys())[0]
first_value = json.loads(data[first_key])
columns = first_value['columns']

# Format
# key: ['line:busstop:busstop_specification']
#        e.g. ['123:1001:01']
# data: ['symbol_2', 'symbol_1', 'brygada', 'kierunek', 'trasa', 'czas']
#       e.g. ['null', 'null', '6', 'Dw.Wschodni (Lubelska)', 'TP-DWL', '22:49:00']

# turn into 1 big dataframe
drop_keys = []
for k in data:
    data[k] = json.loads(data[k])
    del data[k]['index']
    del data[k]['columns']
    data[k] = data[k]['data']
    data[k] = pd.DataFrame(data[k])
    if data[k].empty:
        drop_keys.append(k)
    else:
        data[k].iloc[:, 0] = k

for dk in drop_keys:    # delete empty dataframes
    del data[dk]

# concatenate all dataframes into 1 (get rid of dictionary):
df = pd.concat([data[k] for k in data.keys()], ignore_index=True)

# manipulate df
df = df.drop([1], axis=1)
split_series = df.iloc[:, 0].str.split(pat=':', expand=True)
df['line'] = split_series.iloc[:, 0]
df['stop_id'] = split_series.iloc[:, 1].str.cat(split_series.iloc[:, 2], '_')
df = df.drop([0, 3, 4], axis=1)
df = df.rename({2: 'brigade'}, axis=1)
df = df.rename({5: 'time'}, axis=1)
cols = ['line', 'brigade', 'time', 'stop_id']
df = df.reindex(columns=cols)

# see remark at the top (some times are > 23:59:59, e.g. 25:09:00)
df = df.drop(df.loc[df['time'] > '23:59:59'].index)

# sort by time
df = df.sort_values(by=['time'])

# for debugging:
if debug_only_1_line_and_brigade:
    x = df.loc[(df['brigade'] == '4') & (df['line'] == '123')]
    pd.set_option("display.max_columns", None, "display.max_rows", None)
    print(x)
    x = x.reset_index(drop=True)
    x['order'] = x.index

# get all line-brigade combinations
combos = df.loc[:, ['brigade', 'line']].drop_duplicates()

# create dataframe with order for each combo
order_dict = dict()  # key: (line, brigade) - value: dataframe with times, stop_id, order
for i in range(len(combos)):
    brigade = combos.iloc[i]['brigade']
    line = combos.iloc[i]['line']
    filtered_df = df.loc[(df['brigade'] == brigade) & (df['line'] == line)]
    filtered_df = filtered_df.reset_index(drop=True)
    filtered_df['order'] = filtered_df.index
    order_dict[(line, brigade)] = filtered_df

if export_to_csv:
    df = pd.concat([order_dict[k] for k in order_dict], axis=0).reset_index(drop=True)
    print(df)

    df.to_csv('online_data/stop_times16dec.csv', index=False, header=False)
