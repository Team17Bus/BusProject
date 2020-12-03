from collections import defaultdict
from statistics import median
import pandas as pd
import json

count = 0
times_dict = defaultdict(list)
with open('execution_times.txt', 'r') as fh:
    while True:
        count += 1
        line = fh.readline()

        # if line is empty
        # end of file is reached
        if not line:
            break
        # Get next line from file
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

summary_df = pd.DataFrame.from_dict(summary_dict)
print(summary_df)

