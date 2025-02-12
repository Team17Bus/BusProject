# BusProject
## Why is my bus late? DSDM Master's Project September 2020 - January 2021

### api_key.py
Obtain an api key from https://api.um.warszawa.pl/# and assign this (as a string) to the my_api_key variable in api_key.py

### OurAPIdocs.md
The file 'OurAPIdocs' is intended for a quick overview/translation of the actual documentation

### api_requests.py   
File in which all the functions are defined -- no need to touch this. Is imported by main.py

### main.py (file to run)
In the file 'main.py', play around with functions and their parameters. 
There are 3 functions to call (see also 'OurAPIdocs'):
- busestrams_get()
- dbstore_get()
- dbtimetable_get()    
     
The user only needs to take care of the parameters specified below. Please provide these parameters in the form of a python dictionary to the function.

#### busestrams_get()
Required: -   
Optional: {line='', brigade=''}    
Sample output for busestrams_get():
~~~
     Lines        Lon VehicleNumber                 Time        Lat Brigade
0      213  21.169385          1000  2020-09-29 22:36:13  52.197932       1
1      196  21.177021          1002  2020-09-29 22:36:21  52.256888       1
2      130  21.115345          1003  2020-09-29 21:26:02  52.234556       2
3      213  21.165424          1008  2020-09-29 22:36:14  52.204900       3
4      311  21.115648          1009  2020-09-29 21:09:39  52.234521       1
...    ...        ...           ...                  ...        ...     ...
1001   520  21.014265          9944  2020-09-29 22:36:28  52.225872       5
1002   520  21.002102          9946  2020-09-29 22:36:29  52.243149     012
1003   719  20.898455          9947  2020-09-29 22:36:27  52.239414       2
1004   140  21.111202          9951  2020-09-29 22:36:25  52.360882      08
1005   210  20.808622          9953  2020-09-29 22:36:29  52.293827       5

[1006 rows x 6 columns]
~~~


#### dbstore_get()
Required: -   
Optional: {sortBy='', page='', size=''}    
Sample output for dbstore_get():    
~~~
     zespol slupek        nazwa_zespolu id_ulicy   szer_geo   dlug_geo  \
0      1001     01             Kijowska     2201  52.248455  21.044827   
1      1001     02             Kijowska     2201  52.249078  21.044443   
2      1001     03             Kijowska     2201  52.248998  21.043983   
3      1001     04             Kijowska     2201  52.249905  21.041726   
4      1001     05             Kijowska     1203  52.250319  21.043861   
...     ...    ...                  ...      ...        ...        ...   
7465   R-13     99          ZEA STALOWA     2002  52.263611  21.047777   
7466   R-13     99          ZEA STALOWA     2002       null       null   
7467   R-13     99          ZEA STALOWA     2002  52.263631  21.047922   
7468   R-19     00  WYDZIAŁ WŁOŚCIAŃSKA     2575  52.271236  20.968586   
7469   R-19     99  WYDZIAŁ WŁOŚCIAŃSKA     2575  52.271236  20.968496   

                 kierunek          obowiazuje_od  
0          al.Zieleniecka  2020-06-01 00:00:00.0  
1               Ząbkowska  2020-06-01 00:00:00.0  
2          al.Zieleniecka  2020-06-01 00:00:00.0  
3               Ząbkowska  2020-06-01 00:00:00.0  
4          al.Zieleniecka  2020-06-01 00:00:00.0  
...                   ...                    ...  
7465          ZEA STALOWA  2020-06-01 00:00:00.0  
7466          ZEA STALOWA  2020-06-02 00:00:00.0  
7467          ZEA STALOWA  2020-06-08 00:00:00.0  
7468          Włościańska  2020-06-01 00:00:00.0  
7469  WYDZIAŁ WŁOŚCIAŃSKA  2020-06-01 00:00:00.0  

[7470 rows x 8 columns]
~~~


#### dbtimetable_get()
This function actually refers to 3 different types of datasets (see OurAPIdocs)
Required: one of   
  - {busstopId='', busstopNr='', line=''}
  - {busstopId='', busstopNr=''}
  - {name=''}     
     
Optional: -   
Sample output for dbtimetable_get(dict(busstopId='7009', busstopNr='01', line='523')):
~~~
    symbol_2 symbol_1 brygada                 kierunek   trasa      czas
