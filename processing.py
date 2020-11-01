import pandas as pd
import numpy as np
import datetime
from math import radians, cos, sin, asin, sqrt
import api_requests as api
from collections import defaultdict

def coord_distance(coord1, coord2):
    """
    CREDITS TO GEEKSFORGEEKS.ORG: https://www.geeksforgeeks.org/program-distance-two-points-earth/
        Function that calculates and returns the distance in meters between two coordinates
    Args:
        coord1 (numpy.float64, numpy.float64): tuple with latitude & longitude (in that order) for the first coordinate
        coord2 (numpy.float64, numpy.float64): tuple with latitude & longitude (in that order) for the second coordinate

    Returns:
        dist (float): distance in meters

    Example call:
        coord_distance((52.195248, 21.048823), (52.208840, 21.007883))
    """

    lon1 = radians(coord1[1])
    lon2 = radians(coord2[1])
    lat1 = radians(coord1[0])
    lat2 = radians(coord2[0])

    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2

    c = 2 * asin(sqrt(a))

    # Radius of earth in meters. Use 3956 for miles
    r = 6371000

    return (c * r)


def get_all_lines():
    """Returns a set of all lines
    (Takes some time: ~7500 api requests)
    """
    all_busstops = api.dbstore_get()
    n = len(all_busstops)
    all_lines = set()
    zespol = all_busstops['zespol']
    slupek = all_busstops['slupek']
    for i in range(n):
        print(i)
        stop_id = zespol[i]
        stop_nr = slupek[i]
        lines = api.dbtimetable_get({'busstopId': str(stop_id), 'busstopNr': str(stop_nr)})
        for j in range(len(lines)):
            all_lines.add(lines[j])
    return all_lines


def get_lines_per_busstop():
    """Returns a dictionary with busstops as keys (tuple of (id, nr)), and their lines as values
    (Takes some time: ~7500 api requests)
    """
    all_busstops = api.dbstore_get()
    n = len(all_busstops)
    line_per_busstop_dict = dict()
    zespol = all_busstops['zespol']
    slupek = all_busstops['slupek']
    for i in range(n):
        print(i)
        stop_id = zespol[i]
        stop_nr = slupek[i]
        lines = list(api.dbtimetable_get({'busstopId': str(stop_id), 'busstopNr': str(stop_nr)}))
        line_per_busstop_dict[(stop_id, stop_nr)] = lines
    return line_per_busstop_dict


def get_busstops_per_line(lines_per_busstop_dict):
    """Returns a dictionary with lines as keys and busstops (in a tuple (id, nr)) it passes as values
    Args:
        lines_per_busstop_dict (dictionary): dictionary returned by get_lines_per_busstop with busstops as keys and lines as values
    Returns:
        dictionary with lines as keys and busstops (in a tuple (id, nr)) the line passes as values
    """
    busstops_per_line_dict = defaultdict(list)
    for busstop in lines_per_busstop_dict:
        stop_id = busstop[0]
        stop_nr = busstop[1]
        for line in lines_per_busstop_dict[busstop]:
            busstops_per_line_dict[line].append((stop_id, stop_nr))
    return dict(busstops_per_line_dict)

def get_timetable_per_busstop_per_line(busstops_per_line_dict):
    """Returns a dictionary that shows the timetable for each line at each busstop.
    Args:
        busstops_per_line_dict (dictionary): dictionary with lines as keys and busstops (in a tuple (id, nr)) that the line passes as values
    Returns:
        dictionary with as keys tuples of (line, (stop_id, stop_nr)) and as values the corresponding timetable
    (Takes some time: ~7500 api requests)
    """
    timetable_per_busstop_per_line_dict = dict()
    progress = 0
    for line in busstops_per_line_dict:
        busstops = busstops_per_line_dict[line]
        for stop in busstops:
            stop_id = stop[0]
            stop_nr = stop[1]
            timetable = api.dbtimetable_get({'busstopId': stop_id, 'busstopNr': stop_nr, 'line': line})
            timetable_per_busstop_per_line_dict[(line, (stop_id, stop_nr))] = timetable
            progress += 1
            print(progress)
    return timetable_per_busstop_per_line_dict

#
def find_arrival(stop_time, bus_locations):
    """
    A first attempt to find the right arrival event.
    Also contains some pre-processing and cleaning steps.

    Args:
        stop_time: one line from the stop_times dataset (i.e. one stop event)
        bus_locations: for now all bus locations

    Returns:

    """
    time_obj = datetime.datetime.strptime(stop_time["arrival_time"],' %H:%M:%S')
    for ind,r in bus_locations[0:5].iterrows():
        print(r['TimeGPS'].time())

        #delta = scheduled_arr_time - r['TimeGPS'].time()

        #print(delta)

    scheduled_arr_time = stop_time['arrival_time']
    for ind, r in bus_locations[0:5].iterrows():
        print(r['TimeGPS'].time())
        delta = scheduled_arr_time - r['TimeGPS'].time()
        print(delta)

    return