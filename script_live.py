import json
import pandas as pd
from api_requests import busestrams_get, dbstore_get
from processing import coord_distance, coord_dist_pythagoras
from collections import defaultdict
from datetime import date, datetime, timedelta
import asb
from time import sleep
import csv

DISTANCE_THRESHOLD = 300    # in meters
DISREGARD_X_MINUTES_AGO = True  # disregard buses that have timestamp x minutes ago
X_MINUTES = 25

save_estimations_to_file = True

with open('busstops_per_line.json', 'r') as fh:
    busstops_per_line_dict = json.load(fh)

''' 
with open('timetable_per_line_and_stop.json', 'r') as fh:
    my_dict = json.load(fh)
timetable_per_line_and_stop_dict = dict()
for k in my_dict:
    k_split = k.split(':')
    new_k = (k_split[0], (k_split[1], k_split[2]))
    v = pd.read_json(my_dict[k], orient='split')
    timetable_per_line_and_stop_dict[new_k] = v
'''

stop_locations = dbstore_get()

asb_dict = defaultdict(list)


#TODO: create while loop, run from morning until night
# while(True): # infinite while loop, but use some delay (10s?) in api calls

execution_time = 10

while(True):

    if execution_time < 10:
        sleep(10 - execution_time)

    # to measure execution time --> should not exceed 10 seconds... (or time between subsequent dbstore_get() = live buses calls)
    # currently the execution time is at least 3 minutes.....
    start_time_execution = datetime.now()
    print(f'Start time execution: {start_time_execution.strftime("%H:%M:%S")}')

    # get live buses dataframe
    response, live_buses = busestrams_get()
    while not response:   # in case response from API was not 200 or other error from API
        response, live_buses = busestrams_get()
    with open('live_buses.json', 'w') as fh:
        json.dump(live_buses.to_json(), fh, sort_keys=True, indent=4)

    # disregard buses from a day ago, and possibly from x minutes ago
    today = date.today()
    now = datetime.now()

    date_bus_datetime = live_buses['Time'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S'))

    if DISREGARD_X_MINUTES_AGO:
        datetime_x_minutes_ago = now - timedelta(minutes=X_MINUTES)
        mask = date_bus_datetime > datetime_x_minutes_ago
    else:
        date_bus = date_bus_datetime.apply(lambda x: x.date())
        mask = date_bus == today

    live_buses = live_buses[mask]

    live_buses = live_buses[live_buses['Lines'] == '213']

    # iterate over each live bus
    for bus in live_buses.itertuples():
        bus_line = bus.Lines
        bus_brigade = bus.Brigade
        bus_coord = (bus.Lat, bus.Lon)
        bus_vehicle_no = bus.VehicleNumber
        if bus_line in busstops_per_line_dict:
            stop_list = busstops_per_line_dict[bus_line]
        else:   # if bus line not in busstops_per_line_dict, disregard (should barely happen)
            print(f'bus_line {bus_line} not in busstops_per_line_dict')
            continue

        for s in stop_list:     # check only the stops on the bus' route
            mask1 = stop_locations['zespol'] == s[0]
            mask2 = stop_locations['slupek'] == s[1]
            stop_row = stop_locations[mask1 & mask2]

            if stop_row.empty:  # if bus stop could not be found -- shouldn't happen
                print('Bus stop could not be found in dbstore_get')
                continue

            if (len(stop_row) > 1): # take the entry that is valid (obowiazuje_od) (sometimes there are multiple stops with the same slupek and zespol...)
                valid_from = (stop_row['obowiazuje_od'].str.split(' ')).apply(lambda x: x[0])
                valid_from_datetime = (valid_from.str.split('-')).apply(lambda x: date(int(x[0]), int(x[1]), int(x[2])))
                valid_from_datetime = valid_from_datetime[today >= valid_from_datetime]
                stop_row_index = valid_from_datetime[valid_from_datetime == max(valid_from_datetime)].index[0]
                stop_row = stop_row.loc[stop_row_index, :]

            # if latitude or longitude of the stop is null: disregard this stop
            if isinstance(stop_row['szer_geo'], str):
                if stop_row['szer_geo'] == 'null' or stop_row['dlug_geo'] == 'null':
                    continue
            else:
                if stop_row['szer_geo'].values[0] == 'null' or stop_row['dlug_geo'].values[0] == 'null':
                    continue

            stop_coord = (stop_row['szer_geo'], stop_row['dlug_geo'])
            stop_coord_float = (float(stop_coord[0]), float(stop_coord[1]))
            bus_coord_float = (float(bus_coord[0]), float(bus_coord[1]))

            dist = coord_distance(bus_coord_float, stop_coord_float)
            # with pythagoras (faster? No.)
            #dist = coord_dist_pythagoras(bus_coord_float, stop_coord_float)


            # if asb already exists for this bus at stop s, i.e. not the first time the bus has entered the circle
            #  around s, then add location to asb
            if ((bus_line, bus_brigade, bus_vehicle_no), (s[0], s[1])) in asb_dict:
                if dist < DISTANCE_THRESHOLD: # if bus is still within circle around s
                    asb_dict[((bus_line, bus_brigade, bus_vehicle_no), (s[0], s[1]))].append({'time': bus.Time, 'coord': bus_coord})
                else:   # complete asb

                    # get the coordinates (in tuple (latitude, longitude)) for which _bus_ entered the proximity of _S_ for the first time
                    A = asb_dict[((bus_line, bus_brigade, bus_vehicle_no), (s[0], s[1]))][0]['coord']

                    # get the coordinates (in tuple (latitude, longitude)) for which _bus_ was in the proximity of _S_ last
                    # Note the index '-2' gets the one-but-last entry of the list
                    if len(asb_dict[((bus_line, bus_brigade, bus_vehicle_no), (s[0], s[1]))]) == 1:
                        print(f'JUST ONE POINT -- TIME = {asb_dict[((bus_line, bus_brigade, bus_vehicle_no), (s[0], s[1]))][0]["time"]}')
                        del asb_dict[((bus_line, bus_brigade, bus_vehicle_no), (s[0], s[1]))]
                        continue
                    else:
                        B = asb_dict[((bus_line, bus_brigade, bus_vehicle_no), (s[0], s[1]))][-2]['coord']

                    if len(asb_dict[((bus_line, bus_brigade, bus_vehicle_no), (s[0], s[1]))]) == 2:
                        print(f'TWO POINTS -- take average of A and B = {asb_dict[((bus_line, bus_brigade, bus_vehicle_no), (s[0], s[1]))][0]["time"]}')

                        #average A and B for final time
                        ts1 = asb_dict[((bus_line, bus_brigade, bus_vehicle_no), (s[0], s[1]))][1]['time']
                        ts2 = asb_dict[((bus_line, bus_brigade, bus_vehicle_no), (s[0], s[1]))][1]['time']
                        ts1_date = datetime.strptime(ts1, '%Y-%m-%d %H:%M:%S')
                        ts2_date = datetime.strptime(ts2, '%Y-%m-%d %H:%M:%S')
                        average_delta = (ts2_date - ts1_date) / 2
                        average_ts = ts1_date + average_delta

                        del asb_dict[((bus_line, bus_brigade, bus_vehicle_no), (s[0], s[1]))]
                        continue

                    # line that bisects lines AS and BS
                    angle_bisector = asb.get_angle_bisector(A, stop_coord_float, B)

                    # for each recording in the asb_dict, check whether the coordinate has passed the angle_bisector relative to _A_
                    index_past_bisector = 0
                    some_coord_past_bisector = False
                    for i in range(len(asb_dict[((bus_line, bus_brigade, bus_vehicle_no), (s[0], s[1]))])):
                        coord = asb_dict[((bus_line, bus_brigade, bus_vehicle_no), (s[0], s[1]))][i]['coord']
                        if asb.is_past_angle_bisector(A, coord, angle_bisector):
                            # BINGO! first coordinate just past the angle bisector
                            index_past_bisector = i
                            index_before_bisector = i-1
                            some_coord_past_bisector = True
                            # break out of for loop
                            break
                    if not some_coord_past_bisector: # can happen when there are duplicate items in the list or bus is sitting at exact same location
                    # just take the time of entering the radius (might be somewhat optimistic but not a big problem)
                        print(asb_dict[((bus_line, bus_brigade, bus_vehicle_no), (s[0], s[1]))][0]['time'])
                        del asb_dict[((bus_line, bus_brigade, bus_vehicle_no), (s[0], s[1]))]
                        continue


                    time_before_S = asb_dict[((bus_line, bus_brigade, bus_vehicle_no), (s[0], s[1]))][index_before_bisector]['time']
                    time_after_S = asb_dict[((bus_line, bus_brigade, bus_vehicle_no), (s[0], s[1]))][index_past_bisector]['time']

                    # THE ESTIMATION OF THE TIME AT _S_
                    # Note: could do something more advanced than this (e.g. proportional to the distance to _S_
                    # -- for now just taking the average of the times
                    print('TIME BEFORE AND AFTER BUSSTOP')
                    print(time_before_S)
                    print(time_after_S)
                    #time_at_S = (time_after_S + time_before_S) / 2

                    # dictionary is not needed anymore and should be deleted
                    del asb_dict[((bus_line, bus_brigade, bus_vehicle_no), (s[0], s[1]))]

                    #TODO
                    # del asb_dict[(bus_line, bus_brigade, s)]
                    # compare arrival time with timetable --> get delay
                    print(f'line: {bus_line}, brigade: {bus_brigade}, vehicle number: {bus_vehicle_no}, stop: {s} -- {asb_dict[((bus_line, bus_brigade, bus_vehicle_no), (s[0], s[1]))]}')
                    #del asb_dict[((bus_line, bus_brigade, bus_vehicle_no), (s[0], s[1]))]

            else:
                if dist < DISTANCE_THRESHOLD:   # bus is only interesting if it is within a certain distance of a stop --> create asb
                    asb_dict[((bus_line, bus_brigade, bus_vehicle_no), (s[0], s[1]))].append({'time': bus.Time, 'coord': bus_coord})

    # Execution time
    end_time_execution = datetime.now()
    print(f'End time execution: {end_time_execution.strftime("%H:%M:%S")}')
    execution_time = (end_time_execution - start_time_execution).seconds
    print(f'Number of seconds passed between start and end of execution: {execution_time}')
    print(f'asb_dict: {asb_dict}')



