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