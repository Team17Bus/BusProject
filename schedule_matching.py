

def match_arrival(schedule, arrival):
    """

    Args:
        schedule: the schedule for the day (pre-processed and cleaned up)
        arrival: the particular arrival event for which the scheduled arrival time needs to be estimated
        in the following format: [line, arrival time, stop_id]

    Returns: index of the corresponding arrival event in the schedule (stop_times)

    """

    # line_schedule is the part of the schedule that contains only the schedule for the particular line

    line_schedule = schedule[schedule['trip_id'].str.contains(arrival[0]+'_')]

    # todo: add calculation of difference between scheduled and real arrival time
    for index, row in line_schedule.iterrows():
        i = 1

    i = 0

    return i


def get_delay():
    return