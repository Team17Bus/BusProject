import datetime

debug = True

def match_arrival(schedule, arrival):
    """

    Args:
        schedule: the schedule for the day (pre-processed and cleaned up)
        arrival: the particular arrival event for which the scheduled arrival time needs to be estimated
        in the following format: [line, arrival time, stop_id]

    Returns: schedule with the added actual arrival time

    """

    # line_schedule is the part of the schedule that contains only the schedule for the particular line

    line_schedule = schedule[schedule['trip_id'].str.contains(arrival[0 ] +'_')]

    i = -1

    # Check for exact match
    # the checking for i != 0 is there to check if we do not have more than one corresponding arrival event
    for index, row in line_schedule.iterrows():
        if row['arrival_time'] == arrival[1] and row['stop_id'] == arrival[2]:
            if i != 1:
                row['real_arr_time'] = arrival[1] # todo: add some check if there is not a value stored yet,
                                                    # this should throw an error. As this means that we want to match
                                                    # two actual arrivals with one scheduled arrival
                if debug: print('exact match found', row)
            else:
                print('multiple exact matches have been found')

    if i == -1: print('no exact match found')
    else: return schedule

    # find the scheduled arrival time that is closest (in absolute value) to the real arrival time

    # assuming the biggest dalay that can occur in a file is 2 hours
    old_difference = datetime.timedelta(hours= 2)

    for index, row in line_schedule.iterrows():
        if row['stop_id'] == arrival[2]:
            difference = row['arrival_time'] - arrival[1]

            # make sure to only have positive differences todo: is this valid
            if difference < (arrival[1] - row['arrival_time']):
                difference = arrival[1] - row['arrival_time']

            # if this difference is smaller than the previous one, store the arrival time
            if difference < old_difference:
                old_difference = difference
                row['real_arr_time'] = arrival[1]
                if debug: print('Closest arrival: ', row['arrival_time'], arrival[1])

    return schedule


def get_delay():
    return
