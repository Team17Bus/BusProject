from processing import get_busstops_per_line, get_lines_per_busstop, get_timetable_per_busstop_per_line
import json


# store dictionary of busstops per line in json file 'busstops_per_line.json'
# (~7500 API CALLS)
line_dict = get_lines_per_busstop()
busstops_per_line = get_busstops_per_line(line_dict)
with open('busstops_per_line.json', 'w') as fh:
   json.dump(busstops_per_line, fh, sort_keys=True, indent=4)


# store dictionary of timetables per busstop & line in json file 'timetable_per_line_and_stop.json'
# (~20746 API CALLS)
timetable_per_line_and_stop = get_timetable_per_busstop_per_line(busstops_per_line)
timetable_per_line_and_stop = dict(
    (k[0] + ':' + ':'.join(k[1]), v.to_json(orient='split')) for k, v in timetable_per_line_and_stop.items())
with open('timetable_per_line_and_stop.json', 'w') as fh:
    json.dump(timetable_per_line_and_stop, fh, indent=4)




