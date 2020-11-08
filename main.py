from api_requests import busestrams_get, dbstore_get, dbtimetable_get
import pandas as pd
import datetime
from processing import get_all_lines, get_lines_per_busstop, get_busstops_per_line, get_timetable_per_busstop_per_line, coord_distance, find_arrival
import json
from schedule_matching import match_arrival


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
    # START OF THE SCRIPT - DRAFT


    # ---------------------------------------------------------------------------
    # Only run the following in the morning (start of the day, 4 am?), once:

    # get dictionary of lines per busstop
    # RUN ONCE AND THEN SAVE IN FILE! (~7500 API CALLS)
    """
    line_dict = get_lines_per_busstop()
    line_dict = dict((':'.join(k), v) for k, v in line_dict.items())
    with open('lines_per_busstop.json', 'w') as fh:
       json.dump(line_dict, fh, sort_keys=True, indent=4)
    # --> saved in lines_per_busstop.json
    """

    with open('lines_per_busstop.json', 'r') as fh:
        my_dict = json.load(fh)
    lines_per_busstop_dict = dict()
    for k in my_dict:
        k_split = k.split(':')
        new_k = (k_split[0], k_split[1])
        lines_per_busstop_dict[new_k] = my_dict[k]
    busstops_per_line = get_busstops_per_line(lines_per_busstop_dict)
    print(busstops_per_line)

    # get dictionary of timetables per busstop & line
    # RUN ONCE AND THEN SAVE IN FILE! (~7500 API CALLS)
    timetable_per_line_and_stop = get_timetable_per_busstop_per_line(busstops_per_line)
    timetable_per_line_and_stop = dict((k[0] + ':' + ':'.join(k[1]), v.to_json(orient='split')) for k, v in timetable_per_line_and_stop.items())
    with open('timetable_per_line_and_stop.json', 'w') as fh:
        json.dump(timetable_per_line_and_stop, fh, indent=4)
    # --> saved in timetable_per_line_and_stop.json

    with open('timetable_per_line_and_stop.json', 'r') as fh:
        my_dict = json.load(fh)
    timetable_per_line_and_stop_dict = dict()
    for k in my_dict:
        k_split = k.split(':')
        new_k = (k_split[0], (k_split[1], k_split[2]))
        print(my_dict[k])
        v = pd.read_json(my_dict[k], orient='split')
        timetable_per_line_and_stop_dict[new_k] = v

    # End of morning run
    # ---------------------------------------------------------------------------





    # END OF THE SCRIPT - DRAFT
    # ---------------------------------------------------------------------------
    # ---------------------------------------------------------------------------



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

    today = '2020-09-01' # this is a parameter that indicates the day you are working with,
                        # which is necessary for computing the datetime objects (where only time is available)
    today_dt = datetime.datetime.strptime(today, '%Y-%m-%d').date()

    # Importing the bus locations of a specific day (make sure to use the right directory)
    data_bus = pd.read_csv("C:/Users/jurri/Documents/Studie/DSDM 2020 - 2021/Project 1/Data/buses/t_2020_08_31_23_30",
                       sep=";",
                       header=None)
    data_bus.columns = ["Line","Brigade","TimeGPS","Lat","Long","TimeLog"]

    # TODO: Cleaning and formatting the data (probably move this to a separate function)
    data_bus['TimeGPS'] = pd.to_datetime(data_bus['TimeGPS'])
    data_bus['TimeLog'] = pd.to_datetime(data_bus['TimeLog'])

    # TimeGPS: time of sending the GPS signal
    # TimeLong: time of receiving/processing the location by the system (irrelevant)
    #print(data_bus.head())

    # Importing the routes of a specific day (make sure to use the right directory)
    # Not exactly sure yet what the routes represent
    # data_routes = pd.read_csv("C:/Users/jurri/Documents/Studie/DSDM 2020 - 2021/Project 1/Data/schedules/2020-09-01/routes.txt", sep=",")
    #print(data_routes.head())
    #print(data_routes.shape)

    data_stop_times = pd.read_csv("C:/Users/jurri/Documents/Studie/DSDM 2020 - 2021/Project 1/Data/schedules/2020-09-01/stop_times.txt", sep=",")

    data_stop_times = data_stop_times.loc[0:70000] #to save some time

    # todo: obviously the formatting below does not work when analysis is done on a line that passes midnight, we should include dates for that
    data_stop_times['arrival_time'] = data_stop_times['arrival_time'].str.replace(' 24',' 00')
    data_stop_times['arrival_time'] = data_stop_times['arrival_time'].str.replace(' 25', ' 01')
    data_stop_times['arrival_time'] = data_stop_times['arrival_time'].str.replace(' 26', ' 02')
    data_stop_times['arrival_time'] = data_stop_times['arrival_time'].str.replace(' 27', ' 03')
    data_stop_times['arrival_time'] = data_stop_times['arrival_time'].str.replace(' 28', ' 04')
    data_stop_times['arrival_time'] = data_stop_times['arrival_time'].str.replace(' 29', ' 05')

    data_stop_times['departure_time'] = data_stop_times['departure_time'].str.replace(' 24', ' 00')
    data_stop_times['departure_time'] = data_stop_times['departure_time'].str.replace(' 25', ' 01')
    data_stop_times['departure_time'] = data_stop_times['departure_time'].str.replace(' 26', ' 02')
    data_stop_times['departure_time'] = data_stop_times['departure_time'].str.replace(' 27', ' 03')
    data_stop_times['departure_time'] = data_stop_times['departure_time'].str.replace(' 28', ' 04')
    data_stop_times['departure_time'] = data_stop_times['departure_time'].str.replace(' 29', ' 05')

    data_stop_times['stop_id'] = data_stop_times['stop_id'].str.replace(' ','')

    data_stop_times['arrival_time'] = pd.to_datetime(today+data_stop_times['arrival_time'],
                                                     format='%Y-%m-%d %H:%M:%S')
    data_stop_times['departure_time'] = pd.to_datetime(today+data_stop_times['departure_time'],
                                                       format='%Y-%m-%d %H:%M:%S')

    #data_stop_times['arrival_time'] = pd.datetime.datetime.combine(today, data_stop_times['arrival_time'])

    print(data_stop_times.head())
    #print(data_stop_times.shape)

    # data_stops contains the locations of the bus stops, identified by a stop_id and contains the stop name
    # data_stops = pd.read_csv("C:/Users/jurri/Documents/Studie/DSDM 2020 - 2021/Project 1/Data/schedules/2020-09-01/stops.txt", sep=",")
    #print(data_stops.head())
    #print(data_stops.shape)

    # timetables is not a default within the GTFS standard, therefore: if we can avoid using it, that would make it easier to use for other cities
    # TODO: set right column types for the first two columns
    data_timetables = pd.read_csv("C:/Users/jurri/Documents/Studie/DSDM 2020 - 2021/Project 1/Data/schedules/2020-09-01/timetables.txt", sep=",", header=None)
    #data_timetables.columns = ["line","trip#","stop_lat","stop_long","stop_id","stop_name","time?","code?","number?","stop_nr","number","day/night","platform"]
    #print(data_timetables.head())
    #print(data_timetables.shape)

    # Some trial and error by Jurriaan (doesn't really work)
    #print(data_bus.iloc[0]['TimeLog'].time())
    #find_arrival(data_stop_times.iloc[0],data_bus)

    # data_arrival_times is the table where, for now, we store the actual arrivals for a bus
    data_arrival_times = data_stop_times.copy()
    data_arrival_times["real_arr_time"] = ""

    print(data_arrival_times)

    # todo: is there a more efficient way than sending the whole schedule every time?

    # lines below are for testing schedule matching
    test_arrival_time = '21:18:30'
    test_arrival_time = datetime.datetime.strptime(today+' '+test_arrival_time,'%Y-%m-%d %H:%M:%S')
    test_arrival = ["109",test_arrival_time,'7013_06']
    data_arrival_times = match_arrival(data_arrival_times,test_arrival)

    pass


if __name__ == "__main__":
    main()
