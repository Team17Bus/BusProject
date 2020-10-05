from api_requests import busestrams_get, dbstore_get, dbtimetable_get
import pandas as pd
from processing import get_all_lines, get_lines_per_busstop, get_busstops_per_line, get_timetable_per_busstop_per_line, coord_distance
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
    pass



if __name__ == "__main__":
    main()
