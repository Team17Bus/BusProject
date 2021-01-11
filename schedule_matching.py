import pandas as pd

from datetime import timedelta

debug = True


def match_schedule(schedule, arrivals):

    line_grouped = arrivals.groupby(['bus_line'])

    for line, line_group in line_grouped:
        if debug: print(line)

        grouped = line_group.groupby(['bus_brigade'])
        indexes_to_delete = []

        for brig, group in grouped:  # the grouping by does not make the algorithm particularly faster

            if debug: print("Next Group")
            if not debug: print(line,'+',brig)

            prev_ind_i = []
            prev_stop_seq = []

            this_ind_i = []
            this_stop_seq = []
            this_stop_zespol = ""

            keep_o = 0
            keep_p = 0
            keep_q = 0

            for ind_i, row_i in group.iterrows():

                stop_seq = ""
                prev_scheduled_time = None

                # print(f"ind = {ind_i}    stop = {row_i['stop_zespol']}")
                print('THIS',this_stop_zespol) #up to here similar performance
                print('PREV',keep_p)

                if not this_stop_zespol:  # zespol is not yet identified
                    this_stop_zespol = row_i['stop_zespol']
                    this_ind_i.append(ind_i)
                elif this_stop_zespol == row_i['stop_zespol']:  # zespol has not changed
                    this_ind_i.append(ind_i)
                else:  # arrived at the next zespol
                    # (figure out which of all the previously recorded slupek's is the correct one)

                    if (len(prev_stop_seq) > 0):  # it could be that prev_stop is empty then all this is not necessary
                        print(prev_stop_seq)
                        print(this_stop_seq)
                        keep_p = 0
                        maxdiff = 3 # at most 3 stops missed by ASB

                        new_keep_q = 0

                        for p in prev_stop_seq:
                            for q in this_stop_seq:
                                if debug: print('difference stop seq = ',q-p)

                                if ((q - p) > 0) and ((q - p) < maxdiff):
                                    if debug: print('--- first stop: ', p, 'second stop: ', q, '---')
                                    if debug: print('--- first stop: ', p, 'previous stop: ', keep_o, '---')
                                    #if ((p-keep_o) < 3):
                                    keep_p = p
                                    new_keep_q = q
                                    maxdiff = (q - p)

                                #if (q - p == 1): #todo: this is the point why some matches are not found
                                #    if debug: print('--- first stop: ', p, 'second stop: ', q, '---')
                                #    keep = p
                        #if keep_p != 0: print(arrivals['scheduled_time'].loc[prev_ind_i[prev_stop_seq.index(keep_p)]])
                        #if keep_p != 0: prev_stop_seq = arrivals['scheduled_time'].loc[prev_ind_i[prev_stop_seq.index(keep_p)]]

                        if keep_p == 0 and keep_q != 0: print('NOT SET', prev_stop_seq, keep_q, prev_ind_i)
                        if keep_p == 0 and keep_q != 0:
                            del prev_ind_i[prev_stop_seq.index(keep_q)]
                            keep_o = keep_q

                        keep_q = new_keep_q

                        if keep_p != 0: del prev_ind_i[prev_stop_seq.index(keep_p)]
                        if keep_p != 0: del prev_stop_seq[prev_stop_seq.index(keep_p)]

                        # if keep == 0: print('stops to remove: ', prev_stop_seq)  # todo: what was the point of this

                        indexes_to_delete.append(prev_ind_i)

                    prev_ind_i = this_ind_i.copy()
                    this_ind_i = [ind_i]
                    prev_stop_seq = this_stop_seq.copy()
                    this_stop_seq = []
                    this_stop_zespol = row_i['stop_zespol']

                ### this section finds the closest scheduled arrival time to the recorded arrival time
                old_difference = timedelta(hours=1).total_seconds()

                for ind_j, row_j in schedule.loc[(schedule['stop_id'] == arrivals['stop_id'].loc[ind_i]) &
                                                 (schedule['lines'] == arrivals['bus_line'].loc[ind_i])].iterrows():
                    # for all stops in the timetable that have the same stop_id

                    difference = (row_j['arrival_time'] - row_i['arrival_time']).total_seconds()
                    #if debug: print('DIFF = ',difference)
                    if abs(difference) < old_difference:
                        old_difference = abs(difference)

                        #this arrival time should be after the previous arrival event #todo not sure what happens if this is not the case
                        #if(prev_scheduled_time!=None and row_j['arrival_time']>prev_scheduled_time):

                        arrivals['scheduled_time'].loc[ind_i] = row_j['arrival_time']
                        arrivals['stop_seq'].loc[ind_i] = row_j['stop_sequence']
                        stop_seq = row_j['stop_sequence']

                #
                if stop_seq != "": this_stop_seq.append(stop_seq)

            ### for the second-to-last and last stop
            keep_p = 0
            keep_q = 0
            for p in prev_stop_seq:
                for q in this_stop_seq:
                    if debug: print('difference last stop seq = ', q - p)
                    if (q - p == 1):
                        if debug: print('first stop: ', p, 'second stop: ', q)
                        keep_p = p
                        keep_q = q

            if keep_p != 0: del prev_ind_i[prev_stop_seq.index(keep_p)]
            if keep_q != 0: del this_ind_i[this_stop_seq.index(keep_q)]
            indexes_to_delete.append(prev_ind_i)
            indexes_to_delete.append(this_ind_i)

            for a in indexes_to_delete:
                arrivals['scheduled_time'].loc[a] = None

            latest_arr_time = None

            for ind_k, row_k in group.iterrows():

                if not(arrivals['scheduled_time'].loc[ind_k] is None):
                    if latest_arr_time is None:
                        latest_arr_time = arrivals['scheduled_time'].loc[ind_k]
                    # elif latest_arr_time > arrivals['scheduled_time'].loc[ind_k]: #in this case the scheduled time set at a later bus stop is actually earlier
                        # arrivals['scheduled_time'].loc[ind_k] = None
                    else: latest_arr_time = arrivals['scheduled_time'].loc[ind_k]


        #for a in indexes_to_delete:
            #arrivals['scheduled_time'].loc[a] = None

    return arrivals

    # General approach: try to prove that a scheduled stop is not valid and that a found arrival is not valid
    # In terms of time and in terms of stop sequence
    # If it is valid in both cases, then it must be the correct stop

