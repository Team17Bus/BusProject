import requests
import json
from api_key import my_api_key
import pandas as pd
import numpy as np
from copy import deepcopy

# Assign your api key to the variable 'my_api_key' in the file 'api_key.py'
API_KEY = my_api_key
MAIN_URL = 'https://api.um.warszawa.pl/api/action/'


# helper function
def make_request(end_link, params):
    """ Function that makes a request to the api and returns the data queried if all parameters are valid
            Note: make sure to fill in your api key for the global variable API_KEY above

    Args:
        end_link (string): sub-link to be added to the main link (https://api.um.warszawa.pl/api/action), 
                            for example 'dbstore_get' or 'busestrams_get' (don't include '/')
        params (dict): dictionary with all parameters and their values for the api request

    Returns:
        requests.models.Response

    Example call:
        make_request('busestrams_get', dict(type=1))

    """
    url = MAIN_URL + end_link
    response = requests.get(url, params=params)
    return response

# helper function
def json_print(response):
    """ Checks whether request was successful and if so, 'pretty' prints json object contained in the response object
    Args:
        response (requests.models.Response): response object returned from api request
    """
    if response:
        print('Response OK')
        print(json.dumps(response.json(), sort_keys=True, indent=4))
        if(response.json()["result"] == "false"):
            print('REQUEST FAILED - check api_key and/or other parameters')
    else:
        print('Response Failed')
        print(f'Status code: {response.status_code}')

# helper function
def dict_json_to_pd(json_object):
    """Returns the json_object obtained by the dbstore api request in the form of a pandas DataFrame
    Args:
        json_object
    Returns:
        pandas DataFrame
    """

    data = json_object['result']
    n = len(data)
    lst_data = [{} for _ in range(n)]
    dict_entry = {}
    for i in range(n):
        entry = data[i]['values']
        for attr in entry:
            k = attr['key']
            v = attr['value']
            dict_entry[k] = v
        lst_data[i] = deepcopy(dict_entry)
        dict_entry.clear()
    return pd.DataFrame(lst_data)

# helper function
def line_json_to_lst(json_object):
    data = json_object['result']
    n = len(data)
    lst_data = ['' for _ in range(n)]
    for i in range(n):
        lst_data[i] = data[i]['values'][0]['value']
    return lst_data

# helper function
def zespol_json_to_lst(json_object):
    data = json_object['result']
    n = len(data)
    lst_data = ['' for _ in range(n)]
    for i in range(n):
        key_value_pairs = data[i]['values']
        for kv in key_value_pairs:
            if kv['key'] == 'zespol':
                lst_data[i] = kv['value']
    return lst_data


def busestrams_get(other_params=None, return_pd=True):
    """ Returns the json object or pandas dataframe obtained by the api request to 'https://api.um.warszawa.pl/api/action/busestrams_get'
    Args:
        other_params(dict): for specifying the other parameters to be included in the api request
        return_pd(boolean): True if user wants to return a pandas dataframe, False if user wants a json object
    Returns:
        json object or pandas dataframe obtained by the api request
    Example call:
        busestrams_get(dict(type=1))
    """
    end_link = 'busestrams_get'
    resource_id = 'f2e5503e-927d-4ad3-9500-4ab9e55deb59'
    if other_params is None:
        other_params = {}
    other_params['resource_id'] = resource_id
    other_params['apikey'] = API_KEY
    r = make_request(end_link, other_params)
    if return_pd:
        return pd.DataFrame(r.json()['result'])
    else:
        return r.json()


