# Why is my bus late? 
## API documentation for 
https://api.um.warszawa.pl/api/action/

Website: https://api.um.warszawa.pl/#

-------------------------------------

## busestrams_get
##### Online location of public transport, updated every 10 seconds

#### Required parameters
- resource_id=f2e5503e-927d-4ad3-9500-4ab9e55deb59
- apikey=
- type=1    (2 for tram locations, which we won't need)

#### Optional parameters
- line=
- brigade= &nbsp;&nbsp;&nbsp;&nbsp; (Kuba: "like an ID of a certain vehicle (here: bus) on specific line, e.g. This is why these numbers repeat on various lines.")

#### Available data
- Lat - latitude coordinate in the WGS84 system (EPSG: 4326)
- Lon - longitude coordinate in the WGS84 system (EPSG: 4326)
- Time - time of sending the GPS signal
- Lines - number of a bus or tram line
- Brigade - id of a certain vehicle on a specific line

#### Sample output

~~~
{
	   "result": [
        {
            "Brigade": "1",
            "Lat": 52.1798648,
            "Lines": "213",
            "Lon": 21.232337,
            "Time": "2020-09-18 22:53:42",
            "VehicleNumber": "1001"
        },
        {
            "Brigade": "3",
            "Lat": 52.2120383,
            "Lines": "213",
            "Lon": 21.1047441,
            "Time": "2020-09-18 22:53:52",
            "VehicleNumber": "1004"
        },
        ...
        {
            "Brigade": "3",
            "Lat": 52.249916,
            "Lines": "719",
            "Lon": 20.841076,
            "Time": "2020-09-18 22:53:47",
            "VehicleNumber": "9954"
        }
    ]
}
~~~

-------------------------------------
-------------------------------------

## dbtimetable_get

##### Gives access to public transport timetables  


### Set of stops: 
(id=b27f4c17-5c50-4a5b-89dd-236b282bc499)

#### Required parameters
  - name=
  - apikey=
  
#### Sample output (for name = 'Marysin')
- zespol - busstopId    
- nazwa - name
~~~
{
    "result": [
        {
            "values": [
                {
                    "key": "zespol",
                    "value": "2064"
                },
                {
                    "key": "nazwa",
                    "value": "Marysin"
                }
            ]
        },
        {
            "values": [
                {
                    "key": "zespol",
                    "value": "4072"
                },
                {
                    "key": "nazwa",
                    "value": "Marysin"
                }
            ]
        }
    ]
}
~~~

-------------------------------------

### Lines available at a stop with busstopId and busstopNr: 
(id=88cd555f-6f31-43ca-9de4-66c479ad5942)

#### Required parameters
  - busstopId= &nbsp;&nbsp;&nbsp; (e.g. '7009')
  - busstopNr= &nbsp;&nbsp; (e.g. '01')
  - apikey=

##### Sample output (for busstopId='7009', busstopNr='01'); real output has 13 entries as of 29/09/2020
- linia - line
~~~
{
    "result": [
        {
            "values": [
                {
                    "key": "linia",
                    "value": "138"
                }
            ]
        },
        {
            "values": [
                {
                    "key": "linia",
                    "value": "143"
                }
            ]
        },
        ...
        {
            "values": [
                {
                    "key": "linia",
                    "value": "N25"
                }
            ]
        }
    ]
}
~~~
-------------------------------------

### Timetable for a specific line for a busstopId and a busstopNr:
(id=e923fa0e-d96c-43f9-ae6e-60518c9f3238)

#### Required parameters
  - busstopId= &nbsp;&nbsp;&nbsp; (e.g. '7009')
  - busstopNr= &nbsp;&nbsp; (e.g. '01')
  - line= &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; (e.g. '523')
  - apikey=
 
##### Sample output (for busstopId='7009', busstopNr='01', line='523'); real output has 149 entries as of 29/09/2020
- kierunek - direction (Kuba: "Last stop’s name of a specific route determines direction.")
- trasa (Kuba: "I assume these codes define the first and last stop on a specific line. They may differ for a specific line as some routes end faster than usual (e.g. last course of the day ends in the bus central rather than the final loop).")    
- czas - time


~~~
{
    "result": [
        {
            "values": [
                {
                    "key": "symbol_2",
                    "value": "null"
                },
                {
                    "key": "symbol_1",
                    "value": "null"
                },
                {
                    "key": "brygada",
                    "value": "14"
                },
                {
                    "key": "kierunek",
                    "value": "PKP Olszynka Grochowska"
                },
                {
                    "key": "trasa",
                    "value": "TP-OLS"
                },
                {
                    "key": "czas",
                    "value": "05:00:00"
                }
            ]
        },
        {
            "values": [
                {
                    "key": "symbol_2",
                    "value": "null"
                },
                {
                    "key": "symbol_1",
                    "value": "null"
                },
                {
                    "key": "brygada",
                    "value": "017"
                },
                {
                    "key": "kierunek",
                    "value": "PKP Olszynka Grochowska"
                },
                {
                    "key": "trasa",
                    "value": "TP-OLS"
                },
                {
                    "key": "czas",
                    "value": "05:08:00"
                }
            ]
        },
        ...
        {
            "values": [
                {
                    "key": "symbol_2",
                    "value": "null"
                },
                {
                    "key": "symbol_1",
                    "value": "null"
                },
                {
                    "key": "brygada",
                    "value": "3"
                },
                {
                    "key": "kierunek",
                    "value": "PKP Olszynka Grochowska"
                },
                {
                    "key": "trasa",
                    "value": "TX-OLS"
                },
                {
                    "key": "czas",
                    "value": "23:50:00"
                }
            ]
        }
    ]
}
~~~

-------------------------------------
-------------------------------------

## dbstore_get
##### Coordinates of the stops

#### Required parameters
  - id=ab75c33d-3a26-4342-b36a-6e5fef0a3ac3
  - apikey=
  
#### Optional parameters
- sortBy= [ some 'id' ]
- page= [ e.g. 1 ]
- size= [ e.g. 5 ]

 #### Available data, with examples
- zespol - busstopId  
  &nbsp;&nbsp; '1872'
- slupek - busstopNr (Kuba: "refers to the id of a specific stop with the same name. E.g. there is a stop Radiowa-WAT 1 and Radiowa-WAT 2 (different directions). Sometimes there are 8 stops with the same name but they don’t have to start from 1.")   
  &nbsp;&nbsp; '01', '02', '81'
- nazwa_zespolu - busstop name   
  &nbsp;&nbsp; 'Wrzosowa', 'S\u0142oneczna', 'Rzeczna'
- id_ulicy - street id (??)    
  &nbsp;&nbsp; '1757', '0714'
- szer_geo - latitude   
  &nbsp;&nbsp; '52.419343'
- dlug_geo - longitude   
  &nbsp;&nbsp; '20.945165'
- kierunek - direction (Kuba: "Last stop’s name of a specific route determines direction.")
  &nbsp;&nbsp; 'Ko\u015bcielna', 'Nowodworska', 'Fabryczna'  
- obowiazuje_od - effective as of   
  &nbsp;&nbsp; '2020-06-01 00:00:00.0'

#### Sample output
(The actual output has 7446 stops when last checked (29-09-2020); the sample output below shows 3.)

~~~
{
    "result": [
        {
            "values": [
                {
                    "value": "1001",
                    "key": "zespol"
                },
                {
                    "value": "01",
                    "key": "slupek"
                },
                {
                    "value": "Kijowska",
                    "key": "nazwa_zespolu"
                },
                {
                    "value": "2201",
                    "key": "id_ulicy"
                },
                {
                    "value": "52.248455",
                    "key": "szer_geo"
                },
                {
                    "value": "21.044827",
                    "key": "dlug_geo"
                },
                {
                    "value": "al.Zieleniecka",
                    "key": "kierunek"
                },
                {
                    "value": "2020-06-01 00:00:00.0",
                    "key": "obowiazuje_od"
                }
            ]
        },
        {
            "values": [
                {
                    "value": "1001",
                    "key": "zespol"
                },
                {
                    "value": "02",
                    "key": "slupek"
                },
                {
                    "value": "Kijowska",
                    "key": "nazwa_zespolu"
                },
                {
                    "value": "2201",
                    "key": "id_ulicy"
                },
                {
                    "value": "52.249078",
                    "key": "szer_geo"
                },
                {
                    "value": "21.044443",
                    "key": "dlug_geo"
                },
                {
                    "value": "Z\u0105bkowska",
                    "key": "kierunek"
                },
                {
                    "value": "2020-06-01 00:00:00.0",
                    "key": "obowiazuje_od"
                }
            ]
        },
        ...
        {
            "values": [
                {
                    "value": "R-19",
                    "key": "zespol"
                },
                {
                    "value": "99",
                    "key": "slupek"
                },
                {
                    "value": "WYDZIA\u0141 W\u0141O\u015aCIA\u0143SKA",
                    "key": "nazwa_zespolu"
                },
                {
                    "value": "2575",
                    "key": "id_ulicy"
                },
                {
                    "value": "52.271236",
                    "key": "szer_geo"
                },
                {
                    "value": "20.968496",
                    "key": "dlug_geo"
                },
                {
                    "value": "WYDZIA\u0141 W\u0141O\u015aCIA\u0143SKA",
                    "key": "kierunek"
                },
                {
                    "value": "2020-06-01 00:00:00.0",
                    "key": "obowiazuje_od"
                }
            ]
        }
    ]
}
~~~


