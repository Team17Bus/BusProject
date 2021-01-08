import json
import pandas as pd
from api_requests import busestrams_get, dbstore_get
from processing import coord_distance, coord_dist_pythagoras
from collections import defaultdict
from datetime import date, datetime, timedelta
from asb import get_angle_bisector, is_past_angle_bisector
from time import sleep
import csv

debug = False

# input file

# Import data, create new column with the line of each bus by extracting the first part of the trip_id field.
data = pd.read_csv("stop_times.txt", sep=",", header=None)
data = data.rename(data.iloc[0], axis=1)
data = data[1:]
trip_id = data['trip_id']
x = data['trip_id'].str.split("_", expand=True)
lines = x[0]
data['Lines'] = lines


# Create a dictionary which contains lines as keys and stops for each line as values
busstops_per_line = {}
df = data
for i in range(len(df)):
    if df['Lines'].iloc[i] not in busstops_per_line.keys():
        busstops_per_line[df['Lines'].iloc[i]] = [df['stop_id'].iloc[i]]
    elif df['Lines'].iloc[i] in busstops_per_line.keys():
        if df['stop_id'].iloc[i] not in busstops_per_line[df['Lines'].iloc[i]]:
            busstops_per_line.setdefault(df['Lines'].iloc[i]).append(df['stop_id'].iloc[i])

# set up a python dictionary that holds the reported coordinates of bus when bus is within R meters of S: asb_dict = defaultdict(list)
stops = pd.read_csv("stops.txt", sep=",", header=None)
stops = stops.rename(stops.iloc[0], axis=1)
stops = stops[1:]

locations = pd.read_csv("t_2020_09_01_22_30", sep=";", header=None)
locations['Longitude'] = locations.iloc[:, 3].rename('Longitude', axis=1)
locations['Latitude'] = locations.iloc[:, 4].rename('Latitude', axis=1)

if debug: print(locations)

locations.iloc[:, 5]=locations.iloc[:, 5].str.replace("T", " ")
locations.iloc[:, 5]=locations.iloc[:, 5].str[:-4]

stops_coordinates={}
for i in range(len(stops)):
    stops_coordinates[stops['stop_id'].iloc[i]] = (float(stops['stop_lat'].iloc[i]), float(stops['stop_lon'].iloc[i]))



# asb processing

asb_real = defaultdict(list)
arrival_time_estimations = []