def match_schedule2(schedule, arrivals):
    line_grouped = arrivals.groupby(['bus_line'])

    for line, line_group in line_grouped: # for every line
        if debug: print(line)

        grouped = line_group.groupby(['bus_brigade'])

        for brig, group in grouped: # for every brigade

            stop_sequence = start_stop_sequence(schedule, group)
            stop_sequence_previous = stop_sequence-1
            stop_zespol = ''

            max_sequence = 0

            old_sequence_difference = 0

            change_stop_sequence = False

            index_previous = 0

            n = 0

            for ind_i, row_i in group.iterrows():

                # in case the zespol changed we need to compare this arrival with the stop sequence of the previous arrival
                # which is then considered to be valid
                # in case the zespol did not change, we need to figure out wether this or the previous record is better

                changed_zespol = True
                if stop_zespol == arrivals['stop_zespol'].loc[ind_i] : changed_zespol = False

                # It might be the case that this arrival record is a better match than the previous
                # This can only happen when the zespol did not change
                valid_match_previous = True

                match_found = False # boolean used to know if at least any match in the schedule has been found

                old_time_difference = timedelta(hours=1).total_seconds()

                for ind_j, row_j in schedule.loc[(schedule['stop_id'] == arrivals['stop_id'].loc[ind_i]) &
                                                 (schedule['lines'] == arrivals['bus_line'].loc[ind_i])].iterrows():
                    # only iterate over stops in the timetable that have the same stop_id and the same line

                    # To prove whether a stop in the schedule is valid, based on time and sequence
                    valid_stop_time = False
                    valid_stop_seq = False

                    sequence_difference = row_j['stop_sequence'] - stop_sequence
                    sequence_difference_previous = row_j['stop_sequence'] - stop_sequence_previous
                    time_difference = (row_j['arrival_time'] - row_i['arrival_time']).total_seconds()
                    # if debug: print('DIFF = ',difference)

                    # if this difference is less than the previous difference - the stop is potentially valid
                    if abs(time_difference) < old_time_difference:
                        valid_stop_time = True
                        if max_sequence < row_j['stop_sequence']: max_sequence = row_j['stop_sequence']
                        arrivals['stop_seq'].loc[ind_i] = row_j['stop_sequence']

                    # if this difference is in the correct range (+1, +2 or +3 in stop sequence) - the stop is potentially valid
                    # todo investigate the consequence of use of this number (it prevents matching 17 following on 3)
                    # However it is corrected in some cases by the next conditional - but that only works if the stops are listed in the right order
                    # Therefore this bound should be as low as possible.
                    # But from (small) investigations it appears to be working better when this bound is not to tight, as quite some stops can be missed
                    # For now tried to solve this by loosening the bound increasingly when it takes more time to find a match (not sure)
                    # Also figure out what happens at the beginning: it will pick the first arrival that has a sequence of 0-4
                    if sequence_difference > 0 and sequence_difference < (4+n):
                        valid_stop_seq = True


                    # this stop is also valid (in terms of sequence) with respect to the stop before the previous one
                    # this only needs to be checked when the zespol did not change
                    if not changed_zespol:
                        if debug: print('seq diff: ', sequence_difference, 'prev seq diff: ',
                                        sequence_difference_previous)
                        #if sequence_difference_previous < sequence_difference:
                        if sequence_difference_previous > 0 and sequence_difference_previous < old_sequence_difference:
                                #if debug : print('seq diff: ',sequence_difference,'prev seq diff: ',sequence_difference_previous)
                            valid_stop_seq = True
                            if valid_stop_time: valid_match_previous = False

                    # todo maybe add the option that when the zespol did change and the sequence did not, but the time is better
                    # in which case the better time is used

                    # when the bus reached the end of line
                    # there is no valid sequence possible according to above
                    # instead, the sequence one lower than the maximum will appear

                    # todo check validity
                    if (row_j['stop_sequence'] == stop_sequence_previous or row_j['stop_sequence'] == stop_sequence_previous-1) and row_j['stop_sequence'] < stop_sequence:
                        if debug: print('TURNAROUND', row_j['stop_sequence'], stop_sequence, max_sequence)

                        # by keeping track of the highest sequence number that has been found, a too early turnaround is killed
                        if row_j['stop_sequence'] - max_sequence > -3:
                            change_stop_sequence = True
                        elif debug: print('PRANK',row_j['stop_sequence'] - max_sequence)

                    # the stop is valid, but there still might exist a better match
                    if valid_stop_time and valid_stop_seq:
                        old_time_difference = abs(time_difference)
                        best_time = row_j['arrival_time']
                        best_sequence = row_j['stop_sequence']
                        best_sequence_difference = sequence_difference
                        match_found = True

                # It turned out that the previous match was not correct
                # Because this match has a better sequence for the same zespol
                if not valid_match_previous:
                    if debug: print('delete: time = ', arrivals['scheduled_time'].loc[index_previous],
                                    ' sequence = ', arrivals['stop_seq'].loc[index_previous])
                    arrivals['scheduled_time'].loc[index_previous] = None
                    stop_sequence = stop_sequence_previous
                    # arrivals['stop_seq'].loc[ind_i-1] = None

                # match found is only set to true when best_time and best_sequence are initialized
                if match_found :
                    # writing the scheduled arrival time and sequence in the dataframe
                    arrivals['scheduled_time'].loc[ind_i] = best_time
                    arrivals['stop_seq'].loc[ind_i] = best_sequence

                    # update the sequence where the bus is at
                    stop_sequence_previous = stop_sequence
                    stop_sequence = best_sequence
                    old_sequence_difference = best_sequence_difference

                    # update the zespol where the bus is at
                    stop_zespol = arrivals['stop_zespol'].loc[ind_i]

                    index_previous = ind_i

                    n = 0

                    #if best_sequence>max_sequence: max_sequence = best_sequence

                    if debug: print('match : time = ',best_time,' sequence = ',best_sequence)
                else : n = n+1

                # it has been determined that the bus reached the end of the line
                # reset the stop sequence parameters

                # it has been investigated to pick up the arrival time of stop with sequence 2,
                # it is not guaranteed that stop sequence = 2 is always present in the found arrivals
                if change_stop_sequence :
                    stop_sequence = 1
                    stop_sequence_previous = 0
                    change_stop_sequence = False
                    max_sequence = 0
                    if debug: print('RESET SEQUENCE')

                # this method fails if the bus arrives in the wrong order at the bus stops by the ASB method

    return

