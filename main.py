import pandas as pd
import datetime
from schedule_matching import match_schedule

def main():

    today = '2020-01-09' # this is a parameter that indicates the day you are working with,
                        # which is necessary for computing the datetime objects (where only time is available)

    data_stop_times = pd.read_csv("C:/Users/jurri/Documents/Studie/DSDM 2020 - 2021/Project 1/Data/schedules/2020-09-01/stop_times.txt", sep=",")
    del data_stop_times['departure_time']

    # todo: obviously the formatting below does not work when analysis is done on a line that passes midnight, we should include dates for that
    #best would be to delete these rows, but to include the ones of a day earlier (after all these are the buses that are being recorded)

    data_stop_times['arrival_time'] = data_stop_times['arrival_time'].str.replace(' 24',' 00')
    data_stop_times['arrival_time'] = data_stop_times['arrival_time'].str.replace(' 25', ' 01')
    data_stop_times['arrival_time'] = data_stop_times['arrival_time'].str.replace(' 26', ' 02')
    data_stop_times['arrival_time'] = data_stop_times['arrival_time'].str.replace(' 27', ' 03')
    data_stop_times['arrival_time'] = data_stop_times['arrival_time'].str.replace(' 28', ' 04')
    data_stop_times['arrival_time'] = data_stop_times['arrival_time'].str.replace(' 29', ' 05')

    # formatting the the stop id
    data_stop_times['stop_id'] = data_stop_times['stop_id'].str.replace(' ','')

    # formatting the times
    data_stop_times['arrival_time'] = pd.to_datetime(today+data_stop_times['arrival_time'],
                                                     format='%Y-%m-%d %H:%M:%S')

    #Get the line number
    x = data_stop_times['trip_id'].str.split("_",expand=True)
    lines = x[0]
    data_stop_times['lines'] = lines

    #data_stop_times['arrival_time'] = pd.datetime.datetime.combine(today, data_stop_times['arrival_time'])

    print(data_stop_times.head())

    '''
    
    # FOR ONLINE DATA
    test_arrival2 = pd.read_csv("C:/Users/jurri/Documents/Studie/DSDM 2020 - 2021/Project 1/arrival_estimations.csv", sep=",",
                                dtype={'bus_line':str,'stop_zespol':str,'stop_slupek':str,})
    test_arrival2 = test_arrival2.rename(columns={'scheduled_arrival':'scheduled_time',
                                                  'estimated_arrival':'arrival_time'})
    test_arrival2['arrival_time'] = test_arrival2['arrival_time'].str.replace('2020-11-23','2020-09-01')
    test_arrival2['stop_id'] = test_arrival2[["stop_zespol","stop_slupek"]].agg('_'.join, axis=1)
    test_arrival2['arrival_time'] = pd.to_datetime(test_arrival2['arrival_time'])
    test_arrival2['stop_seq'] = ""
    #print(test_arrival2.info())
    #print(test_arrival2['stop_id'])

    matched_arrivals2 = match_schedule(data_stop_times,test_arrival2)
    #print(matched_arrivals2.head())
    # test_arrival2.to_csv("C:/Users/jurri/Documents/Studie/DSDM 2020 - 2021/Project 1/arrival_matches2.csv", ';')

    '''

    # FOR HISTORIC DATA TRIALS
    test_arrival3 = pd.read_csv("C:/Users/jurri/Documents/Studie/DSDM 2020 - 2021/Project 1/Arrivals/arrival_estimations_i.csv",';',
                                dtype={'bus_line':str,'stop_id':str},index_col=False)
    print(test_arrival3.info())
    test_arrival3['arrival_time'] = pd.to_datetime(test_arrival3['arrival_time'])
    #test_arrival3 = test_arrival3.sort_values(by='arrival_time',ascending=True)
    test_arrival3['scheduled_time'] = ""
    # test_arrival3['location'] = ""
    test_arrival3[['stop_zespol','stop_slupek']] = test_arrival3.stop_id.str.split("_",expand=True)
    test_arrival3['stop_seq'] = ""

    matched_arrivals3 = match_schedule(data_stop_times, test_arrival3)
    test_arrival3.to_csv("C:/Users/jurri/Documents/Studie/DSDM 2020 - 2021/Project 1/Arrivals/arrival_matches_k.csv", ';', index=False)

    print(test_arrival3.head())
    
    '''

    # FOR HISTORIC DATA
    test_arrival4 = pd.read_csv(
        "C:/Users/jurri/Documents/Studie/DSDM 2020 - 2021/Project 1/Arrivals/arrival_estimations_i.csv", ',',
        dtype={'bus_line': str, 'stop_id': str}, index_col=False, header=None)
    test_arrival4.columns=['bus_line','bus_brigade','stop_id','location','arrival_time','scheduled_time']
    test_arrival4['stop_id'] = test_arrival4['stop_id'].str.replace(' ','')
    test_arrival4['arrival_time'] = pd.to_datetime(test_arrival4['arrival_time'])
    test_arrival4[['stop_zespol', 'stop_slupek']] = test_arrival4.stop_id.str.split("_", expand=True)
    test_arrival4['stop_seq'] = ""

    matched_arrivals4 = match_schedule(data_stop_times, test_arrival4)
    test_arrival4.to_csv("C:/Users/jurri/Documents/Studie/DSDM 2020 - 2021/Project 1/Arrivals/arrival_matches_h.csv",
                         ';', index=False)

    print(test_arrival4.head())
    '''

    pass


if __name__ == "__main__":
    main()