0       null     null      14  PKP Olszynka Grochowska  TP-OLS  05:00:00
1       null     null     017  PKP Olszynka Grochowska  TP-OLS  05:08:00
2       null     null       1  PKP Olszynka Grochowska  TP-OLS  05:15:00
3       null     null       2  PKP Olszynka Grochowska  TP-OLS  05:23:00
4       null     null     023  PKP Olszynka Grochowska  TP-OLS  05:30:00
..       ...      ...     ...                      ...     ...       ...
144     null     null       8  PKP Olszynka Grochowska  TX-OLS  22:35:00
145     null     null      10  PKP Olszynka Grochowska  TP-OLS  22:50:00
146     null     null      11  PKP Olszynka Grochowska  TX-OLS  23:05:00
147     null     null      12  PKP Olszynka Grochowska  TX-OLS  23:20:00
148     null     null       3  PKP Olszynka Grochowska  TX-OLS  23:50:00

[149 rows x 6 columns]
~~~   
    
Sample output for dbtimetable_get(dict(busstopId='7009', busstopNr='01')):
~~~
0     138
1     143
2     151
3     182
4     187
5     188
6     411
7     502
8     514
9     520
10    523
11    525
12    N25
Name: linia, dtype: object
~~~   
    
Sample output for dbtimetable_get(dict(busstopId='7009', busstopNr='01')):
~~~
0    2064
1    4072
Name: zespol, dtype: object
~~~
    
#### Important translations (see 'OurAPIDocs' for others ):
- zespol == busstopId   
- slupek == busstopNr   
- brygada: id of a vehicle (bus/tram) on a specific line
- linia: line number

### Description of the files
A short description of what is in the files from the Warsaw public transport.

#### Buses
For every day there is a separate file specifying the locations of buses, for every record the following is available:
- number of the bus or tram line
- vehicle brigade number
- time of sending the GPS signal
- latitude coordinate in the WGS84 system
- longitude coordinate in the WGS84 system
- time of obtaining information by the internal system BCM

!!Note that there is no unique id for every bus - a combination of line number and brigade number will have to serve as a unique ID. It has, so far not been confirmed that this is safe to do!!

#### Schedules
The individual catalogs contain the timetable in GTFS format (https://developers.google.com/transit/gtfs).
For 2020-09-07, 2020-09-14 files have not been generated.

on the open data portal m.st. Warsaw (https://api.um.warszawa.pl) provides information about:
- stops
- lines available at the stop
- line departure time from the stop (current and archived about 2 months back)

For every day there is a separate folder with the following files:
- Agency: Transit agencies with service represented in this dataset.
- Calendar: Service dates specified using a weekly schedule with start and end dates. 
- Routes: Transit routes. A route is a group of trips that are displayed to riders as a single service.
- Stop_times: Times that a vehicle arrives at and departs from stops for each trip.
- Stops: Stops where vehicles pick up or drop off riders. Also defines stations and station entrances.
- Timetables: Basically the complete timetable for the day* (Not present in the GTFS documentation)
- Trips: Trips for each route. A trip is a sequence of two or more stops that occur during a specific time period.
For more information about these files, please check the GTFS documentation (it's nice :)

*) This is what I figured to be in the timetables file:

1. Line number
2. Trip# (the line is driven let's say 20 times per day, every trip has its own number Can als be identified with the departure time for the first stop on the line, in other datasets)
3. Stop_lat: Latitude of the bus stop
4. Stop_long: Longitude of the bus stop
5. Stop_id: Identification of the bus stop. Is the same one as used in other datasets (e.g. 7009_01), not confirmed.
6. Stop_name: Normal name of the bus stop. Is the same name as used in other datasets, not confirmed.
7. Time: a time that belongs to a combination of stop and line-trip. Unknown wether this is the arrival or departure time.
8. Code: some unice code line_trip_magicNumber_departureTimeFirstStopInTrip
9. A magic number which I don't know what it represents.
10. Stop_number: a number that indicates the index of the stop at the trip (e.g. 5, then it is the fifth bus stop on the trip). Sometimes these numbers do not start at 1, or jumps are being made.
11. Another magic number, which is 1 in many cases
12. Has either the value 'day' or 'night'
13. Platform number, is also indicated in the stop_id (the 01 ofter 7009). However, for some reason the needed it as another separate variable.
