import json
import pandas as pd
from api_requests import busestrams_get, dbstore_get
from processing import coord_distance
from collections import defaultdict
from datetime import date, datetime, timedelta

DISTANCE_THRESHOLD = 300    # in meters
DISREGARD_X_MINUTES_AGO = True  # disregard buses that have timestamp x minutes ago
X_MINUTES = 25

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
# while(True): # infinite while loop, but use some delay in api calls
start_time_execution = datetime.now()
print(f'Start time execution: {start_time_execution.strftime("%H:%M:%S")}')

live_buses = busestrams_get()
with open('live_buses.json', 'w') as fh:
    json.dump(live_buses.to_json(), fh, sort_keys=True, indent=4)


today = date.today()
now = datetime.now()
#date = str(today.year) + '-' + str(today.month) + '-' + str(today.day)
#date_bus_str = (live_buses['Time'].str.split(' ')).apply(lambda x: x[0])
#date_bus_datetime = date_bus_str.apply(lambda x: datetime.strptime(x, '%Y-%m-%d ').date())
date_bus_datetime = live_buses['Time'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S'))

if DISREGARD_X_MINUTES_AGO:
    datetime_x_minutes_ago = now - timedelta(minutes=X_MINUTES)
    mask = date_bus_datetime > datetime_x_minutes_ago
else:
    date_bus = date_bus_datetime.apply(lambda x: x.date())
    mask = date_bus == today

#time_mask = now() - timedelta(minutes=X_MINUTES)
#date_mask = date_bus_datetime == today
live_buses = live_buses[mask]


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

        # if latitude or langitude of the stop is null: disregard this stop
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

        # if asb already exists for this bus at stop s, i.e. not the first time the bus has entered the circle
        #  around s, then add location to asb
        if ((bus_line, bus_brigade, bus_vehicle_no), (s[0], s[1])) in asb_dict:
            if dist < DISTANCE_THRESHOLD: # if bus is still within circle around s
                asb_dict[((bus_line, bus_brigade, bus_vehicle_no), (s[0], s[1]))].append({'time': bus.Time, 'coord': bus_coord})
            else:   # complete asb
                #TODO
                # calculate arrival time
                # del asb_dict[(bus_line, bus_brigade, s)]
                # compare arrival time with timetable --> get delay
                print(f'line: {bus_line}, brigade: {bus_brigade}, vehicle number: {bus_vehicle_no}, stop: {s} -- {asb_dict[((bus_line, bus_brigade), (s[0], s[1]))]}')
                #del asb_dict[((bus_line, bus_brigade), (s[0], s[1]))]

        else:
            if dist < DISTANCE_THRESHOLD:   # bus is only interesting if it is within a certain distance of a stop --> create asb
                asb_dict[((bus_line, bus_brigade, bus_vehicle_no), (s[0], s[1]))].append({'time': bus.Time, 'coord': bus_coord})

end_time_execution = datetime.now()
print(f'End time execution: {end_time_execution.strftime("%H:%M:%S")}')
print(f'Number of seconds passed between start and end of execution: {(end_time_execution - start_time_execution).seconds}')


