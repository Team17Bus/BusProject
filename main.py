from api_requests import busestrams_get, dbstore_get, dbtimetable_get
import pandas as pd
import datetime
from processing import get_all_lines, get_lines_per_busstop, get_busstops_per_line, get_timetable_per_busstop_per_line, coord_distance, find_arrival
import json


def main():
    # Example calls from api_requests.py (uncomment and print to see the results):
    # -----------------------
    # df = busestrams_get()
    # -----------------------
    # df = dbstore_get()
    # -----------------------
    # retrieving the line list for the Marszałkowska stop  (busstopId = 7009) and bar number 01 (busstopNr = 01) and line 523 (line = 523)
    # df = dbtimetable_get(dict(busstopId='7009', busstopNr='01', line='523'))
    # -----------------------
    # retrieving the line list for the Marszałkowska stop (busstopId = 7009) and bar number 01 (busstopNr = 01)
    # df = dbtimetable_get(dict(busstopId='7009', busstopNr='01'))
    # -----------------------
    # retrieving all the 'zespol' (??) for the busstop 'Marysin'
    # df = dbtimetable_get(dict(name='Marysin'))
    # -----------------------
    # pd.set_option('display.max_columns', None)
    # print(df)

    # ---------------------------------------------------------------------------
    # ---------------------------------------------------------------------------
    # SOME STUFF TO TRY OUT OTHER STUFF:

    # For each line, get list of busstopId+nr on route

    # Unnecessary, but whatever:
    # get a list of all lines
    # all_lines = get_all_lines()
    # --> saved in all_lines.txt: 342 lines

    # get dictionary of lines per busstop
    # line_dict = get_lines_per_busstop()
    # line_dict = dict((':'.join(k), v) for k, v in line_dict.items())
    # with open('lines_per_busstop.json', 'w') as fh:
    #    json.dump(line_dict, fh, sort_keys=True, indent=4)
    # --> saved in lines_per_busstop.json

    """
    with open('lines_per_busstop.json', 'r') as fh:
        my_dict = json.load(fh)
    test_dict = dict()
    for k in my_dict:
        k_split = k.split(':')
        new_k = (k_split[0], k_split[1])
        test_dict[new_k] = my_dict[k]
    busstops_per_line = get_busstops_per_line(test_dict)
    print(busstops_per_line)
    """
    # timetables = get_timetable_per_busstop_per_line(busstops_per_line)
    # print(timetables)

    # QUESTION: are there any two bus stops on the same line
    #   that are within a 2r meter distance of each other (to start: r=300)?
    # CONCLUSION (run commented code below): YES, MANY! Even distances of just 17 meters...
    """ 
    all_stops = dbstore_get()
    pd.set_option('display.max_columns', None)
    print(all_stops)

    for line in busstops_per_line:
        stop_list = busstops_per_line[line]
        permutations = [(stop_list[i], stop_list[j]) for i in range(len(stop_list)) for j in range(i+1, len(stop_list))]

    for p in permutations:
        stop1 = p[0]
        stop2 = p[1]
        stop1_info = all_stops.loc[(all_stops['zespol'] == stop1[0]) & (all_stops['slupek'] == stop1[1])]
        stop2_info = all_stops.loc[(all_stops['zespol'] == stop2[0]) & (all_stops['slupek'] == stop2[1])]
        lat1 = stop1_info['szer_geo']
        lon1 = stop1_info['dlug_geo']
        lat2 = stop2_info['szer_geo']
        lon2 = stop2_info['dlug_geo']
        dist = coord_distance((lat1, lon1), (lat2, lon2))
        print(dist)
    """

    # Importing the bus locations of a specific day (make sure to use the right directory)
    data_bus = pd.read_csv("C:/Users/jurri/Documents/Studie/DSDM 2020 - 2021/Project 1/Data/buses/t_2020_08_31_23_30",
                       sep=";",
                       header=None)
    data_bus.columns = ["Line","Brigade","TimeGPS","Lat","Long","TimeLog"]

    # TODO: Cleaning and formatting the data (probably move this to a separate function)
    # For some reason this actually does not overwrite the value???
    for i,r in data_bus.iterrows():
        datetime_object = datetime.datetime.strptime(r["TimeGPS"], '%Y-%m-%d %H:%M:%S')
        r["TimeGPS"] = datetime_object

        r['TimeLog'] = r['TimeLog'].replace("T"," ")
        datetime_object = datetime.datetime.strptime(r["TimeLog"], '%Y-%m-%d %H:%M:%S.%f')
        r['TimeLog'] = datetime_object

    # TimeGPS: time of sending the GPS signal
    # TimeLong: time of receiving/processing the location by the system (irrelevant)
    #print(data_bus.head())

    # Importing the routes of a specific day (make sure to use the right directory)
    # Not exactly sure yet what the routes represent
    data_routes = pd.read_csv("C:/Users/jurri/Documents/Studie/DSDM 2020 - 2021/Project 1/Data/schedules/2020-09-01/routes.txt", sep=",")
    #print(data_routes.head())
    #print(data_routes.shape)

    data_stop_times = pd.read_csv("C:/Users/jurri/Documents/Studie/DSDM 2020 - 2021/Project 1/Data/schedules/2020-09-01/stop_times.txt", sep=",")
    #print(data_stop_times.head())
    #print(data_stop_times.shape)

    # data_stops contains the locations of the bus stops, identified by a stop_id and contains the stop name
    data_stops = pd.read_csv("C:/Users/jurri/Documents/Studie/DSDM 2020 - 2021/Project 1/Data/schedules/2020-09-01/stops.txt", sep=",")
    #print(data_stops.head())
    #print(data_stops.shape)

    # timetables is not a default within the GTFS standard, therefore: if we can avoid using it, that would make it easier to use for other cities
    # TODO: set right column types for the first two columns
    data_timetables = pd.read_csv("C:/Users/jurri/Documents/Studie/DSDM 2020 - 2021/Project 1/Data/schedules/2020-09-01/timetables.txt", sep=",", header=None)
    data_timetables.columns = ["line","trip#","stop_lat","stop_long","stop_id","stop_name","time?","code?","number?","stop_nr","number","day/night","platform"]
    #print(data_timetables.head())
    #print(data_timetables.shape)

    # Some trial and error by Jurriaan (doesn't really work)
    #find_arrival(data_stop_times.iloc[0],data_bus)

    pass



if __name__ == "__main__":
    main()