#a function to figure out what the starting number of the sequence is
def start_stop_sequence(schedule, group_arrivals):
    no_of_stops = 0
    this_sequence = 0

    zespol1 = ""
    sequence1 = []
    zespol2 = ""
    sequence2 = []

    # determine the possible sequences for z1 and z2 (only mixed up if there is an appearance of z3 before the latest z2)
    for ind_i, row_i in group_arrivals.iterrows():

        if no_of_stops>2: break

        if no_of_stops==0:
            zespol1 = row_i['stop_zespol']
            no_of_stops = no_of_stops+1
            if debug: print('first stop:',zespol1)
        if no_of_stops==1:
            if zespol1 != row_i['stop_zespol']:
                zespol2 = row_i['stop_zespol']
                no_of_stops = no_of_stops+1
                if debug: print('second stop:',zespol2)
            elif debug: print('first stop again:', zespol1)
        if no_of_stops==2:
            if zespol1 != row_i['stop_zespol'] and zespol2 != row_i['stop_zespol']:
                no_of_stops = no_of_stops+1
                if debug: print('third stop')
            elif debug: print('first or second stop:',row_i['stop_zespol'])

        old_time_difference = timedelta(hours=1).total_seconds()

        for ind_j, row_j in schedule.loc[(schedule['stop_id'] == group_arrivals['stop_id'].loc[ind_i]) &
                                         (schedule['lines'] == group_arrivals['bus_line'].loc[ind_i])].iterrows():
            time_difference = (row_j['arrival_time'] - row_i['arrival_time']).total_seconds()

            if abs(time_difference) < old_time_difference:
                this_sequence = row_j['stop_sequence']

        if zespol1 == row_i['stop_zespol']: sequence1.append(this_sequence)

        if zespol2 == row_i['stop_zespol']: sequence2.append(this_sequence)

    #determine the correct order - and what z1 must be
    sequence_start = 0
    maxdiff = 4

    for p in sequence1:
        for q in sequence2:
            if debug: print('difference stop seq = ', q - p)
            if ((q - p) > 0) and ((q - p) < maxdiff):
                sequence_start = p
                maxdiff = q - p
                if debug: print('sequence start set to:',sequence_start)

    return (sequence_start - 1)