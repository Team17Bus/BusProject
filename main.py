import pandas as pd
import datetime
from schedule_matching import match_schedule, match_schedule2
from schedule_format import format

def main():

    today = '2020-09-01' # this is a parameter that indicates the day you are working with,
                        # which is necessary for computing the datetime objects (where only time is available)

    data_stop_times = pd.read_csv("C:/Users/jurri/Documents/Studie/DSDM 2020 - 2021/Project 1/Data/schedules/2020-09-01/stop_times.txt", sep=",")
    data_stop_times_yesterday = pd.read_csv("C:/Users/jurri/Documents/Studie/DSDM 2020 - 2021/Project 1/Data/schedules/2020-09-02/stop_times.txt", sep=",")
    #note that the yesterday in this case should actually be 08-31 (but that file doesn't exist)

    del data_stop_times['departure_time']
    del data_stop_times_yesterday['departure_time']

    # todo: obviously the formatting below does not work when analysis is done on a line that passes midnight, we should include dates for that
    #best would be to delete these rows, but to include the ones of a day earlier (after all these are the buses that are being recorded)

    #remove all the scheduled arrivals that actually take place on the next day (night buses etc.)
    data_stop_times = data_stop_times[~(data_stop_times['arrival_time'].str.contains(' 24'))]
    data_stop_times = data_stop_times[~(data_stop_times['arrival_time'].str.contains(' 25'))]
    data_stop_times = data_stop_times[~(data_stop_times['arrival_time'].str.contains(' 26'))]
    data_stop_times = data_stop_times[~(data_stop_times['arrival_time'].str.contains(' 27'))]
    data_stop_times = data_stop_times[~(data_stop_times['arrival_time'].str.contains(' 28'))]
    data_stop_times = data_stop_times[~(data_stop_times['arrival_time'].str.contains(' 29'))]

    #add all scheduled arrivals that actually take place on this day, but are in yesterday's schedule
    data_stop_times.append(data_stop_times_yesterday[(data_stop_times_yesterday['arrival_time'].str.contains(' 24'))])
    data_stop_times.append(data_stop_times_yesterday[(data_stop_times_yesterday['arrival_time'].str.contains(' 25'))])
    data_stop_times.append(data_stop_times_yesterday[(data_stop_times_yesterday['arrival_time'].str.contains(' 26'))])
    data_stop_times.append(data_stop_times_yesterday[(data_stop_times_yesterday['arrival_time'].str.contains(' 27'))])
    data_stop_times.append(data_stop_times_yesterday[(data_stop_times_yesterday['arrival_time'].str.contains(' 28'))])
    data_stop_times.append(data_stop_times_yesterday[(data_stop_times_yesterday['arrival_time'].str.contains(' 29'))])

    #recplace the 'imaginary' hours
    data_stop_times['arrival_time'] = data_stop_times['arrival_time'].str.replace(' 24',' 00')
    data_stop_times['arrival_time'] = data_stop_times['arrival_time'].str.replace(' 25', ' 01')
    data_stop_times['arrival_time'] = data_stop_times['arrival_time'].str.replace(' 26', ' 02')
    data_stop_times['arrival_time'] = data_stop_times['arrival_time'].str.replace(' 27', ' 03')
    data_stop_times['arrival_time'] = data_stop_times['arrival_time'].str.replace(' 28', ' 04')
    data_stop_times['arrival_time'] = data_stop_times['arrival_time'].str.replace(' 29', ' 05')

    # formatting the times
    data_stop_times['arrival_time'] = pd.to_datetime(today + data_stop_times['arrival_time'],
                                                     format='%Y-%m-%d %H:%M:%S')

    # formatting the the stop id
    data_stop_times['stop_id'] = data_stop_times['stop_id'].str.replace(' ','')

    #Get the line number
    x = data_stop_times['trip_id'].str.split("_",expand=True)
    lines = x[0]
    data_stop_times['lines'] = lines

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

    

    # FOR HISTORIC DATA TRIALS
    test_arrival3 = pd.read_csv("C:/Users/jurri/Documents/Studie/DSDM 2020 - 2021/Project 1/Arrivals/arrival_estimations_n.csv",';',
                                dtype={'bus_line':str,'stop_id':str},index_col=False)
    print(test_arrival3.info())

    #test_arrival3 = test_arrival3[test_arrival3['bus_line']=="104"]
    #test_arrival3 = test_arrival3[test_arrival3['bus_brigade']==2.0]

    test_arrival3['arrival_time'] = pd.to_datetime(test_arrival3['arrival_time'], format='%Y-%m-%d %H:%M:%S')
    test_arrival3 = test_arrival3.sort_values(by='arrival_time',ascending=True)
    test_arrival3['scheduled_time'] = ""
    test_arrival3['stop_id'] = test_arrival3['stop_id'].str.replace(' ', '')
    # test_arrival3['location'] = ""

    test_arrival3[['stop_zespol','stop_slupek']] = test_arrival3.stop_id.str.split("_",expand=True)
    test_arrival3['stop_seq'] = ""

    print(test_arrival3.head())

    matched_arrivals3 = match_schedule(data_stop_times, test_arrival3)
    test_arrival3.to_csv("C:/Users/jurri/Documents/Studie/DSDM 2020 - 2021/Project 1/Arrivals/arrival_matches_n.csv", ';', index=False)

    print(test_arrival3.head())

    

    # FOR HISTORIC DATA
    test_arrival4 = pd.read_csv(
        "C:/Users/jurri/Documents/Studie/DSDM 2020 - 2021/Project 1/Arrivals/arrival_estimations_o.csv", ',',
        dtype={'bus_line': str, 'stop_id': str}, index_col=False, header=None)
    test_arrival4.columns=['bus_line','bus_brigade','stop_id','location','arrival_time','scheduled_time']
    test_arrival4['stop_id'] = test_arrival4['stop_id'].str.replace(' ','')
    test_arrival4['arrival_time'] = pd.to_datetime(test_arrival4['arrival_time'])
    test_arrival4[['stop_zespol', 'stop_slupek']] = test_arrival4.stop_id.str.split("_", expand=True)
    test_arrival4['stop_seq'] = ""
    test_arrival3 = test_arrival4.sort_values(by='arrival_time',ascending=True)

    matched_arrivals4 = match_schedule(data_stop_times, test_arrival4)
    test_arrival4.to_csv("C:/Users/jurri/Documents/Studie/DSDM 2020 - 2021/Project 1/Arrivals/arrival_matches_o.csv",
                         ';', index=False)

    print(test_arrival4.head())
    '''

    test_arrival5 = pd.read_csv(
        "C:/Users/jurri/Documents/Studie/DSDM 2020 - 2021/Project 1/Arrivals/arrival_estimations_n.csv", ';',
        dtype={'bus_line': str, 'stop_id': str}, index_col=False)
    #test_arrival5.columns = ['bus_line', 'bus_brigade', 'stop_id', 'location', 'arrival_time', 'scheduled_time']
    test_arrival5['scheduled_time'] = ""
    test_arrival5['stop_id'] = test_arrival5['stop_id'].str.replace(' ', '')
    test_arrival5['arrival_time'] = pd.to_datetime(test_arrival5['arrival_time'], format='%Y-%m-%d %H:%M:%S')
    test_arrival5[['stop_zespol', 'stop_slupek']] = test_arrival5.stop_id.str.split("_", expand=True)
    test_arrival5['stop_seq'] = ""
    test_arrival5 = test_arrival5.sort_values(by='arrival_time', ascending=True)

    print(test_arrival5.head())

    matched_arrival5 = match_schedule2(data_stop_times, test_arrival5)
    test_arrival5.to_csv("C:/Users/jurri/Documents/Studie/DSDM 2020 - 2021/Project 1/Arrivals/arrival_matches2_c.csv",
                         ';', index=False)

    print(test_arrival5.head())

    pass


if __name__ == "__main__":
    main()
    #format()