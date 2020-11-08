import json
import pandas as pd
from api_requests import busestrams_get, dbstore_get
from processing import coord_distance
from collections import defaultdict
from datetime import date, datetime


DISTANCE_THRESHOLD = 300    # in meters

with open('busstops_per_line.json', 'r') as fh:
    busstops_per_line_dict = json.load(fh)

with open('timetable_per_line_and_stop.json', 'r') as fh:
    my_dict = json.load(fh)
timetable_per_line_and_stop_dict = dict()
for k in my_dict:
    k_split = k.split(':')
    new_k = (k_split[0], (k_split[1], k_split[2]))
    v = pd.read_json(my_dict[k], orient='split')
    timetable_per_line_and_stop_dict[new_k] = v

stop_locations = dbstore_get()

asb_dict = defaultdict(list)


#TODO: create while loop, run from morning until night
# while(True): # infinite while loop, but use some delay in api calls
live_buses = busestrams_get()

today = date.today()
now = datetime.now()
date = str(today.year) + '-' + str(today.month) + '-' + str(today.day)
date_bus = (live_buses['Time'].str.split(' ')).apply(lambda x: x[0])
date_mask = date_bus == date
live_buses = live_buses[date_mask]

#TODO: also filter out buses that have time too long ago?
#time_bus = (live_buses['Time'].str.split(' ')).apply(lambda x: x[1])


for bus in live_buses.itertuples():
    bus_line = bus.Lines
    bus_brigade = bus.Brigade
    bus_coord = (bus.Lat, bus.Lon)
    stop_list = busstops_per_line_dict[bus_line]

    for s in stop_list:     # check only the stops on the bus' route
        mask1 = stop_locations['zespol'] == s[0]
        mask2 = stop_locations['slupek'] == s[1]
        stop_row = stop_locations[mask1 & mask2]

        if (len(stop_row) > 1): # take the entry that is valid (obowiazuje_od) (sometimes there are multiple stops with the same slupek and zespol...)
            valid_from = (stop_row['obowiazuje_od'].str.split(' ')).apply(lambda x: x[0])
            valid_from_datetime = (valid_from.str.split('-')).apply(lambda x: date(int(x[0]), int(x[1]), int(x[2])))
            valid_from_datetime = valid_from_datetime[today >= valid_from_datetime]
            stop_row_index = valid_from_datetime[valid_from_datetime == max(valid_from_datetime)].index[0]
            stop_row = stop_row.loc[stop_row_index, :]

        if stop_row.loc[:, 'szer_geo'].values[0] == 'null' or stop_row.loc[:, 'dlug_geo'].values[0] == 'null':
            continue

        stop_coord = (stop_row['szer_geo'], stop_row['dlug_geo'])
        dist = coord_distance(bus_coord, stop_coord)

        # if asb already exists for this bus at stop s, i.e. not the first time the bus has entered the circle
        #  around s, then add location to asb
        if ((bus_line, bus_brigade), (s[0], s[1])) in asb_dict:
            if dist < DISTANCE_THRESHOLD: # if bus is still within circle around s
                asb_dict[((bus_line, bus_brigade), (s[0], s[1]))].append({'time': bus.Time, 'coord': bus_coord})
            else:   # complete asb
                #TODO
                # calculate arrival time
                # del asb_dict[(bus_line, bus_brigade, s)]
                # compare arrival time with timetable --> get delay
                print(asb_dict[((bus_line, bus_brigade), (s[0], s[1]))])
                del asb_dict[((bus_line, bus_brigade), (s[0], s[1]))]

        else:
            if dist < DISTANCE_THRESHOLD:   # bus is only interesting if it is within a certain distance of a stop --> create asb
                asb_dict[((bus_line, bus_brigade), (s[0], s[1]))].append({'time': bus.Time, 'coord': bus_coord})


