from os import listdir

FOLDER = '/Volumes/KESU/Project_Bus/buses_per_day/'

files = listdir(FOLDER)

if '.DS_Store' in files:
    files.remove('.DS_Store')

file_list = []
for i in range(len(files)):
    filename = files[i]
    file_list.append(filename)

print(*file_list, sep=' ')