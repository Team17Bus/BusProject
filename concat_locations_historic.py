from os import listdir
from collections import defaultdict

FOLDER_IN = '/Volumes/KESU/Project_Bus/buses'
FOLDER_OUT = '/Volumes/KESU/Project_Bus/buses_per_day/'

files = listdir(FOLDER_IN)

if '_opis.txt' in files:
    files.remove('_opis.txt')
if 't_2020_08_31_23_30' in files:
    files.remove('t_2020_08_31_23_30')
if 't_2020_10_01_00_30' in files:
    files.remove('t_2020_10_01_00_30')

files.sort()

dict_per_day = defaultdict(list)
for i in range(len(files)):
    file = files[i]
    file_split = file.split('_')
    curr_day = file_split[3]
    dict_per_day[curr_day].append(file)


# source: https://stackoverflow.com/questions/13613336/python-concatenate-text-files

for day in dict_per_day:
    filenames = dict_per_day[day]
    out_filename = FOLDER_OUT + '2020_09_' + day + '.csv'
    with open(out_filename, 'w') as outfile:
        for fname in filenames:
            full_path = FOLDER_IN + '/' + fname
            with open(full_path) as infile:
                for line in infile:
                    outfile.write(line)