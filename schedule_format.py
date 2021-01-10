# from https://www.geeksforgeeks.org/convert-json-to-csv-in-python/

import json
import csv
import pandas

def format():

    '''
    with open(
            "C:/Users/jurri/Documents/Studie/DSDM 2020 - 2021/Project 1/Online Data/timetable_per_line_and_stop_16dec.json") as json_file:
        data = json_file

    schedule_data = data['123:1001:01']

    # now we will open a file for writing
    data_file = open(
        'C:/Users/jurri/Documents/Studie/DSDM 2020 - 2021/Project 1/Online Data/timetable_per_line_and_stop_16dec.csv',
        'w')

    # create the csv writer object
    csv_writer = csv.writer(data_file)

    # Counter variable used for writing
    # headers to the CSV file
    count = 0

    for lin in schedule_data:
        if count == 0:
            # Writing headers of CSV file
            header = lin.keys()
            csv_writer.writerow(header)
            count += 1

        # Writing data of CSV file
        csv_writer.writerow(lin.values())

    data_file.close()
    '''

    with open('C:/Users/jurri/Documents/Studie/DSDM 2020 - 2021/Project 1/Online Data/timetable_per_line_and_stop_16dec.json', 'r') as f:
        data = json.loads(f.read())

    print(data['102:1232:01'])
    print(type(data['102:1232:01']))

    f.close()


    #df = pandas.read_json("C:/Users/jurri/Documents/Studie/DSDM 2020 - 2021/Project 1/Online Data/timetable_per_line_and_stop_16dec.json")
    #df.to_csv("C:/Users/jurri/Documents/Studie/DSDM 2020 - 2021/Project 1/Online Data/timetable_per_line_and_stop_16dec.csv")