for i in range(len(locations)):

    bus_line = locations.iloc[i, 0]
    bus_brigade = locations.iloc[i, 1]

    if debug:
        if not bus_line == '739':
            continue
        if not bus_brigade == 3.0:
            continue

    if bus_line in busstops_per_line:
        stops = busstops_per_line[bus_line]
    # else: debug -- should rarely happen

    for stop in stops:

        if debug:
            if not stop == ' 3018_01':
                continue

        if debug: print(asb_real)

        if ((bus_line, bus_brigade),
            (stop)) in asb_real.keys():  # Keys are now ((bus,bus_brigade),(stop)) to make it clearer
            stop_coordinate = stops_coordinates[stop[1:]]  # coordinates of the stop
            bus_coordinate = (float(locations['Latitude'].iloc[i]), float(locations['Longitude'].iloc[i]))
            distance = coord_distance(bus_coordinate, stop_coordinate)
            if debug:
                print('if')
                print(distance)
                print(bus_coordinate)
                print(stop_coordinate)
            if distance > 600:
                continue
            if distance < 300:
                # APPEND
                asb_real[((bus_line, bus_brigade), (stop))].append(
                    {'time': [locations.iloc[i, 5]], 'coord': [(bus_coordinate)]})

            else:  # complete ASB

                A = asb_real[((bus_line, bus_brigade), (stop))][0]['coord']

                if len(asb_real[((bus_line, bus_brigade), (stop))]) == 1:
                    arrival_time = asb_real[((bus_line, bus_brigade), (stop))][0]['time'][0]
                    if debug: print(f'len==1: {stop}, {arrival_time}')
                    arrival_time_estimations.append([bus_line, bus_brigade, stop, stop_coordinate, arrival_time, None])
                    del asb_real[((bus_line, bus_brigade), (stop))]
                    continue

                elif len(asb_real[((bus_line, bus_brigade), (stop))]) == 2:  # take average

                    ts1 = asb_real[((bus_line, bus_brigade), (stop))][0]['time'][0]
                    ts2 = asb_real[((bus_line, bus_brigade), (stop))][1]['time'][0]
                    ts1_date = datetime.strptime(ts1, '%Y-%m-%d %H:%M:%S')
                    ts2_date = datetime.strptime(ts2, '%Y-%m-%d %H:%M:%S')
                    average_delta = (ts2_date - ts1_date) / 2
                    arrival_time = ts1_date + average_delta
                    if debug: print(f'len==2: {stop}, {arrival_time}')
                    arrival_time_estimations.append([bus_line, bus_brigade, stop, stop_coordinate, arrival_time, None])
                    del asb_real[((bus_line, bus_brigade), (stop))]
                    continue

                else:
                    B = asb_real[((bus_line, bus_brigade), (stop))][-2]['coord']
                    S = stop_coordinate
                    angle_bisector = get_angle_bisector(A[0], S, B[0])
                    index_past_bisector = 0

                    some_coord_past_bisector = False

                    for i in range(len(asb_real[((bus_line, bus_brigade), (stop))])):

                        coord = asb_real[((bus_line, bus_brigade), (stop))][i]['coord']

                        if is_past_angle_bisector(A[0], coord[0], angle_bisector):
                            index_past_bisector = i
                            index_before_bisector = i - 1
                            some_coord_past_bisector = True

                            # break out of for loop
                            break

                    if not some_coord_past_bisector:  # can happen when there are duplicate items in the list or bus is sitting at exact same location
                        # just take the time of entering the radius (might be somewhat optimistic but not a big problem)
                        arrival_time = asb_real[((bus_line, bus_brigade), (stop))][0]['time'][0]
                        arrival_time_estimations.append(
                            [bus_line, bus_brigade, stop, stop_coordinate, arrival_time, None])
                        if debug: print(f'no coords pas bisector: {stop}, {arrival_time}')
                        del asb_real[((bus_line, bus_brigade), (stop))]
                        continue

                    time_before_S = asb_real[((bus_line, bus_brigade), (stop))][index_before_bisector]['time'][0]
                    time_after_S = asb_real[((bus_line, bus_brigade), (stop))][index_past_bisector]['time'][0]
                    ts1_date = datetime.strptime(time_before_S, '%Y-%m-%d %H:%M:%S')
                    ts2_date = datetime.strptime(time_after_S, '%Y-%m-%d %H:%M:%S')
                    average_delta = (ts2_date - ts1_date) / 2
                    arrival_time = ts1_date + average_delta
                    if debug: print(f'len==multiple: {stop}, {arrival_time}')
                    arrival_time_estimations.append([bus_line, bus_brigade, stop, stop_coordinate, arrival_time, None])
                    del asb_real[((bus_line, bus_brigade), (stop))]
                    continue

        else:
            stop_coordinate = stops_coordinates[stop[1:]]
            bus_coordinate = (float(locations['Latitude'].iloc[i]), float(locations['Longitude'].iloc[i]))
            distance = coord_distance(bus_coordinate, stop_coordinate)
            if debug:
                print('else')
                print(distance)
                print(bus_coordinate)
                print(stop_coordinate)
            if distance < 300:
                # APPEND
                asb_real[((bus_line, bus_brigade), (stop))].append(
                    {'time': [locations.iloc[i, 5]], 'coord': [(bus_coordinate)]})


# write results to output file

with open('arrival_estimations.csv', 'w') as arrival_times:
    arrival_writer = csv.writer(arrival_times, delimiter=',', quotechar='"')
    for i in range(len(arrival_time_estimations)):
        arrival_writer.writerow(arrival_time_estimations[i])