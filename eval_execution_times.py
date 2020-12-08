from collections import defaultdict
from statistics import median
import pandas as pd
import json
import matplotlib.pyplot as plt
import numpy as np

FILE_NAME = 'execution_times.txt'
pd.set_option("display.max_rows", None, "display.max_columns", None)
pd.set_option('display.max_colwidth', None)

visualize = False

count = 0
weird_lines = 0
empty_lines = 0
times_dict = defaultdict(list)
with open(FILE_NAME, 'r') as fh:
    while True:
        count += 1
        line = fh.readline()
        # if line is empty
        # end of file is reached
        if not line:
            break
        # Get next line from file
        if line == '\n':
            empty_lines += 1
            continue
        if not line[0] == '[':
            weird_lines += 1
            continue

        weird_line = False
        for c in line[1:]:
            if c == '[':
                weird_lines += 1
                weird_line = True
                break
        if weird_line:
            continue

        split_line = line.split(':')
        k = split_line[0]
        v = int(split_line[1][:-1])
        times_dict[k].append(v)

    fh.close()

# process times_dict
summary_dict = dict()
for k in times_dict:
    times = times_dict[k]
    num_stamps = len(times)
    total_time = sum(times)
    avg_time = total_time / num_stamps
    min_time = min(times)
    max_time = max(times)
    median_time = median(times)
    summary_dict[k] = {'num_stamps': num_stamps,
                       'total_time': total_time,
                       'avg_time': avg_time,
                       'min_time': min_time,
                       'max_time': max_time,
                       'median_time': median_time}

with open('summary_execution_times.json', 'w') as f_out:
    json.dump(summary_dict, f_out, indent=4)

summary_df = pd.DataFrame.from_dict(summary_dict).transpose()
summary_df.sort_values(by=['total_time'])
print(summary_df)

# visualize with histogram
# one for times < 12 seconds, one for times > 12 seconds
if visualize:
    for k in times_dict:
        vals = times_dict[k]
        np_vals = np.array(vals)
        under_twelve = np_vals[np_vals < 12]
        over_twelve = np_vals[np_vals >= 12]
        plt.hist(under_twelve, 12)
        plt.rcParams["axes.titlesize"] = 6
        plt.title(k)
        plt.show()
        plt.hist(over_twelve, 10)
        plt.rcParams["axes.titlesize"] = 6
        plt.title(k)
        plt.show()