import pandas as pd
from datetime import datetime, time
import numpy as np
import matplotlib.pyplot as plt
from textwrap import wrap

def summary(df, description):
    means = df.groupby(by=['line']).mean()['avg_delay_diff_sec'].sort_values(ascending=False)
    medians = df.groupby(by=['line']).median()['avg_delay_diff_sec'].sort_values(ascending=False)
    counts = df.groupby(by=['line']).count()['avg_delay_diff_sec'].sort_values(ascending=False)

    median_count = np.median(counts)

    agg_df = pd.concat([medians, counts[medians.index], means[medians.index]], axis=1)
    agg_df.columns = ['MEDIAN_avg_delay_diff_sec', 'COUNT', 'MEAN_avg_delay_diff_sec']

    if delete_low_counts:
        agg_df = agg_df[agg_df['COUNT'] > ratio_of_median * median_count]

    num_lines = 10
    big_delays_lines = agg_df[0:10].index
    big_earlys_lines = agg_df[-10:].index  # negative delays (= early buses)

    print(description)
    print(agg_df[0:num_lines])
    print(agg_df[-num_lines:])
    print('-------------------------------------------')

    """ works but not 100% sure it handles NaN correctly (99% though)
    df_big_delays = pd.concat([df[df['line'] == l]['avg_delay_diff_sec'] for l in big_delays_lines], axis=1)
    df_big_delays.columns = [str(l) for l in big_delays_lines]
    boxplot = df_big_delays.boxplot()
    plt.show()
    """

    # late buses
    avg_delays_per_line = [df[df['line'] == l]['avg_delay_diff_min'] for l in big_delays_lines]

    fig, ax = plt.subplots()
    ax.set_title("\n".join(wrap(f'Top {num_lines} lines with largest median average delay difference, {description}', 60)))
    ax.set_xlabel('Line')
    ax.set_ylabel('Average delay difference (minutes)')
    ax.boxplot(avg_delays_per_line)
    plt.xticks([i for i in range(1, num_lines + 1)], [str(l) for l in big_delays_lines])
    plt.show()

    # early buses
    avg_delays_per_line = [df[df['line'] == l]['avg_delay_diff_min'] for l in big_earlys_lines]

    fig, ax = plt.subplots()
    ax.set_title("\n".join(wrap(f'Top {num_lines} lines with smallest median average delay difference, {description}', 60)))
    ax.set_xlabel('Line')
    ax.set_ylabel('Average delay difference (minutes)')
    ax.boxplot(avg_delays_per_line)
    plt.xticks([i for i in range(1, num_lines + 1)], [str(l) for l in big_earlys_lines])
    plt.show()

    return big_delays_lines

delete_low_counts, ratio_of_median = True, 0.1    # delete rows with counts less than or equal to ratio_of_median
show_full_day = False
show_morning_peak = False
show_afternoon_peak = False
show_non_peak = True


FOLDER = '/Volumes/KESU/Project_Bus/delays_edges_historical/'
FILENAME = 'delays_edges_2020_09_08.csv'

date = (FILENAME.split(sep='.')[0]).split('_')[2:]
datetime_obj = datetime(int(date[0]), int(date[1]), int(date[2]))
week_no = datetime_obj.weekday()

if week_no < 5:     # Mo = 0, Tu = 1, We = 2, Th = 3, Fri = 4
    weekday = True
else:               # Sa = 5, Su = 6
    weekday = False

df = pd.read_csv(FOLDER + FILENAME)

if show_full_day:
    big_delays_lines = summary(df, '-'.join(date))

# -----------------------------------------------------------------

# Filter on morning-peak / afternoon-peak
morning_peak_start, morning_peak_end = time(6, 30), time(9, 30)
afternoon_peak_start, afternoon_peak_end = time(15, 30), time(19)
df['time'] = pd.to_datetime(df.sched_datetime, format='%Y-%m-%d %H:%M:%S').apply(lambda x: x.time())

morning_peak_df = df[(df['time'] > morning_peak_start) & (df['time'] < morning_peak_end)]
afternoon_peak_df = df[(df['time'] > afternoon_peak_start) & (df['time'] < afternoon_peak_end)]
non_peak_df = df[(df['time'] < morning_peak_start) | ((df['time'] > morning_peak_end) & (df['time'] < afternoon_peak_start)) | (df['time'] > afternoon_peak_end)]

if show_morning_peak:
    big_delays_lines_morn_peak = summary(morning_peak_df, '-'.join(date) + ', 6:30-9:30')
if show_afternoon_peak:
    big_delays_lines_aft_peak = summary(afternoon_peak_df, '-'.join(date) + ', 15:30-19:00')
if show_non_peak:
    big_delays_lines_non_peak = summary(non_peak_df, '-'.join(date) + ', non-peak hours (i.e. excluding 6:30-9:30 and 15:30-19:00')

