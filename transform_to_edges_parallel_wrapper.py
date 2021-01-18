from process_matched_data import edges_transform
from os import listdir
import sys

# input arguments
# 1. filename of matched arrivals
# 2. folder to which output files should be written

kwargs = sys.argv
assert len(kwargs) == 3, "Please only provide 2 arguments (folder in which matched arrivals are located & folder to which output files should be written)"

FILE, FOLDER_OUT = kwargs[1], kwargs[2]
file_path = FILE.split('/')
filename = file_path[-1]
if len(file_path) == 1:
    folder_in = ''
else:
    folder_in = file_path[:-1][0]

print(filename)
print(folder_in)
edges_transform(filename, folder_in, FOLDER_OUT)