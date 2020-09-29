from api_requests import busestrams_get, dbstore_get, dbtimetable_get
import pandas as pd



def main():
    # Example calls (uncomment and print to see the results):

    df = busestrams_get(dict(type=1))

    # df = dbstore_get()

    # retrieving the line list for the Marszałkowska stop  (busstopId = 7009) and bar number 01 (busstopNr = 01) and line 523 (line = 523)
    # df = dbtimetable_get(dict(busstopId='7009', busstopNr='01', line='523'))

    # retrieving the line list for the Marszałkowska stop (busstopId = 7009) and bar number 01 (busstopNr = 01)
    # df = dbtimetable_get(dict(busstopId='7009', busstopNr='01'))


    # retrieving all the 'zespol' (??) for the busstop 'Marysin'
    # df = dbtimetable_get(dict(name='Marysin'))

    pd.set_option('display.max_columns', None)
    print(df)



if __name__ == "__main__":
    main()