def dbstore_get(other_params=None, return_pd=True):
    """ Returns the json object or pandas dataframe obtained by the api request to 'https://api.um.warszawa.pl/api/action/dbstore_get'
        This is a json object containing the coordinates of all the stops.
    Args:
        other_params(dict): for specifying the other parameters to be included in the api request
        return_pd(boolean): True if user wants to return a pandas dataframe, False if user wants a json object
    Returns:
        json object or pandas dataframe obtained by the api request
    Example call:
        dbstore_get(dict(size=5), print_flag=False)
    """
    end_link = 'dbstore_get'
    id_param = 'ab75c33d-3a26-4342-b36a-6e5fef0a3ac3'
    if other_params is None:
        other_params = {}
    other_params['id'] = id_param
    other_params['apikey'] = API_KEY
    r = make_request(end_link, other_params)
    r_json = r.json()
    if return_pd:
        return dict_json_to_pd(r_json)
    else:
        return r_json


def dbtimetable_get(other_params=None, return_pd=True):
    """ Returns the json object or pandas dataframe / python list object obtained by the api request to 'https://api.um.warszawa.pl/api/action/timetable_get'
        Depending on the parameters given, one of the following data is returned:
            - timetable for a specific line for a busstopId and a busstopNr     (if 'line', 'busstopId', 'busstopNr' provided)
            - set of stops                                                      (if 'name' provided)
            - lines available at a stop with busstopId and busstopNr            (if 'busstopId', 'busstopNr' provided)
    Args:
        other_params(dict): for specifying the other parameters to be included in the api request
        return_pd(boolean): True if user wants to return a pandas dataframe, False if user wants a json object
    Returns:
        json object or pandas dataframe obtained by the api request
    Example calls:
            - Retrieving the line list for the Marszałkowska stop  (busstopId = 7009) and bar number 01 (busstopNr = 01) and line 523 (line = 523)
                dbtimetable_get(dict(busstopId='7009', busstopNr='01', line='523'))
            - Retrieving the line list for the Marszałkowska stop (busstopId = 7009) and bar number 01 (busstopNr = 01)
                dbtimetable_get(dict(busstopId='7009', busstopNr='01'))
            - Retrieving the line list for the stop "Marszałkowska"
                dbtimetable_get(dict(name='Marsza\u0142kowska'))
    """

    end_link = 'dbtimetable_get'
    request_type = ''

    # Request: timetable for a specific line for a busstopId and a busstopNr
    if 'line' in other_params:
        request_type = 'timetable'
        id_param = 'e923fa0e-d96c-43f9-ae6e-60518c9f3238'
    # Request: set of stops with 'name'
    elif 'name' in other_params:
        request_type = 'set_of_stops'
        id_param = 'b27f4c17-5c50-4a5b-89dd-236b282bc499'
    # Request: lines available at a stop with busstopId and busstopNr
    else:
        request_type = 'line_list'
        id_param = '88cd555f-6f31-43ca-9de4-66c479ad5942'

    other_params['id'] = id_param
    other_params['apikey'] = API_KEY
    r = make_request(end_link, other_params)
    r_json = r.json()
    if return_pd:
        #TODO: write function so that pandas DataFrame / python list object is returned
        if request_type == 'line_list':
            return line_json_to_lst(r_json)
        elif request_type == 'set_of_stops':
            return zespol_json_to_lst(r_json)
        else:
            return dict_json_to_pd(r_json)
    else:
        return r_json()




def main():
    # Example calls (uncomment and print to see the results):

    # df = busestrams_get(dict(type=1))

    # df = dbstore_get()

    # retrieving the line list for the Marszałkowska stop  (busstopId = 7009) and bar number 01 (busstopNr = 01) and line 523 (line = 523)
    # df = dbtimetable_get(dict(busstopId='7009', busstopNr='01', line='523'))

    # retrieving the line list for the Marszałkowska stop (busstopId = 7009) and bar number 01 (busstopNr = 01)
    # df = dbtimetable_get(dict(busstopId='7009', busstopNr='01'))

    # retrieving all the 'zespol' (??) for the busstop 'Marysin'
    # df = dbtimetable_get(dict(name='Marysin'))

    # pd.set_option('display.max_columns', None)

    pass



if __name__ == "__main__":
    main()
